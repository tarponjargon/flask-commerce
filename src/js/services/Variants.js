import { arrayUnique, copy, formatPrice } from "./Utils";

export default class Variants {
  constructor(variantMap, menuLen) {
    this.variantMap = variantMap;
    this.menuLen = menuLen;

    // for getter/setter/change notification on selected
    this.ops = {
      localSelected: [],
      selectedListener: function (val) {},
      set selected(val) {
        this.localSelected = val;
        this.selectedListener(val);
      },
      get selected() {
        return this.localSelected;
      },
      registerListener: function (listener) {
        this.selectedListener = listener;
      },
    };

    this.firstTouchedIndex = -1;
    this.lastTouchedIndex = -1;
  }

  init = () => {
    this.ops.selected = copy(Array.apply(null, Array(this.menuLen))); // creates array with length, values are null

    let isNla = this.checkNla();
    if (!isNla) {
      // listen for clicks on option buttons
      Array.prototype.forEach.call(document.querySelectorAll("[data-option-code]"), (el) => {
        if (!el.hasListener) {
          el.hasListener = true;
          el.addEventListener("click", this.onSelectOption, false);
        }
      });

      // emit events on selection/all selected
      this.ops.registerListener((sel) => {
        let selectedEvent = new CustomEvent("optionselected", {
          bubbles: true,
          detail: { selected: sel },
        });
        document.dispatchEvent(selectedEvent);
        if (this.isAllSelected()) {
          let allSelectedEvt = new CustomEvent("allselected", {
            bubbles: true,
            detail: { selected: sel },
          });
          document.dispatchEvent(allSelectedEvt);
        } else {
          let hasUnselectedEvt = new CustomEvent("hasunselected", {
            bubbles: true,
            detail: { selected: sel },
          });
          document.dispatchEvent(hasUnselectedEvt);
        }
      });
    }
  };

  getSelected = () => {
    return this.ops.selected;
  };

  getFirstTouchedIndex = () => {
    return this.firstTouchedIndex;
  };

  getLastTouchedIndex = () => {
    return this.lastTouchedIndex;
  };

  preScan = () => {
    for (let i = 0; i < this.ops.selected.length; i++) {
      const $availableEls = $(`[data-option-index="${i}"]:not([data-option-nla="1"])`);
      // if there is only one option or one non-NLA option, preselect it
      if ($availableEls.length === 1) {
        // simulating a click on the only available variant is the best option here.
        // it will trigger image switches and price updates (if there are any)
        const evt = new Event("click");
        $availableEls[0].dispatchEvent(evt);
      }
    }
    this.updateMatrix();
    this.updateSelectedButtons();
  };

  getSkuidObject = () => {
    if (!this.isAllSelected()) return undefined;
    return this.variantMap.filter((i) => {
      return JSON.stringify(i.codeList) === JSON.stringify(this.ops.selected);
    })[0];
  };

  removeParen = (text) => {
    return text.replace(/ *\([^)]*\) */g, "");
  };

  isUnselected = () => {
    return this.ops.selected.every(function (x) {
      return x === null;
    });
  };

  isAllSelected = () => {
    return this.ops.selected.every(function (x) {
      return x !== null;
    });
  };

  countSelected = () => {
    return this.ops.selected.filter(function (x) {
      return x !== null;
    }).length;
  };

  getFirstValue = () => {
    return this.isUnselected()
      ? null
      : this.ops.selected.filter(function (x) {
          return x !== null;
        })[0];
  };

  checkNla = () => {
    let legalSkus = this.getLegalSkus(this.ops.selected);
    if (!legalSkus.length) {
      Array.prototype.forEach.call(document.querySelectorAll("[data-option-index]"), function (el) {
        el.setAttribute("data-option-nla", "1");
      });
    }
    //console.log("init legalSkus", legalSkus);
    return legalSkus.length ? false : true;
  };

  // get the readable name (option set type) for given option index.  used for validation message ("select SIZE before adding")
  getOptionType = (index) => {
    let el = document.querySelector('[data-matrix-index="' + index + '"]');
    return el ? el.getAttribute("data-menu-type") : null;
  };

  // query variant map to get all legal skus (combination possibilities) based on what codes ahve already been selected
  getLegalSkus = (codes) => {
    let conditions = [];
    //let codes = copy(selected);
    //codes[lastTouchedIndex] = null; // always exclude the code of current menu from the criteria

    //console.log("getting legal skus for selected", codes);
    codes.forEach(function (val, i) {
      if (val) conditions.push([i, val]);
    });

    // private func that queries (filters) the variantMap codeLists to return "legal" skus
    const queryVmap = (conditions) => {
      return this.variantMap.filter(function (v) {
        let result = true;
        if (v.nla) return false;
        for (let i = 0; i < conditions.length; i++) {
          if (v["codeList"][conditions[i][0]] != conditions[i][1]) result = false;
        }
        return result;
      });
    };
    return queryVmap(conditions);
  };

  // returns an array of arrays. in the outer array, each position is an options set.
  // each inner array contains the options available in that set.
  getLegalSets = (curSelected) => {
    let legalSets = [];
    let legalSkus = this.getLegalSkus(curSelected);
    if (!legalSkus.length) return [];
    for (let i = 0; i < curSelected.length; i++) {
      let legalsSetsIndex = legalSkus.map(function (x) {
        return x.codeList[i];
      });
      let legalSkusArr = legalsSetsIndex.length ? arrayUnique(legalsSetsIndex) : [];
      legalSets.push(legalSkusArr);
    }
    //console.log("legalSkus", legalSkus);
    //console.log("legalSets", legalSets);
    return legalSets;
  };

  // update button matrix UI to show selected state
  updateSelectedButtons = () => {
    for (let i = 0; i < this.ops.selected.length; i++) {
      document.querySelector('[data-selected-name="' + i + '"]').innerText = "";
      Array.prototype.forEach.call(
        document.querySelectorAll('[data-option-index="' + i + '"]'),
        (el) => {
          // generate button title
          let nla = el.getAttribute("data-option-nla");
          let disabled = el.classList.contains("disabled") ? true : false;
          let dataTitle = el.getAttribute("data-title");
          let title =
            disabled || nla === "1" ? dataTitle + " Not Available" : "Select " + dataTitle;

          // set selected state if conditions met

          el.setAttribute("data-option-selected", "0");
          if (
            this.ops.selected[i] &&
            this.ops.selected[i] === el.getAttribute("data-option-code")
          ) {
            el.setAttribute("data-option-selected", "1");
            document.querySelector('[data-selected-name="' + i + '"]').innerText = this.removeParen(
              el.getAttribute("data-option-name")
            );
            title = "Selected " + el.getAttribute("data-title");
          }

          el.setAttribute("title", title);
        }
      );
    }
  };

  // update the matrix in the UI to reflect availability
  // returns a (possibly) mutated selections
  updateMatrix = () => {
    let legalSets = [];

    let curSelected = this.ops.selected;

    // call legalSets subtractively with curSelected (removing from the front) until the end or a set of legalSets is returned
    for (let x = 0; x < curSelected.length; x++) {
      //console.log("LS check", x);
      //console.log("lasttouched", this.lastTouchedIndex);
      legalSets = this.getLegalSets(curSelected);
      if (legalSets.length) break;
      // if possible, do not unselect an option the customer has JUST selected.
      // instead, unselect previous options.
      const delIdx =
        this.lastTouchedIndex && this.lastTouchedIndex < this.ops.selected.length - 1
          ? this.lastTouchedIndex + 1
          : x;
      curSelected[delIdx] = null;
    }

    legalSets.forEach(function (options, i) {
      Array.prototype.forEach.call(
        document.querySelectorAll('[data-option-index="' + i + '"]'),
        function (el) {
          el.classList.remove("disabled"); // reset
          let curCode = el.getAttribute("data-option-code");
          if (curSelected[i]) {
            // do nothing to the other options within selected sets.
            // even though they are technically unavailable (you can't order 2 options within the same set at the same time),
            // disabling them makes it appear that they are not available at all
          } else {
            // if current option is not in the list of "legal" options within this set, disable

            if (options.indexOf(curCode) === -1) {
              el.classList.add("disabled");
            }
          }
        }
      );
    });
    return curSelected;
  }; // end updateMatrix

  // update current state when an option box is clicked,
  // then call updateMatrix to update the whole UI based on availability after selection
  onSelectOption = (e) => {
    let buttonEl = e.target;
    let optionIndex = parseInt(buttonEl.getAttribute("data-option-index"));
    let code = buttonEl.getAttribute("data-option-code");
    let nla = buttonEl.getAttribute("data-option-nla");
    let disabled = buttonEl.classList.contains("disabled") ? true : false;
    if (disabled || nla === "1") return false;

    // update local state vars
    this.lastTouchedIndex = optionIndex;
    if (this.firstTouchedIndex > -1 && !this.ops.selected[this.firstTouchedIndex])
      this.firstTouchedIndex = this.getFirstValue();
    if (this.firstTouchedIndex === -1 && this.isUnselected()) this.firstTouchedIndex = optionIndex;
    this.ops.selected[optionIndex] = this.ops.selected[optionIndex] === code ? null : code;

    // calculate legal options
    let newSelected = this.updateMatrix();
    this.ops.selected = newSelected;
    this.updateSelectedButtons(this.ops.selected); // update buttons in UI

    // reset state if post-calc selected is now empty
    if (this.isUnselected()) this.firstTouchedIndex = -1;
  }; // end onSelectOption

  setMaxPrice = (el) => {
    if (!el) return;
    const basePrice = parseFloat(el.getAttribute("data-price"));
    const maxPrice = this.getMaxPrice(basePrice);
    if (!maxPrice || basePrice >= maxPrice) return;
    const origText = el.innerText;
    const newText = origText + "-" + formatPrice(maxPrice);
    el.innerText = newText;
    el.setAttribute("data-default", newText);
  };

  setPriceRange = () => {
    const priceEls = document.querySelectorAll('.product-details [data-js="detail-item-price"]');
    if (!priceEls.length) return;
    priceEls.forEach((priceEl) => {
      const origPriceEl = priceEl.querySelector(".price-original");
      const newPriceEl = priceEl.querySelector(".price-sale");
      const regularPriceEl = priceEl.querySelector(".regular-price");
      [origPriceEl, newPriceEl, regularPriceEl].forEach((el) => {
        if (el) this.setMaxPrice(el);
      });
    });
  };

  getMaxPrice = (basePrice = this.getBasePrice()) => {
    /* the pricechange array looks like this:
      [0,0,0],
      [0,5,9],
      [0,0,2]
      You basically have to tic-tac-toe total all combinations, create a list of prices,
      then sort it to get max
    */
    const pricechangeArrays = [];
    this.variantMap.forEach((i) => {
      if (i.nla === 0) pricechangeArrays.push(i.pricechanges);
    });
    const prices = [];
    pricechangeArrays.forEach((pricechangeArr) => {
      let curPrice = basePrice;
      for (let i = 0; i < this.menuLen; i++) {
        curPrice += pricechangeArr[i];
      }
      prices.push(curPrice);
    });
    if (!prices.length) return;
    prices.sort((a, b) => a - b);
    const maxPrice = prices[prices.length - 1];
    return maxPrice;
  };

  getBasePrice = () => {
    // I am getting base price from the DOM (rather than variantMap)
    // b/c the dom has any discounts reflected
    const basePriceEls = document.querySelectorAll(
      '.product-details [data-js="detail-item-price"] [data-price]'
    );
    if (!basePriceEls.length) return;
    // the base price is the LAST data-price in the document
    const basePriceEl = basePriceEls[basePriceEls.length - 1];
    return parseFloat(basePriceEl.getAttribute("data-price"));
  };

  setVariantPriceChanges = () => {
    const basePrice = this.getBasePrice();
    const firstPricechangeEl = document.querySelector(
      '[data-pricechange]:not([data-pricechange=""])'
    );
    if (!firstPricechangeEl) return;
    const firstPriceChangeSet = firstPricechangeEl.getAttribute("data-option-index");

    document.querySelectorAll(`[data-option-index="${firstPriceChangeSet}"]`).forEach((el) => {
      const priceChangeStr = el.getAttribute("data-pricechange") || 0;
      const priceChange = parseFloat(priceChangeStr);
      if (priceChange > 0 || /[Gg]arment/.test(el.getAttribute("data-title"))) {
        // match: Option Name (Add $9.99)
        const regex = /^(.*?)(\s?\(Add \$\d+(\.\d+)?\))/gi;
        let newText = el.innerText.replace(regex, "$1");
        // match: Option Name - 50.99
        const regex2 = /^(.*?)(\s?\-\s\$?\d+(\.\d+)?)$/gi;
        newText = newText.replace(regex2, "$1");
        // match: Option Name ($50.99)
        const regex3 = /^(.*)\s?\(\$\d+(\.\d+)?\)$/gi;
        newText = newText.replace(regex3, "$1");
        const newPrice = basePrice + priceChange;
        const newPriceFormatted = formatPrice(newPrice);
        newText = newText + " (" + newPriceFormatted + ")";
        el.innerText = newText;
      }
    });
  };
} // end Variants class

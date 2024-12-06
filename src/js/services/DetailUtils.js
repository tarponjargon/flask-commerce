import { spinButton, unSpinButton, getBodyData } from "./Utils";
import Variants from "./Variants";
import messages from "./Messages";
import { fetchContent } from "./Ajax";

export const initMatrixVariants = function (el, switchGalleryImage, updateProductName) {
  // initializes matrix style options buttons if they exist in given element
  const menuLen = el.querySelectorAll("[data-matrix-index]").length;
  if (!window.vMap || !window.vMap.length || !menuLen) return false;
  const variants = new Variants(window.vMap, menuLen);
  variants.init();

  const availContainer = el.querySelector('[data-js="detail-item-availability"]');

  // set initial state
  el.querySelector("#add-to-cart-btn").disabled = true;
  if (variants.checkNla()) {
    availContainer.innerText = "No Longer Available";
    availContainer.className = "text-danger";
  }

  // set prices in buttons on first level of pricechanges
  variants.setVariantPriceChanges();

  // set pricerange
  // variants.setPriceRange();

  document.addEventListener(
    "optionselected",
    (e) => {
      //console.log("option selected", e.detail.selected);
      switchGalleryImage(e.detail.selected);
      updateProductName(e.detail.selected);
    },
    false
  );

  document.addEventListener(
    "allselected",
    (e) => {
      //console.log("all options selected", e.detail.selected);
      el.querySelector("#add-to-cart-btn").disabled = false;
      const s = variants.getSkuidObject();
      updateAvailability(availContainer, s.invlevel, s.invmessage);
    },
    false
  );

  document.addEventListener(
    "hasunselected",
    (e) => {
      //console.log("some options unselected", e.detail.selected);
      el.querySelector("#add-to-cart-btn").disabled = true;
      resetAvailability(availContainer);
    },
    false
  );

  // do an initial scan to update state to reflect what's obviously not available
  variants.preScan();
};

export const initPriceUpdateListener = function (el, skuid = el.getAttribute("data-detail-skuid")) {
  // handles both select menu style options and matrix button
  const optionsSelects = el.querySelectorAll(`form[data-add-item="${skuid}"] select`);
  Array.prototype.forEach.call(optionsSelects, (menu) => {
    menu.addEventListener("change", () => {
      setTimeout(() => {
        updatePrice(el, skuid);
      }, 200);
    });
  });
  const matrixButtons = el.querySelectorAll(
    `form[data-add-item="${skuid}"] [data-option-selected]`
  );
  Array.prototype.forEach.call(matrixButtons, (btn) => {
    btn.addEventListener("click", () => {
      setTimeout(() => {
        updatePrice(el, skuid);
      }, 200);
    });
  });
};

export const resetAvailability = function (availContainer) {
  var defaultMessage = availContainer.getAttribute("data-default-availability-string");
  var defaultClass = availContainer.getAttribute("data-default-availability-class");
  availContainer.innerText = defaultMessage;
  availContainer.className = defaultClass;
};

export const updateAvailability = function (availContainer, invlevel, invmessage) {
  //console.log(availContainer, invlevel, invmessage);
  if (!availContainer) return false;
  if (invlevel && !isNaN(invlevel)) invlevel = parseInt(invlevel);
  if (/Ships /.test(invmessage) || /Ready to /.test(invmessage)) {
    availContainer.innerText = invmessage;
    availContainer.className = "text-success";
  } else if (invlevel && invlevel >= 1 && invlevel <= 10) {
    availContainer.innerText = "Hurry! Only " + invlevel + " left in stock.";
    availContainer.className = "text-danger";
  } else if ((!invlevel || invlevel > 10) && invmessage) {
    if (/In stock/i.test(invmessage)) {
      availContainer.innerText = "In Stock & Ready to Ship";
      availContainer.className = "text-success";
    } else if (/Avail/.test(invmessage)) {
      availContainer.innerText = invmessage.replace("Avail ", "Available ");
      availContainer.className = "text-warning";
    } else {
      resetAvailability(availContainer);
    }
  } else {
    resetAvailability(availContainer);
  }
};

export const initAvailabilityUpdateListener = function (
  el,
  skuid = el.getAttribute("data-detail-skuid")
) {
  /*
    ONLY HANDLES OPTION SELECT MENUS (NOT MATRIX BUTTON SELECTS)
    if skuid is the current one on the detail page, get the last options set
    See if it has data-invlevel on it.  If so, check if is within threshold
    and if so, update the inventory message area to urge custoemr to buy
  */
  // was formerly inlined so I haven't really updated the es5
  var availContainer = el.querySelector('[data-js="detail-item-availability"]');
  if (!availContainer) return false;
  const optionsSelects = el.querySelectorAll(`form[data-add-item="${skuid}"] select`);
  if (optionsSelects && optionsSelects.length) {
    var lastOptions = optionsSelects[optionsSelects.length - 1];
    lastOptions.addEventListener(
      "change",
      function () {
        var selectedEl = this.options[this.selectedIndex];
        var invlevel = selectedEl.getAttribute("data-invlevel");
        var invmessage = selectedEl.getAttribute("data-invmessage");
        updateAvailability(availContainer, invlevel, invmessage);
      },
      false
    );
    //if more than one selectbox, reset message on select of any of the menus except last one
    if (optionsSelects.length > 1) {
      for (var i = 0; i < optionsSelects.length - 1; i++) {
        optionsSelects[i].addEventListener(
          "change",
          function () {
            resetAvailability(availContainer);
          },
          false
        );
      }
    }
  }
};

export const updatePrice = function (el, skuid = el.getAttribute("data-detail-skuid")) {
  // was formerly inlined so I haven't really updated the es5
  const optionsSelects = el.querySelectorAll(`form[data-add-item="${skuid}"] select`);
  const matrixButtons = el.querySelectorAll(
    `form[data-add-item="${skuid}"] [data-option-selected="1"]`
  );

  /* Update price when options are selected */
  var defaultPrices = el.querySelectorAll('[data-js="detail-item-price"] [data-price]');
  if (defaultPrices.length) {
    // function resets prices to their original values
    const resetPrices = function () {
      Array.prototype.forEach.call(defaultPrices, function (price) {
        price.innerText = price.getAttribute("data-default");
      });
    };

    // get & total upcharges from any/all selected menu options
    var upcharges = 0;
    var origPriceUpcharges = 0;
    var hasSelected = 0;

    if (optionsSelects) {
      Array.prototype.forEach.call(optionsSelects, function (menu) {
        if (menu.selectedIndex > 0 && !menu.disabled) hasSelected++;
        var upcharge = menu.options[menu.selectedIndex].getAttribute("data-pricechange");
        if (upcharge && !isNaN(upcharge)) {
          upcharges += parseFloat(upcharge);
        }
        // original price can have a different (original) upcharge value per option, track separately
        var origPriceUpcharge = menu.options[menu.selectedIndex].getAttribute(
          "data-origprice-pricechange"
        );
        if (origPriceUpcharge && !isNaN(origPriceUpcharge)) {
          origPriceUpcharges += parseFloat(origPriceUpcharge);
        }
      });
    }

    if (matrixButtons) {
      Array.prototype.forEach.call(matrixButtons, function (btnEl) {
        hasSelected++;
        var upcharge = btnEl.getAttribute("data-pricechange");
        if (upcharge && !isNaN(upcharge)) {
          upcharges += parseFloat(upcharge);
        }
        // original price can have a different (original) upcharge value per option, track separately
        var origPriceUpcharge = btnEl.getAttribute("data-origprice-pricechange");
        if (origPriceUpcharge && !isNaN(origPriceUpcharge)) {
          origPriceUpcharges += parseFloat(origPriceUpcharge);
        }
      });
    }

    if (hasSelected > 0) {
      // update prices
      Array.prototype.forEach.call(defaultPrices, function (price) {
        var updatedPrice = parseFloat(price.getAttribute("data-price")) + upcharges;
        // if this is the original price and there's a separately-tracked origPriceUpcharges set, use that in the upcharge calc
        if (origPriceUpcharges && price.getAttribute("data-price-original")) {
          updatedPrice = parseFloat(price.getAttribute("data-price")) + origPriceUpcharges;
        }
        price.innerText = "$" + updatedPrice.toFixed(2);
      });
    } else {
      // nothing is selected, resert to original price value(s)
      resetPrices();
    }
  }
};

export const getOptionedInventory = function (fullSkuid) {};

export const getOptionsAjax = function (menu, skuid, menuIndex, menuLength) {
  const selectedVal = $(menu).val();
  const nextIndex = menuIndex + 2;

  // f they manually set this box to unselected, re-set subsequent fields to unselected and blank
  if (!selectedVal) {
    for (let c = nextIndex; c <= menuLength; c++) {
      var thisSel = `#${skuid}_${skuid}_${c}`;
      $(thisSel).prop("selectedIndex", 0);
      $(thisSel).prop("disabled", true);
    }
    return false;
  }

  const formSel = `form[data-add-item="${skuid}"]`;
  const allOps = $.map($(`${formSel} select option:selected`), (i) => $(i).val());
  const curFull = allOps.slice(0, menuIndex + 1); // get all options up to and including this one
  const curFullStr = skuid + curFull.join("");
  const nextSel = `#${skuid}_${skuid}_${nextIndex}`;
  let url = `/store?action=multi_option&OPTIONS_SET=${skuid}_${nextIndex}&LOOKUPSKUID=${curFullStr}&LOOKUPOPTION=${selectedVal}`;
  if ($(menu).data("blankgood")) url += "&PRODBLANKGOOD=1";

  //loop thru remaining options sets and clear their fullskuid array slots (in the event a previous choice has been changed)
  for (let x = nextIndex; x <= menuLength; x++) {
    const thisSel = `#${skuid}_${skuid}_${x}`;
    $(thisSel).prop("selectedIndex", 0);
    if (x >= nextIndex) $(thisSel).prop("disabled", true);
  }

  $.ajax({
    type: "GET",
    url: url,
    dataType: "json",
    success: (data) => {
      $(nextSel).prop("disabled", false);
      let options = `<option value="">Select ${$(nextSel).data("menu-type")}</option>`;
      if (data) {
        data.forEach((i) => {
          options += `<option data-pricechange="${i.optionPriceChange}" data-invlevel="${i.optionInvLevel}" data-invmessage="${i.optionAvailMessage}" value="${i.optionValue}" ${i.optionAttribute}>${i.optionDisplay}</option>`;
        });
        $(nextSel).html(options);
      }
    },
  });
};

export const initMultiSelectListeners = function (el, sku = el.getAttribute("data-detail-skuid")) {
  // loops each form on the page, then each select menu in each form, adds listener.  change triggers ajax call to get legal options
  $(el)
    .find(`form[data-add-item="${sku}"]`)
    .each((i, form) => {
      const skuid = $(form).data("add-item") || sku;
      const formSel = `form[data-add-item="${skuid}"]`;
      const selectMenus = $(`${formSel} select`);
      if (selectMenus.length > 1) {
        $(selectMenus).each((index, el) => {
          $(el).on("change", (e) => {
            getOptionsAjax(e.delegateTarget, skuid, index, selectMenus.length);
          });
        });
      }
    });
};

export const initAddListeners = function (el, skuid = el.getAttribute("data-detail-skuid")) {
  $(el)
    .find(`form[data-add-item="${skuid}"]`)
    .each((i, form) => {
      $(form).on("submit", (e) => {
        e.preventDefault();
        const formEl = e.delegateTarget;
        addItem(formEl, skuid);
      });
    });
};

export const addItem = function (formEl, sku) {
  const skuid = $(formEl).data("add-item") || sku;
  if (!validate(skuid)) return false;

  const btnId = $(formEl).find('[data-js="add-button"]').attr("id");
  spinButton(btnId, "<span class='d-none d-sm-inline'>ADDING</span>");

  const addUrl = createAddUrl(skuid, "cartadd.html");

  // add to cart AND call modal
  addModal(addUrl)
    .then(() =>
      unSpinButton(
        btnId,
        "<span class='d-inline d-sm-none'>ADD</span><span class='d-none d-sm-inline'>ADDED!</span>"
      )
    )
    .catch(() => {
      unSpinButton(btnId);
      flashMessage({ message: messages.itemnotadded });
    });
};

export const directAdd = function (skuid) {
  if (!skuid) return false;
  if (window.pageItemsObject.hasOwnProperty(skuid)) {
    sessionStorage.setItem(
      window.pageItemsObject[skuid].id,
      JSON.stringify({
        item_list_name: window.pageItemsObject[skuid].list,
        item_list_id: window.pageItemsObject[skuid].listId,
        timestamp: Date.now(),
      })
    );
  }
  return new Promise((resolve, reject) => {
    addModal(createAddUrl(skuid, "cartadd.html", 1))
      .then(() => resolve())
      .catch(() => reject());
  });
};

export const createAddUrl = function (skuid, template, quantity = 1) {
  // get values from fields, create a url that both adds the item to hazel cart and also calls the cart-add modal
  const formSel = `form[data-add-item="${skuid}"]`;
  let qty = $(`${formSel} input[data-js="quantity"]`).val() || quantity;
  qty = isNaN(qty) ? 1 : parseInt(qty);
  const formQty = qty;
  let addStr;
  const $selectMenus = $(`${formSel} select`);
  const $matrixMenus = $(`${formSel} [data-matrix-index]`);

  // if optioned
  if ($selectMenus.length || $matrixMenus.length) {
    let ops = null;
    if ($matrixMenus.length) {
      const $selected = $(`${formSel} [data-option-selected="1"]`);
      ops = $.map($selected, (i) => $(i).attr("data-option-code"));
    } else {
      ops = $.map($(`${formSel} select option:selected`), (i) => $(i).val());
    }
    const opsStr = ops.join("-");
    const fullskuid = `${skuid}-${opsStr}`;
    if (window.cartItemsObject && window.cartItemsObject[fullskuid])
      qty += window.cartItemsObject[fullskuid].quantity;
    addStr = `/quick-add?OPTIONED_QUANTITY_${skuid}=${qty}&OPTIONED_${skuid}=${opsStr}&last_added=${fullskuid}&last_qty=${formQty}`;
  } else {
    if (window.cartItemsObject && window.cartItemsObject[skuid])
      qty += window.cartItemsObject[skuid].quantity;
    addStr = `/quick-add?PRODUCT_${skuid}=${qty}&last_added=${skuid}&last_qty=${formQty}`;
  }

  if (template) addStr += `&template=${template}`;

  // look for any hidden fields matching this selector and serialize them.  they are items designated to be removed from the cart (i.e. not properly config'd)
  const rmv = $(`${formSel} input[type="hidden"][data-js="remove-from-cart"]`).serialize();
  if (rmv) addStr += "&" + rmv;

  return addStr;
};

export const addModal = function (url) {
  const modal = document.querySelector("#cart-modal .modal-content");
  const client = getBodyData("data-client-id");
  return new Promise((resolve, reject) => {
    const startModal = (content) => {
      const html = $.parseHTML($.trim(content), document, true); // will execute <script> in minicart html
      $(modal).html(html);
      $("#cart-modal").modal("show");
      const updatedQty = $("#cartquantity2").text();
      if (updatedQty && !isNaN(updatedQty.trim())) {
        $('[data-js="cart-item-quantity"]').text(updatedQty.trim());
        $('[data-js="cart-item-container"]').removeClass("invisible").addClass("visible");
      }
      if (window.dataLayer) window.dataLayer.push({ event: "detailItemAdd" });
      resolve();
    };

    fetchContent(url)
      .then((content) => {
        startModal(content);
        resolve();
      })
      .catch(() => {
        console.error("add to cart failed", client, url);
        reject();
      });
  });
};

export const validate = function (skuid) {
  const formSel = `form[data-add-item="${skuid}"]`;
  const itemName = $(formSel).data("item-name");
  let showError = false;
  const $selectMenus = $(`${formSel} select`);
  const $matrixMenus = $(`${formSel} [data-matrix-index]`);
  // if the form has select menus, make sure all have selected values
  if (
    $selectMenus &&
    $selectMenus.length &&
    $.map($(`${formSel} select option:selected`), (i) => !$(i).val()).includes(true)
  ) {
    showError = true;
  }
  // if the form has matrix buttons, make sure each group has one option selected
  if (
    $matrixMenus &&
    $matrixMenus.length &&
    $(`${formSel} [data-option-selected="1"]`).length < $matrixMenus.length
  ) {
    showError = true;
  }
  if (showError) {
    let error = itemName ? `Select options for ${itemName}` : messages.selectoptions.text;
    flashMessage.show({ message: error, alertType: "danger" });
    return false;
  }
  const qtyEl = $(`${formSel} input[data-js="quantity"]`);
  const qty = $(qtyEl).val();
  const maxq = $(qtyEl).data("maxq") || 0;

  // make sure the qty entered is a number > 0
  if (!qty || isNaN(qty) || parseInt(qty) <= 0) {
    let error = itemName ? `Enter a quantity for ${itemName}` : messages.enterquantity.text;
    flashMessage.show({ message: error, alertType: "danger" });
    return false;
  }

  // if there's a max qty allowed, limit qty entered to that
  if (maxq && !isNaN(maxq) && parseInt(qty) > parseInt(maxq)) {
    let error = itemName
      ? `The maximum quantity allowed for ${itemName} is ${maxq}`
      : `The maximum quantity allowed is ${maxq}`;
    flashMessage.show({ message: error, alertType: "danger" });
    return false;
  }
  return true;
};

export const getUnconfigured = function (addingSkus = []) {
  // compares list of all unoptioned items with configured ones about to be added and returns any remaining unoptioned ones
  if (!Array.isArray(addingSkus)) return [];
  const allUnconfigured = $("[data-detail-skuid]")
    .map(function () {
      return $(this).data("detail-skuid");
    })
    .get();
  return allUnconfigured.filter((i) => !addingSkus.includes(i));
};

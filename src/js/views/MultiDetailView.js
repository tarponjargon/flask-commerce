//import { elementImagesLoaded, allImagesLoaded, scrollToSelector } from "../services/Utils";
import {
  initPriceUpdateListener,
  initAvailabilityUpdateListener,
  initMultiSelectListeners,
  validate,
  createAddUrl,
  getUnconfigured,
} from "../services/DetailUtils";
import { spinButton, unSpinButton, promiseSerial, updateMiniCart } from "../services/Utils";

/*
	This class is used for 3 similar views and is stupid complicated and needs to be rethought.  The core functionality of each page is the same
	(thus the reason the code is shared), but they each have slight differences like, what to do when all items have been configured (stay on page? go to cart?).  additionally,
	#1 and #2 update the dom differently than #3 so checking WHEN all items are configured (i.e. the "Select item options" container is empty) is tricky.
	This class gets re-initted when items are added for 1 and 2.  For 3 it doesn't.

	1.  /quickorder - customer enters skus and can see a full view of their order w/tax and shipping.  is prompted to configure any optioned items.
			 when all items have been configured customer should stay on this page.
			 this view is denoted by: data-multidetail-type="order-builder"

	2.  /selectoptions - an alternate view of the above page.  customer ends up here when they are clicking to add optioned items and the select
			 menus haven't been presented.
			 when products are all configured they should redirect to /cart
			 this view is denoted by: data-multidetail-type="select-options"

	3.  /cart BUT hazel has found that at least one of the items in the cart is unconfigured.  this should ideally never happen but it does.
			 the view presents the unoptioned items to the customer and when configured ALSO removes the unoptioned skus from the cart while adding
			 the configured ones.
			 when all items are configured it needs to redirect to /cart
			 this view is denoted by: data-multidetail-type="missing-options"
*/

export default class MultiDetailView {
  constructor() {
    this.container = document.querySelector('[data-js="unconfigured-skuids"]');
    this.detailType = $("[data-multidetail-type]").data("multidetail-type");
    //console.log("detailType", this.detailType);

    if (this.container) {
      this.detailEls = this.container.querySelectorAll("[data-detail-skuid]");
      this.itemsShown = this.detailEls.length;
    }
  }
  init = (view) => {
    return new Promise((resolve) => {
      if (this.container) {
        this.detailEls.forEach((el) => {
          const skuid = el.getAttribute("data-detail-skuid");
          if (this.detailType !== "missing-options") {
            // addresses issue of the last item removed being auto-added back because of the cart cookie
            this.initRemoveItemListeners(el, skuid);
          }
          this.initAddListeners(el, skuid);
          initMultiSelectListeners(el, skuid);
          initAvailabilityUpdateListener(el, skuid);
          initPriceUpdateListener(el, skuid);
        });
        this.initAddAllListener();
      }
      //console.log("multidetail init");
      this.checkIfContainerEmpty();
      resolve(view);
    });
  };

  checkIfContainerEmpty = () => {
    if (document.querySelectorAll("[data-detail-skuid]").length === 0) {
      //console.log("EMPTY!");
      //return false;

      $(this.container).slideUp();
      $(this.container).remove();
      // on these views, if all skus are config'd, redirect to regular cart page
      if (["missing-options", "select-options"].includes(this.detailType)) {
        window.location.href = "/cart";
      }
    }
  };

  initAddListeners = (el, skuid) => {
    $(el)
      .find("form[data-add-item]")
      .each((i, form) => {
        $(form).on("submit", (e) => {
          e.preventDefault();
          const formEl = e.delegateTarget;
          this.addItem(formEl, skuid);
        });
      });
  };

  removeItemElement = (el) => {
    $(el).slideUp();
    $(el).remove();
    this.itemsShown -= 1;
    this.checkIfContainerEmpty();
    this.detailEls = this.container.querySelectorAll("[data-detail-skuid]"); // need a refresh
  };

  initRemoveItemListeners = (el, skuid) => {
    $(el)
      .find('[data-js="remove-skuid"]')
      .on("click", (e) => {
        e.preventDefault();
        this.removeItemElement(el);
        // be sure it's removed from hazel
        $.get(`/default?PRODUCT_${skuid}=0`, function () {
          updateMiniCart();
        });
      });
  };

  initAddAllListener = () => {
    $("#quick-add-all-btn").on("click", () => {
      this.multiAdd();
    });
  };

  validateAll = () => {
    let hasError = false;
    this.detailEls.forEach((el) => {
      const formEl = $(el).find("form[data-add-item]");
      const skuid = $(formEl).data("add-item") || el.getAttribute("data-detail-skuid");
      if (!validate(skuid) && !hasError) {
        hasError = true;
      }
    });
    return hasError;
  };

  ajaxAdd = (formEl, skuid) => {
    return new Promise((resolve, reject) => {
      // get all selected options for this item
      const options = $(formEl)
        .find("select")
        .children("option:selected")
        .map(function () {
          return $(this).val();
        })
        .get();

      let fullSkuid = skuid;
      if (options.length) fullSkuid += "-" + options.join("-");

      const addUrl = createAddUrl(skuid, "ajax_cartadd.html");
      $.get(
        addUrl,
        (data) => {
          if (
            data &&
            "cart" in data &&
            data.cart.items.filter((i) => i.skuid === fullSkuid).length
          ) {
            resolve();
          } else {
            if (data?.errors) {
              reject(data.errors[0]);
            } else {
              reject(`Problem adding ${skuid} to your cart`);
            }
          }
        },
        "json"
      );
    });
  };

  multiAdd = () => {
    const addProms = [];
    const hasError = this.validateAll();
    if (hasError) {
      return false;
    }

    const btnId = $("#quick-add-all-btn").attr("id");
    spinButton(btnId, "UPDATING");

    let added = [];
    this.detailEls.forEach((el) => {
      const formEl = $(el).find("form[data-add-item]");
      const skuid = $(formEl).data("add-item") || el.getAttribute("data-detail-skuid");
      added.push(skuid);
      const prom = () => this.ajaxAdd(formEl, skuid);
      addProms.push(prom);
    });

    const unconfigured = getUnconfigured(added);

    promiseSerial(addProms)
      .then(() => {
        unSpinButton(btnId, "ALL ITEMS UPDATED");
        // if on one of these pages, all items have been added, redirect to regular cart
        if (["missing-options", "select-options"].includes(this.detailType)) {
          window.location.href = "/cart";
        } else {
          // sends custom event to window (for other views to listen to) that items have been added
          const itemsAddedEvent = new CustomEvent("itemsadded", {
            detail: {
              added,
              unconfigured,
            },
          });
          document.dispatchEvent(itemsAddedEvent);
        }
      })
      .catch((e) => {
        unSpinButton(btnId);
        flashMessage.show({ message: e, alertType: "danger" });
        console.error("multiAdd promiseserial reject", e);
      });
  };

  addItem = (formEl, sku) => {
    const skuid = $(formEl).data("add-item") || sku;
    if (!validate(skuid)) return false;

    const btnId = $(formEl).find('[data-js="add-button"]').attr("id");
    spinButton(btnId, "UPDATING");

    const unconfigured = getUnconfigured([skuid]);
    const added = [skuid];

    this.ajaxAdd(formEl, skuid)
      .then(() => {
        unSpinButton(btnId, "UPDATED");
        if (["missing-options"].includes(this.detailType)) {
          this.removeItemElement($(`[data-detail-skuid="${skuid}"]`));
        } else {
          // sends custom event to window (for other views to listen to) that items have been added
          const itemsAddedEvent = new CustomEvent("itemsadded", {
            detail: {
              added,
              unconfigured,
            },
          });
          document.dispatchEvent(itemsAddedEvent);
        }
      })
      .catch((e) => {
        unSpinButton(btnId);
        flashMessage.show({ message: e, alertType: "danger" });
      });
  };
} // end MultiDetailView class

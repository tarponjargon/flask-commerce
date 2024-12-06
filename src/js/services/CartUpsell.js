import { fetchJson } from "../services/Ajax";
import {
  validate,
  initMultiSelectListeners,
  initPriceUpdateListener,
  createAddUrl,
} from "../services/DetailUtils";
import { getBodyData, spinButton, unSpinButton, waitForSelector } from "../services/Utils";

export default class CartUpsell {
  constructor() {
    window.dataLayer = window.dataLayer || [];
    this.sel = '[data-js="upsell-popup"]';
    this.skuid = null;
  }

  init = () => {
    // if an upsell is to be shown data-cart-upsell will be on the body tab and will have the ID of the promo as the value
    const id = getBodyData("data-cart-upsell");
    if (id && !isNaN(id)) {
      // when upsell modal is shown, listen for submit
      $("#smallModal").on("shown.bs.modal", () => {
        waitForSelector(`${this.sel} form[data-add-item]`).then((form) => {
          this.skuid = form.getAttribute("data-add-item");
          this.upsellSubmitListener(form);
        });
      });

      // if upsell modal is hidden, offer is declined
      $("#smallModal").on("hide.bs.modal", () => {
        window.dataLayer.push({
          event: "trackEvent",
          eventCategory: "Cart Upsell",
          eventAction: "Declined",
          eventLabel: this.skuid,
        });
        fetchJson("/default?US_REFUSED=1"); // sets the decline to their session
      });

      // show modal
      $("#smallModal .modal-content").load(`/cart-upsell?cart_upsell_id=${id}`, function () {
        $("#smallModal").modal("show");
        window.dataLayer.push({
          event: "VirtualPageView",
          VirtualPageURL: "/cart-upsell",
          VirtualPageTitle: "UPSELL",
        });
      });
    }
  };

  ajaxAdd = (skuid) => {
    return new Promise((resolve, reject) => {
      let id = "1";
      const form = document.querySelector(`form[data-add-item="${skuid}"]`);
      if (form) {
        id = form.querySelector('input[name="SO_ACCEPT"]').value;
      }
      const addUrl = createAddUrl(skuid, "ajax_cartadd.html") + `&SO_ACCEPT=${id}`;
      $.get(
        addUrl,
        (data) => {
          if (data?.cart?.items.filter((i) => addUrl.includes(i.skuid)).length) {
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

  upsellSubmitListener = (form) => {
    const el = document.querySelector(this.sel);
    const skuid = form.getAttribute("data-add-item");
    initMultiSelectListeners(el, skuid);
    initPriceUpdateListener(el, skuid);
    $(form).on("submit", (e) => {
      e.preventDefault();
      if (!validate(skuid)) return false;
      spinButton("cart-upsell-yes-btn", "ADDING");
      window.dataLayer.push({
        event: "trackEvent",
        eventCategory: "Cart Upsell",
        eventAction: "Accepted",
        eventLabel: form.getAttribute("data-add-item"),
      });
      sessionStorage.setItem(
        form.getAttribute("data-add-item"),
        JSON.stringify({
          item_list_name: "Cart Upsell",
          item_list_id: "Cart Upsell",
          timestamp: Date.now(),
        })
      );
      this.ajaxAdd(skuid)
        .then(() => {
          unSpinButton("cart-upsell-yes-btn", "ADDED");
          // sends custom event to window (for other views to listen to) that items have been added
          const itemsAddedEvent = new CustomEvent("itemsadded", {
            detail: {
              added: [skuid],
            },
          });
          document.dispatchEvent(itemsAddedEvent);
          window.location.href = "/cart";
        })
        .catch((e) => {
          unSpinButton("cart-upsell-yes-btn");
          flashMessage.show({ message: e, alertType: "danger" });
        });
    });
  };
} // end CartUpsell class

import { fetchJson } from "../services/Ajax";
import { getBodyData } from "../services/Utils";

export default class EmptyView {
  /**
   * Controller class for when the "cart empty page is viewed"
   * @constructor
   */
  constructor() {
    this.path = window.location.pathname;
    this.params = window.location.search;
  }
  init = (view) => {
    return new Promise((resolve) => {
      /** detects if the empty page is shown and the URL is checkout.
       * if so, it tries to find the cart via ajax and if found, reloads.
       */
      if (this.path === "/checkout") {
        document.querySelector(".shopping-cart-header h1.header-title").innerText =
          "Please wait...";
        fetchJson("/store?action=ajax_carttotals")
          .then((cartData) => {
            if (cartData && cartData.quantities && cartData.quantities > 0) {
              if (/CARTRELOAD/i.test(this.params)) {
                console.error(
                  "encountered checkout reload situation - failed due to potential infinite loop",
                  getBodyData("data-client-id")
                );
                document.querySelector(".shopping-cart-header h1.header-title").innerText =
                  "Your Cart is Empty";
              } else {
                console.error(
                  "encountered checkout reload situation",
                  getBodyData("data-client-id")
                );
                window.location = "/checkout?CARTRELOAD=1";
              }
            } else {
              document.querySelector(".shopping-cart-header h1.header-title").innerText =
                "Your Cart is Empty";
            }
          })
          .catch((e) => {
            console.error("problem fetching cart data in EmptyView", e);
          });
      }
      resolve(view);
    });
  };
}

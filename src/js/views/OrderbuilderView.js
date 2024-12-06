import { spinButton, unSpinButton, updateMiniCart, getUrlParams } from "../services/Utils";
import { getUnconfigured } from "../services/DetailUtils";

export default class OrderbuilderView {
  constructor() {
    this.skuEntryForm = document.querySelector('form[data-js="quick-order-form"]');
  }
  init = (view) => {
    return new Promise((resolve) => {
      this.checkUrlParams();
      this.initSubmitListener();
      this.initItemAddedListener();
      this.viewLoader();
      resolve(view);
    });
  };

  viewLoader = () => {
    if (document.querySelectorAll("[data-detail-skuid]")) {
      import(
        /* webpackPreload: true */
        /* webpackChunkName: "multidetail" */
        "./MultiDetailView"
      ).then((MultiDetailView) => new MultiDetailView.default().init());
    }

    if (document.getElementById("cart-container")) {
      import(
        /* webpackPreload: true */
        /* webpackChunkName: "cart" */
        "./CartView"
      ).then((CartView) => new CartView.default().init());
    }
  };

  checkUrlParams = () => {
    // check if skus are being passed on the url
    const params = getUrlParams();
    if (params.includeskuids) {
      let skuString = decodeURIComponent(params.includeskuids);
      skuString = skuString.replace(/\s\s+/g, " ");
      const skuids = skuString.split(" ");
      this.getOrderItems(skuids);
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  };

  initItemAddedListener = () => {
    $(document).on("itemsadded", (e) => {
      const unconfigured =
        "unconfigured" in e.detail && e.detail.unconfigured.length ? e.detail.unconfigured : [];
      this.getOrderItems(unconfigured);
    });
  };

  initSubmitListener = () => {
    $(this.skuEntryForm).on("submit", (e) => {
      e.preventDefault();
      this.getOrderItems(getUnconfigured());
    });
  };

  getOrderItems = (unconfigured = []) => {
    //console.log("getorderitems");

    spinButton("quick-order-add-button", " ");
    $("#cart-container").html("");
    $("#cart-container").addClass("loading-mask mask-300");
    let url = "/buildorder?ADDSKUIDS=";
    let skuEntry = $('[data-js="quick-order-field"]').val();
    if (skuEntry) url += encodeURIComponent(skuEntry);
    if (unconfigured && unconfigured.length) url += "%20" + unconfigured.join("%20");

    $.get(url, (cart) => {
      //console.log("get complete");
      $("#cart-container").html(cart);
      $('[data-js="quick-order-field"]').val("");
      this.viewLoader();
      unSpinButton("quick-order-add-button");
      $("#cart-container").removeClass("loading-mask mask-300");
      updateMiniCart();
    });
  };
} // end OrderbuilderView class

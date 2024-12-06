import Cookies from "js-cookie";
import { signupHandler } from "../services//Utils";

export default class ReceiptView {
  constructor() {}
  init = (view) => {
    return new Promise((resolve) => {
      this.handleReceipt();
      this.initSignupListener();
      // trying to make sure that cart cookie is being deleted.  though I don't even know if these will work
      Cookies.remove("cart", { path: "/", domain: window.location.host });
      Cookies.remove("cart", {
        path: "/",
        domain: window.location.host.replace(/^(.*?)\./, "."),
      });
      resolve(view);
    });
  };

  initSignupListener = () => {
    // signup submit
    $("#receipt-signup-form").on("submit", (e) => {
      e.preventDefault();
      signupHandler(e.delegateTarget, false);
    });
  };

  handleReceipt = (hash = $("body").data("receipt")) => {
    if (!hash) return false;
    $.ajax({
      type: "GET",
      cache: false,
      url: `/store?action=do&TMP_VAL=${hash}`,
      dataType: "html",
    });
  };
}

import { spinButton } from "./Utils";

export default class CartModal {
  constructor() {}

  init = () => {
    return new Promise((resolve) => {
      this.startListeners();
      resolve();
    });
  };

  unListen = () => {
    // public method called on modal close.  removes all listeners
    $("#cart-modal").find("*").off();
  };

  startListeners = () => {
    // personalization form submit
    if ($("#personalization-modal").length) {
      $("#personalization-modal").on("submit", (e) => {
        e.preventDefault();
        this.persHandler();
      });
    }
  };

  persHandler = () => {
    spinButton("personalization-modal-submit", "UPDATING");
    const returnPage = $("#cart-modal [data-return]").data("return") || null;
    $.ajax({
      url: "/store?action=default",
      data: $("#personalization-modal").serialize(),
      type: "POST",
      success: () => {
        if (returnPage) {
          window.location.href = returnPage;
        } else {
          $("#cart-modal .modal-content").load(`/cart?template=cartadd.html`, function () {});
        }
      },
      error: function (xhr, status, errorThrown) {
        console.error("personalization modal", xhr, status, errorThrown);
        alert(
          "Sorry, there was a problem!  Please click 'contact us' and let us know you saw this error."
        );
      },
    });
  };
}

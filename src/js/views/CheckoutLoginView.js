import { unSpinButton, spinButton, fieldValidListener, getBodyData } from "../services/Utils";
import messages from "../services/Messages";

export default class CheckoutLoginView {
  constructor() {}
  init = (view) => {
    return new Promise((resolve) => {
      this.startListeners();
      resolve(view);
    });
  };

  startListeners = () => {
    fieldValidListener($("#guest-checkout-form input, #member-checkout-form input"));
    fieldValidListener($("#guest-checkout-form input"));
    $("#member-checkout-form").on("submit", (e) => {
      this.loginHandler(e);
    });
    $('[data-js="checkout-heading-button"]').on("click", (e) => {
      if ($("#password_input").val()) {
        $("#member-checkout-button").trigger("click");
      } else {
        $("#guest-checkout-button").trigger("click");
      }
    });
  };

  loginHandler = (e) => {
    e.preventDefault();
    if ($("#member-checkout-form .error-card").is(":visible")) {
      $("#member-checkout-form .error-card").slideUp();
    }
    spinButton("member-checkout-button", "PLEASE WAIT");
    const client = getBodyData("data-client-id");
    $.ajax({
      url: `/store?action=ajax_login&client=${client}`,
      data: $("#member-checkout-form").serialize(),
      dataType: "json",
      type: "POST",
      success: (data) => {
        if (data && data.success) {
          window.location.href = "/checkout";
        } else {
          if ("errors" in data) {
            unSpinButton("member-checkout-button");
            $("#member-checkout-form .error-card .card-text").html(data.errors.join(", "));
            $("#member-checkout-form .error-card").slideDown();
          }
        }
      },
      error: (xhr, status, errorThrown) => {
        unSpinButton("member-checkout-button");
        flashMessage.show({ message: messages.fatal });
        console.error("checkout login", xhr, status, errorThrown);
      },
    });
  };
}

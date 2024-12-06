import { spinButton, fieldValidListener, scrollToSelector } from "../services/Utils";
import {
  addressbookListeners,
  quantityChangeListeners,
  persListeners,
  giftListeners,
} from "../services/CheckoutUtils";

export default class ConfirmationView {
  constructor() {}
  init = (view) => {
    return new Promise((resolve) => {
      // usage of shipping_meat.inc.hzml (whose home is billing.html) requires conversion of data-required attr to required in this context
      $('[data-required="required"]').attr("required", "required");
      this.startListeners();
      quantityChangeListeners();
      giftListeners();
      persListeners();
      addressbookListeners();
      resolve(view);
    });
  };

  submitOrder = () => {
    $('button[data-js="submit-order-button"]').each(function () {
      const btnId = $(this).attr("id");
      $(this).attr("disabled", "true");
      spinButton(btnId, "PROCESSING");
    });
    $('form[data-js="confirmation-form"]').off();
    document.confirmation_form.submit();
  };

  startListeners = () => {
    // listen for submit order events
    $('button[data-js="submit-order-button"]').on("click", (e) => {
      e.preventDefault();
      this.submitOrder();
    });
    $('form[data-js="confirmation-form"]').on("submit", (e) => {
      e.preventDefault();
      this.submitOrder();
    });

    // tax exempt checkbox togglin
    $('[data-js="tax-exempt-field"]').on("click", function () {
      if ($(this).is(":checked")) {
        $('[data-js="tax-info-card"]').slideDown();
        $.get("/default?TAX_EXEMPT=1");
      } else {
        $('[data-js="tax-info-card"]').slideUp();
        $.get("/default?TAX_EXEMPT=0");
      }
    });

    // attach custom validation handler on each field
    fieldValidListener($('[data-js="billing-field"], [data-js="shipping-field"]'));

    // if there are any shipping errors showing on load, expand the shipping options div
    if (
      $("[data-js='confirmation-content'] .error-card").length &&
      $("[data-js='confirmation-content'] .error-card").text().indexOf("shipping method") > -1
    ) {
      $("#shipping_method .toggle-default").hide();
      $("#shipping_method .toggle-view").show();
      $("#shipping_method .toggle-default-animate").slideUp("fast");
      $("#shipping_method .toggle-view-animate").slideDown("fast");
    }

    // pattern abscratction for show/hide of divs
    $('[data-js="trigger-expand"]').on("click", function (e) {
      e.preventDefault();
      var thisId = $(this).data("id");
      if (thisId) {
        var id = "#" + thisId;
        if ($(id + " .toggle-view").is(":visible")) {
          // trigger close
          $(id + " .toggle-view").hide();
          $(id + " .toggle-default").show();
          $(id + " .toggle-view-animate").slideUp("fast");
          $(id + " .toggle-default-animate").slideDown("fast");
        } else {
          // trigger open
          $(id + " .toggle-default").hide();
          $(id + " .toggle-view").show();
          $(id + " .toggle-default-animate").slideUp("fast");
          $(id + " .toggle-view-animate").slideDown("fast");
        }
        scrollToSelector(id);
      }
    });

    $("#edit-shipping-form").on("submit", (e) => {
      e.preventDefault();
      // disable the hidden fields where addressbook data is stored
      $('[data-js="addressbook-field"]').prop("disabled", true);
      $("#edit-shipping-form").off().submit();
      spinButton("update-shipping-button", "UPDATING");
    });

    $("#edit-method-form").on("submit", function () {
      spinButton("ship-method-update-button", "Updating");
    });

    //toggle gift message area
    $("#displayGift").on("click", function () {
      $("#toggleGift").slideToggle("fast");
    });
  };
}

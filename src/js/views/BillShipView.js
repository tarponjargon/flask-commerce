import {
  spinButton,
  unSpinButton,
  scrollToSelector,
  fieldValidListener,
  getBodyData,
} from "../services/Utils";
import { clearShipping, addressbookListeners } from "../services/CheckoutUtils";
import messages from "../services/Messages";

export default class BillShipView {
  constructor() {
    this.formSel = "#billing-shipping-form";
    this.errorSel = '[data-js="billing-content"] .error-card';
    this.continueBtnId = "billing-continue-button";
  }
  init = (view) => {
    return new Promise((resolve) => {
      // since the billing fields are visible by default (at least on this view), convert the data-required attr to a regular required attr
      // so that html5 validation will work.. has to happen before listeners (fieldValidListener specifically)
      // $('[data-js="billing-form"] [data-required="required"]').attr("required", "required");

      this.startListeners();
      addressbookListeners();

      resolve(view);
    });
  };

  startListeners = () => {
    // attach custom fielf validation handler on each field
    fieldValidListener($('[data-js="billing-field"]'));

    // if there is an addressbook selection previously chosen, show "reset" link next to it
    if (
      $('[data-js="addressbook-address"]').prop("selectedIndex") > 0 &&
      !$("#reset-shipping-address-link").is(":visible")
    ) {
      $("#reset-shipping-address-link").show();
    }

    // it's possible for the addresses to become out of sync with the 'shipSame' radio choice
    // if the address was edited downstream.  If the addresses have values on page load,
    // compare the two and force the appropriate radio button choice
    if ($(`${this.formSel} #bill_fname`).val() && $("#ship_fname").val()) {
      if (this.compareBillShip()) {
        $("#shipSameYes").prop("checked", true);
        if ($('[data-js="shipping-form"]').is(":visible")) {
          this.hideShipping();
        }
      } else {
        $("#shipSameNo").prop("checked", true);
        if (!$('[data-js="shipping-form"]').is(":visible")) {
          this.showShipping();
        }
      }
    }

    // if page is loaded and shipSameNo is already checked (Can happen if there are server-side errors)
    // then expand shipping fields
    if ($("#shipSameNo").is(":checked") && !$('[data-js="shipping-form"]').is(":visible")) {
      this.showShipping();
    }

    // listen for clicks on "ship to same addr" radio btns
    // copy billing -> shipping, or enter new on radio trigger
    $(`${this.formSel} .shipSame`).on("click", () => {
      clearShipping();
      if ($("#shipSameNo").is(":checked")) {
        this.showShipping();
        scrollToSelector('[data-js="shipping-form"]');
      } else {
        this.copyBillToShip();
        if ($('[data-js="shipping-form"]').length) {
          if ($('[data-js="shipping-form"]').is(":visible")) {
            this.hideShipping();
          }
        }
      }
    });

    // validate form, then submit
    $(this.formSel).on("submit", (e) => {
      e.preventDefault();

      // this shouldn't happen because shipSame=yes is selected by default in the html, but just in case...
      if (!$("input[name='shipSame']:checked").val()) {
        alert("Please enter a shipping address");
        return false;
      }

      // copy billing address to the hidden shipping fields so shipping address gets submitted to backend
      if ($("#shipSameYes").is(":checked")) {
        this.copyBillToShip();
      }

      // disable the hidden fields where addressbook data is stored
      $('[data-js="addressbook-field"]').prop("disabled", true);

      spinButton(this.continueBtnId, "PLEASE WAIT");

      // submit the form via ajax (and collect any errors)
      // this allows the user to freely use the back button
      if ($(this.errorSel).is(":visible")) {
        $(this.errorSel).slideUp();
        $(`${this.errorSel} .card-text`).text("");
      }

      const client = getBodyData("data-client-id");
      const url = `/store?action=ajax_billinginfo&client=${client}`;
      const data = $(this.formSel).serialize();

      fetch(url, {
        method: "POST",
        credentials: "same-origin",
        body: data,
      })
        .then((r) => {
          return r.json();
        })
        .then((data) => {
          if (data && data.success) {
            window.location.href = "/payment";
          } else {
            if ("errors" in data) {
              unSpinButton(this.continueBtnId);
              $(`${this.errorSel} .card-text`).html(data.errors.join(", "));
              $(this.errorSel).slideDown();
              scrollToSelector(this.errorSel);
            }
          }
        })
        .catch((e) => {
          unSpinButton(this.continueBtnId);
          flashMessage.show({
            message: "Something went wrong.  Please click 'Continue' again.",
            type: "danger",
          });
          console.error("checkout billing fail", e, client);
        });
    });
  };

  showShipping = () => {
    $('[data-js="shipping-form"]').slideDown("fast");
    // this is important.  if the form is visible, enable html5 validations
    $('[data-js="shipping-form"] [data-required="required"]').attr("required", "required");
    fieldValidListener($('[data-js="shipping-field"]'));
  };

  hideShipping = () => {
    // this is important.  if the form fields are hidden they can't have the required attribute or the form won't submit
    // I'm also finding I have to manually set customvalidity to empty
    $('[data-js="shipping-field"]').each(function () {
      $(this).removeAttr("required");
      $(this)[0].setCustomValidity("");
      $(this).off();
    });
    $('[data-js="shipping-form"]').slideUp("fast");
  };

  compareBillShip = () => {
    let billShipAreSame = true;
    $('[data-js="shipping-field"]').each(function () {
      let shipId = "#" + $(this).attr("id");
      let billId = "#" + $(this).attr("id").replace("ship_", "bill_");
      if ($(shipId).val() !== $(billId).val()) {
        billShipAreSame = false;
        return false;
      }
    });
    return billShipAreSame;
  };

  copyBillToShip = () => {
    $('[data-js="billing-field"]').each(function () {
      var shipId = "#" + $(this).attr("id").replace("bill_", "ship_");
      if ($(this).is("select")) {
        if ($(this).val())
          $(shipId + " option[value=" + $(this).val() + "]").prop("selected", true);
      } else {
        $(shipId).val($(this).val());
      }
    });
  };
}

import {
  unSpinButton,
  spinButton,
  scrollToSelector,
  fieldValidListener,
  getBodyData,
} from "../services/Utils";
import messages from "../services/Messages";

export default class PaymentView {
  constructor() {
    this.errorSel = '[data-js="payment-content"] .error-card';
  }
  init = (view) => {
    return new Promise((resolve) => {
      this.startListeners();
      resolve(view);
    });
  };

  startListeners = () => {
    fieldValidListener(
      $(
        "#credit-payment-form input, #credit-payment-form select, #giftcertificate-entry-form input"
      )
    );

    // click handler for pay by cc
    $("#pay-cc").on("click", function () {
      $("#cc-entry").slideDown();
      $("#gc-payment").slideUp();
      $('#pay-gc [data-js="payment-indicator"]').removeClass("d-sm-inline");
      $('#pay-cc [data-js="payment-indicator"]').addClass("d-sm-inline");
      //$("#alternate-payment").slideUp();
      $("html, body").animate({ scrollTop: $("#cc-entry").offset().top }, "fast");
    });

    // click handler for pay by gc
    $("#pay-gc").on("click", function () {
      $("#gc-payment").slideDown();
      $("#cc-entry").slideUp();
      $('#pay-cc [data-js="payment-indicator"]').removeClass("d-sm-inline");
      $('#pay-gc [data-js="payment-indicator"]').addClass("d-sm-inline");
      //$("#alternate-payment").slideUp();
      $("html, body").animate({ scrollTop: $(".gc-payment").offset().top }, "fast");
    });

    // if shopper clicks into credit fields directly, remove pseudo-disabled styling
    $("#credit-payment-form input,#credit-payment-form select").on("click", function () {
      $("#credit-payment-form input,#credit-payment-form select").css("background-color", "#fff");
    });

    // on load, a selected credit year is a proxy indicator for having been to this page previously, remove pseudo-disabled styling
    if (
      $("#CreditYear").length &&
      $("#CreditYear").is(":visible") &&
      $("#CreditYear").prop("selectedIndex") > 0
    ) {
      $("#credit-payment-form input,#credit-payment-form select").css("background-color", "#fff");
    }

    // validate credit card #, submit form
    $("#credit-payment-form").on("submit", (e) => {
      e.preventDefault();
      if (!this.testCreditCard()) {
        return false;
      }
      spinButton("cc-checkout-button", "PLEASE WAIT");
      // submit the form via ajax (and collect any errors)
      // this allows the user to freely use the back button
      if ($(this.errorSel).is(":visible")) {
        $(this.errorSel).slideUp();
        $(`${this.errorSel} .card-text`).text("");
      }

      const client = getBodyData("data-client-id");
      const url = `/store?action=ajax_payment&client=${client}`;
      const data = $("#credit-payment-form").serialize();
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
            window.location.href = "/confirmation";
          } else {
            if ("errors" in data) {
              unSpinButton("cc-checkout-button");
              $(`${this.errorSel} .card-text`).html(data.errors.join(", "));
              $(this.errorSel).slideDown();
              scrollToSelector(this.errorSel);
            }
          }
        })
        .catch((e) => {
          unSpinButton("cc-checkout-button");
          flashMessage.show({
            message: "Please click 'Continue' again.",
            type: "danger",
          });
          console.error("checkout payment fail", e, client);
        });
    });

    // Gift certificate, validate form, then submit
    $("#giftcertificate-entry-form").on("submit", (e) => {
      e.preventDefault();
      if ($(this.errorSel).is(":visible")) {
        $(this.errorSel).slideUp();
        $(`${this.errorSel} .card-text`).text("");
      }
      if ($("#gc-message").is(":visible")) {
        $("#gc-message").slideUp();
        $("#gc-message-text").text("");
      }
      spinButton("giftcertificate-apply-button", "Processing");
      $.ajax({
        type: "POST",
        url: "/store?action=ajax_gc",
        data: $("#giftcertificate-entry-form").serialize(),
        dataType: "json",
        success: (data) => {
          if (data.success) {
            unSpinButton("giftcertificate-apply-button", "Applied!");
            $("#gc-message-text").text(data.message);
            $("#gc-message").slideDown();
            if (data.additional_payment) {
              $("#alternate-payment").hide();
              $("#cc-entry").slideDown();
              $("#gc-continue-button").hide();
            } else {
              $("#gc-continue-button").show();
            }
          } else {
            if ("error" in data) {
              unSpinButton("giftcertificate-apply-button", "Apply");
              $(`${this.errorSel} .card-text`).html(data.error);
              $(this.errorSel).slideDown();
              scrollToSelector(this.errorSel);
            }
          }
        },
        error: function (xhr, status, errorThrown) {
          flashMessage.show({ message: messages.fatal });
          console.error("checkout gc", xhr, status, errorThrown);
          unSpinButton("giftcertificate-apply-button", "Apply");
        },
      });
    });
  };

  checkdate = (year, month, day) => {
    var sendDate = year + "/" + month + "/" + day;
    sendDate = new Date(Date.parse(sendDate.replace(/-/g, " ")));
    var today = new Date();
    today.setHours(0, 0, 0, 0);
    if (sendDate < today) {
      return false;
    } else {
      return true;
    }
  };

  testCreditCard = () => {
    var cardErrorCode = this.checkCreditCard(
      document.getElementById("CardNumber").value,
      document.getElementById("CardType").value,
      document.getElementById("CreditMonth").value,
      document.getElementById("CreditYear").value,
      document.getElementById("CreditCVV").value
    );

    if (cardErrorCode === -1) return true;
    var ccErrors = new Array();
    ccErrors[0] = "Please check your credit card type and credit card number.";
    ccErrors[1] = "No credit card number provided";
    ccErrors[2] = "Your credit card number is not formatted correctly";
    ccErrors[3] = "Your credit card number is not valid";
    ccErrors[4] = "Your credit card number doesn't have enough digits";
    ccErrors[5] = "Please select an expiration month";
    ccErrors[6] = "Please select an expiration year";
    ccErrors[7] = "Your credit card appears to be expired";
    ccErrors[8] = "Please enter your credit card security code (CVV)";
    ccErrors[9] = "Credit card security code (CVV) should be either 3 or 4 digits long";

    window.flashMessage.show({ message: ccErrors[cardErrorCode], alertType: "danger" });
    return false;
  };

  checkCreditCard = (cardnumber, cardname, creditmonth, credityear, cvv) => {
    // Array to hold the permitted card characteristics
    var cards = new Array();
    var ccErrorNo = -1;

    // Define the cards we support. You may add addtional card types.

    //  Name:      As in the selection box of the form - must be same as user's
    //  Length:    List of possible valid lengths of the card number for the card
    //  prefixes:  List of possible prefixes for the card
    //  checkdigit Boolean to say whether there is a check digit

    cards[0] = {
      name: "MC",
      length: "16",
      prefixes: "51,52,53,54,55,22,23,24,25,26,27",
      checkdigit: true,
    };
    cards[1] = { name: "VI", length: "13,16", prefixes: "4", checkdigit: true };
    cards[2] = { name: "DI", length: "16", prefixes: "6011", checkdigit: true };
    cards[3] = { name: "AX", length: "15", prefixes: "34,37", checkdigit: true };

    // Establish card type
    var cardType = -1;
    for (var i = 0; i < cards.length; i++) {
      // See if it is this card (ignoring the case of the string)
      if (cardname.toLowerCase() == cards[i].name.toLowerCase()) {
        cardType = i;
        break;
      }
    }

    // If card type not found, report an error
    if (cardType == -1) {
      ccErrorNo = 0;
      return ccErrorNo;
    }

    // Ensure that the user has provided a credit card number
    if (cardnumber.length == 0) {
      ccErrorNo = 1;
      return ccErrorNo;
    }

    // Ensure that the user has provided a CVV number
    if (cvv.length == 0) {
      ccErrorNo = 8;
      return ccErrorNo;
    }

    // Ensure that the user has provided a CVV number that's the correct length
    if (cvv.length < 3 || cvv.length > 4) {
      ccErrorNo = 9;
      return ccErrorNo;
    }

    //make sure credit month and year are ehntered
    if (creditmonth.length == 0) {
      ccErrorNo = 5;
      return ccErrorNo;
    }
    if (credityear.length == 0) {
      ccErrorNo = 6;
      return ccErrorNo;
    }

    //checkthat the expire date is not int he past
    var myDay = "31";
    if (this.checkdate(credityear, creditmonth, myDay) == false) {
      ccErrorNo = 7;
      return ccErrorNo;
    }

    if ((cardnumber.indexOf("xxxx") === 0) == false) {
      // Check that the number is numeric, although we do permit a space to occur
      // every four digits.
      var cardNo = cardnumber;
      var cardexp = /^([0-9]{4})\s?([0-9]{4})\s?([0-9]{4})\s?([0-9]{1,4})$/;
      if (!cardexp.exec(cardNo)) {
        ccErrorNo = 2;
        return ccErrorNo;
      }

      // Now remove any spaces from the credit card number
      cardexp.exec(cardNo);
      cardNo = RegExp.$1 + RegExp.$2 + RegExp.$3 + RegExp.$4;

      // Now check the modulus 10 check digit - if required
      if (cards[cardType].checkdigit) {
        var checksum = 0; // running checksum total
        var j = 1; // takes value of 1 or 2

        // Process each digit one by one starting at the right
        var calc;
        for (i = cardNo.length - 1; i >= 0; i--) {
          // Extract the next digit and multiply by 1 or 2 on alternative digits.
          calc = Number(cardNo.charAt(i)) * j;

          // If the result is in two digits add 1 to the checksum total
          if (calc > 9) {
            checksum = checksum + 1;
            calc = calc - 10;
          }

          // Add the units element to the checksum total
          checksum = checksum + calc;

          // Switch the value of j
          if (j == 1) {
            j = 2;
          } else {
            j = 1;
          }
        }

        // All done - if checksum is divisible by 10, it is a valid modulus 10.
        // If not, report an error.
        if (checksum % 10 != 0) {
          ccErrorNo = 3;
          return ccErrorNo;
        }
      }

      // The following are the card-specific checks we undertake.
      var LengthValid = false;
      var PrefixValid = false;

      // We use these for holding the valid lengths and prefixes of a card type
      var prefix = new Array();
      var lengths = new Array();

      // Load an array with the valid prefixes for this card
      prefix = cards[cardType].prefixes.split(",");

      // Now see if any of them match what we have in the card number
      for (i = 0; i < prefix.length; i++) {
        var exp = new RegExp("^" + prefix[i]);
        if (exp.test(cardNo)) PrefixValid = true;
      }

      // If it isn't a valid prefix there's no point at looking at the length
      if (!PrefixValid) {
        ccErrorNo = 3;
        return ccErrorNo;
      }

      // See if the length is valid for this card
      lengths = cards[cardType].length.split(",");
      for (j = 0; j < lengths.length; j++) {
        if (cardNo.length == lengths[j]) LengthValid = true;
      }

      // See if all is OK by seeing if the length was valid. We only check the
      // length if all else was hunky dory.
      if (!LengthValid) {
        ccErrorNo = 4;
        return ccErrorNo;
      }
    } /* end clasue for xxxx */

    // The credit card is in the required format.
    return ccErrorNo;
  };
}

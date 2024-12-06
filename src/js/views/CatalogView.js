import { spinButton, unSpinButton, scrollToSelector, fieldValidListener } from "../services/Utils";
import messages from "../services/Messages";

export default class CatalogView {
  constructor() {
    this.formSel = "#catalog-form";
    this.errorSel = "#error-card";
    this.continueBtnId = "catalog-submit-button";
  }
  init = (view) => {
    return new Promise((resolve) => {
      this.startListeners();
      resolve(view);
    });
  };

  formSuccess = (hash) => {
    $("#entry-content").slideUp();
    $("#success-content").slideDown();
    // sends welcome email async
    if (hash) {
      $.ajax({
        type: "GET",
        cache: false,
        url: `/store?action=do_crm&do_crm=${hash}`,
        dataType: "html",
      });
    }
  };

  startListeners = () => {
    fieldValidListener($('#catalog-form [required="required"]'));

    // validate form, then submit
    $(this.formSel).on("submit", (e) => {
      e.preventDefault();

      spinButton(this.continueBtnId, "SUBMITTING");

      // submit the form via ajax (and collect any errors)
      // this allows the user to freely use the back button
      if ($(this.errorSel).is(":visible")) {
        $(this.errorSel).slideUp();
        $(`${this.errorSel} .card-text`).text("");
      }

      $.ajax({
        url: "/store?action=ajax_catalog",
        data: $(this.formSel).serialize(),
        dataType: "json",
        type: "POST",
        success: (data) => {
          if (data && data.success) {
            unSpinButton(this.continueBtnId, "SUBMITTED!");
            this.formSuccess(data.hash);
            window.dataLayer.push({
              event: "welcomeEmailSent",
              email: $(this.formSel).find('[name="bill_email"]').val(),
              requestType: "catalogrequest",
            });
          } else {
            if ("errors" in data) {
              unSpinButton(this.continueBtnId);
              $(`${this.errorSel} .card-text`).html(data.errors.join(", "));
              $(this.errorSel).slideDown();
              scrollToSelector(this.errorSel);
            }
          }
        },
        error: (xhr, status, errorThrown) => {
          unSpinButton(this.continueBtnId);
          flashMessage.show({ message: messages.fatal });
          console.error("catalog form", xhr, status, errorThrown);
        },
      });
    });
  };
}

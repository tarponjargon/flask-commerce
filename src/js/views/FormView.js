import { spinButton, unSpinButton, scrollToSelector, fieldValidListener } from "../services/Utils";
import messages from "../services/Messages";

/*
this is an abstraction for handling general-use forms submitted with AJAX.
Page can contain multiple forms.  Forms need to be structured in a specific way:

<hazel-vset name="PAGE" value="GENERALFORM"> (top of page)
...
<div data-js="general-form-container">
	<div class="general-form-content">
		<!-- error printout, shown if submitted form has errors from backend -->
		<div data-js="general-form-error" class="card text-white bg-danger error-card" style="display: none">
			<div class="card-body">
				<p class="card-text"></p>
			</div>
		</div>

		<!-- the form itself. NOTE the 'action' attribute needs to be a hazel action that returns JSON -->
		<form data-js="general-form" action="ajax_donotrent">
			<div class="form-group row">
				...
				<div class="col-12 new-mandatory-input-wrapper">
					<input
						type="text"
						class="form-control"
						required="required"
						title="Please enter a last name"
						name="BILL_LNAME"
						placeholder="Last Name"
					>
				</div>
				...
				<!-- submit button, NOTE, it needs a random ID attr -->
				<div class="form-group row">
					<div class="col-12 not-mandatory">
						<hazel-vset name="RAND_ID" random="10" />
						<button
							type="submit"
							class="button-primary submit-button"
							id="general-submit-%HZ{V_RAND_ID}"
						>SUBMIT</button>
					</div>
				</div>
		</form>
	</div>
	<!-- success container, shown when form submit successful (form content gets hidden) -->
	<div data-js="general-success-content" style="display: none">
		<div class="card text-white bg-success my-4 mx-0 mx-md-4">
			<div class="card-header"><h2>Request Submitted</h2></div>
			<div class="card-body">
				<p class="card-text text-larger">Your request has been submitted.  Thank you! </p>
			</div>
		</div>
	</div>
</div>

*/
export default class FormView {
  constructor() {
    // these are selector values for format: data-js="general-form-container"
    this.dataContainerSel = "general-form-container";
    this.dataContentSel = "general-form-content";
    this.dataErrorSel = "general-form-error";
    this.dataFormSel = "general-form";
    this.dataSuccessContent = "general-success-content";
  }
  init = (view) => {
    return new Promise((resolve) => {
      this.startListeners();
      resolve(view);
    });
  };

  startListeners = () => {
    fieldValidListener($(`[data-js="${this.dataFormSel}"] [required="required"]`)); // handles validity on any field with 'required' attr

    // validate form, then submit
    $(`[data-js="${this.dataFormSel}"]`).on("submit", (e) => {
      e.preventDefault();

      const form = $(e.delegateTarget);
      const formButtonId = $(form).find(`button[type="submit"]`).attr("id");
      const container = $(form).closest(`[data-js="${this.dataContainerSel}"]`);
      const formContent = $(container).find(`[data-js="${this.dataContentSel}"]`);
      const errorContent = $(formContent).find(`[data-js="${this.dataErrorSel}"]`);
      const successContent = $(container).find(`[data-js="${this.dataSuccessContent}"]`);
      const ajaxAction = $(form).attr("action");

      // console.log("e", e);
      // console.log("form", form);
      // console.log("formButtonId", formButtonId);
      // console.log("container", container);
      // console.log("formContent", formContent);
      // console.log("errorContent", errorContent);
      // console.log("successContent", successContent);
      // console.log("ajaxAction", ajaxAction);
      // console.log("data", $(form).serialize());

      spinButton(formButtonId, "SUBMITTING");

      if ($(errorContent).is(":visible")) {
        $(errorContent).slideUp();
        $(errorContent).find(`.card-text`).text("");
      }

      $.ajax({
        url: `/store?action=${ajaxAction}`,
        data: $(form).serialize(),
        dataType: "json",
        type: "POST",
        success: (data) => {
          if (data && data.success) {
            unSpinButton(formButtonId, "SUBMITTED!");
            $(`[data-js="${this.dataSuccessContent}"]`).slideUp(); // hide any success containers already on the screen.  Unlikely but could happen on page w/multiple forms
            $(formContent).slideUp();
            $(successContent).slideDown();
            // scrollToSelector(successContent);
          } else {
            if ("errors" in data) {
              unSpinButton(formButtonId);
              $(errorContent).html(data.errors.join(", "));
              $(errorContent).slideDown();
              scrollToSelector(errorContent);
            }
          }
        },
        error: (xhr, status, errorThrown) => {
          unSpinButton(formButtonId);
          flashMessage.show({ message: messages.fatal });
          console.error("general form", window.location.pathname, xhr, status, errorThrown);
        },
      });
    });
  };
}

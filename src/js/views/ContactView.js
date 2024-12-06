import { spinButton, unSpinButton, scrollToSelector, fieldValidListener } from "../services/Utils";
import messages from "../services/Messages";

export default class ContactView {
	constructor() {
		this.formSel = "#contact-form";
		this.errorSel = "#error-card";
		this.continueBtnId = "contact-submit-button";
	}
	init = view => {
		return new Promise(resolve => {
			this.startListeners();
			resolve(view);
		});
	};

	toggleFields = (outType, inType) => {
		$(`[data-js="${outType}"]`).each(function() {
			const field = $(this).find('[required="required"]');
			if (field.length) {
				$(this).slideUp("fast");
				$(field).removeAttr("required");
				$(field)[0].setCustomValidity("");
				$(field).off();
			}
		});
		$(`[data-js="${inType}"]`).slideDown("fast");
		$(`[data-js="${inType}"] [data-required="required"]`).attr("required", "required");
		fieldValidListener($(`[data-js="${inType}"] [required="required"]`));
	};

	formSuccess = () => {
		$("#contact-content").slideUp();
		$("#success-content").slideDown();
	};

	startListeners = () => {
		fieldValidListener($('#contact-form [required="required"]'));
		$('select[name="info_request_type"]').on("change", e => {
			if ($(e.delegateTarget).val() === "info_request_subject_order") {
				this.toggleFields("inquiry-field", "order-field");
			}
			if ($(e.delegateTarget).val() === "info_request_subject_inquiry") {
				this.toggleFields("order-field", "inquiry-field");
			}
		});

		// validate form, then submit
		$(this.formSel).on("submit", e => {
			e.preventDefault();

			spinButton(this.continueBtnId, "SUBMITTING");

			// submit the form via ajax (and collect any errors)
			// this allows the user to freely use the back button
			if ($(this.errorSel).is(":visible")) {
				$(this.errorSel).slideUp();
				$(`${this.errorSel} .card-text`).text("");
			}

			$.ajax({
				url: "/store?action=ajax_contact",
				data: $(this.formSel).serialize(),
				dataType: "json",
				type: "POST",
				success: data => {
					if (data && data.success) {
						unSpinButton(this.continueBtnId, "SUBMITTED!");
						this.formSuccess();
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
					console.error("contact form", xhr, status, errorThrown);
				}
			});
		});
	};
}

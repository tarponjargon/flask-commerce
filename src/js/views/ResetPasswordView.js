import { unSpinButton, spinButton, fieldValidListener } from "../services/Utils";
import messages from "../services/Messages";

export default class ResetPassword {
	constructor() {}
	init = view => {
		return new Promise(resolve => {
			this.initListener();
			fieldValidListener($("#reset-password-form input"));
			resolve(view);
		});
	};

	formSuccess = () => {
		let message = "Password updated! You are now logged in...";
		flashMessage.show({
			message: message,
			alertType: "success",
			timeout: false
		});
		setTimeout(() => {
			window.location.href = "/account";
		}, 1000);
	};

	formHandler = () => {
		if ($(".reset-password-content .error-card").is(":visible")) {
			$(".reset-password-content .error-card").slideUp();
		}
		spinButton("reset-password-button", "PLEASE WAIT");
		$.ajax({
			url: "/store?action=ajax_updatepassword",
			data: $("#reset-password-form").serialize(),
			dataType: "json",
			type: "POST",
			success: data => {
				if (data && data.success) {
					this.formSuccess();
					unSpinButton("reset-password-button", "Password Updated!");
				} else {
					if ("errors" in data) {
						unSpinButton("reset-password-button");
						$(".reset-password-content .error-card .card-text").html(
							data.errors.join(", ")
						);
						$(".reset-password-content .error-card").slideDown();
					}
				}
			},
			error: (xhr, status, errorThrown) => {
				unSpinButton("reset-password-button");
				flashMessage.show({ message: messages.fatal });
				console.error("checkout login", xhr, status, errorThrown);
			}
		});
	};

	initListener = () => {
		$("#reset-password-form").on("submit", e => {
			e.preventDefault();
			this.formHandler();
		});
	};
}

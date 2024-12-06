import { safeString, dataSelect } from "../services/Utils";

class Alert {
	constructor() {
		//this.alertNodeSelector = "#bs-alert";
		//this.alertContentSelector = "#alert-content";
		//this.alertClose = "#alert-close-button";
		this.showSelector = "fadeIn";

		this.alertNode = dataSelect("alert-container"); //document.querySelector(this.alertNodeSelector);
		this.alertCloseButton = dataSelect("alert-close-button", this.alertNode); //this.alertNode.querySelector(this.alertClose);
		this.alertContent = dataSelect("alert-content", this.alertNode); // this.alertNode.querySelector(this.alertContentSelector);
		this.alertTimer = null;
		this.message = null;
		this.alertType = null;
		this.alertClass = null;
		this.timeout = null;
	}

	getAlertClass = alertType => {
		const types = [
			"primary",
			"secondary",
			"success",
			"danger",
			"warning",
			"info",
			"light",
			"dark"
		];
		return types.indexOf(alertType) > -1 ? `alert-${alertType}` : "alert-primary";
	};

	docEventListener = event => {
		if (event.target.closest('[data-js="alert-container"]')) return;
		this.close();
		return true;
	};

	isVisible = () => {
		return this.alertNode.classList.contains(this.showSelector);
	};

	show = ({ message = null, alertType = null, timeout = null } = {}) => {
		if (this.isVisible()) {
			//console.log("cancelling earlier alert");
			this.close();
		}

		if (!message) {
			return false;
		}
		if (typeof message === "object") {
			this.message = message.text;
			this.alertType = alertType ? alertType : message.type;
		} else {
			this.message = message;
			this.alertType = alertType ? alertType : "primary";
		}
		if (timeout === null) {
			this.timeout = CFG.alertTimeout;
		} else if (!isNaN(timeout)) {
			this.timeout = timeout;
		} else {
			this.timeout = false;
		}

		this.alertClass = this.getAlertClass(this.alertType);
		this.alertNode.setAttribute(
			"style",
			"position: fixed; top: 10px; right: 10px; bottom: auto;"
		);
		this.alertNode.classList.add(this.showSelector);
		this.alertNode.classList.add(this.alertClass);
		//let finalMsg = safeString(this.message);
		// strings of a special format are converted for use as links in alerts.
		// this: @/profile/wishlist/123:View wishlist@
		// converted to this: <a href="/profile#wishlist/123">View wishlist</a>
		// const m = finalMsg.match(/@(.*?):(.*?)@/);
		// if (m && m.length > 2 && !/http/i.test(m[1])) {
		// 	finalMsg = finalMsg.replace(m[0], `<a href="${m[1]}">${m[2]}</a>`);
		//}
		this.alertContent.innerHTML = this.message;

		// time it to auto-close unless timeout is falsey
		if (this.timeout) {
			this.alertTimer = setTimeout(() => {
				this.close();
			}, this.timeout);
		}

		// Listen for clicks outside the alert, which trigger close
		// delay it a bit to get it clear of any initial clicks that triggered it
		setTimeout(() => {
			document.addEventListener("click", this.docEventListener);
		}, 100);

		// listen for clicks on the close button
		this.alertCloseButton.addEventListener("click", this.close, false);
	};

	close = () => {
		this.alertNode.classList.remove(this.showSelector);
		this.alertNode.classList.remove(this.alertClass);
		this.alertContent.innerHTML = null; //this.alertNode.querySelector(this.alertContentSelector).innerText = null;
		this.alertNode.removeAttribute("style");

		if (this.alertTimer) {
			clearTimeout(this.alertTimer);
		}
		document.removeEventListener("click", this.docEventListener);
		this.alertCloseButton.removeEventListener("click", this.close, false);
		this.message, this.alertType, (this.timeout = null);
	};
} // end alert object

export default Alert;

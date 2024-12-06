import dayjs from "dayjs";
import qs from "qs";
import { fetchJson } from "../services/Ajax";
import { getBodyData } from "./Utils";

export const formatOrderId = function(id) {
	return `${CFG.orderPrefix}${id}`;
};

// general-use sort function for object values
export const sortObjectValues = (obj, fieldName, sortOrder = "DESC") => {
	if (sortOrder === "ASC") {
		obj = obj.sort((a, b) => {
			if (isNaN(a[fieldName])) {
				return a[fieldName] === b[fieldName] ? 0 : a[fieldName] > b[fieldName] ? 1 : -1;
			} else {
				return parseFloat(a[fieldName]) > parseFloat(b[fieldName]) ? 1 : -1;
			}
		});
	} else {
		obj = obj.sort((a, b) => {
			if (isNaN(a[fieldName])) {
				return a[fieldName] === b[fieldName] ? 0 : a[fieldName] < b[fieldName] ? 1 : -1;
			} else {
				return parseFloat(a[fieldName]) < parseFloat(b[fieldName]) ? 1 : -1;
			}
		});
	}
	return obj;
};

export const groupProductsBySkuid = productArr => {
	if (!productArr || !Array.isArray(productArr) || productArr.length === 0) return [];

	let products = {};
	productArr.forEach(p => {
		if (!(p.skuid in products)) {
			products[p.skuid] = p;
		} else {
			products[p.skuid].quantity += p.quantity;
			if (p.lastOrderedDate > products[p.skuid].lastOrderedDate) {
				products[p.skuid].lastOrderedDate = p.lastOrderedDate;
			}
		}
	});
	return Object.values(productArr);
};

export const dateFormat = function(date, type, format) {
	// see https://github.com/iamkun/dayjs/blob/master/docs/en/API-reference.md for API
	let newDate = date;
	switch (type) {
		case "unix":
			if (date.toString().length === 10) newDate = dayjs(date * 1000).format(format);
			if (date.toString().length === 13) newDate = dayjs(date).format(format);
			break;
		case "ymd":
			date = date.toString();
			newDate = dayjs(date).format(format);
			break;
	}
	return newDate;
};

export const getAccountData = function() {
	return new Promise((resolve, reject) => {
		let client = getBodyData('data-client-id');
		fetchJson(`/store?action=ajax_account&client=${client}`)
			.then(data => {
				resolve(data);
			})
			.catch(e => {
				reject(e);
			});
	});
};

export const updateUserAccount = function(user) {
	return new Promise((resolve, reject) => {
		let client = getBodyData('data-client-id');
		fetch(`/store?action=ajax_updateaccount&client=${client}`, {
			method: "POST",
			credentials: 'same-origin',
			body: qs.stringify(user)
		})
			.then(r => r.json())
			.then(result => {
				if (result.success) {
					resolve();
				} else if (result.errors) {
					reject(result.errors.join(" "));
				} else {
					reject("Problem updating your account");
				}
			})
			.catch(e => {
				console.error("problem updating user account", user, e);
				reject("Problem updating account");
			});
	});
};

export const updateUserPassword = function(password, passwordConfirm) {
	return new Promise((resolve, reject) => {
		let client = getBodyData('data-client-id');
		fetch(`/store?action=ajax_updatepassword&client=${client}`, {
			method: "POST",
			credentials: 'same-origin',
			body: qs.stringify({
				bill_account_password: password,
				bill_account_password_confirm: passwordConfirm
			})
		})
			.then(r => r.json())
			.then(result => {
				if (result.success) {
					resolve();
				} else if ("errors" in result && result.errors.length) {
					reject(result.errors.join(" "));
				} else {
					reject("Problem updating your password");
				}
			})
			.catch(e => {
				console.error("problem updating password", e);
				reject("Problem updating password");
			});
	});
};

export const copyToClipboard = str => {
	return new Promise(resolve => {
		const el = document.createElement("textarea");
		el.value = str;
		el.setAttribute("readonly", "");
		el.style.position = "absolute";
		el.style.left = "-9999px";
		document.body.appendChild(el);
		el.select();
		document.execCommand("copy");
		document.body.removeChild(el);
		resolve();
	});
};

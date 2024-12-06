import qs from "qs";

const address = {
	namespaced: true,
	state: {
		addresses: []
	},
	getters: {
		getAddressById: state => id => {
			return state.addresses.find(n => n.id === id);
		}
	},
	mutations: {
		SET_ADDRESSES(state, addresses) {
			state.addresses = addresses;
		},
		SET_ADDRESS(state, address) {
			const idx = state.addresses.findIndex(i => i.id.toString() === address.id.toString());
			state.addresses.splice(idx, 1, address);
		},
		DELETE_ADDRESS(state, id) {
			state.addresses = state.addresses.filter(a => a.id.toString() !== id.toString());
		}
	},
	actions: {
		updateAddress({ commit }, address) {
			if (!address.id) return false;
			return new Promise((resolve, reject) => {
				// send hazel alternative key names (prefixed with TEMP_)
				const newAddress = {};
				for (const [key, value] of Object.entries(address)) {
					newAddress[`TEMP_${key}`] = value;
				}
				//console.log("editaddress", address, newAddress, qs.stringify(newAddress));
				fetch("/store?action=ajax_editaddress", {
					method: "POST",
					credentials: 'same-origin',
					body: qs.stringify(newAddress)
				})
					.then(r => {
						return r.json();
					})
					.then(data => {
						if (data && "addresses" in data && data.addresses) {
							commit("SET_ADDRESSES", data.addresses);
							resolve();
						} else {
							reject(data.errors.join(" "));
						}
					})
					.catch(e => {
						console.error("problem updating address", address, e);
						reject("Problem updating address");
					});
			});
		},
		deleteAddress({ commit }, id) {
			if (!id) return false;
			return new Promise((resolve, reject) => {
				fetch(`/store?action=ajax_deleteaddress`, {
					method: "POST",
					credentials: 'same-origin',
					body: qs.stringify({
						address: id
					})
				})
					.then(r => {
						return r.json();
					})
					.then(data => {
						if (data && "addresses" in data && data.addresses) {
							commit("SET_ADDRESSES", data.addresses);
							resolve();
						} else {
							reject(data.errors.join(" "));
						}
					})
					.catch(e => {
						console.error("problem deleting address", address, e);
						reject("Problem deleting address");
					});
			});
		},
		newAddress({ commit }, address) {
			return new Promise((resolve, reject) => {
				// send hazel alternative key names (prefixed with TEMP_)
				const newAddress = {};
				for (const [key, value] of Object.entries(address)) {
					newAddress[`TEMP_${key}`] = value;
				}
				//console.log("address", address, newAddress, qs.stringify(newAddress));
				fetch("/store?action=ajax_newaddress", {
					method: "POST",
					credentials: 'same-origin',
					body: qs.stringify(newAddress)
				})
					.then(r => {
						return r.json();
					})
					.then(data => {
						if (data && "addresses" in data && data.addresses) {
							commit("SET_ADDRESSES", data.addresses);
							resolve();
						} else {
							reject(data.errors.join(" "));
						}
					})
					.catch(e => {
						console.error("problem adding address", address, e);
						reject("Problem adding address");
					});
			});
		}
	}
};
export default address;

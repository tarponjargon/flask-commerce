import { fetchJson } from "../../services/Ajax";
import { getBodyData } from "../../services/Utils";

const wishlist = {
	namespaced: true,
	state: {
		id: null,
		items: []
	},
	getters: {
		getItemBySkuid: state => skuid => {
			return state.items.find(n => n.skuid === skuid);
		},
		getAllSkuids: state => () => {
			return state.items.map(n => n.skuid);
		}
	},
	mutations: {
		SET_WISHLIST(state, wishlist) {
			state.items = wishlist.items;
			state.id = wishlist.hwlid;
		}
	},
	actions: {
		getWishlist({ commit }, wishlistId) {
			return new Promise((resolve, reject) => {
				fetchJson(`/store?action=ajax_getwishlist&hwlid=${wishlistId}`)
					.then(data => {
						if (data && "wishlist" in data) {
							commit("SET_WISHLIST", data.wishlist);
						} else {
							const msg =
								data && "errors" in data
									? data.errors.join(", ")
									: "Could not retrieve wishlist";
							console.error("getWishlist response but no wishlist payload", msg);
							reject(msg);
						}
					})
					.catch(e => {
						console.error("could not load wishlist data", e);
						resolve("could not retrieve wishlist data");
					});
			});
		},
		updateQuantity({ commit }, [skuid, qty, id]) {
			return new Promise((resolve, reject) => {
				fetchJson(`/wishlistupdate?wl_skuid=${skuid}&wl_quantity=${qty}&hwlid=${id}`)
					.then(data => {
						if (data && "wishlist" in data) {
							commit("SET_WISHLIST", data.wishlist);
							resolve();
						} else {
							const msg =
								data && "errors" in data
									? data.errors.join(", ")
									: "Could not retrieve your wishlist";
							console.error("wishlistupdate response but no wishlist payload", msg);
							reject(msg);
						}
					})
					.catch(e => {
						console.error("rejected wishlistupdate", e);
						reject("Could not update wishlist");
					});
			});
		},
		removeItem({ commit }, [skuid, id]) {
			return new Promise((resolve, reject) => {
				fetchJson(`/wishlistremove?wl_skuid=${skuid}&hwlid=${id}`)
					.then(data => {
						if (data && "wishlist" in data) {
							commit("SET_WISHLIST", data.wishlist);
							resolve();
						} else {
							const msg =
								data && "errors" in data
									? data.errors.join(", ")
									: "Could not retrieve your wishlist";
							console.error("wishlistremove response but no wishlist payload", skuid, id, msg, getBodyData('data-client-id'));
							reject(msg);
						}
					})
					.catch(e => {
						console.error("rejected wishlistremove", e);
						reject("Could not remove item from your wishlist");
					});
			});
		},
		removeMany({ commit }, [skuids, id]) {
			return new Promise((resolve, reject) => {
				fetchJson(`/wishlistremove?wl_skuid=${skuids.join(";")}&hwlid=${id}`)
					.then(data => {
						if (data && "wishlist" in data) {
							commit("SET_WISHLIST", data.wishlist);
							resolve();
						} else {
							const msg =
								data && "errors" in data
									? data.errors.join(", ")
									: "Could not retrieve your wishlist";
							console.error("wishlistremove response but no wishlist payload", skuids, id, msg, getBodyData('data-client-id'));
							reject(msg);
						}
					})
					.catch(e => {
						console.error("rejected wishlistremove", e);
						reject("Could not remove item from your wishlist");
					});
			});
		}
	}
};
export default wishlist;

import { createStore, createLogger } from "vuex";
import address from "./modules/address";
import order from "./modules/order";
import wishlist from "./modules/wishlist";
import { fetchJson } from "../services/Ajax";
import { getAccountData, updateUserAccount } from "../services/AccountUtils";
import { getBodyData } from "../services/Utils";

const store = createStore({
  modules: {
    address,
    order,
    wishlist,
  },
  state: {
    loading: false,
    error: false,
    user: {},
    states: [],
    countries: [],
  },
  mutations: {
    SET_LOADING(state, loading) {
      state.loading = loading;
    },
    SET_ERROR(state, error) {
      state.error = error;
    },
    SET_USER(state, user) {
      state.user = user;
    },
    SET_STATES(state, states) {
      state.states = states;
    },
    SET_COUNTRIES(state, countries) {
      state.countries = countries;
    },
  },
  actions: {
    setUserData({ commit }, data) {
      commit("SET_USER", data.user);
      commit("address/SET_ADDRESSES", data.addresses);
      commit("order/SET_ORDERS", data.orders);
      commit("wishlist/SET_WISHLIST", data.wishlist);
    },
    loadSummary({ commit, dispatch }) {
      return new Promise((resolve, reject) => {
        commit("SET_LOADING", true);
        commit("SET_ERROR", false);
        let client = getBodyData("data-client-id");
        getAccountData()
          .then((data) => {
            dispatch("setUserData", data);
            commit("SET_LOADING", false);
            resolve();
          })
          .catch((e) => {
            console.error("Problem loading summary data for client", client, e);
            commit("SET_LOADING", false);
            commit("SET_ERROR", true);
            reject();
          });
      });
    },

    getStates({ commit }) {
      // states and countries arrays are in the same payload
      return fetchJson("/store?action=ajax_states").then((r) => {
        commit("SET_STATES", r.states);
        commit("SET_COUNTRIES", r.countries);
      });
    },

    saveUser({ dispatch }, user) {
      return new Promise((resolve, reject) => {
        updateUserAccount(user)
          .then(() => {
            getAccountData()
              .then((data) => {
                dispatch("setUserData", data);
              })
              .catch((e) => {
                flashMessage.show({ message: e, alertType: "danger" });
                console.error("saveUser failed at getUser call", e);
                reject(e);
              });
            resolve(); // let the getAccountData run optimistically
          })
          .catch((e) => {
            console.error("saveUser failed", e);
            reject(e);
          });
      });
    },
  }, // end actions
});
export default store;

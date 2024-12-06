import dayjs from "dayjs";
import { sortObjectValues } from "../../services/AccountUtils";

const order = {
	namespaced: true,
	state: {
		orders: [],
		sortBy: "date",
		sortOrder: "DESC",
		selectedDateRange: {
			from: dayjs()
				.subtract(3, "month")
				.startOf("month")
				.toDate(),
			to: dayjs()
				.endOf("month")
				.toDate()
		}
	},
	getters: {
		getOrderById: state => id => {
			return state.orders.filter(n => n.id === parseInt(id))[0];
		}
	},
	mutations: {
		SET_ORDERS(state, orders) {
			state.orders = orders;
		},
		SET_SORTBY(state, by) {
			state.sortBy = by;
		},
		SET_SORTORDER(state, order) {
			state.sortOrder = order;
		},
		SET_SELECTEDDATERANGE(state, range) {
			state.selectedDateRange = range;
		}
	},
	actions: {
		sortOrders({ commit, state }, fieldName = "date") {
			commit("SET_SORTBY", fieldName);
			commit("SET_SORTORDER", !state.sortOrder || state.sortOrder === "ASC" ? "DESC" : "ASC");
			commit("SET_ORDERS", sortObjectValues(state.orders, state.sortBy, state.sortOrder));
		},
		setSelectedDateRange({ commit }, range) {
			commit("SET_SELECTEDDATERANGE", range);
		}
	}
};
export default order;

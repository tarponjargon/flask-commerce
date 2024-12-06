<script>
import { mapState } from "vuex";
import dayjs from "dayjs";
import { formatPrice, fullOrderId } from "../../services/Utils";
import { dateFormat } from "../../services/AccountUtils";
import dateRangePicker from "../DateRangePicker";

export default {
  components: {
    "date-range-picker": dateRangePicker,
  },
  computed: {
    ...mapState("order", ["orders", "sortBy", "sortOrder"]),
    selectedDateRange: {
      get() {
        return this.$store.state.order.selectedDateRange;
      },
      set(val) {
        this.$store.dispatch("order/setSelectedDateRange", val);
      },
    },
    filteredOrders() {
      return this.orders.filter(
        (i) =>
          i.date >= parseInt(dayjs(this.selectedDateRange.from).format("YYYYMMDD")) &&
          i.date <= parseInt(dayjs(this.selectedDateRange.to).format("YYYYMMDD"))
      );
    },
    selectedDateRangeFormatted() {
      if (this.selectedDateRange) {
        return (
          dayjs(this.selectedDateRange.from).format("YYYYMMDD") +
          " - " +
          dayjs(this.selectedDateRange.to).format("YYYYMMDD")
        );
      } else {
        return "None";
      }
    },
  },
  methods: {
    dateFormat,
    formatPrice,
    fullOrderId,
    sortOrders(order) {
      this.$store.dispatch("order/sortOrders", order);
    },
  },
};
</script>

<template>
  <div class="account-orders">
    <h2>Your Orders</h2>
    <hr class="mb-4" />

    <div class="filter mb-4">
      <date-range-picker v-model="selectedDateRange"></date-range-picker>
    </div>

    <div v-if="filteredOrders.length" class="table-responsive">
      <table class="table account-summary-table">
        <thead>
          <tr>
            <th>
              <span v-on:click="sortOrders('id')">Order ID</span>
              <a href="javascript:;" class="text-decoration-none" v-on:click="sortOrders('id')">
                <i
                  class="ms-1 fa"
                  :class="{
                    'fa-caret-up': sortBy === 'id' && sortOrder === 'ASC',
                    'fa-sort-down': sortBy === 'id' && sortOrder === 'DESC',
                    'fa-sort': sortBy !== 'id',
                  }"
                ></i>
              </a>
            </th>
            <th>
              <span v-on:click="sortOrders('date')">Date</span>
              <a href="javascript:;" class="text-decoration-none" v-on:click="sortOrders('date')">
                <i
                  class="ms-1 fa"
                  :class="{
                    'fa-caret-up': sortBy === 'date' && sortOrder === 'ASC',
                    'fa-sort-down': sortBy === 'date' && sortOrder === 'DESC',
                    'fa-sort': sortBy !== 'date',
                  }"
                ></i>
              </a>
            </th>
            <th>
              <span v-on:click="sortOrders('totalOrder')">Total</span>
              <a href="javascript:;" class="text-decoration-none" v-on:click="sortOrders('totalOrder')">
                <i
                  class="ms-1 fa"
                  :class="{
                    'fa-caret-up': sortBy === 'totalOrder' && sortOrder === 'ASC',
                    'fa-sort-down': sortBy === 'totalOrder' && sortOrder === 'DESC',
                    'fa-sort': sortBy !== 'totalOrder',
                  }"
                ></i>
              </a>
            </th>
            <th>
              <span v-on:click="sortOrders('orderStatus')">Status</span>
              <a href="javascript:;" class="text-decoration-none" v-on:click="sortOrders('orderStatus')">
                <i
                  class="ms-1 fa"
                  :class="{
                    'fa-caret-up': sortBy === 'orderStatus' && sortOrder === 'ASC',
                    'fa-sort-down': sortBy === 'orderStatus' && sortOrder === 'DESC',
                    'fa-sort': sortBy !== 'orderStatus',
                  }"
                ></i>
              </a>
            </th>
          </tr>
        </thead>
        <tbody class="border-top" data-test="profile-orders">
          <tr v-for="order in filteredOrders" :key="order.id">
            <td>
              <router-link :data-order-id="order.id" :to="{ name: 'order', params: { id: order.id } }">{{
                fullOrderId(order.id)
              }}</router-link>
            </td>
            <td>{{ dateFormat(order.date, "ymd", "MMM DD, YYYY") }}</td>
            <td>{{ formatPrice(order.totalOrder) }}</td>
            <td>{{ order.orderStatus }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else>No orders in selected date range</div>
  </div>
</template>

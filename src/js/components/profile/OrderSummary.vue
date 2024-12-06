<script>
import { dateFormat, formatOrderId } from "../../services/AccountUtils";
import { mapState } from "vuex";
export default {
  computed: {
    ...mapState({
      loading: (state) => state.loading,
      orders: (state) => state.order.orders,
    }),
    filteredOrders() {
      return this.orders.length ? this.orders.slice(0, 5) : [];
    },
  },
  methods: {
    dateFormat,
    formatOrderId,
  },
};
</script>

<template>
  <div v-if="!loading" class="col-md-6 d-flex align-items-stretch mb-4">
    <div class="card w-100">
      <div class="card-header d-flex align-items-center w-100 mh-25">
        <div class="row w-100 mx-0">
          <div class="col-6 col-md-6 px-0 d-flex align-items-center">
            <h5 class="card-title">Recent Orders</h5>
          </div>
          <div class="col-6 col-md-6 px-0 d-flex align-items-center justify-content-end">
            <router-link :to="{ name: 'orders' }" class="btn btn-sm btn-info"> SEE ALL </router-link>
          </div>
        </div>
      </div>
      <div class="card-body">
        <div v-if="orders.length">
          <table class="table account-summary-table">
            <tbody>
              <tr v-for="order in filteredOrders" :key="order.id">
                <td>
                  <router-link :to="{ name: 'order', params: { id: order.id } }">
                    {{ formatOrderId(order.id) }}
                  </router-link>
                </td>
                <td>{{ dateFormat(order.date, "ymd", "MMM DD, YYYY") }}</td>
                <td>{{ order.orderStatus }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="orders.length > 5" class="w-100 d-block text-center">
            <span v-if="orders.length">
              <strong>
                <router-link :to="{ name: 'orders' }" class="brand-link">
                  See all {{ orders.length }} orders...
                </router-link>
              </strong>
            </span>
          </div>
        </div>
        <div v-else>No orders yet</div>
      </div>
    </div>
  </div>
</template>

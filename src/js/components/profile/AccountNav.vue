<script>
import { useStore, mapState } from "vuex";
import { useRoute } from "vue-router";
export default {
  setup() {
    const store = useStore();
    const route = useRoute();
    return { route, store };
  },
  computed: {
    ...mapState({
      routeName: (state) => state.route.name,
      orders: (state) => state.order.orders,
      addresses: (state) => state.address.addresses,
      wishlistItems: (state) => state.wishlist.items,
      user: (state) => state.user,
    }),
    routeName() {
      return this.route.name;
    },
  },
  methods: {
    closeMobileMenu() {
      this.$parent.mobileMenu = false;
    },
    showShipping() {
      try {
        $("#smallModal .modal-content").load("/shippinginfo", function () {
          $("#smallModal").modal("show");
        });
      } catch (e) {}
    },
  },
};
</script>

<template>
  <div @click="closeMobileMenu()">
    <aside class="d-none d-md-block user-info-wrapper">
      <div class="user-info">
        <div v-if="user" class="user-data">
          <h4 class="mb-0">
            Hello,
            {{ user.bill_fname ? user.bill_fname : "Shopper" }}!
          </h4>
          <span>{{ user.bill_email }}</span>
        </div>
      </div>
    </aside>
    <nav class="list-group">
      <router-link class="list-group-item" :to="{ name: 'home' }">
        <i class="fa fa-user"></i>
        Account Summary
      </router-link>

      <router-link class="list-group-item" :to="{ name: 'update' }">
        <i class="fa fa-pencil"></i>
        Update Your Info
      </router-link>

      <router-link class="list-group-item" :to="{ name: 'passwordupdate' }">
        <i class="fa fa-lock"></i>
        Change Your Password
      </router-link>

      <router-link
        :class="{ active: routeName && routeName.indexOf('order') > -1 }"
        class="list-group-item with-badge"
        :to="{ name: 'orders' }"
      >
        <i class="fa fa-cube"></i>
        Orders
        <span class="badge badge-primary badge-pill">
          <span v-if="orders && orders.length">{{ orders.length }}</span>
          <span v-else>0</span>
        </span>
      </router-link>

      <router-link
        class="list-group-item with-badge"
        :class="{ active: routeName && routeName.indexOf('address') > -1 }"
        :to="{ name: 'addresses' }"
      >
        <i class="fa fa-location-arrow"></i>
        Addresses
        <span class="badge badge-primary badge-pill">
          <span v-if="addresses && addresses.length">{{ addresses.length }}</span>
          <span v-else>0</span>
        </span>
      </router-link>

      <router-link class="list-group-item with-badge" :to="{ name: 'wishlist' }">
        <i class="fa fa-heart"></i>
        Wish List
        <span class="badge badge-primary badge-pill">
          <span v-if="wishlistItems && wishlistItems.length">{{ wishlistItems.length }}</span>
          <span v-else>0</span>
        </span>
      </router-link>

      <a class="list-group-item" href="/quickorder">
        <i class="fa fa-check"></i>
        Quick Order
      </a>

      <a class="list-group-item" href="javascript:;" @click="showShipping">
        <i class="fa fa-truck"></i>
        Shipping Information
      </a>

      <a class="list-group-item" href="/contact">
        <i class="fa fa-comments-o"></i>
        Contact Us
      </a>

      <a class="list-group-item text-danger" href="/logout">
        <i class="fa fa-sign-out"></i>
        Log Out
      </a>
    </nav>
  </div>
</template>

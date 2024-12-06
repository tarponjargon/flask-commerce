import { createRouter, createWebHashHistory } from "vue-router";

import index from "./components/profile/Index";
import accountUpdate from "./components/profile/AccountUpdate";
import passwordUpdate from "./components/profile/PasswordUpdate";
import accountOrders from "./components/profile/AccountOrders";
import accountOrder from "./components/profile/AccountOrder";
import accountAddresses from "./components/profile/AccountAddresses";
import accountWishlist from "./components/profile/AccountWishlist";
import newAddressForm from "./components/profile/AccountNewAddress";
import editAddressForm from "./components/profile/AccountEditAddress";

const router = new createRouter({
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else if (from.path === to.path) {
      // do not scroll when only query params are changed
      return {};
    } else if (to.hash) {
      return {
        el: to.hash,
        behavior: "smooth",
      };
    } else {
      return {
        top: 0,
        behavior: "smooth",
      };
    }
  },
  mode: "hash",
  history: createWebHashHistory(),
  base: "/",
  linkExactActiveClass: "active",
  routes: [
    {
      path: "/",
      name: "home",
      component: index,
    },
    {
      path: "/update",
      name: "update",
      component: accountUpdate,
    },
    {
      path: "/passwordupdate",
      name: "passwordupdate",
      component: passwordUpdate,
    },
    {
      path: "/orders",
      name: "orders",
      component: accountOrders,
    },
    {
      path: "/order/:id",
      name: "order",
      component: accountOrder,
    },
    {
      path: "/addresses",
      name: "addresses",
      component: accountAddresses,
    },
    {
      path: "/newaddress",
      name: "newaddress",
      component: newAddressForm,
    },
    {
      path: "/editaddress/:id",
      name: "editaddress",
      component: editAddressForm,
    },
    {
      path: "/wishlist",
      name: "wishlist",
      component: accountWishlist,
    },
  ],
});

export default router;

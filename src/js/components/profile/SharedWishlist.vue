<script>
import { mapState, mapGetters } from "vuex";
import { promiseSerial } from "../../services/Utils";
import { createAddUrl, addModal } from "../../services/DetailUtils";
import messages from "../../services/Messages";
import LineItem from "../LineItem";
export default {
  data() {
    return {
      id: null,
      container: document.querySelector(".sharedwishlist-wrapper"),
      addingAll: false,
    };
  },
  computed: {
    ...mapGetters("wishlist", ["getItemBySkuid", "getAllSkuids"]),
    ...mapState({
      wishlistItems: (state) => state.wishlist.items,
    }),
  },
  components: {
    LineItem,
  },
  created() {
    const el = document.querySelector('[data-js="sharedwishlist-data"]');
    this.id = el ? el.getAttribute("data-hwlid") : null;
    if (this.id) this.$store.dispatch("wishlist/getWishlist", this.id);
  },
  mounted() {
    this.removeMask();
  },
  methods: {
    removeMask() {
      this.container.classList.remove("loading-mask");
      this.container.classList.remove("mask-300");
    },
    updateQuantity(skuid, qty) {
      return false; // not sure if a wishlist owner's friend should be allowed to update the quantity directly.  for now, no.
    },
    addToCart(skuid, qty) {
      if (isNaN(qty) || qty <= 0) {
        flashMessage.show({ message: messages.enterquantity });
        return false;
      }
      const item = this.getItemBySkuid(skuid);
      // does the qty this buddy is trying to order equal the number the owner wants? yes = removeItem no = updateQuantity
      let prom = null;
      if (qty < item.quantity) {
        const remaining = item.quantity - qty;
        prom = () => this.$store.dispatch("wishlist/updateQuantity", [skuid, remaining, this.id]);
      } else {
        prom = () => this.$store.dispatch("wishlist/removeItem", [skuid, this.id]);
      }
      if (item.hasOptions) {
        prom().then(() => {
          window.location.href = `/selectoptions?addskuids=${skuid}&${skuid}_qty=${qty}`;
        });
      } else {
        const url = createAddUrl(skuid, "cartadd.html", qty);
        addModal(url).then(() => {
          prom();
        });
      }
    },
    addAllToCart() {
      this.addingAll = true;
      // transform wishlist item data into a funky hazel url and redirect to it
      const unoptioned = this.wishlistItems.filter((i) => !i.hasOptions);
      const optioned = this.wishlistItems.filter((i) => i.hasOptions);
      const unoptionedStr = unoptioned.length
        ? unoptioned.map((p) => `PRODUCT_${p.skuid}=${this.$refs[p.skuid][0].qty}`).join("&")
        : "";
      const optionedSkuStr = optioned.length ? "ADDSKUIDS=" + optioned.map((i) => i.skuid).join("%20") : "";
      const optionedQtyStr = optioned.length
        ? optioned.map((p) => `${p.skuid}_QTY=${this.$refs[p.skuid][0].qty}`).join("&")
        : "";

      let url = "";
      if (optioned.length) {
        url = `/selectoptions?${optionedSkuStr}&${optionedQtyStr}`;
        url += unoptioned ? `&${unoptionedStr}` : "";
      } else {
        url = `/add?${unoptionedStr}`;
      }
      // loop each item and determine if this buddy is ordering all of the desired qty.  for each: if yes - push to removeSkus if no, update qty
      const removeSkus = [];
      const proms = [];
      this.wishlistItems.forEach((p) => {
        if (this.$refs[p.skuid][0].qty < p.quantity) {
          const remaining = p.quantity - this.$refs[p.skuid][0].qty;
          const prom = () => this.$store.dispatch("wishlist/updateQuantity", [p.skuid, remaining, this.id]);
          proms.push(prom);
        } else {
          removeSkus.push(p.skuid);
        }
      });
      if (removeSkus.length) {
        const prom = () => this.$store.dispatch("wishlist/removeMany", [removeSkus, this.id]);
        proms.push(prom);
      }
      promiseSerial(proms)
        .then(() => {
          window.location.href = url;
        })
        .catch((e) => {
          console.error("promiseSerial failed in shared allAllToCart", e);
          flashMessage.show({
            message: "Problem adding all SKUs",
            alertType: "danger",
          });
          this.addingAll = false;
        });
    },
  },
};
</script>
<template>
  <div class="row receipt-container wishlist-container fadeIn">
    <div class="col-12">
      <div class="shopping-cart-header">
        <h1 class="header-title primary-color border-bottom-0 mb-0">Your Friend's Wish List</h1>
      </div>
      <hr />
    </div>

    <div class="col-12 receipt-content fadeIn mt-3">
      <div v-if="wishlistItems.length" class="lineitems">
        <div class="lineitem-headings row">
          <div class="col-md-7 lineitem-heading-product">Item</div>
          <div class="col-md-2 lineitem-heading-qty">Quantity</div>
          <div class="col-md-2 lineitem-heading-price">Price</div>
          <div class="col-md-1 lineitem-heading-total">Total</div>
        </div>

        <div v-for="item in wishlistItems" :key="item.skuid" class="lineitem-wrapper" data-js="lineitem">
          <LineItem
            :item="item"
            :editable="true"
            :sharedWishlistView="true"
            @updateQuantity="updateQuantity"
            @addToCart="addToCart"
            :ref="item.skuid"
          />
        </div>
        <!-- /lineitem-wrapper -->

        <div class="w-100 text-center mt-4">
          <button class="btn btn-primary btn-block btn-xl" @click="addAllToCart">
            <span v-if="addingAll">
              ADDING ...
              <i class="spinner icomoon-spinner"></i>
            </span>
            <span v-else>
              ADD ALL ITEMS
              <i class="fa fa-arrow-up"></i>
            </span>
          </button>
        </div>
      </div>
      <div v-else>
        No items.
        <a href="/">Shop around!</a>
      </div>
    </div>
  </div>
</template>

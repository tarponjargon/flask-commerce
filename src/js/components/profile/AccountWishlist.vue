<script>
import { mapState, mapGetters } from "vuex";
import { createAddUrl, addModal } from "../../services/DetailUtils";
import messages from "../../services/Messages";
import LineItem from "../LineItem";
import ShareWishlist from "./ShareWishlist";
export default {
  computed: {
    ...mapState({
      wishlistItems: (state) => state.wishlist.items,
      id: (state) => state.wishlist.id,
    }),
    ...mapGetters("wishlist", ["getItemBySkuid", "getAllSkuids"]),
  },
  components: {
    LineItem,
    ShareWishlist,
  },
  data() {
    return {
      addingAll: false,
    };
  },
  methods: {
    updateQuantity(skuid, qty) {
      if (isNaN(qty) || qty <= 0) {
        flashMessage.show({ message: messages.enterquantity });
        return false;
      }
      this.$store
        .dispatch("wishlist/updateQuantity", [skuid, qty, this.id])
        .then(() => {
          flashMessage.show({ message: messages.wishlistupdated });
        })
        .catch((msg) => {
          flashMessage.show({ message: msg, alertType: "danger" });
        });
    },
    remove(skuid) {
      this.$store
        .dispatch("wishlist/removeItem", [skuid, this.id])
        .then(() => {
          flashMessage.show({ message: messages.itemremoved });
        })
        .catch((msg) => {
          flashMessage.show({ message: msg, alertType: "danger" });
        });
    },
    addToCart(skuid, qty) {
      if (isNaN(qty) || qty <= 0) {
        flashMessage.show({ message: messages.enterquantity });
        return false;
      }
      const item = this.getItemBySkuid(skuid);
      if (item.hasOptions) {
        this.$store.dispatch("wishlist/removeItem", [skuid, this.id]).then(() => {
          window.location.href = `/selectoptions?addskuids=${skuid}&${skuid}_qty=${qty}`;
        });
      } else {
        const url = createAddUrl(skuid, "cartadd.html", qty);
        addModal(url).then(() => {
          this.$store.dispatch("wishlist/removeItem", [skuid, this.id]);
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
      this.$store.dispatch("wishlist/removeMany", [this.getAllSkuids(), this.id]).then(() => {
        window.location.href = url;
      });
    },
  },
};
</script>
<template>
  <div class="row receipt-container wishlist-container fadeIn">
    <div class="col-12">
      <h2>Your Wish List</h2>

      <div v-if="wishlistItems.length">
        <ShareWishlist :id="id" />
      </div>
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
            @updateQuantity="updateQuantity"
            @remove="remove"
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

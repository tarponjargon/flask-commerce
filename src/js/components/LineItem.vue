<script>
import { safeString, formatPrice, isEmpty, removeEmpty, correctDoubleEscaped } from "../services/Utils";
export default {
  props: ["item", "editable", "sharedWishlistView"],
  data() {
    return {
      qty: this.item.quantity,
      adding: false,
      imageBase: CFG.imageBase,
    };
  },
  computed: {
    notOrderable() {
      return !this.item.productExists && !this.item.nla;
    },
    isOrderable() {
      return this.item.productExists && this.item.nla;
    },
    productUrl() {
      return this.item.productExists && !this.item.isGiftwrap ? `/${this.item.productExists}.html` : "javascript:;";
    },
    personalization() {
      if (!this.item.personalization) return null;
      return this.item.personalization;
    },
    maxq() {
      return this.sharedWishlistView ? this.item.quantity : this.item.maxq;
    },
    imagePath() {
      return /^http/.test(this.item.thumbPath) ? this.item.thumbPath : this.imageBase + "/" + this.item.thumbPath;
    },
  },
  methods: {
    safeString,
    formatPrice,
    updateQuantity() {
      this.$emit("updateQuantity", this.item.skuid, this.qty);
    },
    remove() {
      this.$emit("remove", this.item.skuid);
    },
    addToCart() {
      this.adding = true;
      this.$emit("addToCart", this.item.skuid, this.qty);
    },
  },
};
</script>
<template>
  <div class="lineitem row" data-js="row" :data-detail-skuid="item.skuid">
    <div class="col-4 col-md-2 d-flex align-items-center justify-content-center">
      <a :href="productUrl" :class="{ 'dead-link': notOrderable }">
        <img :src="imagePath" onerror="imageError(this)" class="img-fluid cart-thumb" />
      </a>
    </div>

    <div class="lineitem-product col-8 col-md-10 position-relative">
      <div class="row">
        <div class="lineitem-product-description col-md-6">
          <!-- order status (if available) card -->
          <div v-if="item.itemStatus" class="card border-info mb-3">
            <div class="card-header text-white bg-info">
              Status: {{ item.itemStatus }}
              <span v-if="item.shipDate">{{ item.shipDate }}</span>
            </div>
            <div class="card-body">
              Ship Method: {{ item.shipMethodName }}
              <span v-if="item.trackingUrl">
                -
                <a :href="item.trackingUrl" target="_blank" rel="noopener">
                  Track
                  <span class="d-none d-sm-inline">{{ item.trackingNumber }}</span>
                </a>
              </span>
            </div>
          </div>

          <a :href="productUrl" class="product-title" :class="{ 'dead-link': notOrderable }">
            <span v-html="item.itemName" />
            <span v-if="item.optionedNotes">- {{ item.optionedNotes }}</span>
          </a>

          <div class="text-muted my-1" v-if="item.skuid">Item #: {{ item.skuid }}</div>

          <div v-if="item.giftWrapped" class="text-muted my-1">(Gift-bagged)</div>

          <div v-if="personalization" class="text-muted my-1">
            <div v-for="(persSet, i) in personalization" :key="i">
              <div v-for="(persLine, x) in persSet" :key="x">{{ persLine.prompt }}: {{ persLine.value }}</div>
            </div>
          </div>
        </div>
        <!-- /lineitem-product-description -->

        <div class="lineitem-qty col-md-2">
          <div class="lineitem-qty-line mt-2 mt-md-0">
            <span class="d-md-none">Qty: &nbsp;</span>

            <!-- if quantity is editable in this context -->
            <span v-if="editable">
              <form @submit.stop.prevent="updateQuantity" :data-add-item="item.skuid">
                <input
                  type="number"
                  class="quantity-field"
                  min="1"
                  pattern="^[0-9]+$"
                  required="required"
                  :max="maxq"
                  v-model="qty"
                  @change="updateQuantity"
                />
              </form>
              <div v-if="!sharedWishlistView" class="my-4 d-none d-md-block">
                <a
                  title="remove this product"
                  class="blue-link cart-product-btn remove-btn remove-from-cart text-decoration-none"
                  href="javascript:;"
                  @click.stop.prevent="remove"
                >
                  <i class="fa fa-times-circle me-1"></i>
                  <span>Remove</span>
                </a>
              </div>
            </span>

            <!-- if quantity is not editable in this context -->
            <span v-else class="d-inline d-md-block px-0 px-md-3 py-0 py-md-3">
              <span v-if="item.quantity">{{ item.quantity }}</span>
            </span>
          </div>
        </div>

        <div class="lineitem-price product-price col-md-2">
          <span class="d-md-none">Price:</span>
          <span v-if="item.price">{{ formatPrice(item.price) }}</span>
        </div>

        <div class="lineitem-total col-md-2">
          <span class="d-md-none">Total:</span>
          <span v-if="item.totalPrice">{{ formatPrice(item.totalPrice) }}</span>

          <button
            v-if="editable"
            class="d-block d-md-none mt-3 button-primary submit-button cart-button-mobile"
            type="button"
            @click.stop.prevent="addToCart"
          >
            <span v-if="adding">
              ADDING ...
              <i class="spinner icomoon-spinner"></i>
            </span>
            <span v-else>ADD TO CART</span>
          </button>
        </div>
      </div>

      <a
        v-if="editable"
        href="javascript:;"
        title="Remove item"
        class="remove-item-icon-mobile d-md-none blue-link text-decoration-none"
        @click.stop.prevent="remove"
      >
        <i class="fa fa-times-circle"></i>
      </a>
    </div>
    <div class="col-12 d-none d-md-block text-end">
      <button v-if="editable" class="btn btn-primary btn-xl w-25" type="button" @click.stop.prevent="addToCart">
        <span v-if="adding">
          ADDING ...
          <i class="spinner icomoon-spinner"></i>
        </span>
        <span v-else>ADD TO CART</span>
      </button>
    </div>
  </div>
</template>

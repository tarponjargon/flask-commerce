<script>
import { safeString, formatPrice, removeEmpty, fullOrderId } from "../services/Utils";
import Address from "./Address";
import LineItem from "./LineItem";
export default {
  props: ["order", "buttonText"],
  components: {
    Address,
    LineItem,
  },
  data() {
    return {
      billingAddress: {
        firstName: this.order.billingFirstName,
        lastName: this.order.billingLastName,
        address1: this.order.billingAddress1,
        address2: this.order.billingAddress2,
        city: this.order.billingCity,
        state: this.order.billingState,
        postalCode: this.order.billingPostalCode,
        country: this.order.billingCountry,
        email: this.order.billingEmail,
      },
      shippingAddress: {
        firstName: this.order.shippingFirstName,
        lastName: this.order.shippingLastName,
        address1: this.order.shippingAddress1,
        address2: this.order.shippingAddress2,
        city: this.order.shippingCity,
        state: this.order.shippingState,
        postalCode: this.order.shippingPostalCode,
        country: this.order.shippingCountry,
      },
    };
  },
  methods: {
    safeString,
    formatPrice,
    fullOrderId,
  },
  computed: {
    notes() {
      if (!this.order.notes) return null;
      return removeEmpty(this.order.notes.split("<br />"));
    },
    returnButtonText() {
      return this.buttonText ? this.buttonText : "Find another order";
    },
    hasOrderItems() {
      return "items" in this.order && this.order.items.length && this.order.items.map((i) => i.skuid).every((v) => v)
        ? true
        : false;
    },
  },
};
</script>
<template>
  <div class="row receipt-container fadeIn">
    <div class="col-10 d-flex align-items-center justify-content-start">
      <div class="shopping-cart-header">
        <h1 class="header-title primary-color border-bottom-0 mb-0">Order {{ fullOrderId(order.orderId) }}</h1>
      </div>
    </div>
    <div class="col-2 d-flex align-items-center justify-content-end">
      <button type="button" class="button-primary submit-button" @click="$emit('resetOrder')">
        <i class="fa fa-mail-reply me-1"></i>
        <span class="d-none d-md-inline">{{ returnButtonText }}</span>
      </button>
    </div>
    <div class="col-12">
      <hr />
    </div>

    <div class="col-12 receipt-content fadeIn mt-3">
      <div class="w-100 text-left d-block d-lg-none mt-3">
        <a href="/" aria-label="Homepage">
          <img src="/assets/images/logo.svg" class="logo" alt="Our Logo" />
        </a>
      </div>
      <div class="row mb-4">
        <div class="col-12 col-md-4 pe-4">
          <div class="row">
            <div class="col-12 text-left d-flex">
              <h4 class="mb-0">Billing Address</h4>
            </div>
          </div>
          <hr class="mb-3 mt-1" />
          <Address :address="billingAddress" />
        </div>
        <div class="col-12 col-md-4 pe-4 mt-3 mt-md-0" v-if="shippingAddress.address1">
          <div class="row">
            <div class="col-12 text-left d-flex">
              <h4 class="mb-0">Shipping Address</h4>
            </div>
          </div>
          <hr class="mb-3 mt-1" />
          <Address :address="shippingAddress" />
        </div>
        <div class="col-12 col-md-4 mt-3 mt-md-0" v-if="order.totalOrder">
          <div class="row">
            <div class="col-12 text-left d-flex">
              <h4 class="mb-0">Order Totals</h4>
            </div>
          </div>
          <hr class="mb-3 mt-1" />
          <div class="checkout-totals">
            <div class="row" v-if="order.totalDiscount">
              <div class="col-6 text-success">Discount:</div>
              <div class="col-6 text-end text-success">-{{ formatPrice(order.totalDiscount) }}</div>
            </div>
            <div class="row" v-if="order.totalSubtotal">
              <div class="col-6">Subtotal:</div>
              <div class="col-6 text-end">
                {{ formatPrice(order.totalSubtotal) }}
              </div>
            </div>
            <div class="row" v-if="order.totalShipping">
              <div class="col-6">Shipping:</div>
              <div class="col-6 text-end">
                {{ formatPrice(order.totalShipping) }}
              </div>
            </div>
            <div class="row" v-if="order.totalTax">
              <div class="col-6">Tax</div>
              <div class="col-6 text-end">
                {{ formatPrice(order.totalTax) }}
              </div>
            </div>
            <div class="row" v-if="order.totalCredit">
              <div class="col-6 text-success">Credit:</div>
              <div class="col-6 text-end text-success">-{{ formatPrice(order.totalCredit) }}</div>
            </div>
            <div class="row border-bottom-0 border-top mt-4" v-if="order.totalOrder">
              <div class="col-6">
                <strong>Total:</strong>
              </div>
              <div class="col-6 text-end">
                <strong>{{ formatPrice(order.totalOrder) }}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="your-items mt-4">
        <h3>YOUR ITEMS</h3>
      </div>

      <div class="lineitems">
        <div class="lineitem-headings row">
          <div class="col-md-7 lineitem-heading-product">Item</div>
          <div class="col-md-2 lineitem-heading-qty">Quantity</div>
          <div class="col-md-2 lineitem-heading-price">Price</div>
          <div class="col-md-1 lineitem-heading-total">Total</div>
        </div>

        <div v-for="item in order.items" :key="item.skuid" class="lineitem-wrapper" data-js="lineitem">
          <LineItem :item="item" />
        </div>
        <!-- /lineiotem-wrapper -->
      </div>
      <!-- /lineitems -->

      <div id="receipt-messages">
        <div class="row">
          <div class="col-12 col-md-6 pb-4">
            <div class="card h-100">
              <div class="card-header">
                <h3 class="mb-0">ORDER DETAILS</h3>
              </div>
              <div class="card-body">
                <div class="table-responsive w-auto">
                  <table class="table w-auto">
                    <tbody>
                      <tr>
                        <td class="border-top-0">
                          <strong>Order ID:</strong>
                        </td>
                        <td class="border-top-0">
                          {{ fullOrderId(order.orderId) }}
                        </td>
                      </tr>
                      <tr>
                        <td>
                          <strong>Order Date:</strong>
                        </td>
                        <td>{{ order.orderDate }}</td>
                      </tr>

                      <tr v-if="order.giftMessage">
                        <td>
                          <strong>Gift Message:</strong>
                        </td>
                        <td>{{ order.giftMessage.replaceAll("^", " ") }}</td>
                      </tr>

                      <tr v-if="notes && notes.length">
                        <td>
                          <strong>Notes:</strong>
                        </td>
                        <td>
                          <ul class="ps-2">
                            <li v-for="(note, i) in notes" :key="i">
                              {{ note }}
                            </li>
                          </ul>
                        </td>
                      </tr>

                      <tr v-if="order.couponCode">
                        <td>
                          <strong>Coupon Code:</strong>
                        </td>
                        <td>{{ order.couponCode }}</td>
                      </tr>

                      <tr v-if="order.sourceCode">
                        <td>
                          <strong>Catalog Code:</strong>
                        </td>
                        <td>{{ order.sourceCode }}</td>
                      </tr>

                      <tr v-if="order.comments">
                        <td>
                          <strong>Comments:</strong>
                        </td>
                        <td>{{ order.comments }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

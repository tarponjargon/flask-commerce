<script>
import { formatPrice } from "../../services/Utils";
export default {
  methods: {
    formatPrice,
  },
  props: ["order"],
};
</script>

<template>
  <div>
    <div class="checkout-totals">
      <div v-if="order.discount" class="row">
        <div class="col-6">Discount</div>
        <div class="col-6 text-end">-{{ formatPrice(order.discount) }}</div>
      </div>

      <div class="row">
        <div class="col-6">Subtotal</div>
        <div class="col-6 text-end">{{ formatPrice(order.subtotal) }}</div>
      </div>

      <div class="row">
        <div class="col-6">Tax</div>
        <div class="col-6 text-end">{{ formatPrice(order.tax) }}</div>
      </div>

      <div class="row">
        <div class="col-6">Shipping <span class="d-none d-md-inline-block">&nbsp;& Processing</span></div>
        <div class="col-6 text-end">{{ formatPrice(order.shipping) }}</div>
      </div>

      <div v-if="order.credit" class="row">
        <div class="col-6">Credit</div>
        <div class="col-6 text-end">{{ formatPrice(order.credit) }}</div>
      </div>

      <div class="row border-bottom-0 border-top-1">
        <div class="col-6"><strong>Total</strong></div>
        <div class="col-6 text-end">
          <strong>{{ formatPrice(order.orderTotal) }}</strong>
        </div>
      </div>
    </div>
  </div>
</template>

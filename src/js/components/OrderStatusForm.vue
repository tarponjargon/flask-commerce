<script>
import { fetchContent } from "../services/Ajax";
export default {
  props: ["orderId", "lastName", "zip", "loading", "error", "isCs"],
  data() {
    return {
      id: this.orderId,
      name: this.lastName,
      postcode: this.zip,
    };
  },
  methods: {
    getOrder() {
      this.$emit("getOrder", this.id, this.name, this.postcode);
    },
  },
  computed: {
    orderIdRequired() {
      return this.isCs ? false : "required";
    },
  },
  // mounted() {
  //   fetchContent("/store?action=get_inline_banner")
  //     .then((content) => {
  //       document.getElementById("inline-banner").innerHTML = content;
  //     })
  //     .catch((e) => {});
  // },
};
</script>
<template>
  <div class="row fadeIn mb-5">
    <div class="col-12">
      <div class="shopping-cart-header">
        <h1 class="header-title primary-color border-bottom-0 mb-0">Your Order Status</h1>
      </div>
      <hr />
      <div v-if="error" class="card text-white bg-danger mt-4 mb-2 mx-0 error-card">
        <div class="card-body">
          <p class="card-text">{{ error }}</p>
        </div>
      </div>
    </div>

    <div class="col-lg-6 col-md-12 mt-4">
      <form @submit.prevent="getOrder">
        <div class="row">
          <div class="col-12">
            <div class="form-group">
              <input
                type="text"
                v-model="id"
                :required="orderIdRequired"
                pattern="^[A-Za-z]?[A-Za-z]?[0-9]{6,9}$"
                title="Order IDs contain 7-9 digits"
                placeholder="Your Order ID"
                class="form-control"
              />
            </div>
          </div>
          <div class="col-12">
            <div class="form-group">
              <input
                type="text"
                v-model="name"
                required="required"
                title="Please enter your last name"
                placeholder="Last Name"
                class="form-control"
              />
            </div>
          </div>
          <div class="col-12">
            <div class="form-group">
              <input
                type="text"
                v-model="postcode"
                required="required"
                title="Check the format of your zip/postal code"
                placeholder="Billing Zip/Postal Code"
                pattern="^(\d{5}(-\d{4})?|[A-Z]\d[A-Z] ?\d[A-Z]\d)$"
                class="form-control"
              />
            </div>
          </div>
        </div>
        <button type="submit" class="button-primary submit-button">
          <span v-if="loading">
            SUBMITTING ...
            <i class="spinner icomoon-spinner"></i>
          </span>
          <span v-else>GET STATUS</span>
        </button>
      </form>
    </div>
    <div class="col-lg-6 col-md-12 mt-4 text-center" id="inline-banner"></div>
  </div>
</template>

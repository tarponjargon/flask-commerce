<script>
import { isEmpty, scrollToSelector } from "../../services/Utils";
import messages from "../../services/Messages";
import addressForm from "../AddressForm.vue";
export default {
  components: {
    "address-form": addressForm,
  },
  data() {
    return {
      updating: false,
      error: null,
      emptyAddress: {
        ship_fname: null,
        ship_lname: null,
        ship_street: null,
        ship_street2: null,
        ship_city: null,
        ship_state: null,
        ship_country: null,
        ship_postal_code: null,
      },
    };
  },
  computed: {},
  methods: {
    addAddress(address) {
      this.updating = true;
      this.error = null;
      this.$store
        .dispatch("address/newAddress", address)
        .then(() => {
          this.updating = false;
          flashMessage.show({ message: messages.addressadded });
          this.$router.push("/addresses");
        })
        .catch((e) => {
          this.error = e;
          scrollToSelector(".error-card");
          this.updating = false;
        });
    },
  },
};
</script>

<template>
  <div>
    <div class="row">
      <div class="col-6 col-md-6 d-flex align-items-center justify-content-start">
        <h2 class="mt-1 mb-0"><span class="d-none d-sm-inline">Add a</span> New Address</h2>
      </div>
      <div class="col-6 col-md-6 d-flex align-items-center justify-content-end">
        <router-link class="btn btn-sm btn-info me-0" :to="{ name: 'addresses' }">
          <i class="fa fa-mail-reply me-1"></i>
          <span class="d-none d-sm-inline me-1">Return to</span>addresses
        </router-link>
      </div>
    </div>
    <hr class="my-4" />

    <div v-if="error" class="card text-white bg-danger my-2 mx-0 error-card">
      <div class="card-body">
        <p class="card-text">
          <span v-html="error" />
        </p>
      </div>
    </div>

    <address-form
      :addressModel="emptyAddress"
      :buttonText="'Add Address'"
      :updating="updating"
      @submitAddress="addAddress"
    />
  </div>
</template>

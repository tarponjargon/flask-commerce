<script>
import { mapGetters } from "vuex";
import { scrollToSelector } from "../../services/Utils";
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
    };
  },
  computed: {
    ...mapGetters("address", ["getAddressById"]),
    address() {
      return this.getAddressById(this.$route.params.id);
    },
  },
  methods: {
    updateAddress(address) {
      this.updating = true;
      this.error = null;
      this.$store
        .dispatch("address/updateAddress", address)
        .then(() => {
          this.updating = false;
          flashMessage.show({ message: messages.addressupdated });
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
        <h2 class="mt-1 mb-0">
          Edit
          <span class="d-none d-sm-inline">Shipping</span>Address
        </h2>
      </div>
      <div class="col-6 col-md-6 d-flex align-items-center justify-content-end">
        <router-link class="btn btn-sm btn-info me-0" :to="{ name: 'addresses' }">
          <i class="fa fa-mail-reply"></i>
          <span class="d-none d-sm-inline">Return to</span>addresses
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
      v-if="address"
      :addressModel="address"
      :buttonText="'Update Address'"
      :updating="updating"
      @submitAddress="updateAddress"
    />
    <div v-else>Invalid address</div>
  </div>
</template>

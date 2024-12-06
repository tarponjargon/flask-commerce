<script>
import { useStore, mapGetters } from "vuex";
import messages from "../../services/Messages";
import { isEmpty, scrollToSelector } from "../../services/Utils";
import addressRender from "../Address.vue";
import popoverButton from "../PopoverBtn.vue";
export default {
  setup() {
    const store = useStore();
    return { store };
  },
  components: {
    "address-render": addressRender,
    "popover-button": popoverButton,
  },
  data() {
    return {
      updating: false,
      error: null,
    };
  },
  computed: {
    ...mapGetters("address", ["getAddressById"]),
    addresses() {
      return this.store.state.address.addresses;
    },
    shippingAddresses() {
      return this.store.state.address.addresses.filter((i) => i.id !== "billing");
    },
    user() {
      return this.store.state.user;
    },
    billingAddress() {
      return {
        firstName: this.user.bill_fname,
        lastName: this.user.bill_lname,
        address1: this.user.bill_street,
        address2: this.user.bill_street2,
        city: this.user.bill_city,
        state: this.user.bill_state,
        postalCode: this.user.bill_postal_code,
        country: this.user.bill_country,
        email: this.user.bill_email,
      };
    },
  },
  methods: {
    isEmptyObj(val) {
      return isEmpty(val);
    },
    deleteAddress(id) {
      this.updating = true;
      this.error = false;
      this.store
        .dispatch("address/deleteAddress", id)
        .then(() => {
          this.updating = false;
          flashMessage.show({ message: messages.addressdeleted });
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
        <h2 class="mt-1 mb-0"><span class="d-none d-sm-inline me-1">Your</span>Addresses</h2>
      </div>
      <div class="col-6 col-md-6 d-flex align-items-center justify-content-end">
        <router-link class="btn btn-sm btn-info me-0" :to="{ name: 'newaddress' }">
          <i class="fa fa-plus"></i>
          Add
          <span class="d-none d-sm-inline">an address</span>
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

    <div class="row">
      <!--billing address-->
      <div class="col-md-6 d-flex align-items-stretch mb-4">
        <div class="border-info card w-100">
          <div class="card-header d-flex align-items-center w-100 mh-25 text-bold">
            <h4 class="m-0">Billing Address</h4>
          </div>
          <div class="card-body">
            <span v-if="billingAddress.firstName">
              <address-render :address="billingAddress" />
            </span>
            <span v-else>
              <router-link :to="{ name: 'update' }">Please add a billing address</router-link>
            </span>
          </div>
          <div class="card-footer text-center px-0">
            <router-link data-test="editbilling" class="btn btn-sm btn-info mx-0" :to="{ name: 'update' }">
              <i class="fa fa-pencil"></i>
              Edit
            </router-link>
          </div>
        </div>
      </div>

      <!--shipping addresses-->
      <div
        v-for="address in shippingAddresses"
        :key="address.id"
        class="col-md-6 d-flex align-items-stretch mb-4"
        data-test-address="shippingaddress"
      >
        <div class="card w-100" :data-test-addressname="address.firstName">
          <div class="card-header d-flex align-items-center w-100 mh-25 text-bold">
            <h4 class="m-0">Shipping Address</h4>
          </div>
          <div class="card-body">
            {{ address.ship_fname }}
            {{ address.ship_lname }}
            <br />
            {{ address.ship_street }}
            <br />
            <span v-if="address.ship_street2">
              {{ address.ship_street2 }}
              <br />
            </span>
            {{ address.ship_city }},
            {{ address.ship_state }}
            {{ address.ship_postal_code }}
            <br />
            {{ address.ship_country }}
          </div>
          <div class="card-footer text-center px-0 position-relative">
            <router-link :to="{ name: 'editaddress', params: { id: address.id } }" class="btn btn-sm btn-info mx-0">
              <i class="fa fa-pencil"></i>
              Edit
            </router-link>
            <popover-button
              @onConfirm="deleteAddress(address.id)"
              :buttonText="'Delete'"
              :buttonClass="'btn btn-sm btn-warning mx-1'"
              :iconClass="'fa fa-trash'"
              :loading="updating"
            />
          </div>
        </div>
      </div>

      <div class="col-md-6 d-flex align-items-stretch mb-4">
        <div class="card w-100 border-0">
          <div class="card-body px-0 d-flex justify-content-center align-items-center">
            <router-link class="text-decoration-none" :to="{ name: 'newaddress' }">
              <h1 class="mb-2 display-1 text-info text-bold text-center">
                <i class="fa fa-plus"></i>
              </h1>
              <h5 class="text-info">Add a new address</h5>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import messages from "../../services/Messages";
import { useRouter } from "vue-router";
import { useStore } from "vuex";
import useVuelidate from "@vuelidate/core";
import { copy, scrollToSelector } from "../../services/Utils";
import ValidatedField from "../ValidatedField";
import ValidatedSelect from "../ValidatedSelect";
import vuelidateMixin from "../../mixins/vuelidateMixin";
import { required, email } from "@vuelidate/validators";
export default {
  setup() {
    const v$ = useVuelidate();
    const store = useStore();
    const router = useRouter();
    return { v$, store, router };
  },
  mixins: [vuelidateMixin],
  components: {
    "validated-field": ValidatedField,
    "validated-select": ValidatedSelect,
  },
  created() {
    this.store.dispatch("getStates");
  },
  data() {
    return {
      user: copy(this.store.state.user),
      updating: false,
      error: null,
    };
  },
  methods: {
    updateBilling() {
      this.error = null;
      this.v$.$touch();
      if (!this.v$.$invalid) {
        this.updating = true;
        if (window.dataLayer) window.dataLayer.push({ event: "userUpdateSubmit" });
        this.store
          .dispatch("saveUser", this.user)
          .then(() => {
            flashMessage.show({ message: messages.profileupdated });
            this.updating = false;
            this.router.push("/");
          })
          .catch((e) => {
            this.error = e;
            scrollToSelector(".error-card");
            this.updating = false;
          });
      }
    },
  },
  computed: {
    bill_email: {
      get() {
        return this.user.bill_email;
      },
      set(val) {
        this.user.bill_email = val;
      },
    },
    optin: {
      get() {
        return this.user.optin;
      },
      set(val) {
        this.user.optin = val;
      },
    },
    bill_fname: {
      get() {
        return this.user.bill_fname;
      },
      set(val) {
        this.user.bill_fname = val;
      },
    },
    bill_lname: {
      get() {
        return this.user.bill_lname;
      },
      set(val) {
        this.user.bill_lname = val;
      },
    },
    bill_street: {
      get() {
        return this.user.bill_street;
      },
      set(val) {
        this.user.bill_street = val;
      },
    },
    bill_street2: {
      get() {
        return this.user.bill_street2;
      },
      set(val) {
        this.user.bill_street2 = val;
      },
    },
    bill_city: {
      get() {
        return this.user.bill_city;
      },
      set(val) {
        this.user.bill_city = val;
      },
    },
    bill_state: {
      get() {
        return this.user.bill_state;
      },
      set(val) {
        this.user.bill_state = val;
      },
    },
    bill_postal_code: {
      get() {
        return this.user.bill_postal_code;
      },
      set(val) {
        this.user.bill_postal_code = val;
      },
    },
    bill_country: {
      get() {
        return this.user.bill_country;
      },
      set(val) {
        this.user.bill_country = val;
      },
    },
    bill_phone: {
      get() {
        return this.user.bill_phone;
      },
      set(val) {
        this.user.bill_phone = val;
      },
    },
    states() {
      return this.store.state.states;
    },
    countries() {
      return this.store.state.countries;
    },
  },
  validations: {
    bill_email: {
      required,
      email,
    },
    bill_fname: { required },
    bill_lname: { required },
    bill_street: { required },
    bill_street2: {},
    bill_city: { required },
    bill_state: { required },
    bill_postal_code: { required },
    bill_country: { required },
    bill_phone: {},
  },
  mounted() {
    // only touch if the address looks like it has values
    if (["lastName", "lastName", "address1"].every((x) => this.user[x])) this.v$.$touch();
  },
};
</script>

<template>
  <form @submit.prevent="updateBilling">
    <h2>Update Your Account Info</h2>
    <hr class="mb-4" />

    <div v-if="error" class="card text-white bg-danger my-2 mx-0 error-card">
      <div class="card-body">
        <p class="card-text">
          <span v-html="error" />
        </p>
      </div>
    </div>

    <div class="row pb-2">
      <div class="col-xs-12 col-md-6">
        <h4>Your E-Mail Address</h4>
        <div :class="validationStyling('bill_email')" class="validate-input">
          <input
            class="form-control"
            type="email"
            name="email"
            v-model.lazy="v$['bill_email'].$model"
            @focus="v$['bill_email'].$reset"
            @blur="v$['bill_email'].$touch"
            id="account-update-email"
          />
        </div>
        <div v-if="v$['bill_email'].$error" class="validate-field-error-message">
          {{ getFirstError("bill_email") }}
        </div>
      </div>

      <div class="col-xs-12 col-md-6 mt-3 mt-md-0 mb-2 mb-md-0 email-updates">
        <h4>Receive E-Mail Updates?</h4>

        <div data-js="checkout-optin">
          <div class="d-inline me-2">
            <input type="radio" name="optin" v-model="optin" value="yes" id="account-option-pref-yes" />
            <label class="mb-0" for="account-option-pref-yes">
              <h6 class="mb-0 ps-1">Yes</h6>
            </label>
          </div>

          <div class="d-inline me-2">
            <input type="radio" name="optin" v-model="optin" value="no" id="account-option-pref-no" />
            <label class="mb-0" for="account-option-pref-no">
              <h6 class="mb-0 ps-1">No</h6>
            </label>
          </div>
        </div>
      </div>
    </div>

    <hr class="mb-4" />

    <h4>Billing Address</h4>
    <hr class="mb-3" />

    <div class="row">
      <div class="col-sm-6" data-test="firstName">
        <div class="form-group">
          <label>First Name</label>
          <validated-field :v$="v$" :fieldName="'bill_fname'" />
        </div>
      </div>
      <div class="col-sm-6">
        <div class="form-group">
          <label>Last Name</label>
          <validated-field :v$="v$" :fieldName="'bill_lname'" />
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-sm-6">
        <div class="form-group">
          <label>Address 1</label>
          <validated-field :v$="v$" :fieldName="'bill_street'" />
        </div>
      </div>
      <div class="col-sm-6">
        <div class="form-group">
          <label>Address 2</label>
          <input class="form-control" v-model="bill_street2" name="bill_street2" type="text" />
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-sm-6">
        <div class="form-group">
          <label>City</label>
          <validated-field :v$="v$" :fieldName="'bill_city'" />
        </div>
      </div>
      <div class="col-sm-6">
        <div class="form-group">
          <label>State</label>
          <validated-select
            :v$="v$"
            :fieldName="'bill_state'"
            :selectList="states"
            :selectLabel="'Select State / Province'"
          />
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-sm-6">
        <div class="form-group">
          <label>Zip/Postal Code</label>
          <validated-field :v$="v$" :fieldName="'bill_postal_code'" />
        </div>
      </div>
      <div class="col-sm-6">
        <div class="form-group">
          <label>Country</label>
          <validated-select
            :v$="v$"
            :fieldName="'bill_country'"
            :selectList="countries"
            :selectLabel="'Select Country'"
          />
        </div>
      </div>
    </div>

    <div class="row pb-2">
      <div class="col-sm-6 col-12">
        <div class="form-group">
          <label>Phone</label>
          <input class="form-control" v-model="bill_phone" data-test="phone" type="text" />
        </div>
      </div>
    </div>

    <button class="btn btn-primary" data-test="account-update-submit" :disabled="v$.$invalid">
      <span v-if="updating">
        Updating ...
        <i class="spinner icomoon-spinner"></i>
      </span>
      <span v-else>Update</span>
    </button>
  </form>
</template>

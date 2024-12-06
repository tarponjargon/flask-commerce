<script>
import { useStore } from "vuex";
import useVuelidate from "@vuelidate/core";
import vuelidateMixin from "../mixins/vuelidateMixin";
import { isEmpty, copy } from "../services/Utils";
import ValidatedField from "./ValidatedField";
import ValidatedSelect from "./ValidatedSelect";
import { required } from "vuelidate/lib/validators";
export default {
  setup() {
    return {
      v$: useVuelidate(),
      store: useStore(),
    };
  },
  props: ["addressModel", "buttonText", "updating"],
  data() {
    return {
      address: copy(this.addressModel),
    };
  },
  mixins: [vuelidateMixin],
  components: {
    "validated-field": ValidatedField,
    "validated-select": ValidatedSelect,
  },
  created() {
    this.store.dispatch("getStates");
  },
  methods: {
    sendAddress() {
      this.v$.$touch();
      if (!this.v$.$invalid) {
        this.$emit("submitAddress", this.address);
      }
    },
  },
  computed: {
    ship_fname: {
      get() {
        return this.address.ship_fname;
      },
      set(val) {
        this.address.ship_fname = val;
      },
    },
    ship_lname: {
      get() {
        return this.address.ship_lname;
      },
      set(val) {
        this.address.ship_lname = val;
      },
    },
    ship_street: {
      get() {
        return this.address.ship_street;
      },
      set(val) {
        this.address.ship_street = val;
      },
    },
    ship_street2: {
      get() {
        return this.address.ship_street2;
      },
      set(val) {
        this.address.ship_street2 = val;
      },
    },
    ship_city: {
      get() {
        return this.address.ship_city;
      },
      set(val) {
        this.address.ship_city = val;
      },
    },
    ship_state: {
      get() {
        return this.address.ship_state;
      },
      set(val) {
        this.address.ship_state = val;
      },
    },
    ship_postal_code: {
      get() {
        return this.address.ship_postal_code;
      },
      set(val) {
        this.address.ship_postal_code = val;
      },
    },
    ship_country: {
      get() {
        return this.address.ship_country;
      },
      set(val) {
        this.address.ship_country = val;
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
    ship_fname: { required },
    ship_lname: { required },
    ship_street: { required },
    ship_street2: {},
    ship_city: { required },
    ship_state: { required },
    ship_postal_code: { required },
    ship_country: { required },
  },
  mounted() {
    if (!isEmpty(this.address)) this.v$.$touch(); // only touch if there are values in address object
  },
};
</script>

<template>
  <form @submit.prevent="sendAddress" class="address-form">
    <div class="row">
      <div class="col-sm-6">
        <div class="form-group">
          <label>First Name</label>
          <validated-field :v$="v$" :fieldName="'ship_fname'" :fieldType="'text'" />
        </div>
      </div>
      <div class="col-sm-6">
        <div class="form-group">
          <label>Last Name</label>
          <validated-field :v$="v$" :fieldName="'ship_lname'" :fieldType="'text'" />
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-sm-6">
        <div class="form-group">
          <label>Address 1</label>
          <validated-field :v$="v$" :fieldName="'ship_street'" :fieldType="'text'" />
        </div>
      </div>
      <div class="col-sm-6">
        <div class="form-group">
          <label>Address 2</label>
          <validated-field :v$="v$" :fieldName="'ship_street2'" :fieldType="'text'" />
        </div>
      </div>
    </div>

    <div class="row">
      <div class="col-sm-6">
        <div class="form-group">
          <label>City</label>
          <validated-field :v$="v$" :fieldName="'ship_city'" :fieldType="'text'" />
        </div>
      </div>
      <div class="col-sm-6">
        <div class="form-group">
          <label>State</label>
          <validated-select
            :v$="v$"
            :fieldName="'ship_state'"
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
          <validated-field :v$="v$" :fieldName="'ship_postal_code'" :fieldType="'text'" />
        </div>
      </div>
      <div class="col-sm-6">
        <div class="form-group">
          <label>Country</label>
          <validated-select
            :v$="v$"
            :fieldName="'ship_country'"
            :selectList="countries"
            :selectLabel="'Select Country'"
          />
        </div>
      </div>
    </div>

    <button class="btn btn-primary" :disabled="v$.$invalid">
      <span v-if="updating">
        Adding ...
        <i class="spinner icomoon-spinner"></i>
      </span>
      <span v-else>{{ buttonText }}</span>
    </button>
  </form>
</template>

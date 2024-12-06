<script>
import { mapState } from "vuex";
import { isEmpty } from "../../services/Utils";
export default {
  methods: {
    isEmptyObj(val) {
      return isEmpty(val);
    },
  },
  computed: {
    ...mapState(["user", "loading"]),
  },
};
</script>

<template>
  <div v-if="!loading" class="col-md-6 d-flex align-items-stretch mb-4">
    <div class="card w-100">
      <div class="card-header d-flex align-items-center w-100">
        <div class="row mx-0 w-100">
          <div class="col-6 col-md-6 px-0 d-flex align-items-center">
            <h5 class="card-title">Your Account Info</h5>
          </div>
          <div class="col-6 col-md-6 px-0 d-flex align-items-center justify-content-end">
            <router-link to="update" class="btn btn-sm btn-info">UPDATE</router-link>
          </div>
        </div>
      </div>
      <div class="card-body" data-test="billing-address">
        <strong>E-Mail:</strong>
        {{ user.bill_email }}
        <br />
        <br />
        <strong>Billing Address:</strong>
        <br />
        <div v-if="user.bill_fname">
          {{ user.bill_fname }} {{ user.bill_lname }}
          <span v-if="user.bill_street">
            <br />
            {{ user.bill_street }}
            <br />
          </span>

          <span v-if="user.bill_street2">
            {{ user.bill_street2 }}
            <br />
          </span>

          <span v-if="user.bill_city">{{ user.bill_city }},&nbsp;</span>

          <span v-if="user.bill_state">{{ user.bill_state }}&nbsp;</span>

          <span v-if="user.bill_postal_code">
            {{ user.bill_postal_code }}
            <br />
          </span>

          <span v-if="user.bill_phone">{{ user.bill_phone }}</span>
          <span v-if="user.bill_email">
            <br />
            {{ user.bill_email }}
            <br />
          </span>
        </div>
        <div v-else>
          <router-link :to="{ name: 'update' }">(add billing address)</router-link>
        </div>

        <span v-if="isEmptyObj(user)">
          <br />
          <router-link :to="{ name: 'update' }">(add a billing address)</router-link>
        </span>
      </div>
    </div>
  </div>
</template>

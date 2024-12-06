<script>
export default {
  computed: {
    loading() {
      return this.$store.state.loading;
    },
    addresses() {
      // put defaults bill and/or ship first
      return this.$store.state.address.addresses.sort(
        (a, b) => b.isDefaultBilling - a.isDefaultBilling || b.isDefaultShipping - a.isDefaultShipping
      );
    },
    filteredAddresses() {
      return this.addresses.length ? this.addresses.slice(0, 5) : [];
    },
  },
};
</script>

<template>
  <div v-if="!loading" class="col-md-6 d-flex align-items-stretch mb-4">
    <div class="card w-100">
      <div class="card-header d-flex align-items-center w-100 mh-25">
        <div class="row w-100 mx-0">
          <div class="col-6 col-md-6 px-0 d-flex align-items-center">
            <h5 class="card-title">Your Addresses</h5>
          </div>
          <div class="col-6 col-md-6 px-0 d-flex align-items-center justify-content-end">
            <router-link class="btn btn-sm btn-info" :to="{ name: 'addresses' }"> VIEW/EDIT </router-link>
          </div>
        </div>
      </div>
      <div class="card-body">
        <div v-if="addresses.length">
          <table class="table account-summary-table">
            <tbody>
              <tr v-for="(address, index) in filteredAddresses" :key="address.id">
                <td>
                  <div>{{ index + 1 }}.</div>
                </td>
                <td>
                  <router-link :to="{ name: 'addresses' }">
                    {{ address.ship_fname }} {{ address.ship_lname }},
                    {{ address.ship_street }}
                  </router-link>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="addresses.length > 5" class="w-100 d-block text-center">
            <span v-if="addresses.length">
              <strong>
                <router-link :to="{ name: 'addresses' }" class="brand-link">
                  See all {{ addresses.length }} addresses...
                </router-link>
              </strong>
            </span>
          </div>
        </div>
        <div v-else>No addresses yet</div>
      </div>
    </div>
  </div>
</template>

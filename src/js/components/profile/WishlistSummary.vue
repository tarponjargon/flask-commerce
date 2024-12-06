<script>
import { formatPrice } from "../../services/Utils";
import { mapState } from "vuex";
export default {
  computed: {
    ...mapState({
      loading: (state) => state.loading,
      wishlistItems: (state) => state.wishlist.items,
    }),
    filteredItems() {
      return this.wishlistItems.length ? this.wishlistItems.slice(0, 3) : [];
    },
  },
  methods: {
    formatPrice,
  },
  data() {
    return {
      imageBase: CFG.imageBase,
    };
  },
};
</script>
<template>
  <div v-if="!loading" class="col-md-6 d-flex align-items-stretch mb-4">
    <div class="card w-100">
      <div class="card-header d-flex align-items-center w-100 mh-25">
        <div class="row w-100 mx-0">
          <div class="col-6 col-md-6 px-0 d-flex align-items-center">
            <h5 class="card-title">Your Wishlist</h5>
          </div>
          <div class="col-6 col-md-6 px-0 d-flex align-items-center justify-content-end">
            <router-link class="btn btn-sm btn-info" :to="{ name: 'wishlist' }">VIEW/EDIT</router-link>
          </div>
        </div>
      </div>
      <div class="card-body">
        <div v-if="wishlistItems.length">
          <table class="table account-summary-table">
            <tbody>
              <tr v-for="item in filteredItems" :key="item.skuid">
                <td>
                  <a :href="item.url">
                    <img
                      :src="imageBase + '/' + item.thumbPath"
                      onerror="imageError(this)"
                      class="img-fluid cart-thumb"
                    />
                  </a>
                </td>
                <td>
                  <router-link :to="{ name: 'wishlist' }">
                    <span v-html="item.itemName" />
                  </router-link>
                </td>
                <td>{{ formatPrice(item.price) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="wishlistItems.length > 3" class="w-100 d-block text-center">
            <span v-if="wishlistItems.length">
              <strong>
                <router-link :to="{ name: 'wishlist' }">See all {{ wishlistItems.length }} items...</router-link>
              </strong>
            </span>
          </div>
        </div>
        <div v-else>No items yet</div>
      </div>
    </div>
  </div>
</template>

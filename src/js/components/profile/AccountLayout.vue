<script>
import store from "../../store";
import accountNav from "./AccountNav.vue";
export default {
  components: {
    "account-nav": accountNav,
  },
  created() {
    this.$store.dispatch("loadSummary");
  },
  data() {
    return {
      mobileMenu: false,
    };
  },
  methods: {
    toggleMobileMenu() {
      this.mobileMenu = !this.mobileMenu;
    },
  },
  computed: {
    authenticated() {
      return true;
    },
    loading() {
      return this.$store.state.loading;
    },
  },
};
</script>

<template>
  <div :class="{ 'loading-mask': loading }" class="container pt-0 pt-lg-4 pb-4 px-3 px-lg-0">
    <div v-if="!loading" class="row fadeIn">
      <div class="col-lg-4 d-none d-lg-block">
        <account-nav />
      </div>

      <!--user nav - mobile-->
      <div class="d-block d-lg-none mb-4 mt-0 w-100 overflow-hidden">
        <button
          @click="toggleMobileMenu()"
          class="btn btn-primary btn-block d-flex align-items-center justify-content-between mb-2"
        >
          <span>Account Menu</span>
          <i v-if="mobileMenu" class="fa fa-angle-up display-4 me-3"></i>
          <i v-else class="fa fa-angle-down display-4 me-3"></i>
        </button>
        <account-nav v-if="mobileMenu" />
      </div>

      <!--right side user content-->
      <div class="col-lg-8 profile-content">
        <router-view></router-view>
      </div>
      <!--end right side user content -->
    </div>
  </div>
</template>

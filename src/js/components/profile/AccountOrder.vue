<script>
import { mapGetters } from "vuex";
import { scrollIt, getBodyData } from "../../services/Utils";
import orderStatusDetail from "../OrderStatusDetail.vue";
export default {
  components: {
    orderStatusDetail,
  },
  data() {
    return {
      loading: false,
      order: null,
      defaultError: "No order found",
    };
  },
  methods: {
    returnToOrders() {
      this.$router.push({ name: "orders" });
    },
    noOrderFound(e = null) {
      console.error("failed account order lookup", this.$route.params.id, getBodyData("data-client-id"), e);
      flashMessage.show({ message: this.defaultError, alertType: "danger" });
      let lname = "";
      let zip = "";
      try {
        if (this.$store.state.user.bill_lname) lname = `&bill_lname=${this.$store.state.user.bill_lname}`;
        if (this.$store.state.user.bill_postal_code)
          zip = `&bill_postal_code=${this.$store.state.user.bill_postal_code}`;
      } catch (e) {}
      setTimeout(() => {
        //window.location.href = `/orderstatus?orderId=${CFG.orderPrefix}${this.$route.params.id}${lname}${zip}`;
      }, 700);
    },
    getOrder() {
      this.loading = true;
      const url = `/store?action=ajax_orderstatus&orderid=${CFG.orderPrefix}${this.$route.params.id}`;
      fetch(url, {
        credentials: "same-origin",
      })
        .then((r) => r.json())
        .then((data) => {
          if (data && "order" in data) {
            this.order = data.order;
            this.loading = false;
          } else {
            this.loading = false;
            this.noOrderFound();
          }
        })
        .catch((e) => {
          this.loading = false;
          this.noOrderFound(e);
        });
    },
  },
  created() {
    this.getOrder();
  },
  mounted() {
    scrollIt();
  },
};
</script>

<template>
  <div :class="{ 'loading-mask': loading }">
    <div v-if="!loading && order" class="fadeIn">
      <orderStatusDetail :order="order" :buttonText="'Return to orders'" @resetOrder="returnToOrders" />
    </div>
  </div>
</template>

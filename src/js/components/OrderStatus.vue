<script>
import OrderStatusForm from "./OrderStatusForm";
import OrderStatusDetail from "./OrderStatusDetail";
import { getUrlParams, serializeToParams, safeString } from "../services/Utils";
export default {
  components: {
    OrderStatusForm,
    OrderStatusDetail,
  },
  data() {
    return {
      container: document.querySelector(".orderstatus-wrapper"),
      loading: false,
      orderId: null,
      lastName: null,
      zip: null,
      error: null,
      order: null,
      isCs: false,
      defaultError: "Problem finding your order.  Please try again and contact us if you continue to have difficulty.",
    };
  },

  created() {
    const p = getUrlParams();
    const id = "orderid" in p ? safeString(p.orderid) : null;
    const name = "bill_lname" in p ? safeString(p.bill_lname) : null;
    const code = "bill_postal_code" in p ? safeString(p.bill_postal_code) : null;
    if (id && name && code) {
      this.getOrder(id, name, code);
    } else {
      // check if there is any session data set in the DOM to seed the form
      const dataEl = document.querySelector('[data-js="orderstatus-data"]');
      if (dataEl) {
        this.orderId = dataEl.getAttribute("data-order-id") || "";
        this.lastName = dataEl.getAttribute("data-lastname") || "";
        this.zip = dataEl.getAttribute("data-zip") || "";
        this.isCs = dataEl.getAttribute("data-cs") ? true : false;
      }
    }
  },

  computed: {
    showForm() {
      if (!this.order && !this.loading) {
        this.removeMask();
        return true;
      } else {
        return false;
      }
    },
  },

  methods: {
    getOrder(id, name, code) {
      // if (
      //   !/^[A-Za-z]?[0-9]{7,8}$/i.test(id.trim()) ||
      //   !name ||
      //   !/^(\d{5}(-\d{4})?|[A-Z]\d[A-Z] ?\d[A-Z]\d)$/i.test(code.trim())
      // ) {
      //   return false;
      // }
      this.loading = true;
      this.error = null;
      this.orderId = id.trim();
      this.lastName = safeString(name.trim());
      this.zip = code.trim();
      this.updateUrl();
      let url = `/store?action=ajax_orderstatus&orderid=${id}&bill_postal_code=${code}&bill_lname=${name}`;
      url += this.isCs ? "&CS=1" : "";
      this.removeMask();
      fetch(url, { credentials: "same-origin" })
        .then((r) => r.json())
        .then((data) => {
          if (data && "order" in data) {
            this.order = data.order;
          } else {
            this.error = data && "errors" in data && data.errors.length ? data.errors.join(" ") : this.defaultError;
            if (this.error) {
              console.error("orderstatus response but error message in payload", url, this.error);
            }
          }
          this.loading = false;
        })
        .catch((e) => {
          this.error = this.defaultError;
          this.loading = false;
          console.error("error loading orderstatus", url, e);
        });
    },
    updateUrl() {
      let params = serializeToParams({
        orderId: this.orderId,
        bill_lname: this.lastName,
        bill_postal_code: this.zip,
      });
      window.history.pushState(null, null, `https://${window.location.hostname}${window.location.pathname}?${params}`);
    },
    resetOrder() {
      this.order = null;
      window.history.pushState(null, null, `https://${window.location.hostname}${window.location.pathname}`);
    },
    removeMask() {
      this.container.classList.remove("loading-mask");
      this.container.classList.remove("mask-300");
    },
  },
};
</script>
<template>
  <div class="w-100" :class="{ 'loading-mask': loading, 'mask-300': loading }">
    <OrderStatusForm
      v-if="showForm"
      :orderId="orderId"
      :lastName="lastName"
      :zip="zip"
      :loading="loading"
      :error="error"
      :isCs="isCs"
      @getOrder="getOrder"
    />

    <OrderStatusDetail v-if="order" :order="order" @resetOrder="resetOrder" />
  </div>
</template>

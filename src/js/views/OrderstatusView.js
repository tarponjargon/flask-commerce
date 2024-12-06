import { createApp, h } from "vue";
import OrderStatus from "../components/OrderStatus.vue";

export default class OrderStatusView {
  constructor() {}
  init = (view) => {
    return new Promise((resolve) => {
      const app = createApp({
        render() {
          return h(OrderStatus);
        },
      });
      app.config.warnHandler = function (msg, vm, trace) {
        return null;
      };
      app.mount("#orderstatus-content");
      resolve(view);
    });
  };
}

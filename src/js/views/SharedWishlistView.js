import { createApp, h } from "vue";
import store from "../store";
import SharedWishlist from "../components/profile/SharedWishlist";
export default class SharedWishlistView {
  constructor() {}
  init = (view) => {
    return new Promise((resolve) => {
      const app = createApp({
        render() {
          return h(SharedWishlist);
        },
      });
      app.config.warnHandler = function (msg, vm, trace) {
        return null;
      };
      app.use(store);
      app.mount("#sharedwishlist-content");
      resolve(view);
    });
  };
}

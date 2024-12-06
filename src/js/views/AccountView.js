import { createApp, h } from "vue";
import store from "../store";
import router from "../router";
import accountLayout from "../components/profile/AccountLayout";
import vClickOutside from "click-outside-vue3";
import { isLoggedIn } from "../services/Utils";

export default class AccountView {
  constructor() {}
  init = (view) => {
    return new Promise((resolve) => {
      const app = createApp({
        render() {
          return h(accountLayout);
        },
      });
      app.use(router);
      app.use(store);
      app.use(vClickOutside);
      app.config.warnHandler = function (msg, vm, trace) {
        return null;
      };
      app.mount(`[data-view='${view}']`);
      this.autoLogout();
      document.querySelector('[data-view="account"]').classList.remove("loading-mask");
      resolve();
    });
  };

  autoLogout = () => {
    if (isLoggedIn() && window.location.pathname === "/account") {
      var idleSeconds = CFG.sessionTimeout;
      var idleTimer;
      var whenUserIdle = function () {
        window.location.href = "/logout";
      };
      var resetTimer = function () {
        clearTimeout(idleTimer);
        idleTimer = setTimeout(whenUserIdle, idleSeconds * 1000);
      };
      $(document.body).on("click", resetTimer);
      resetTimer(); // Start the timer when the page loads
    }
  };
}

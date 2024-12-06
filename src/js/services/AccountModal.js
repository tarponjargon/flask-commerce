import {
  spinButton,
  unSpinButton,
  showForgotPassword,
  showCreateAccount,
  signupHandler,
  getBodyData,
} from "./Utils";
import messages from "./Messages";

export default class AccountModal {
  constructor() {
    this.accountTabs = Array.from(document.querySelectorAll('#signin-tablist [role="tab"]'));
  }

  init = () => {
    return new Promise((resolve) => {
      this.startListeners();

      this.accountTabs[0].focus();
      resolve();
    });
  };

  unListen = () => {
    // public method called on modal close.  removes all listeners
    $("#account-modal").find("*").off();
  };

  getFocusedTabIndex = () => {
    return this.accountTabs.findIndex((i) => i === document.activeElement);
  };

  getNextTabIndex = (currentTabIndex = 0) => {
    let nextTabIndex = currentTabIndex + 1;
    if (currentTabIndex >= this.accountTabs.length - 1) nextTabIndex = 0;
    console.log("nextTabIndex", nextTabIndex);
    return nextTabIndex;
  };

  getPreviousTabIndex = (currentTabIndex = 0) => {
    let prevTabIndex = currentTabIndex - 1;
    if (currentTabIndex <= 0) prevTabIndex = this.accountTabs.length - 1;
    return prevTabIndex;
  };

  tabButtonKeyPress = (tab) => {
    tab.hasTabButtonListener = true;
    tab.addEventListener(
      "keydown",
      (event) => {
        const idx = this.getFocusedTabIndex();
        if (
          event.key === " " ||
          event.code === "Space" ||
          event.keyCode === 32 ||
          event.code === "Enter"
        ) {
          $(this.accountTabs[idx]).tab("show");
          event.preventDefault();
        } else if (event.code === "ArrowRight") {
          const i = this.getNextTabIndex(idx);
          this.accountTabs[i].focus();
          event.preventDefault();
        } else if (event.code === "ArrowLeft") {
          const i = this.getPreviousTabIndex(idx);
          this.accountTabs[i].focus();
          event.preventDefault();
        }
      },
      false
    );
  };

  updateTabAttrs = (newTab) => {
    // reset all
    $("#account-modal .nav-tabs .nav-link")
      .removeClass("active")
      .attr("aria-selected", false)
      .attr("tabindex", "-1");
    $(newTab).addClass("active").attr("aria-selected", true).attr("tabindex", "0");
  };

  startListeners = () => {
    // listen for clicks on tabs
    this.accountTabs.forEach((tab) => {
      if (!tab.hasTabFocusListener) {
        tab.hasTabFocusListener = true;
        tab.addEventListener("focus", (e) => {
          if (!tab.hasTabButtonListener) this.tabButtonKeyPress(tab);
        });
      }
    });

    // listen for tab shown to update active
    $('#account-modal [data-toggle="tab"]').on("shown.bs.tab", (e) => {
      this.updateTabAttrs(e.target);
    });

    // listen for links in text that activate tabs
    $("#signup-link").on("click", (e) => {
      showCreateAccount(e);
    });
    $("#forgotpassword-link").on("click", (e) => {
      showForgotPassword(e);
    });

    // mirror email to the other tab's email fields
    $("#signin-email, #signup-email, #forgotpassword-email").on("input change", function (e) {
      try {
        const fields = ["signin-email", "signup-email", "forgotpassword-email"];
        const val = $("#" + e.target.id).val();
        for (let i = 0; i < fields.length; i++) {
          let field = $("#" + fields[i]);
          if (field.attr("id") !== e.target.id) {
            field.val(val);
          }
        }
      } catch (err) {
        console.error(err);
      }
    });

    // 7/1/20 login form listener moved to WIndowListeners.js

    // signup submit
    $("#user-signup-form").on("submit", (e) => {
      if (window.dataLayer) window.dataLayer.push({ event: "userSignupSubmit" });
      e.preventDefault();
      signupHandler(e.delegateTarget, true);
    });

    // forgot password form submit
    $("#forgot-password-form").on("submit", (e) => {
      e.preventDefault();
      this.forgotPasswordHandler();
    });
  };

  forgotPasswordHandler = () => {
    if ($("#forgot-password-form .error-card").is(":visible")) {
      $("#forgot-password-form .error-card").slideUp();
    }
    spinButton("forgotpassword-button", "Submitting");

    const client = getBodyData("data-client-id");
    const url = `/store?action=forgotpassword_ajax&client=${client}`;
    const data = $("#forgot-password-form").serialize();
    const onSuccess = (data) => {
      if (data.success) {
        window.setTimeout(function () {
          unSpinButton("forgotpassword-button");
          // even on success, show an error about "if you have an account check your email"
          // i.e. we don't want to give an success or fail indicator
          if ("errors" in data) {
            console.log("errors", data.errors.join(", "));
            $("#forgot-password-form .error-card .card-text").html(data.errors.join(", "));
            $("#forgot-password-form .error-card").slideDown();
          }
        }, 1000);
      } else {
        unSpinButton("forgotpassword-button");
        if ("errors" in data) {
          console.log("errors", data.errors.join(", "));
          $("#forgot-password-form .error-card .card-text").html(data.errors.join(", "));
          $("#forgot-password-form .error-card").slideDown();
        }
      }
    };
    const onFail = () => {
      unSpinButton("forgotpassword-button");
      flashMessage.show({ message: messages.fatal });
    };

    fetch(url, {
      method: "POST",
      credentials: "same-origin",
      body: data,
    })
      .then((r) => r.json())
      .then((data) => onSuccess(data))
      .catch(() => {
        console.error("failed forgot password, retrying", client);
        fetch(url, {
          method: "POST",
          credentials: "same-origin",
          body: data,
        })
          .then((r) => r.json())
          .then((data) => onSuccess(data))
          .catch((e) => {
            console.error("failed retry forgot password", e, client);
            onFail();
          });
      });
  };
}

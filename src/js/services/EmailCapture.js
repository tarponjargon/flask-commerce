import Cookies from "js-cookie";
import { fetchContent, fetchJson } from "./Ajax";
import messages from "./Messages";
import {
  getEmailFromGTM,
  submitOptin,
  showCapture,
  getBodyData,
  validEmail,
  fadeOut,
  fadeIn,
} from "./Utils";

export default class EmailCapture {
  constructor() {
    window.dataLayer = window.dataLayer || [];
    this.cookieDuration = 400; //days
    this.email = getEmailFromGTM();
    this.drawerTarget = document.getElementById("footer-drawer");
    this.drawerHeight = "200px";
    this.drawerSpeed = 500;
    this.drawerContent = "";
    this.isUnsolicited = false;
  }
  init = (isUnsolicited = false) => {
    return new Promise((resolve) => {
      if (isUnsolicited) {
        this.isUnsolicited = true;
        window.setTimeout(() => {
          this.checkTrigger(); // after a short delay, check whether the email capture window should be shown in an unsolicited fashion
        }, CFG.captureModalDelay);
      }
      resolve();
    });
  };

  checkTrigger = () => {
    if ($("body").hasClass("modal-open")) return false; // kick the can down the road if there's a modal already open.  we'll get 'em next page load

    // if they have an email websource, an email on their url or are a mobile device, don't ever show window unsolicited
    if (
      this.email ||
      /websource=[A-Za-z]_[0-9A-Za-z]{6,8}/i.test(window.location.search) ||
      /utm_medium=email/i.test(window.location.search) ||
      /bill_email/i.test(window.location.search) ||
      getBodyData("data-collect-shown") || // defensive measures added 3/28/23 because CEO was seeing the slider too often
      Cookies.get("cart_id")
    ) {
      this.setToNoCapture();
    } else {
      this.setToCapture();
    }
  };

  setToNoCapture = () => {
    Cookies.set("capturewin", "nocapture", {
      expires: 400,
      path: "/",
      secure: true,
    });
  };

  setToCapture = () => {
    Cookies.set("capturewin", "capture", {
      expires: 400,
      path: "/",
      secure: true,
    });
    if ($(window).width() < 992) {
      this.viewDrawerCapture();
    } else {
      this.viewCapture();
    }
  };

  viewCapture = () => {
    showCapture()
      .then(() => {
        this.initCaptureListener();
        window.dataLayer.push(
          {
            event: "VirtualPageView",
            VirtualPageURL: "/email_capture",
            VirtualPageTitle: "CAPTURE",
          },
          {
            event: "trackEvent",
            eventCategory: "E-Mail Capture Showed",
            eventAction: "Modal",
            eventLabel: this.isUnsolicited ? "unsolicited" : "clicked",
          }
        );
      })
      .catch(() => {});
  };

  initCaptureListener = () => {
    $("#addcapform").on("submit", function (e) {
      e.preventDefault();
      if (window.dataLayer) window.dataLayer.push({ event: "modalEmailSubmit" });
      submitOptin($("#addcapform #email").val());
    });
  };

  viewDrawerCapture = () => {
    this.showCaptureDrawer()
      .then(() => {
        this.initDrawerCapture();
        window.dataLayer.push(
          {
            event: "VirtualPageView",
            VirtualPageURL: "/email_capture_drawer",
            VirtualPageTitle: "CAPTURE",
          },
          {
            event: "trackEvent",
            eventCategory: "E-Mail Capture Showed",
            eventAction: "Drawer",
            eventLabel: "",
          }
        );
      })
      .catch(() => {});
  };

  initDrawerCapture = () => {
    this.drawerContent.querySelector("#emailsignup-drawer").addEventListener("submit", (e) => {
      e.preventDefault();
      this.submitDrawerOptin(e.target.querySelector("input[name='bill_email']").value);
      if (window.dataLayer) window.dataLayer.push({ event: "drawerEmailSubmit" });
    });
  };

  drawerCloseListener = () => {
    document.querySelectorAll('[data-js="footer-flyout-close"]').forEach((el) => {
      el.addEventListener("click", (e) => {
        e.preventDefault();
        this.drawerContent.animate({ height: [this.drawerHeight, "0px"] }, this.drawerSpeed);
        this.drawerContent.style.height = "0px";
        setTimeout(() => {
          this.drawerTarget.innerHTML = "";
        }, 1000);
      });
    });
  };

  showCaptureDrawer = () => {
    // this shows the email capture drawer that slides up from the bottom
    return new Promise((resolve, reject) => {
      const url = "/email_capture_drawer?collect_shown=1";
      const client = getBodyData("data-client-id");
      fetchContent(url)
        .then((content) => {
          this.drawerTarget.innerHTML = content;
          this.drawerContent = this.drawerTarget.querySelector('[data-js="footer-flyout"]');
          this.drawerContent.animate({ height: ["0px", this.drawerHeight] }, this.drawerSpeed);
          this.drawerContent.style.height = this.drawerHeight;
          this.drawerCloseListener();
          resolve();
        })
        .catch((e) => {
          console.error("showCaptureDrawer failed", client, e);
        });
    });
  };

  submitDrawerOptin = (email) => {
    // submits an optin.  if the capture modal is not showing, load it.
    if (!validEmail(email)) {
      flashMessage.show({ message: messages.invalidemail });
      return false;
    }

    const url = "/process_email_capture";
    const data = `bill_email=${encodeURIComponent(
      email
    )}&request=optinrequest&optin=yes&showpromo=1&capture=Y`;
    const client = getBodyData("data-client-id");
    fetch(url, {
      method: "POST",
      credentials: "same-origin",
      body: data,
    })
      .then((r) => r.json())
      .then((j) => {
        var resultVar = 0;
        for (var i = 0; i < j.length; i++) {
          resultVar = j[i].result;
        }
        if (resultVar === "0") {
          fadeOut(this.drawerContent.querySelector("#drawer-default-content"));
          fadeIn(this.drawerContent.querySelector("#drawer-success-content"));
          fetchJson(`/default?IS_NEW_EMAIL=${CFG.signupCoupon}`);
          window.dataLayer.push({
            event: "trackEvent",
            eventCategory: "E-Mail Capture Complete",
            eventAction: "Drawer",
            eventLabel: "New E-mail",
          });
          window.dataLayer.push({
            event: "welcomeEmailSent",
            email: email,
            requestType: "optinrequest",
          });
        } else {
          fadeOut(this.drawerContent.querySelector("#drawer-default-content"));
          fadeIn(this.drawerContent.querySelector("#drawer-fail-content"));
          window.dataLayer.push({
            event: "trackEvent",
            eventCategory: "E-Mail Capture Complete",
            eventAction: "Drawer",
            eventLabel: "E-mail Exists",
          });
        }
      })
      .catch((e) => {
        console.error("failed submitoptin", client, e);
      });
  };
}

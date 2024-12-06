import Cookies from "js-cookie";
import { disableBodyScroll, enableBodyScroll } from "body-scroll-lock";
import {
  spinButton,
  unSpinButton,
  spinLink,
  unSpinLink,
  submitOptin,
  updateMiniCart,
  getPhase,
  getPageType,
  closeModal,
  lazyLoadImages,
  removeMask,
  showForgotPassword,
  showCreateAccount,
  showTrackOrder,
  showLogin,
  hasCartItems,
  loadCarousel,
  loginHandler,
  waitForSelector,
  scrollToSelector,
  getBodyData,
  handleZendesk,
} from "./Utils";
import { directAdd } from "./DetailUtils";
import AccountModal from "./AccountModal";
import CartModal from "./CartModal";
import { fetchJson } from "./Ajax";
import { trackAutoSuggest } from "./AutoSuggest";
import { showMiniCart } from "./MiniCart";

export default class Listeners {
  constructor() {
    window.dataLayer = window.dataLayer || [];
    this.pageType = getPageType();
    this.phase = getPhase();
    this.accountModal = null;
    this.cartModal = null;
  }
  init = () => {
    return new Promise((resolve) => {
      lazyLoadImages();
      this.startListeners();

      // load any carousels which may appear on this view
      loadCarousel();

      // load header banner slider
      $(".offer_banner").on("init", (event) => {
        $(".offer_banner .offer-slide").css("visibility", "visible");
      });
      $(".offer_banner").slick({
        infinite: true,
        slidesToShow: 1,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 9000,
      });

      // run emailcapture check
      // this.initUnsolicitedCapture();

      // sends ajax request to keep a session alive IF cart is showing it has items
      if (hasCartItems()) {
        this.keepAlive();
      }

      // add some funcs to window for inline use
      window.spinButton = spinButton;
      window.unSpinButton = unSpinButton;
      window.spinLink = spinLink;
      window.unSpinLink = unSpinLink;
      window.closeModal = closeModal;
      window.directAdd = directAdd;
      window.showForgotPassword = showForgotPassword;
      window.showCreateAccount = showCreateAccount;
      window.showTrackOrder = showTrackOrder;
      window.showLogin = showLogin;
      window.lazyLoadImages = lazyLoadImages;
      window.removeMask = removeMask;
      window.waitForSelector = waitForSelector;
      window.emailCapture = this.emailCapture;
      window.handleZendesk = handleZendesk;

      if (getBodyData("data-phase") === "shopping") {
        this.initAutoSuggestListener();
      }

      resolve();
    });
  };

  initAutoSuggestListener = () => {
    const searchSels = [
      ".search .input-group .ss__autocomplete--target",
      ".mobile_search .form-group .ss__autocomplete--target",
    ];
    searchSels.forEach((sel) => {
      waitForSelector(sel)
        .then((el) => {
          const autoSuggestObserver = new MutationObserver(trackAutoSuggest);
          autoSuggestObserver.observe(el, {
            childList: true,
            subtree: true,
          });
        })
        .catch((e) => {});
    });
  };

  startListeners = () => {
    // listen for first interaction with page
    document.addEventListener("scroll", this.onInteraction, false);
    document.addEventListener("click", this.onInteraction, false);
    document.addEventListener("touchstart", this.onInteraction, false);
    document.addEventListener("mousemove", this.onInteraction, false);

    $(".skip-to-main-content-link").on("click", function (e) {
      e.preventDefault();
      scrollToSelector("#main-content");
    });

    $(".mobile_nav-block .trigger").on("click", function (event) {
      event.preventDefault();
      $(this).toggleClass("active").next(".menu_accordion").slideToggle();
      if ($(this).hasClass("active")) {
        $(this).attr("aria-expanded", true);
      } else {
        $(this).attr("aria-expanded", false);
      }
    });
    $(".nav_block .trigger").on("click", function (event) {
      event.preventDefault();
      $(this).toggleClass("active").next(".menu_accordion").slideToggle();
      if ($(this).hasClass("active")) {
        $(this).attr("aria-expanded", true);
      } else {
        $(this).attr("aria-expanded", false);
      }
    });

    $("[data-accessibility-widget]").on("click", function (e) {
      e.preventDefault();
      document.querySelector(".uwy").style.display = "block";
      document.querySelector(".uiiw").click();
    });

    // if /forgetme is the route, also delete the capturewin cookie (set when email capture is seen)
    if (window.location.pathname === "/forgetme") {
      Cookies.remove("capturewin", { path: "/", secure: true });
    }

    // manually trigger the capture window
    $('[data-js="email-signup"], .optin-modal').on("click", (e) => {
      e.preventDefault();
      this.initEmailCapture(false)
        .then((capture) => {
          capture.viewCapture();
        })
        .catch(() => {});
    });

    // listen for minicart clicks
    $('[data-js="mini-cart"]').on("click", (e) => {
      // if they are already on the cart page, reload it
      if (window.location.pathname === "/cart") {
        window.location = "/cart";
        return;
      }
      if (window.dataLayer) window.dataLayer.push({ event: "minicartView" });
      e.preventDefault();
      showMiniCart();
      window.dataLayer.push({
        event: "VirtualPageView",
        VirtualPageURL: "/cart",
        VirtualPageTitle: "Minicart",
      });
    });

    // listen for login form submits
    // NOTE this handles ANY login form on the page with <form data-js="user-login-form">
    $('form[data-js="user-login-form"]').on("submit", (e) => {
      if (window.dataLayer) {
        window.dataLayer.push({ event: "userLoginSubmit" });
      }
      e.preventDefault();
      loginHandler(e.delegateTarget, true);
    });

    // listen for account modal open
    $("#account-modal").on("shown.bs.modal", () => {
      this.accountModal = new AccountModal();
      this.accountModal.init();
    });

    // listen for account modal close
    $("#account-modal").on("hidden.bs.modal", () => {
      this.accountModal.unListen();
    });

    $("#cart-modal").on("shown.bs.modal", () => {
      this.cartModal = new CartModal();
      this.cartModal.init();
    });

    $("#cart-modal").on("hidden.bs.modal", () => {
      this.cartModal.unListen();
    });

    $("#smallModal").on("hidden.bs.modal", () => {
      if (this.cartModal) this.cartModal.unListen();
      $("#smallModal .modal-dialog").css("max-width", "");
      $("#smallModal .modal-content").html("");
    });

    $("#capture-modal").on("hidden.bs.modal", () => {
      $("#addcapform").off();
      $("#capture-modal .modal-content").html("");
    });

    // listen for modal, apply data-aria-labelledby to aria-labelledby
    $(document).on("shown.bs.modal", function (e) {
      const dataAria = $(e.target).attr("data-aria-labelledby");
      if (dataAria) $(e.target).attr("aria-labelledby", dataAria);
    });

    $(document).on("hidden.bs.modal", function (e) {
      if ($(e.target).attr("aria-labelledby") && $(e.target).attr("data-aria-labelledby")) {
        $(e.target).removeAttr("aria-labelledby");
      }
    });

    // footer email signup form submits
    $(document).on("submit", 'form[id="emailsignup"]', function (e) {
      e.preventDefault();
      submitOptin($(this).find("[name='bill_email']").val());
    });

    // check if the id="restrict-ship-modal" exists in the DOM.  if so, show it.
    if ($("#restrict-ship-modal").length) {
      $("#restrict-ship-modal").modal("show");
    }

    // hazel workaround. if the cart is empty AND a 'cart' cookie exists, fire off an ajax request to populate minicart from prev session data in cookie
    let cartq = document.querySelector('[data-js="cart-item-quantity"]');
    if (cartq && !cartq.innerText.trim() && Cookies.get("cart_id")) {
      updateMiniCart();
    }

    // utility modal handler attached by just adding 'showmodal' class
    $(document).on("click", ".showmodal", function (e) {
      e.preventDefault();
      const href = $(this).attr("href");
      $("#smallModal .modal-content").load(href, function () {
        $("#smallModal").modal("show");
        // jump to an anchor if one is on the url
        if (href.indexOf("#") != -1) {
          const hash = href.split("#")[1];
          waitForSelector(`#smallModal .modal-content a[name="${hash}"]`).then((el) => {
            setTimeout(() => {
              el.scrollIntoView();
            }, 600);
          });
        }
      });
    });

    // listen for any ajax errors and report to error service
    $(document).ajaxError(function (event, jqxhr, settings) {
      //console.error('AJAX error: thrownError', thrownError);
      console.error("AJAX error: jqxhr", JSON.stringify(jqxhr, null, 4));
      if (settings && settings.url) console.error("AJAX error:", settings.url);
      //console.error('AJAX error: event', event);
    });

    // listen for clicks on virtual catalog
    $('[data-js="virtual-catalog"]').on("click", function (e) {
      e.preventDefault();
      let dropName = $('[data-js="mobile-virtual-catalog"]').attr("data-title");
      window.dataLayer.push({
        event: "trackEvent",
        eventCategory: "Catalog Flipbook",
        eventAction: dropName,
        eventLabel: "",
      });
      if ($(window).width() < 1200) {
        $.getScript(
          "//static.fliphtml5.com/web/js/plugin/LightBox/js/fliphtml5-light-box-api-min.js",
          function (data, textStatus, jqxhr) {
            waitForSelector(
              '[href="//static.fliphtml5.com/web/js/plugin/LightBox/css/fliphtml5-light-box-api-min.css"]'
            ).then(() => {
              setTimeout(function () {
                $('[data-js="mobile-virtual-catalog"]').trigger("click");
              }, 500);
            });
          }
        );
      } else {
        var href = $(this).attr("href");
        var modalWidth = $(window).width() > 1500 ? $(window).width() - 500 : 1000;
        var iframeWidth = modalWidth - 100;
        var iframeHeight = parseInt((iframeWidth * 400) / 700);
        $("#smallModal .modal-dialog").css("max-width", modalWidth);
        $("#smallModal .modal-content").load(href, function () {
          $("#smallModal").modal("show");
          waitForSelector(".vc-container iframe").then(() => {
            $(".vc-container iframe").css("width", iframeWidth + "px");
            $(".vc-container iframe").css("height", iframeHeight + "px");
          });
        });
      }
    });

    // customer service page mobile menu
    $(".more-less, .switch").on("click", function () {
      if ($(this).children(".more-icon").text() == "+") {
        $(this).children(".more-icon").text("-");
      } else {
        $(this).children(".more-icon").text("+");
      }
    });
    $(".switch").on("click", function () {
      $(this).next(".filter-wrapper").toggle();
      $(".sidebar-nav-wrapper").toggle();
    });
    // shipping methods selection menu
    $('[data-js="ship-methods-menu"]').on("change", (e) => {
      window.location.href = $(e.delegateTarget).val();
    });
  };

  onInteraction = (e) => {
    // called when view is first interacted with. Emit events that trigger deferred dependency loading
    document.removeEventListener("scroll", this.onInteraction, false);
    document.removeEventListener("click", this.onInteraction, false);
    document.removeEventListener("touchstart", this.onInteraction, false);
    document.removeEventListener("mousemove", this.onInteraction, false);
    window.dataLayer.push({ event: "onInteraction" });
    let interactionEvent = new CustomEvent("interaction", {
      bubbles: true,
      detail: { eventType: e.type ? e.type : null },
    });
    document.dispatchEvent(interactionEvent);
  };

  initUnsolicitedCapture = () => {
    // unsolicited email capture modal
    // 11/2/20 - TrackJS is reporting occasional "loading chunk X failed", so adding re-try logic
    if (!Cookies.get("capturewin")) {
      this.initEmailCapture(true);
    }
  };

  emailCapture = (e) => {
    // a window function for opening the email capture modal right from an inline function call
    this.initEmailCapture(false)
      .then((capture) => {
        capture.viewCapture();
      })
      .catch(() => {});
  };

  initEmailCapture = (isUnsolicited = false) => {
    return new Promise((resolve, reject) => {
      import(
        /* webpackChunkName: "capture" */
        /* webpackMode: "lazy" */
        "./EmailCapture"
      )
        .then((EmailCapture) => {
          const capture = new EmailCapture.default();
          capture.init(isUnsolicited);
          resolve(capture);
        })
        .catch(() => {
          import(/* webpackChunkName: "capture" */ "./EmailCapture")
            .then((EmailCapture) => {
              const capture = new EmailCapture.default();
              capture.init(isUnsolicited);
              resolve(capture);
            })
            .catch(() => {
              console.error("failed 2nd time to load EmailCapture", getBodyData("data-client-id"));
              reject();
            });
        });
    });
  };

  checkoutTimeout = () => {
    // called when keepalive expires.  if this is a checkout page, throw an alert (confirm) letting cust
    // know that their session is expired.
    if (this.phase === "checkout" && this.pageType !== "receipt") {
      if (confirm("Your checkout session has timed out due to inactivity. Click OK to continue.")) {
        window.location.href = "/store?action=RELOADCARTCHECKOUT";
      } else {
        window.location.href = "/";
      }
    }
  };

  // if the cart (in the dom) has a qty, send a keep-alive pulse to keep the hazel session alive.  at time of writing it is 12 hours
  keepAlive = () => {
    let r = 0;
    let i = setInterval(() => {
      r += 1;
      if (r > 144) {
        // 12 hours
        clearInterval(i);
        console.log("keep-alive ended " + r);
        this.checkoutTimeout();
      }
      fetchJson("/keepalive")
        .then(() => {
          console.log("keep-alive " + r);
        })
        .catch((e) => {
          console.error("keepalive error", e);
        });
    }, 300000); // 5 min
  };
}

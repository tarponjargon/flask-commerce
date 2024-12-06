// the order of these css imports matters
import "./css/icomoon.css";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";
import "./scss/style.scss";
import "slick-carousel";
// import "./js/polyfills.js";
import "./js/legacy/bootstrap3-custom.js"; // note this is custom-built bs3 js.  not using bs4/popper as it's too large
import { ssAfterResults } from "./js/services/AfterResults";
import WindowListeners from "./js/services/WindowListeners";
import Accessibility from "./js/services/Accessibility";
import NavMenu from "./js/services/NavMenu";
import { mobileNavMenu } from "./js/services/MobileNavMenu";
import { getPhase, getPageType, vendorSearchActive, getBodyData } from "./js/services/Utils";
import Privacy from "./js/services/Privacy";
import Alert from "./js/services/Alert";
import Recommendations from "./js/services/Recommendations";

// even though these are specified in ProvidePlugin, it's not available in the window w/o these
global.$ = require("jquery");
global.jQuery = global.$;
global.Cookies = require("js-cookie");

class App {
  constructor() {
    this.loaded = false;
    this.viewsLoaded = [];
    this.phase = getPhase();
    this.pageType = getPageType();
    this.vendorSearch = vendorSearchActive();
    this.defaultTitle = document.title;
  }

  init = (views) => {
    return new Promise((resolve) => {
      window.ssAfterResults = ssAfterResults;
      const viewPromises = views.map((v) => this.viewLoader(v));
      Promise.all(viewPromises)
        .then((loadedViews) => {
          this.viewsLoaded = loadedViews;
          this.loaded = true;
          resolve(loadedViews);
        })
        .catch((e) => console.error("could load views from app init", e));
    });
  };

  viewLoader = (view) => {
    // 11/2/20 - TrackJS is reporting occasional "loading chunk X failed", so adding re-try logic to all import statements
    // TODO figure out how to abstract import statements into a promise.  tho webpackchunkname might need to be statically generated

    return new Promise((resolve) => {
      let viewInit = null;
      switch (view) {
        case "index":
          import(
            /* webpackChunkName: "home" */
            "./js/views/HomeView"
          )
            .then((HomeView) => {
              viewInit = new HomeView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              import(/* webpackChunkName: "home" */ "./js/views/HomeView")
                .then((HomeView) => {
                  viewInit = new HomeView.default();
                  viewInit.init(view).then(() => resolve(view));
                })
                .catch((e) => {
                  console.error(
                    "failed 2nd time to load HomeView",
                    e,
                    getBodyData("data-client-id")
                  );
                });
            });
          break;

        case "detail":
          import(
            /* webpackChunkName: "detail" */
            "./js/views/DetailView"
          )
            .then((DetailView) => {
              viewInit = new DetailView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              import(/* webpackChunkName: "detail" */ "./js/views/DetailView")
                .then((DetailView) => {
                  viewInit = new DetailView.default();
                  viewInit.init(view).then(() => resolve(view));
                })
                .catch((e) => {
                  console.error(
                    "failed 2nd time to load DetailView",
                    e,
                    getBodyData("data-client-id")
                  );
                });
            });
          break;

        case "category":
          import(
            /* webpackChunkName: "category" */
            "./js/views/CategoryView"
          )
            .then((CategoryView) => {
              viewInit = new CategoryView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              import(/* webpackChunkName: "category" */ "./js/views/CategoryView")
                .then((CategoryView) => {
                  viewInit = new CategoryView.default();
                  viewInit.init(view).then(() => resolve(view));
                })
                .catch((e) => {
                  console.error(
                    "failed 2nd time to load CategoryView",
                    e,
                    getBodyData("data-client-id")
                  );
                });
            });
          break;

        case "search":
          import(
            /* webpackChunkName: "search" */
            "./js/views/SearchView"
          )
            .then((SearchView) => {
              viewInit = new SearchView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              import(/* webpackChunkName: "search" */ "./js/views/SearchView")
                .then((SearchView) => {
                  viewInit = new SearchView.default();
                  viewInit.init(view).then(() => resolve(view));
                })
                .catch((e) => {
                  console.error(
                    "failed 2nd time to load SearchView",
                    e,
                    getBodyData("data-client-id")
                  );
                });
            });
          break;

        case "view":
          import(
            /* webpackChunkName: "cart" */
            "./js/views/CartView"
          )
            .then((CartView) => {
              viewInit = new CartView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              import(/* webpackChunkName: "cart" */ "./js/views/CartView")
                .then((CartView) => {
                  viewInit = new CartView.default();
                  viewInit.init(view).then(() => resolve(view));
                })
                .catch((e) => {
                  console.error(
                    "failed 2nd time to load CartView",
                    e,
                    getBodyData("data-client-id")
                  );
                });
            });
          break;

        case "login":
          import(
            /* webpackChunkName: "login" */
            "./js/views/CheckoutLoginView"
          )
            .then((CheckoutLoginView) => {
              viewInit = new CheckoutLoginView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              import(/* webpackChunkName: "login" */ "./js/views/CheckoutLoginView")
                .then((CheckoutLoginView) => {
                  viewInit = new CheckoutLoginView.default();
                  viewInit.init(view).then(() => resolve(view));
                })
                .catch((e) => {
                  console.error(
                    "failed 2nd time to load CheckoutLoginView",
                    e,
                    getBodyData("data-client-id")
                  );
                });
            });
          break;

        case "resetpassword":
          import(
            /* webpackChunkName: "resetpassword" */
            "./js/views/ResetPasswordView"
          )
            .then((ResetPasswordView) => {
              viewInit = new ResetPasswordView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              import(/* webpackChunkName: "resetpassword" */ "./js/views/ResetPasswordView")
                .then((ResetPasswordView) => {
                  viewInit = new ResetPasswordView.default();
                  viewInit.init(view).then(() => resolve(view));
                })
                .catch((e) => {
                  console.error(
                    "failed 2nd time to load ResetPasswordView",
                    e,
                    getBodyData("data-client-id")
                  );
                });
            });
          break;

        case "billing":
          import(
            /* webpackChunkName: "billing" */
            "./js/views/BillShipView"
          )
            .then((BillShipView) => {
              viewInit = new BillShipView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              import(/* webpackChunkName: "billing" */ "./js/views/BillShipView")
                .then((BillShipView) => {
                  viewInit = new BillShipView.default();
                  viewInit.init(view).then(() => resolve(view));
                })
                .catch((e) => {
                  console.error(
                    "failed 2nd time to load BillShipView",
                    e,
                    getBodyData("data-client-id")
                  );
                });
            });
          break;

        case "payment":
          import(
            /* webpackChunkName: "payment" */
            "./js/views/PaymentView"
          )
            .then((PaymentView) => {
              viewInit = new PaymentView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              import(/* webpackChunkName: "payment" */ "./js/views/PaymentView")
                .then((PaymentView) => {
                  viewInit = new PaymentView.default();
                  viewInit.init(view).then(() => resolve(view));
                })
                .catch((e) => {
                  console.error(
                    "failed 2nd time to load PaymentView",
                    e,
                    getBodyData("data-client-id")
                  );
                });
            });
          break;

        case "confirmation":
          import(
            /* webpackChunkName: "confirmation" */
            "./js/views/ConfirmationView"
          )
            .then((ConfirmationView) => {
              viewInit = new ConfirmationView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              import(/* webpackChunkName: "confirmation" */ "./js/views/ConfirmationView")
                .then((ConfirmationView) => {
                  viewInit = new ConfirmationView.default();
                  viewInit.init(view).then(() => resolve(view));
                })
                .catch((e) => {
                  console.error(
                    "failed 2nd time to load ConfirmationView",
                    e,
                    getBodyData("data-client-id")
                  );
                });
            });
          break;

        case "receipt":
          import(
            /* webpackChunkName: "receipt" */
            "./js/views/ReceiptView"
          )
            .then((ReceiptView) => {
              viewInit = new ReceiptView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              import(/* webpackChunkName: "receipt" */ "./js/views/ReceiptView")
                .then((ReceiptView) => {
                  viewInit = new ReceiptView.default();
                  viewInit.init(view).then(() => resolve(view));
                })
                .catch((e) => {
                  console.error(
                    "failed 2nd time to load ReceiptView",
                    e,
                    getBodyData("data-client-id")
                  );
                });
            });
          break;

        case "orderstatus":
          import(
            /* webpackChunkName: "orderstatus" */
            "./js/views/OrderstatusView"
          )
            .then((OrderstatusView) => {
              viewInit = new OrderstatusView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              import(/* webpackChunkName: "orderstatus" */ "./js/views/OrderstatusView")
                .then((OrderstatusView) => {
                  viewInit = new OrderstatusView.default();
                  viewInit.init(view).then(() => resolve(view));
                })
                .catch((e) => {
                  console.error(
                    "failed 2nd time to load OrderstatusView",
                    e,
                    getBodyData("data-client-id")
                  );
                });
            });
          break;

        case "contact":
          import(
            /* webpackChunkName: "contact" */
            "./js/views/ContactView"
          )
            .then((ContactView) => {
              viewInit = new ContactView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              import(/* webpackChunkName: "contact" */ "./js/views/ContactView")
                .then((ContactView) => {
                  viewInit = new ContactView.default();
                  viewInit.init(view).then(() => resolve(view));
                })
                .catch((e) => {
                  console.error(
                    "failed 2nd time to load ContactView",
                    e,
                    getBodyData("data-client-id")
                  );
                });
            });
          break;

        case "catalog":
          import(
            /* webpackChunkName: "catalog" */
            "./js/views/CatalogView"
          )
            .then((CatalogView) => {
              viewInit = new CatalogView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              import(/* webpackChunkName: "catalog" */ "./js/views/CatalogView")
                .then((CatalogView) => {
                  viewInit = new CatalogView.default();
                  viewInit.init(view).then(() => resolve(view));
                })
                .catch((e) => {
                  console.error(
                    "failed 2nd time to load CatalogView",
                    e,
                    getBodyData("data-client-id")
                  );
                });
            });
          break;

        case "generalform":
          import(
            /* webpackChunkName: "generalform" */
            "./js/views/FormView"
          )
            .then((FormView) => {
              viewInit = new FormView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              import(/* webpackChunkName: "generalform" */ "./js/views/FormView")
                .then((FormView) => {
                  viewInit = new FormView.default();
                  viewInit.init(view).then(() => resolve(view));
                })
                .catch((e) => {
                  console.error(
                    "failed 2nd time to load FormView",
                    e,
                    getBodyData("data-client-id")
                  );
                });
            });
          break;

        case "account":
          import(
            /* webpackChunkName: "account" */
            "./js/views/AccountView"
          )
            .then((AccountView) => {
              viewInit = new AccountView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              import(/* webpackChunkName: "account" */ "./js/views/AccountView")
                .then((AccountView) => {
                  viewInit = new AccountView.default();
                  viewInit.init(view).then(() => resolve(view));
                })
                .catch((e) => {
                  console.error(
                    "failed 2nd time to load AccountView",
                    e,
                    getBodyData("data-client-id")
                  );
                });
            });
          break;

        case "multidetail":
          import(
            /* webpackChunkName: "multidetail" */
            "./js/views/MultiDetailView"
          )
            .then((MultiDetailView) => {
              viewInit = new MultiDetailView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              import(/* webpackChunkName: "multidetail" */ "./js/views/MultiDetailView")
                .then((MultiDetailView) => {
                  viewInit = new MultiDetailView.default();
                  viewInit.init(view).then(() => resolve(view));
                })
                .catch((e) => {
                  console.error(
                    "failed 2nd time to load MultiDetailView",
                    e,
                    getBodyData("data-client-id")
                  );
                });
            });
          break;

        case "orderbuilder":
          import(
            /* webpackChunkName: "orderbuilder" */
            "./js/views/OrderbuilderView"
          )
            .then((OrderbuilderView) => {
              viewInit = new OrderbuilderView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              import(/* webpackChunkName: "orderbuilder" */ "./js/views/OrderbuilderView")
                .then((OrderbuilderView) => {
                  viewInit = new OrderbuilderView.default();
                  viewInit.init(view).then(() => resolve(view));
                })
                .catch((e) => {
                  console.error(
                    "failed 2nd time to load OrderbuilderView",
                    e,
                    getBodyData("data-client-id")
                  );
                });
            });
          break;

        case "sharedwishlist":
          import(
            /* webpackChunkName: "sharedwishlist" */
            "./js/views/SharedWishlistView"
          )
            .then((SharedWishlistView) => {
              viewInit = new SharedWishlistView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              import(/* webpackChunkName: "sharedwishlist" */ "./js/views/SharedWishlistView")
                .then((SharedWishlistView) => {
                  viewInit = new SharedWishlistView.default();
                  viewInit.init(view).then(() => resolve(view));
                })
                .catch((e) => {
                  console.error(
                    "failed 2nd time to load SharedWishlistView",
                    e,
                    getBodyData("data-client-id")
                  );
                });
            });
          break;

        case "empty":
          import(
            /* webpackChunkName: "empty" */
            "./js/views/EmptyView"
          )
            .then((EmptyView) => {
              viewInit = new EmptyView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              import(/* webpackChunkName: "empty" */ "./js/views/EmptyView")
                .then((EmptyView) => {
                  viewInit = new EmptyView.default();
                  viewInit.init(view).then(() => resolve(view));
                })
                .catch((e) => {
                  console.error(
                    "failed 2nd time to load EmptyView",
                    e,
                    getBodyData("data-client-id")
                  );
                });
            });
          break;

        case "receiptlookup":
          import(
            /* webpackChunkName: "receiptlookup" */
            "./js/views/ReceiptLookupView"
          )
            .then((ReceiptLookupView) => {
              viewInit = new ReceiptLookupView.default();
              viewInit.init(view).then(() => resolve(view));
            })
            .catch(() => {
              console.error("failed to load ReceiptLookupView", e, getBodyData("data-client-id"));
            });
          break;

        default:
          resolve("none");
      }
    });
  };

  // callback function runs when current view is completely loaded into dom.
  //
  afterViewsLoad = (views) => {
    // starts Alert functionality available globally.  template should be in footer
    let flashMessage = new Alert();
    window.flashMessage = flashMessage;

    // listen for general events that can occur in each view, like (optin submits, clicks for login modal...)
    const listeners = new WindowListeners();
    listeners.init();

    const accessibility = new Accessibility();
    accessibility.init();

    if (this.phase === "shopping") {
      // nav hover menus
      const navMenu = new NavMenu();
      navMenu.init();

      // mobile nav menu
      mobileNavMenu();
    }

    const privacy = new Privacy();
    privacy.init();

    const recs = new Recommendations();
    recs.init();
  };
}

// init the base app and any js associated with the current page ("view" value found in data-view selector)
// 6/28/20 a page can have multiple views... (like in the case of components)
let views = [];
Array.prototype.forEach.call(document.querySelectorAll("[data-view]"), function (loadViewEl) {
  if (loadViewEl && loadViewEl.getAttribute("data-view")) {
    views.push(loadViewEl.getAttribute("data-view"));
  }
});

window._fcapp = new App();
window._fcapp
  .init(views)
  .then((viewsLoadedList) => {
    window._fcapp.afterViewsLoad(viewsLoadedList);
  })
  .catch((e) => console.error("could not init app", e));

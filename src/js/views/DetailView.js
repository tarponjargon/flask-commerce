import Cookies from "js-cookie";
import {
  scrollToSelector,
  isLoggedIn,
  getUrlParams,
  promiseSerial,
  isEmpty,
  getFirstFocusable,
  waitForSelector,
  spinButton,
  unSpinButton,
} from "../services/Utils";
import {
  initPriceUpdateListener,
  initAvailabilityUpdateListener,
  initMultiSelectListeners,
  initAddListeners,
  initMatrixVariants,
  directAdd,
} from "../services/DetailUtils";
import messages from "../services/Messages";
import "../legacy/cloudzoom.js";
export default class DetailView {
  constructor() {
    this.detailEl = document.querySelector("[data-detail-skuid]"); // using querySelector just gets the FIRST item on the page, which is the one we want
    this.skuid = this.detailEl.getAttribute("data-detail-skuid");
    this.loggedIn = isLoggedIn();
    this.$detailSlickInstance = undefined;
    this.$gallerySlickInstance = undefined;
    this.$zoomInstance = undefined;
  }
  init = (view) => {
    return new Promise((resolve) => {
      // there may be more than 1 orderable item on the detail page.  attach listeners to all
      const itemContainers = document.querySelectorAll(`[data-detail-skuid]`);
      // Array.prototype.forEach.call(itemContainers, (el) => {
      //   const skuid = el.getAttribute("data-detail-skuid");
      //   initAddListeners(el, skuid);
      //   initMultiSelectListeners(el, skuid);
      //   initAvailabilityUpdateListener(el, skuid);
      //   initPriceUpdateListener(el, skuid);
      //   initMatrixVariants(el, this.switchGalleryImage, this.updateProductName);
      // });
      this.initMobileAddVisibility();
      this.stickyAtcButtonClick();
      this.initTabListeners();
      this.initWishlistListener();
      this.initGalleryListeners();
      this.checkIfFullyOptioned();
      this.initGallery();
      this.setInitialImageDesc();
      this.initVideoPreview();

      // "interaction" is a custom event emitted from windowlisteners.js (globals)
      // it's a denotes that the page has been interacted with
      // used for deferred loading of nonessential assets
      document.addEventListener(
        "interaction",
        (e) => {
          import("../../css/cloudzoom.css");
        },
        false
      );

      this.productViewed();

      $('[data-js="scrolltorelated"]').on("click", function (e) {
        e.preventDefault();
        $([document.documentElement, document.body]).animate(
          {
            scrollTop: $("#related-target").offset().top,
          },
          400
        );
      });
      resolve(view);
    });
  };

  initMobileAddVisibility = () => {
    if ("IntersectionObserver" in window) {
      const addButtonEl = this.detailEl.querySelector('[data-js="add-button"]');
      const stickyAtcContainer = document.querySelector('[data-js="sticky-atc-container"]');
      if (!addButtonEl || !stickyAtcContainer) return;
      let mobileButtonObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            stickyAtcContainer.classList.remove("fadeInFast");
            stickyAtcContainer.classList.add("fadeOut");
          } else {
            stickyAtcContainer.classList.remove("fadeOut");
            stickyAtcContainer.classList.add("fadeInFast");
          }
        });
      });
      mobileButtonObserver.observe(addButtonEl);
    }
  };

  stickyAtcButtonClick = () => {
    // listen for clicks on the sticky add-to-cart button
    // when clicked, scroll the "regular" add-to-cart button into view
    const atcButton = document.getElementById("sticky-atc-button");
    const detailForm = this.detailEl.querySelector('[data-js="order-form"]');
    const hasOptions = this.detailEl.querySelector('[data-js="options-matrix"]');
    if (!atcButton || !detailForm) return;
    atcButton.addEventListener("click", () => {
      if (hasOptions) {
        detailForm.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
        this.selectOptionsReminder();
      } else {
        spinButton("sticky-atc-button", "ADDING");
        directAdd(this.skuid).finally(() => {
          unSpinButton("sticky-atc-button", "ADDED");
          setTimeout(() => {
            atcButton.style.display = "none";
          }, 300);
        });
      }
    });
  };

  // shows a warning if the user tries to add to cart without selecting options
  selectOptionsReminder = () => {
    const croWarningSelector = ".select-options-reminder";

    const warning = document.createElement("div");
    warning.classList.add("select-options-reminder", "hide");

    warning.innerHTML = /* html */ `
      <div class="body">
        <div class="close">
          <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 11 11" fill="none">
            <path d="M10.3379 9.09879C10.4733 9.23421 10.5493 9.41786 10.5493 9.60936C10.5493 9.80087 10.4733 9.98452 10.3379 10.1199C10.2024 10.2553 10.0188 10.3314 9.82729 10.3314C9.63579 10.3314 9.45213 10.2553 9.31672 10.1199L5.50306 6.30507L1.68819 10.1187C1.55278 10.2541 1.36912 10.3302 1.17762 10.3302C0.986121 10.3302 0.802464 10.2541 0.667052 10.1187C0.53164 9.98332 0.455566 9.79966 0.455566 9.60816C0.455566 9.41666 0.53164 9.233 0.667052 9.09759L4.48191 5.28393L0.668253 1.46907C0.532841 1.33365 0.456768 1.15 0.456768 0.958496C0.456768 0.766995 0.532841 0.583338 0.668253 0.447926C0.803665 0.312514 0.987322 0.23644 1.17882 0.23644C1.37032 0.23644 1.55398 0.312514 1.68939 0.447926L5.50306 4.26279L9.31792 0.447325C9.45333 0.311913 9.63699 0.23584 9.82849 0.23584C10.02 0.23584 10.2036 0.311913 10.3391 0.447325C10.4745 0.582737 10.5505 0.766394 10.5505 0.957896C10.5505 1.1494 10.4745 1.33305 10.3391 1.46847L6.5242 5.28393L10.3379 9.09879Z" fill="#818181"/>
          </svg>
        </div>
        <div class="warn">select style to continue</div>
      </div>
     `;

    // warning close
    warning.querySelector(".close")?.addEventListener("click", () => {
      warning.classList.toggle("hide", true);
    });

    window.addEventListener("click", (evt) => {
      const target = evt.target;
      if (!target.closest(".options-matrix")) return;

      warning.classList.toggle("hide", true);
    });

    // if btn is disabled show warning on click
    const atcBtn = document.querySelector(".sticky-atc");

    if (!document.querySelector(croWarningSelector))
      document.querySelector("#add-to-cart-btn")?.insertAdjacentElement("beforebegin", warning);

    atcBtn?.addEventListener("click", (e) => {
      if (
        document.querySelector("#add-to-cart-btn")?.hasAttribute("disabled") &&
        !document.querySelector(".options-matrix button.selected")
      ) {
        warning.classList.toggle("hide", false);
        document
          .querySelector(".options-matrix .text-large")
          ?.scrollIntoView({ behavior: "smooth", block: "start" });
      } else {
        const orgAddBtn = document.querySelector("#add-to-cart-btn");
        e.preventDefault();
        orgAddBtn?.click();
        warning.focus();
      }
    });
  };

  productViewed = () => {
    const cart =
      window.cartItemsArray && window.cartItemsArray.length
        ? window.cartItemsArray.map((i) => i.id)
        : [];

    if (!cart.includes(this.skuid)) {
      let viewed = [];
      let viewedCookie = Cookies.get("viewed_products");

      if (viewedCookie) {
        viewedCookie = viewedCookie.replace(/[^A-Za-z0-9;]/g, "");
        viewed = viewedCookie.split(";");
      }
      if (!viewed.includes(this.skuid)) {
        viewed.unshift(this.skuid);
        viewed = viewed.slice(0, 25);
        const viewedStr = viewed.join(";");
        Cookies.set("viewed_products", viewedStr, {
          expires: 400,
          path: "/",
          secure: true,
        });
      }
    }
  };

  initVideoPreview = () => {
    // videos load in an iframe, which is synchronous and therefore blocking the d/l and execution of the page js
    // in the html I put the the url in data-src and am leaving src blank.  when this func runs it will add data-src to src therefore deferring load of the video
    const videoIframe = $('[data-js="video-player"]');
    if (videoIframe && $(videoIframe).data("src")) {
      if (/^http/.test($(videoIframe).data("src"))) {
        $(videoIframe).attr("src", $(videoIframe).data("src"));
      }
    }
  };

  waitForEnabled = (jqEl) => {
    // promise waits for disabled element to not be disabled.  NOTE: receives a jquery element as an argument
    return new Promise((resolve, reject) => {
      let r = 0;
      let i = setInterval(() => {
        r += 1;
        if (r > 80) {
          clearInterval(i);
          reject("element never enabled");
        }
        if (!$(jqEl).attr("disabled")) {
          clearInterval(i);
          resolve();
        }
      }, 100);
    });
  };

  optionSelectProm = (val, index) => {
    // called from checkIfFullyOptioned. programmatically selects val from menu[index], then checks
    // if there are subsequent menus.  if so, it waits for them to become enabled (i.e. inventory check done)
    return new Promise((resolve, reject) => {
      const menu = $(`form[data-add-item="${this.skuid}"] select`).eq(index);
      if (val) val = val.toUpperCase();
      if (!val || !$(menu).find(`option[value=${val}]`).length) {
        reject("requested option does not exist");
        return false;
      }
      $(menu).val(val);
      var event = new Event("change"); // tried using jq's 'change' and also 'trigger' and it didn't work
      $(menu)[0].dispatchEvent(event);
      const nextMenu = $(`form[data-add-item="${this.skuid}"] select`).eq(index + 1);
      if ($(nextMenu).length) {
        this.waitForEnabled($(nextMenu))
          .then(() => resolve())
          .catch((e) => reject(e));
      } else {
        resolve();
      }
    });
  };

  matrixSelectProm = (val, index) => {
    //console.log("called with", val, index);

    // called from checkIfFullyOptioned. programmatically selects val from menu[index]
    return new Promise((resolve, reject) => {
      const menu = $(`form[data-add-item="${this.skuid}"] [data-matrix-index="${index}"]`);
      if (val) val = val.toUpperCase();
      const $el = $(menu).find(`[data-option-code="${val}"]`);
      if (!val || !$el.length || $el.attr('[data-option-nla="1"]') || $el.hasClass("disabled")) {
        reject("requested option is not available");
        return false;
      }
      setTimeout(() => {
        const evt = new Event("click");
        $el[0].dispatchEvent(evt);
        resolve($el[0]);
      }, 100);
    });
  };

  checkIfFullyOptioned = async () => {
    // if the options selections are set on the url, pre-select the options menus and update price
    if (/op1=/i.test(window.location.search)) {
      let params = getUrlParams();
      const selectProms = [];
      const $selectMenus = $(`form[data-add-item="${this.skuid}"] select`);
      const $matrixMenus = $(`form[data-add-item="${this.skuid}"] [data-matrix-index]`);
      const menusLen = $matrixMenus.length ? $matrixMenus.length : $selectMenus.length;
      for (let i = 0; i < menusLen; i++) {
        const opkey = `op${i + 1}`;
        if (opkey in params && params[opkey]) {
          let prom = null;
          if ($selectMenus.length) prom = this.optionSelectProm(params[opkey], i);
          if ($matrixMenus.length) prom = this.matrixSelectProm(params[opkey], i);
          if (prom) selectProms.push(prom);
        }
      }
      if (selectProms.length) {
        const optionDescs = [];
        for (const [index, prom] of selectProms.entries()) {
          try {
            const el = await prom;
            if (el instanceof HTMLButtonElement) {
              optionDescs.push(el.textContent.trim());
              this.updateImage(el.getAttribute("data-image"));
            }
          } catch (error) {
            console.error(`Options preselect ${index} failed with`, error);
          }
        }
      }
    }
  };

  // bootstrap's .tab function was causing me major problems (esp on mobile) so I manually wired it up (and disabled the data-api)
  switchTab = (tabSel) => {
    if (!tabSel || !$(tabSel)) return false;
    let tabContentSel = $(tabSel).attr("href");
    if (!tabContentSel || !$(tabContentSel)) return false;

    // collapse any visible tab
    $("#product-tabs .nav-link").removeClass("active").parent().attr("aria-selected", "false");
    $("#product-tabs .card.tab-pane").removeClass("active show");
    $("#product-tabs .card-header").removeClass("active");
    $('#product-tabs a[data-parent="#myTabContent"]')
      .removeClass("collapse")
      .addClass("collapsed")
      .attr("aria-expanded", "false");
    $('#product-tabs [data-js="tab-body"]').removeClass("show");

    // show selected
    $(tabSel).addClass("active").parent().attr("aria-selected", "true");
    $(tabContentSel + ".card.tab-pane").addClass("active show");
    $(tabContentSel + " .card-header").addClass("active");
    $(tabContentSel + ' a[data-parent="#myTabContent"]')
      .removeClass("collapsed")
      .addClass("collapse")
      .attr("aria-expanded", "true");
    $(tabContentSel + ' [data-js="tab-body"]').addClass("show");
  };

  initTabListeners = () => {
    // listen for links in text that activate tabs
    $("#additional-information-tab, a[href='#collapse-additional-information'], #more-link").on(
      "click",
      (e) => {
        e.preventDefault();
        this.switchTab("#additional-information-tab");
        scrollToSelector("#product-tabs");
      }
    );
    $("#customer-review-tab, a[href='#collapse-customer-review'], [data-js='review-link']").on(
      "click",
      (e) => {
        e.preventDefault();
        this.switchTab("#customer-review-tab");
        scrollToSelector("#product-tabs");
        waitForSelector("#collapse-customer-review .yotpo-display-wrapper").then((el) => {
          // unfortunately I cannot get this to work w/o the timer as well.
          setTimeout(() => {
            const focusOn = getFirstFocusable(el);
            focusOn.focus();
          }, 500);
        });
      }
    );
    $("#media-reviews-tab, a[href='#collapse-media-reviews']").on("click", (e) => {
      e.preventDefault();
      this.switchTab("#media-reviews-tab");
      scrollToSelector("#product-tabs");
    });
    $("#preview-tab, a[href='#collapse-preview'], #video-scroll-thumbnail").on("click", (e) => {
      e.preventDefault();
      this.switchTab("#preview-tab");
      scrollToSelector("#product-tabs");
    });
  };

  initWishlistListener = () => {
    $("#wishlist-link").on("click", () => {
      if (!this.loggedIn) {
        flashMessage.show({
          message: messages.loginfirst,
        });
        $("#account-modal").modal("show");
      } else {
        this.addToWishlist();
      }
    });
  };

  addToWishlist = (skuid = this.skuid) => {
    $.ajax({
      type: "GET",
      url: `/wishlistupdate?wl_skuid=${skuid}`,
      dataType: "json",
      success: (data) => {
        if (data && data.success) {
          const successMsg = `Item added to your wishlist. <a href="/account#/wishlist">View wishlist</a>.`;
          flashMessage.show({
            message: successMsg,
            alertType: "success",
            timeout: false,
          });
        } else {
          if ("errors" in data) {
            flashMessage.show({
              message: data.errors.join(", "),
              alertType: "danger",
            });
          }
        }
      },
      error: (xhr, status, errorThrown) => {
        flashMessage.show({ message: messages.fatal });
        console.error("add to wishlist", xhr, status, errorThrown);
      },
    });
  };

  initGalleryListeners = () => {
    const $optionsSelects = $(`form[data-add-item="${this.skuid}"] select`);
    if ($optionsSelects.length) {
      $(`form[data-add-item="${this.skuid}"] select`).each((i, select) => {
        $(select).on("change", () => {
          this.switchGalleryImage();
        });
      });
    }
  };

  switchGalleryImage = (ops) => {
    let fullSkuid = this.skuid;
    let imageFilename = undefined;

    if (!ops)
      ops = $.map($(`form[data-add-item="${this.skuid}"] select option:selected`), (i) =>
        $(i).val()
      );

    // loop select menus and progressively concat each chosen option to base skuid, at each step, check if that string is a key in window.imageMap
    // keep stepping until all select values have been tried.  if any matches found, update gallery
    ops.forEach((thisVal) => {
      if (thisVal) {
        fullSkuid += thisVal;
        if (window.imageMap && Array.isArray(window.imageMap) && !isEmpty(window.imageMap)) {
          const imageObj = window.imageMap.find((i) => i.fullskuid === fullSkuid);
          if (imageObj && imageObj.image) {
            imageFilename = imageObj.image;
          }
        }
      }
    });
    if (imageFilename) {
      this.updateImage(imageFilename);
    }
  };

  appendVariantDescsToName = (descsString) => {
    const variantEl = this.detailEl.querySelectorAll("[data-selected-variants]");
    if (variantEl && variantEl.length) {
      variantEl.forEach((el) => {
        if (descsString) {
          el.textContent = " - " + descsString;
        } else {
          el.textContent = "";
        }
      });
    }
  };

  updateProductName = (ops) => {
    if (!ops || !Array.isArray(ops) || !ops.length) return;
    const optionDescs = [];
    if (ops.every((element) => !element)) {
      this.appendVariantDescsToName("");
    }
    ops.forEach((value, index) => {
      if (!value) return;
      const opEl = this.detailEl.querySelector(
        `[data-option-index="${index}"][data-option-code="${value}"]`
      );
      if (!opEl || !opEl.getAttribute("data-option-name")) return;
      optionDescs.push(opEl.getAttribute("data-option-name"));
    });
    if (!optionDescs.length) return;
    const descsString = optionDescs.join(" - ");
    this.appendVariantDescsToName(descsString);
  };

  updateShownDescription = (imageType = null, imageDesc = null) => {
    if (!imageDesc) {
      $('[data-js="image-shown"]').css("visibility", "hidden");
    } else {
      $('[data-js="image-type"]').text(imageType);
      $('[data-js="image-desc"]').text(imageDesc);
      $('[data-js="image-shown"]').css("visibility", "visible");
    }
  };

  setImageDescByFilename = (filename) => {
    if (window.imageMap && Array.isArray(window.imageMap) && !isEmpty(window.imageMap)) {
      const imageObj = window.imageMap.find((i) => i.image === filename);
      if (imageObj && !isEmpty(imageObj.variantData)) {
        this.updateShownDescription(imageObj.variantData.type, imageObj.variantData.description);
      } else {
        this.updateShownDescription(null);
      }
    }
  };

  setInitialImageDesc = () => {
    const filename = $('[data-js="detail-image"] img').first().data("image");
    this.setImageDescByFilename(filename);
  };

  startZoom = ($el) => {
    if (!$el || !$el.length || !$el.data("zoom") || $(window).width() < 1024) return;
    if (this.$zoomInstance && this.$zoomInstance.destroy) this.$zoomInstance.destroy();
    const zoomOptions = {
      zoomImage: $el.data("zoom"),
      zoomPosition: "inside",
      autoInside: true,
      variableMagnification: false,
      startMagnification: 2,
      hoverIntentDelay: 40,
      captionSource: "none",
    };
    this.$zoomInstance = new CloudZoom($el, zoomOptions);
    return this.$zoomInstance;
  };

  initGallery = () => {
    // start the zoom function on the default image
    this.startZoom($('[data-js="detail-image"] img').first());

    // if there is no alternate images, no need to instantiate slick carousel
    if (!$('[data-js="gallery-images"]').length) return;

    // instantiate slick for the main detail image
    const slickDetailConfig = {
      slidesToShow: 1,
      slidesToScroll: 1,
      arrows: false,
      fade: false,
      dots: $('[data-js="gallery-images"] img').length <= 20,
      infinite: true,
      asNavFor: '[data-js="gallery-images"]',
      speed: 200,
    };
    this.$detailSlickInstance = $('[data-js="detail-image"]').slick(slickDetailConfig);

    // instantiate slick for the gallery images
    const slickGalleryConfig = {
      slidesToShow: 5,
      slidesToScroll: 1,
      dots: false,
      arrows: true,
      focusOnSelect: true,
      infinite: true,
      asNavFor: '[data-js="detail-image"]',
      speed: 200,
      responsive: [
        {
          breakpoint: 640,
          settings: {
            slidesToShow: 4,
            slidesToScroll: 1,
          },
        },
        {
          breakpoint: 420,
          settings: {
            slidesToShow: 3,
            slidesToScroll: 1,
          },
        },
      ],
    };
    this.$gallerySlickInstance = $('[data-js="gallery-images"]')
      .on("init", (event, slick) => {
        $('[data-js="gallery-images"] .slick-slide').first().addClass("is-active");
        $('[data-js="gallery-images"] .slick-prev')
          .addClass("disabled")
          .attr("aria-disabled", "true");
      })
      .slick(slickGalleryConfig);

    this.$detailSlickInstance.on("beforeChange", (event, slick, currentSlide, nextSlide) => {
      $('[data-js="gallery-images"] .is-active').removeClass("is-active");
      $(`[data-js="gallery-images"] [data-slick-index="${nextSlide}"]`).addClass("is-active");
    });

    this.$detailSlickInstance.on("afterChange", (event, slick, currentSlide) => {
      //prev/next buttons are showing disabled at the wrong times.  handling it manually...
      if (currentSlide + 1 === $('[data-js="gallery-images"] [data-slick-index]').length) {
        $('[data-js="gallery-images"] .slick-next')
          .addClass("disabled")
          .attr("aria-disabled", "true");
      } else {
        $('[data-js="gallery-images"] .slick-next')
          .removeClass("disabled")
          .attr("aria-disabled", "false");
      }

      if (currentSlide === 0) {
        $('[data-js="gallery-images"] .slick-prev')
          .addClass("disabled")
          .attr("aria-disabled", "true");
      } else {
        $('[data-js="gallery-images"] .slick-prev')
          .removeClass("disabled")
          .attr("aria-disabled", "false");
      }

      this.setImageDescByFilename(
        $(`[data-js="detail-image"] [data-slick-index="${currentSlide}"] img`).data("image")
      );
      this.startZoom($(`[data-js="detail-image"] [data-slick-index="${currentSlide}"] img`));
    });
  };

  getSlideByFilename = (filename) => {
    // returns a jquery object
    const $myImage = $(`[data-js="detail-image"] img[data-image="${filename}"]`);
    if (!$myImage) return undefined;
    const $mySlide = $myImage.closest("[data-slick-index]");
    if (!$mySlide) return undefined;
    return $mySlide.data("slick-index");
  };

  updateImage = (imageFilename) => {
    if (!this.$detailSlickInstance || !this.$detailSlickInstance.length) return;
    const slideIndex = this.getSlideByFilename(imageFilename);
    if (typeof slideIndex === "undefined") return;
    this.$detailSlickInstance.slick("slickGoTo", slideIndex);
  };
} // end DetailView class

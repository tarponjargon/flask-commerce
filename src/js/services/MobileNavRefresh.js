/*****************************************************
 * This runs on all targeted pages in all variations *
 * This is the compiled version of the code above.   *
 *****************************************************/
export const mobileNavRefresh = () => {
  function _slicedToArray(arr, i) {
    return (
      _arrayWithHoles(arr) ||
      _iterableToArrayLimit(arr, i) ||
      _unsupportedIterableToArray(arr, i) ||
      _nonIterableRest()
    );
  }
  function _nonIterableRest() {
    throw new TypeError(
      "Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."
    );
  }
  function _iterableToArrayLimit(r, l) {
    var t =
      null == r ? null : ("undefined" != typeof Symbol && r[Symbol.iterator]) || r["@@iterator"];
    if (null != t) {
      var e,
        n,
        i,
        u,
        a = [],
        f = !0,
        o = !1;
      try {
        if (((i = (t = t.call(r)).next), 0 === l)) {
          if (Object(t) !== t) return;
          f = !1;
        } else for (; !(f = (e = i.call(t)).done) && (a.push(e.value), a.length !== l); f = !0);
      } catch (r) {
        (o = !0), (n = r);
      } finally {
        try {
          if (!f && null != t.return && ((u = t.return()), Object(u) !== u)) return;
        } finally {
          if (o) throw n;
        }
      }
      return a;
    }
  }
  function _arrayWithHoles(arr) {
    if (Array.isArray(arr)) return arr;
  }
  function _createForOfIteratorHelper(o, allowArrayLike) {
    var it = (typeof Symbol !== "undefined" && o[Symbol.iterator]) || o["@@iterator"];
    if (!it) {
      if (
        Array.isArray(o) ||
        (it = _unsupportedIterableToArray(o)) ||
        (allowArrayLike && o && typeof o.length === "number")
      ) {
        if (it) o = it;
        var i = 0;
        var F = function F() {};
        return {
          s: F,
          n: function n() {
            if (i >= o.length) return { done: true };
            return { done: false, value: o[i++] };
          },
          e: function e(_e) {
            throw _e;
          },
          f: F,
        };
      }
      throw new TypeError(
        "Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."
      );
    }
    var normalCompletion = true,
      didErr = false,
      err;
    return {
      s: function s() {
        it = it.call(o);
      },
      n: function n() {
        var step = it.next();
        normalCompletion = step.done;
        return step;
      },
      e: function e(_e2) {
        didErr = true;
        err = _e2;
      },
      f: function f() {
        try {
          if (!normalCompletion && it.return != null) it.return();
        } finally {
          if (didErr) throw err;
        }
      },
    };
  }
  function _unsupportedIterableToArray(o, minLen) {
    if (!o) return;
    if (typeof o === "string") return _arrayLikeToArray(o, minLen);
    var n = Object.prototype.toString.call(o).slice(8, -1);
    if (n === "Object" && o.constructor) n = o.constructor.name;
    if (n === "Map" || n === "Set") return Array.from(o);
    if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n))
      return _arrayLikeToArray(o, minLen);
  }
  function _arrayLikeToArray(arr, len) {
    if (len == null || len > arr.length) len = arr.length;
    for (var i = 0, arr2 = new Array(len); i < len; i++) arr2[i] = arr[i];
    return arr2;
  }

  // @oli:meta:usac124
  var id = 100342383;
  var tag = "usac124";
  var revision = 158;

  // ../../_includes/cromedics/css.ts
  function initCSS(variation) {
    var el =
      arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : document.documentElement;
    console.log("Adding ".concat(variation, " CSS classes ", tag));
    el.classList.add(tag, tag + variation);
    return function () {
      console.log("Removing ".concat(variation, " CSS classes"));
      el.classList.remove(tag, tag + variation);
    };
  }

  // src/utils/parseSVG.ts
  var parseSVG = function parseSVG(svgString) {
    var parser = new DOMParser();
    var doc = parser.parseFromString(svgString, "image/svg+xml");
    return doc.documentElement;
  };
  var parseSVG_default = parseSVG;

  // src/utils/replaceIcon.ts
  var replaceIcon = function replaceIcon(element, svgString) {
    var iconImg = element === null || element === void 0 ? void 0 : element.querySelector("img");
    var iconBtn = element === null || element === void 0 ? void 0 : element.querySelector("button");
    if (iconBtn) {
      iconBtn.replaceChild(parseSVG_default(svgString), iconImg);
    } else {
      element === null ||
        element === void 0 ||
        element.replaceChild(parseSVG_default(svgString), iconImg);
    }
  };
  var replaceIcon_default = replaceIcon;

  // src/utils/capitalize.ts
  var capitalizeWords = function capitalizeWords(text) {
    return text.toLowerCase().replace(/\b\w/g, function (letter) {
      return letter.toUpperCase();
    });
  };
  var capitalizeAnchorsText = function capitalizeAnchorsText(anchors) {
    var _iterator = _createForOfIteratorHelper(anchors),
      _step;
    try {
      for (_iterator.s(); !(_step = _iterator.n()).done; ) {
        var anchor = _step.value;
        anchor.textContent = capitalizeWords(anchor.textContent);
      }
    } catch (err) {
      _iterator.e(err);
    } finally {
      _iterator.f();
    }
  };

  // src/utils/elementDisplay.ts
  var displayELement = function displayELement(el) {
    el === null || el === void 0 || el.style.setProperty("display", "block", "important");
  };
  var hideELement = function hideELement(el) {
    el === null || el === void 0 || el.style.setProperty("display", "none", "important");
  };

  // src/utils/removeEl.ts
  var removeEl = function removeEl(el) {
    var _el$parentElement;
    el === null ||
      el === void 0 ||
      (_el$parentElement = el.parentElement) === null ||
      _el$parentElement === void 0 ||
      _el$parentElement.removeChild(el);
  };
  var removeEl_default = removeEl;

  // src/svg/signal.svg
  var signal_default =
    '<svg width="85" height="30" viewBox="0 0 85 30" fill="none" xmlns="http://www.w3.org/2000/svg">\n<path d="M64.4191 9.39571C63.162 8.41982 61.5818 7.84232 59.8694 7.84232C55.77 7.84232 52.4473 11.165 52.4473 15.2645C52.4473 19.3622 55.77 22.685 59.8694 22.685C61.7869 22.685 63.5403 21.9535 64.8569 20.7591C65.2938 21.8254 64.4191 8.77302 64.4191 9.39571ZM64.4191 17.9268C63.5495 19.23 62.0572 20.108 60.3733 20.108C57.6984 20.108 55.5281 17.9394 55.5281 15.2645C55.5281 12.5879 57.6984 10.4193 60.3733 10.4193C62.0455 10.4193 63.5487 11.2663 64.4191 12.5552" fill="#226B49"/>\n<path d="M40.5203 9.78321C41.3623 8.78053 42.7332 7.87076 44.9662 7.87076C48.5861 7.87076 49.6206 10.806 49.6206 12.8749V18.5437C49.6206 20.0058 51.0049 20.1264 51.7364 19.6719V22.2179C51.4401 22.3836 50.9488 22.6582 49.7696 22.6582C47.606 22.6582 46.6217 20.8554 46.6217 19.276V13.3905C46.6217 11.5007 45.5873 10.662 43.8297 10.662C42.7232 10.662 41.3313 11.1232 40.5203 12.9888V22.4849H37.5215V8.15784H40.5203" fill="#226B49"/>\n<path d="M13.7607 8.15787V19.2995C13.7607 21.0077 14.8404 22.6582 16.9613 22.6582C17.7748 22.6582 18.4686 22.4816 18.8746 22.218V19.6719C17.8945 20.1984 16.7596 19.8402 16.7596 18.5437V8.15787" fill="#226B49"/>\n<path d="M70.9814 0.101257V19.2994C70.9814 21.0077 72.0611 22.6573 74.182 22.6573C74.9947 22.6573 75.6893 22.4816 76.0953 22.2179V19.6719C75.1152 20.1983 73.9803 19.8401 73.9803 18.5437V0.101257" fill="#226B49"/>\n<path d="M64.4189 8.15787V19.2995C64.4189 21.0077 65.4986 22.6582 67.6195 22.6582C68.4322 22.6582 69.1268 22.4816 69.5328 22.218V19.6719C68.5519 20.1984 67.4169 19.8402 67.4169 18.5437V8.15787" fill="#226B49"/>\n<mask id="mask0_2358_111" style="mask-type:luminance" maskUnits="userSpaceOnUse" x="19" y="7" width="16" height="23">\n<path d="M19.7109 7.71426H34.9235V30H19.7109V7.71426Z" fill="white"/>\n</mask>\n<g mask="url(#mask0_2358_111)">\n<path d="M31.8908 21.1065C30.632 22.0874 29.0594 22.6858 27.3403 22.6858C23.2417 22.6858 19.9189 19.3623 19.9189 15.2637C19.9189 11.1651 23.2417 7.84235 27.3403 7.84235C29.0602 7.84235 30.632 8.43994 31.8908 9.42169V8.15788H34.8888V23.6919C34.8888 26.3802 33.0274 30 28.9949 30L28.0642 27.2079C30.1324 27.2079 31.8908 26.0705 31.8908 23.6919V21.1065ZM31.8908 12.6791C31.0195 11.3902 29.5172 10.4202 27.845 10.4202C25.1692 10.4202 22.9998 12.5879 22.9998 15.2637C22.9998 17.9403 25.1692 20.108 27.845 20.108C29.5289 20.108 31.0221 19.153 31.8908 17.8499" fill="#226B49"/>\n</g>\n<path d="M17.5501 2.20623C17.5501 0.987613 16.5625 0 15.3439 0C14.1261 0 13.1377 0.987613 13.1377 2.20623C13.1377 3.42484 14.1261 4.41245 15.3439 4.41245C16.5625 4.41245 17.5501 3.42484 17.5501 2.20623Z" fill="#226B49"/>\n<path d="M80.538 16.0294C81.637 16.997 82.2513 17.4632 82.2513 18.4457C82.2513 19.2208 81.5357 20.113 80.4769 20.113C79.7764 20.113 78.9905 19.6769 78.7486 19.4593L77.5752 21.7199C78.5193 22.3786 79.6642 22.6849 80.6954 22.6849C83.0146 22.6849 85.0007 21.0311 85.0007 18.3939C85.0007 16.3776 83.6038 15.3473 82.7618 14.5338C81.7081 13.5169 80.9389 13.0942 80.9389 12.1116C80.9389 11.3358 81.6227 10.5607 82.6832 10.5607C83.382 10.5607 83.8189 10.8143 84.0608 11.0328V8.34448C83.8424 8.22396 82.9945 7.98877 82.4647 7.98877C80.1455 7.98877 78.1594 9.6426 78.1594 12.2799C78.1594 14.2969 79.6266 15.2276 80.538 16.0294Z" fill="#226B49"/>\n<path d="M9.62406 0.887161C9.04321 0.743204 7.91834 0.589203 7.38101 0.589203C4.07502 0.589203 0.907962 2.96701 0.907962 6.0512C0.907962 11.0604 8.02045 13.5211 8.02045 16.8974C8.02045 18.927 5.91382 19.9891 4.26919 19.9891C3.22383 19.9891 1.85038 19.6242 1.06782 19.0249L-0.000976562 21.6789C1.05778 22.2631 2.64465 22.6766 4.19973 22.6766C8.00622 22.6766 11.2335 20.3381 11.2335 16.8647C11.2335 12.1937 3.98797 9.543 3.98797 6.09305C3.98797 4.55305 5.54639 3.1888 7.36762 3.1888C8.31087 3.1888 9.00639 3.35536 9.65503 3.67926" fill="#226B49"/>\n</svg>\n';

  // src/svg/bag.svg
  var bag_default =
    '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none">\n<path d="M16 3C13.2539 3 11 5.25391 11 8V9H6.0625L6 9.9375L5 27.9375L4.9375 29H27.0625L27 27.9375L26 9.9375L25.9375 9H21V8C21 5.25391 18.7461 3 16 3ZM16 5C17.6562 5 19 6.34375 19 8V9H13V8C13 6.34375 14.3438 5 16 5ZM7.9375 11H11V14H13V11H19V14H21V11H24.0625L24.9375 27H7.0625L7.9375 11Z" fill="#226C49"/>\n</svg>\n';

  // src/svg/arrow.svg
  var arrow_default =
    '<svg xmlns="http://www.w3.org/2000/svg" width="6" height="11" viewBox="0 0 6 11" fill="none">\n<path d="M1 9.5L5 5.5L1 1.5" stroke="#236A49" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>\n</svg>\n';

  // src/svg/back.svg
  var back_default =
    '<svg xmlns="http://www.w3.org/2000/svg" width="6" height="11" viewBox="0 0 6 11" fill="none">\n<path d="M5 9.5L1 5.5L5 1.5" stroke="#236A49" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>\n</svg>\n';

  // src/svg/close.svg
  var close_default =
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">\n<path d="M4.39535 3.03L3.03035 4.395L10.6354 12L2.98535 19.665L4.33535 21.015L12.0004 13.365L19.6504 21.015L21.0154 19.65L13.3654 12L20.9704 4.395L19.6054 3.03L12.0004 10.635L4.39535 3.03Z" fill="black"/>\n</svg>\n';

  // src/svg/search.svg
  var search_default =
    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">\n<path d="M6.93294 1.60001C3.99374 1.60001 1.59961 3.99414 1.59961 6.93334C1.59961 9.87254 3.99374 12.2667 6.93294 12.2667C8.21108 12.2667 9.38488 11.8128 10.3048 11.0594L13.4892 14.2438C13.5383 14.2949 13.5972 14.3358 13.6623 14.364C13.7275 14.3921 13.7976 14.407 13.8685 14.4077C13.9395 14.4084 14.0099 14.395 14.0756 14.3682C14.1413 14.3413 14.2009 14.3017 14.2511 14.2515C14.3013 14.2013 14.3409 14.1417 14.3678 14.076C14.3946 14.0103 14.408 13.9399 14.4073 13.8689C14.4066 13.798 14.3917 13.7279 14.3636 13.6627C14.3354 13.5976 14.2945 13.5387 14.2434 13.4896L11.059 10.3052C11.8124 9.38528 12.2663 8.21148 12.2663 6.93334C12.2663 3.99414 9.87214 1.60001 6.93294 1.60001ZM6.93294 2.66667C9.29567 2.66667 11.1996 4.57061 11.1996 6.93334C11.1996 9.29607 9.29567 11.2 6.93294 11.2C4.57021 11.2 2.66628 9.29607 2.66628 6.93334C2.66628 4.57061 4.57021 2.66667 6.93294 2.66667Z" fill="#226C49"/>\n</svg>\n';

  // src/svg/user.svg
  var user_default =
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">\n<path d="M12 3.75C9.1084 3.75 6.75 6.1084 6.75 9C6.75 10.8076 7.67285 12.4131 9.07031 13.3594C6.39551 14.5078 4.5 17.1621 4.5 20.25H6C6 16.9277 8.67773 14.25 12 14.25C15.3223 14.25 18 16.9277 18 20.25H19.5C19.5 17.1621 17.6045 14.5078 14.9297 13.3594C16.3271 12.4131 17.25 10.8076 17.25 9C17.25 6.1084 14.8916 3.75 12 3.75ZM12 5.25C14.0801 5.25 15.75 6.91992 15.75 9C15.75 11.0801 14.0801 12.75 12 12.75C9.91992 12.75 8.25 11.0801 8.25 9C8.25 6.91992 9.91992 5.25 12 5.25Z" fill="#226B49"/>\n</svg>\n';

  // src/svg/phone.svg
  var phone_default =
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none">\n<path d="M6.49187 2.25C6.0993 2.25 5.71258 2.39063 5.39031 2.64844L5.34344 2.67188L5.32 2.69531L2.97625 5.10938L2.99969 5.13281C2.27605 5.80078 2.0534 6.7998 2.36687 7.66406C2.3698 7.66992 2.36394 7.68164 2.36687 7.6875C3.00262 9.50684 4.62859 13.0195 7.80437 16.1953C10.9919 19.3828 14.5514 20.9443 16.3122 21.6328H16.3356C17.2468 21.9375 18.2341 21.7207 18.9372 21.1172L21.3044 18.75C21.9255 18.1289 21.9255 17.0508 21.3044 16.4297L18.2575 13.3828L18.2341 13.3359C17.613 12.7148 16.5114 12.7148 15.8903 13.3359L14.3903 14.8359C13.8483 14.5752 12.5563 13.9072 11.32 12.7266C10.0925 11.5547 9.46551 10.207 9.23406 9.67969L10.7341 8.17969C11.3639 7.54981 11.3757 6.50098 10.7106 5.88281L10.7341 5.85938L10.6637 5.78906L7.66375 2.69531L7.64031 2.67188L7.59344 2.64844C7.27117 2.39063 6.88445 2.25 6.49187 2.25ZM6.49187 3.75C6.54754 3.75 6.6032 3.77637 6.65594 3.82031L9.65594 6.89063L9.72625 6.96094C9.72039 6.95508 9.77019 7.03418 9.67937 7.125L7.80437 9L7.45281 9.32813L7.61687 9.79688C7.61687 9.79688 8.4782 12.1025 10.2887 13.8281L10.4528 13.9688C12.196 15.5596 14.2497 16.4297 14.2497 16.4297L14.7184 16.6406L16.945 14.4141C17.0739 14.2852 17.0505 14.2852 17.1794 14.4141L20.2497 17.4844C20.3786 17.6133 20.3786 17.5664 20.2497 17.6953L17.9528 19.9922C17.6071 20.2881 17.2409 20.3496 16.8044 20.2031C15.1052 19.5352 11.8034 18.085 8.85906 15.1406C5.89129 12.1729 4.34148 8.80664 3.77312 7.17188C3.65887 6.86719 3.7409 6.41602 4.0075 6.1875L4.05437 6.14063L6.32781 3.82031C6.38055 3.77637 6.43621 3.75 6.49187 3.75Z" fill="#226B49"/>\n</svg>\n';

  // src/experiment.ts
  console.log("Revision #".concat(revision));
  var slideTransition = "slide-left";
  var mobileMenuClosed = "mobile-menu-closed";
  var mobileMenuOpened = "mobile-menu-opened";
  var mobileFlyoutOpened = "mobile-flyout-opened";
  var topCategoryClicked = "top-category-clicked";
  var backDropSelector = "#modal-backdrop";
  var fixed = "fixed";
  var unlockPage = function unlockPage() {
    document.documentElement.classList.remove(fixed);
  };
  var lockPage = function lockPage() {
    document.documentElement.classList.add(fixed);
  };
  var applyTreatmentToSiteLogo = function applyTreatmentToSiteLogo() {
    var logoAnchor = document.querySelector(".mobile_logo a");
    logoAnchor.innerHTML = signal_default;
  };
  var getSubNavPanel = function getSubNavPanel(container) {
    var subNav = container === null || container === void 0 ? void 0 : container.nextElementSibling;
    return subNav === null || subNav === void 0 ? void 0 : subNav.querySelector(".panel");
  };
  var revealHamburgerIcon = function revealHamburgerIcon(mobileMenu, closeBtn) {
    closeBtn.classList.add("hidden");
    mobileMenu.classList.add("show");
    mobileMenu.classList.remove("hidden");
  };
  var revealCloseButton = function revealCloseButton(closeBtn, mobileMenu) {
    mobileMenu.classList.add("hidden");
    closeBtn.classList.add("show");
    closeBtn.classList.remove("hidden");
  };
  var setupMobileMenuEventHandlers = function setupMobileMenuEventHandlers(mobileMenu, closeBtn) {
    mobileMenu.addEventListener("click", function () {
      revealCloseButton(closeBtn, mobileMenu);
      document.dispatchEvent(new CustomEvent(mobileMenuOpened));
    });
  };
  var updatePhoneIconInHeader = function updatePhoneIconInHeader(phoneAnchor) {
    phoneAnchor === null ||
      phoneAnchor === void 0 ||
      phoneAnchor.replaceChild(parseSVG_default(phone_default), phoneAnchor.firstChild);
  };
  var addArrowToSubCategories = function addArrowToSubCategories(panel) {
    var subCategoryContainers =
      panel === null || panel === void 0 ? void 0 : panel.querySelectorAll(".sub-category");
    var _iterator2 = _createForOfIteratorHelper(subCategoryContainers),
      _step2;
    try {
      for (_iterator2.s(); !(_step2 = _iterator2.n()).done; ) {
        var subCategory = _step2.value;
        addArrowToAnchor(subCategory);
      }
    } catch (err) {
      _iterator2.e(err);
    } finally {
      _iterator2.f();
    }
  };
  var createOrderFromCatalogButton = function createOrderFromCatalogButton() {
    var button = document.createElement("button");
    button.ariaLabel = "Order From Catalog Search";
    button.type = "submit";
    button.classList.add("order-from-catalog-btn");
    button.innerHTML = search_default;
    return button;
  };
  var setupMobileMenuCloseButton = function setupMobileMenuCloseButton(headerMobile) {
    var closeBtn = document.createElement("button");
    closeBtn.classList.add("close-menu", "mobile_menu", "hidden");
    closeBtn.ariaLabel = "Close Menu";
    closeBtn.innerHTML = close_default;
    headerMobile.append(closeBtn);
    return closeBtn;
  };
  var addArrowToAnchor = function addArrowToAnchor(container) {
    var anchor = container.querySelector("a");
    if (anchor.getAttribute("aria-expanded") === "false") {
      var arrowSpan = document.createElement("span");
      arrowSpan.innerHTML = arrow_default;
      anchor.append(arrowSpan);
    }
  };
  var addBackArrowToSubNavHeader = function addBackArrowToSubNavHeader(subNavHeaderAnchor) {
    var subNavHeaderArrow = document.createElement("span");
    subNavHeaderArrow.innerHTML = back_default;
    subNavHeaderAnchor.prepend(subNavHeaderArrow);
  };
  var removePrevSubNavHeaderArrow = function removePrevSubNavHeaderArrow(
    subNavHeader,
    subNavHeaderAnchor
  ) {
    subNavHeader.classList.add("sub-nav-header");
    subNavHeaderAnchor.removeChild(subNavHeaderAnchor.querySelector("span"));
  };
  var applyTreatmentToMenuOrder = function applyTreatmentToMenuOrder(menuOrder) {
    var menuOrderTitle = menuOrder.querySelector("span");
    var menuOrderForm = menuOrder.querySelector("form");
    var orderFromCatalogBtn = createOrderFromCatalogButton();
    menuOrderForm.append(orderFromCatalogBtn);
    menuOrderTitle.textContent = capitalizeWords(menuOrderTitle.textContent);
  };
  var applyTreatmentToMobileSearch = function applyTreatmentToMobileSearch(mobileSearch) {
    var _mobileSearch$parentN;
    var hr = document.createElement("hr");
    var searchInput = mobileSearch.querySelector(".mobile-search-field");
    var mobileSearchBtn = mobileSearch.querySelector(".mobile-search-button");
    (_mobileSearch$parentN = mobileSearch.parentNode) === null ||
      _mobileSearch$parentN === void 0 ||
      _mobileSearch$parentN.insertBefore(hr, mobileSearch);
    mobileSearchBtn.innerHTML = search_default;
    searchInput === null ||
      searchInput === void 0 ||
      searchInput.setAttribute("placeholder", "Search");
  };
  var revealMainPanelLinks = function revealMainPanelLinks(containers, belowMenuOrderItems) {
    var mainPanel = document.querySelector(".mobile_categories > .menu-element > .panel");
    requestAnimationFrame(function () {
      mainPanel.style.height = "auto";
    });
    document.body.classList.remove("sub-mobile-flyout-opened");
    var _iterator3 = _createForOfIteratorHelper(containers),
      _step3;
    try {
      for (_iterator3.s(); !(_step3 = _iterator3.n()).done; ) {
        var tc = _step3.value;
        tc.classList.remove(slideTransition);
        displayELement(tc);
      }
    } catch (err) {
      _iterator3.e(err);
    } finally {
      _iterator3.f();
    }
    var _iterator4 = _createForOfIteratorHelper(belowMenuOrderItems),
      _step4;
    try {
      for (_iterator4.s(); !(_step4 = _iterator4.n()).done; ) {
        var item = _step4.value;
        displayELement(item);
      }
    } catch (err) {
      _iterator4.e(err);
    } finally {
      _iterator4.f();
    }
  };
  var handleSubNavHeaderClick = function handleSubNavHeaderClick(
    subNavHeader,
    containers,
    belowMenuOrderItems
  ) {
    subNavHeader.addEventListener("click", function () {
      revealMainPanelLinks(containers, belowMenuOrderItems);
    });
  };
  var handleTransitionEnd = function handleTransitionEnd(element) {
    var display = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : "none";
    element.addEventListener("transitionend", function handleTransitionEnd2(event) {
      element.removeEventListener("transitionend", handleTransitionEnd2);
      if (event.propertyName === "transform") {
        element.style.display = display;
      }
    });
  };
  var handleTopCategoryWrapperClick = function handleTopCategoryWrapperClick(
    container,
    containers,
    belowMenuOrderItems
  ) {
    container.addEventListener("click", function () {
      document.dispatchEvent(new CustomEvent(topCategoryClicked));
      document.body.classList.add("sub-mobile-flyout-opened");
      var _iterator5 = _createForOfIteratorHelper(containers),
        _step5;
      try {
        for (_iterator5.s(); !(_step5 = _iterator5.n()).done; ) {
          var tc = _step5.value;
          tc.classList.add(slideTransition);
          handleTransitionEnd(tc);
        }
      } catch (err) {
        _iterator5.e(err);
      } finally {
        _iterator5.f();
      }
      var _iterator6 = _createForOfIteratorHelper(belowMenuOrderItems),
        _step6;
      try {
        for (_iterator6.s(); !(_step6 = _iterator6.n()).done; ) {
          var item = _step6.value;
          hideELement(item);
        }
      } catch (err) {
        _iterator6.e(err);
      } finally {
        _iterator6.f();
      }
    });
  };
  var appendOrderFromCatalogAreaToPanel = function appendOrderFromCatalogAreaToPanel(
    panel,
    belowMenuOrderItems
  ) {
    var _belowMenuOrderItems = _slicedToArray(belowMenuOrderItems, 4),
      accSection = _belowMenuOrderItems[0],
      grayMenu1 = _belowMenuOrderItems[1],
      grayMenu2 = _belowMenuOrderItems[2],
      menuOrder = _belowMenuOrderItems[3];
    var grayMenus = [grayMenu1, grayMenu2];
    var menuOrderClone =
      menuOrder === null || menuOrder === void 0 ? void 0 : menuOrder.cloneNode(true);
    var orderFromCatalogArea = document.createElement("ul");
    applyTreatmentToMenuOrder(menuOrderClone);
    orderFromCatalogArea.append(menuOrderClone);
    for (var _i = 0, _grayMenus = grayMenus; _i < _grayMenus.length; _i++) {
      var gm = _grayMenus[_i];
      orderFromCatalogArea.append(gm === null || gm === void 0 ? void 0 : gm.cloneNode(true));
    }
    orderFromCatalogArea.append(
      accSection === null || accSection === void 0 ? void 0 : accSection.cloneNode(true)
    );
    panel === null || panel === void 0 || panel.append(orderFromCatalogArea);
  };
  var getBelowMenuOrderItems = function getBelowMenuOrderItems() {
    var menuItems = document.querySelector(".mobile_flyout nav ul");
    var menuOrder = menuItems.querySelector(".mobile_categories ~ .menu_order");
    var accSection = menuItems.querySelector(".mobile_categories ~ .acc_section");
    var grayMenus = menuItems.querySelectorAll(".mobile_categories ~ .gray_menu");
    var belowMenuOrderItems = [];
    belowMenuOrderItems.push(accSection);
    belowMenuOrderItems.push(Array.from(grayMenus));
    belowMenuOrderItems.push(menuOrder);
    return belowMenuOrderItems.flat(2);
  };
  var setupTopCategoryContainers = function setupTopCategoryContainers(containers) {
    var belowMenuOrderItems = getBelowMenuOrderItems();
    var _iterator7 = _createForOfIteratorHelper(containers),
      _step7;
    try {
      for (_iterator7.s(); !(_step7 = _iterator7.n()).done; ) {
        var container = _step7.value;
        addArrowToAnchor(container);
        var subNavPanel = getSubNavPanel(container);
        addArrowToSubCategories(subNavPanel);
        var subNavHeader = container.cloneNode(true);
        subNavPanel === null ||
          subNavPanel === void 0 ||
          subNavPanel.insertBefore(subNavHeader, subNavPanel.firstChild);
        appendOrderFromCatalogAreaToPanel(subNavPanel, belowMenuOrderItems);
        var subNavHeaderAnchor = subNavHeader.querySelector("a");
        removePrevSubNavHeaderArrow(subNavHeader, subNavHeaderAnchor);
        addBackArrowToSubNavHeader(subNavHeaderAnchor);
        handleSubNavHeaderClick(subNavHeader, containers, belowMenuOrderItems);
        handleTopCategoryWrapperClick(container, containers, belowMenuOrderItems);
      }
    } catch (err) {
      _iterator7.e(err);
    } finally {
      _iterator7.f();
    }
  };
  var setupCloseButtonEventHandlers = function setupCloseButtonEventHandlers(
    closeBtn,
    mobileFlyout,
    defaultFlyoutCloseBtn
  ) {
    var userAccountAnchor = document.querySelector(".pe-0");
    var phoneAnchor = document.querySelector(".pe-1");
    replaceIcon_default(userAccountAnchor, user_default);
    updatePhoneIconInHeader(phoneAnchor);
    waitForSelector(backDropSelector)
      .then(function () {
        for (
          var _i2 = 0, _arr = [phoneAnchor, userAccountAnchor, closeBtn];
          _i2 < _arr.length;
          _i2++
        ) {
          var anchor = _arr[_i2];
          anchor.addEventListener("click", function () {
            if (document.body.classList.contains("mobile-flyout-opened")) {
              var modalBackdrop = document.querySelector(backDropSelector);
              mobileFlyout.classList.remove("active");
              modalBackdrop && document.body.removeChild(modalBackdrop);
              defaultFlyoutCloseBtn.click();
            }
          });
        }
      })
      .catch((error) => {
        console.error(error);
      });
  };
  var applyTreatment = function applyTreatment(variation) {
    initCSS(variation);

    console.log("STARTING TREATMENT!");
    var mobileFlyout = document.querySelector(".mobile_flyout");
    var mobileSearch = document.querySelector(".mobile_search");
    var mobileMenu = document.querySelector(".mobile_menu");
    var defaultFlyoutCloseBtn = mobileFlyout.querySelector(".close.d-none");
    var menuOrder = mobileFlyout.querySelector(".menu_order");
    var accSectionAnchor = document.querySelectorAll(".mobile_flyout .acc_section a");
    var grayMenuAnchor = document.querySelectorAll(".mobile_flyout .gray_menu a");
    var topCategoryContainers = document.querySelectorAll(".category-link-wrapper.top-category");
    var rfID;
    var onTopCategoryClicked = function onTopCategoryClicked() {
      console.log("on top nav clicked");

      var mainPanel = document.querySelector(".mobile_categories > .menu-element > .panel");
      var hr = document.querySelector("header .header_mobile + hr");
      requestAnimationFrame(function () {
        mainPanel.style.height = "calc(100vh - "
          .concat(hr.offsetTop, "px - ")
          .concat(window.scrollY, "px)");
      });
      setTimeout(function () {
        mobileFlyout.scrollTo({
          top: 0,
        });
      }, 5);
    };
    var onFlyoutCloseBtnClick = function onFlyoutCloseBtnClick() {
      document.dispatchEvent(new CustomEvent(mobileMenuClosed));
    };
    var slideToMainPanel = function slideToMainPanel() {
      var activePanel = document.querySelector(".panel-collapse.in");
      activePanel && activePanel.classList.remove("in");
      menuOrder.classList.remove(slideTransition);
      var _iterator8 = _createForOfIteratorHelper(topCategoryContainers),
        _step8;
      try {
        for (_iterator8.s(); !(_step8 = _iterator8.n()).done; ) {
          var container = _step8.value;
          container.classList.remove(slideTransition);
        }
      } catch (err) {
        _iterator8.e(err);
      } finally {
        _iterator8.f();
      }
      var _iterator9 = _createForOfIteratorHelper(grayMenuAnchor),
        _step9;
      try {
        for (_iterator9.s(); !(_step9 = _iterator9.n()).done; ) {
          var _anchor$parentElement;
          var anchor = _step9.value;
          (_anchor$parentElement = anchor.parentElement) === null ||
            _anchor$parentElement === void 0 ||
            _anchor$parentElement.classList.remove(slideTransition);
        }
      } catch (err) {
        _iterator9.e(err);
      } finally {
        _iterator9.f();
      }
      var _iterator10 = _createForOfIteratorHelper(accSectionAnchor),
        _step10;
      try {
        for (_iterator10.s(); !(_step10 = _iterator10.n()).done; ) {
          var _anchor$parentElement2;
          var _anchor = _step10.value;
          (_anchor$parentElement2 = _anchor.parentElement) === null ||
            _anchor$parentElement2 === void 0 ||
            _anchor$parentElement2.classList.remove(slideTransition);
        }
      } catch (err) {
        _iterator10.e(err);
      } finally {
        _iterator10.f();
      }
    };
    var onMobileMenuClosed = function onMobileMenuClosed() {
      mobileFlyout.scrollTo({
        top: 0,
        behavior: "smooth",
      });
      unlockPage();
      document.body.classList.remove(mobileFlyoutOpened);
      revealHamburgerIcon(mobileMenu, closeBtn);
      slideToMainPanel();
      revealMainPanelLinks(topCategoryContainers, getBelowMenuOrderItems());
      cancelAnimationFrame(rfID);
    };
    var onMobileMenuOpened = function onMobileMenuOpened() {
      var mobileCat = document.querySelector(".mobile_cat");
      document.body.classList.add(mobileFlyoutOpened);
      lockPage();
      removeInertAttributeFrom(mobileCat.parentNode);
    };
    var removeInertAttributeFrom = function removeInertAttributeFrom(element) {
      element.removeAttribute("inert");
      rfID = requestAnimationFrame(removeInertAttributeFrom.bind(null, element));
    };
    capitalizeAnchorsText(grayMenuAnchor);
    capitalizeAnchorsText(accSectionAnchor);
    setupTopCategoryContainers(topCategoryContainers);
    applyTreatmentToSiteLogo();
    applyTreatmentToMenuOrder(menuOrder);
    applyTreatmentToMobileSearch(mobileSearch);
    document.addEventListener(mobileMenuOpened, onMobileMenuOpened);
    document.addEventListener(mobileMenuClosed, onMobileMenuClosed);
    document.addEventListener(topCategoryClicked, onTopCategoryClicked);
    defaultFlyoutCloseBtn.addEventListener("click", onFlyoutCloseBtnClick);
    var closeBtn = setupMobileMenuCloseButton(
      mobileMenu === null || mobileMenu === void 0 ? void 0 : mobileMenu.parentNode
    );
    setupCloseButtonEventHandlers(closeBtn, mobileFlyout, defaultFlyoutCloseBtn);
    setupMobileMenuEventHandlers(mobileMenu, closeBtn);
  };
  applyTreatment("v1");
};

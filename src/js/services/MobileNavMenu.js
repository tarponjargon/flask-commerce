/*****************************************************
this is used basically as-is from the CRO USAC-124 experiment
 *****************************************************/
export const mobileNavMenu = () => {
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

  // src/utils/elementDisplay.ts
  var displayELement = function displayELement(el) {
    el === null || el === void 0 || el.style.setProperty("display", "block", "important");
  };
  var hideELement = function hideELement(el) {
    el === null || el === void 0 || el.style.setProperty("display", "none", "important");
  };

  // src/svg/arrow.svg
  var arrow_default =
    '<svg xmlns="http://www.w3.org/2000/svg" width="6" height="11" viewBox="0 0 6 11" fill="none">\n<path d="M1 9.5L5 5.5L1 1.5" stroke="#236A49" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>\n</svg>\n';

  // src/svg/back.svg
  var back_default =
    '<svg xmlns="http://www.w3.org/2000/svg" width="6" height="11" viewBox="0 0 6 11" fill="none">\n<path d="M5 9.5L1 5.5L5 1.5" stroke="#236A49" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>\n</svg>\n';

  // src/svg/search.svg
  var search_default =
    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none">\n<path d="M6.93294 1.60001C3.99374 1.60001 1.59961 3.99414 1.59961 6.93334C1.59961 9.87254 3.99374 12.2667 6.93294 12.2667C8.21108 12.2667 9.38488 11.8128 10.3048 11.0594L13.4892 14.2438C13.5383 14.2949 13.5972 14.3358 13.6623 14.364C13.7275 14.3921 13.7976 14.407 13.8685 14.4077C13.9395 14.4084 14.0099 14.395 14.0756 14.3682C14.1413 14.3413 14.2009 14.3017 14.2511 14.2515C14.3013 14.2013 14.3409 14.1417 14.3678 14.076C14.3946 14.0103 14.408 13.9399 14.4073 13.8689C14.4066 13.798 14.3917 13.7279 14.3636 13.6627C14.3354 13.5976 14.2945 13.5387 14.2434 13.4896L11.059 10.3052C11.8124 9.38528 12.2663 8.21148 12.2663 6.93334C12.2663 3.99414 9.87214 1.60001 6.93294 1.60001ZM6.93294 2.66667C9.29567 2.66667 11.1996 4.57061 11.1996 6.93334C11.1996 9.29607 9.29567 11.2 6.93294 11.2C4.57021 11.2 2.66628 9.29607 2.66628 6.93334C2.66628 4.57061 4.57021 2.66667 6.93294 2.66667Z" fill="#226C49"/>\n</svg>\n';

  // src/experiment.ts
  var slideTransition = "slide-left";
  var topCategoryClicked = "top-category-clicked";
  var unlockPage = function unlockPage() {
    document.documentElement.classList.remove("fixed");
    document.body.classList.remove("fixed");
    document.querySelectorAll("main, header, footer").forEach((el) => {
      el.removeAttribute("inert");
    });
  };
  var lockPage = function lockPage() {
    document.body.classList.add("fixed");
    document.documentElement.classList.add("fixed");
    document.querySelectorAll("main, header, footer").forEach((el) => {
      el.setAttribute("inert", "true");
    });
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
    var menuOrderForm = menuOrder.querySelector("form");
    var orderFromCatalogBtn = createOrderFromCatalogButton();
    menuOrderForm.append(orderFromCatalogBtn);
  };
  var applyTreatmentToMobileSearch = function applyTreatmentToMobileSearch(mobileSearch) {
    var _mobileSearch$parentN;
    var hr = document.createElement("hr");
    var mobileSearchBtn = mobileSearch.querySelector(".mobile-search-button");
    (_mobileSearch$parentN = mobileSearch.parentNode) === null ||
      _mobileSearch$parentN === void 0 ||
      _mobileSearch$parentN.insertBefore(hr, mobileSearch);
    mobileSearchBtn.innerHTML = search_default;
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
    if (!subNavHeader.hasListener) {
      subNavHeader.hasListener = true;
      subNavHeader.addEventListener("click", function () {
        revealMainPanelLinks(containers, belowMenuOrderItems);
      });
    }
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
    if (!container.hasListener) {
      container.hasListener = true;
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
    }
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

  // console.log("STARTING TREATMENT!");
  var mobileFlyout = document.querySelector(".mobile_flyout");
  var mobileSearch = document.querySelector(".mobile_search");
  var mobileMenu = document.querySelector(".mobile_menu");
  var menuOrder = mobileFlyout.querySelector(".menu_order");
  var accSectionAnchor = document.querySelectorAll(".mobile_flyout .acc_section a");
  var grayMenuAnchor = document.querySelectorAll(".mobile_flyout .gray_menu a");
  var topCategoryContainers = document.querySelectorAll(".category-link-wrapper.top-category");
  var closeBtn = document.querySelector("#mobile-menu-close");
  var backDropSelector = "#modal-backdrop";
  var rfID;
  var onTopCategoryClicked = function onTopCategoryClicked() {
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

  setupTopCategoryContainers(topCategoryContainers);
  applyTreatmentToMenuOrder(menuOrder);
  applyTreatmentToMobileSearch(mobileSearch);

  if (!document.topCategoryClickedListener) {
    document.topCategoryClickedListener = true;
    document.addEventListener(topCategoryClicked, onTopCategoryClicked);
  }

  var closeMobileMenu = function () {
    // console.log("closeMobileMenu");
    var modalBackdrop = document.querySelector(backDropSelector);
    mobileFlyout.classList.remove("active");
    modalBackdrop && document.body.removeChild(modalBackdrop);
    mobileFlyout.scrollTo({
      top: 0,
      behavior: "smooth",
    });
    document.removeEventListener("click", handleClickOutside);
    unlockPage();
    document.body.classList.remove("mobile-flyout-opened");
    revealHamburgerIcon(mobileMenu, closeBtn);
    slideToMainPanel();
    revealMainPanelLinks(topCategoryContainers, getBelowMenuOrderItems());
    cancelAnimationFrame(rfID);
  };

  var handleClickOutside = function (event) {
    // console.log("handleClickOutside");
    const mobileFlyout = document.querySelector(".mobile_categories");
    if (!mobileFlyout.contains(event.target)) {
      // console.log("click outside");
      closeMobileMenu();
    }
  };

  // listen for clicks on the hamburger icon to trigger slideout
  if (!mobileMenu.hasClickListener) {
    mobileMenu.hasClickListener = true;
    mobileMenu.addEventListener("click", function () {
      // console.log("mobileMenu clicked");
      mobileFlyout.classList.add("active");
      document.body.classList.add("mobile-flyout-opened");
      lockPage();
      revealCloseButton(closeBtn, mobileMenu);
      document.body.appendChild(
        Object.assign(document.createElement("div"), {
          id: "modal-backdrop",
          className: "modal-backdrop fade in",
        })
      );
      setTimeout(() => {
        document.addEventListener("click", handleClickOutside);
      }, 500);
    });
  }
};

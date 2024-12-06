export default class NavMenu {
  constructor() {
    this.menuNodes = document.querySelectorAll(".main-desk-nav .dropdown, #gift-guide-tab");
    this.navMenuActive = undefined;
    this.focusableEls = undefined;
    this.firstFocusableEl = undefined;
    this.lastFocusableEl = undefined;
  }
  init = () => {
    this.addGiftsByPrice();
    this.stickyNav();
    this.navOverlay();

    // on init (page load), listen for events on menu dropdown nodes in this.menuNodes
    this.menuNodes.forEach((nav) => {
      nav.addEventListener(
        "mouseenter",
        (e) => {
          this.showNavMenu(nav);
        },
        false
      );
      nav.addEventListener(
        "mouseleave",
        (e) => {
          this.hideNavMenu();
        },
        false
      );
      nav.querySelector("a").addEventListener("focus", (e) => {
        if (!nav.hasMenuButtonListener) this.menuButtonKeyPress(nav);
      });
    });
  };

  toggleMenu = (menu) => {
    if (menu === this.navMenuActive) {
      this.hideNavMenu();
    } else {
      this.showNavMenu(menu);
    }
  };

  menuButtonKeyPress = (menu) => {
    // if a menu heading link is focused, listen for keyboard events...
    // which will indicate menus are being nav'd by keyboard.  focus + "Space" or "Enter" keys
    // should expand menus
    menu.hasMenuButtonListener = true;
    menu.querySelector("a").addEventListener(
      "keydown",
      (event) => {
        if (
          event.key === " " ||
          event.code === "Space" ||
          event.keyCode === 32 ||
          event.code === "Enter"
        ) {
          event.preventDefault();
          this.toggleMenu(menu);
        }
      },
      false
    );
  };

  unHover = () => {
    // update all menu nodes to closed state
    this.menuNodes.forEach((menu) => {
      menu.classList.remove("hovered");
      menu.querySelector("a").setAttribute("aria-expanded", "false");
    });
  };

  showNavMenu = (menu) => {
    // main function for showing a hover menu
    this.unHover(); // reset all to closed state to be sure we have a clean slate
    menu.classList.add("hovered");
    menu.querySelector("a").setAttribute("aria-expanded", "true");
    this.onMenuShown(menu);
  };

  hideNavMenu = () => {
    // main function for hiding a hover menu
    this.unHover();
    this.onMenuHidden();
  };

  onMenuShown = (menu) => {
    // do when a menu is shown
    this.navMenuActive = menu;
    this.trapFocus(menu);
  };

  onMenuHidden = () => {
    // do when a menu is hidden
    if (this.navMenuActive) {
      this.unTrapFocus(this.navMenuActive);
      this.navMenuActive = undefined;
    }
  };

  trapFocus = (element) => {
    // limit focusable (keyboard navigable) elements to within given element
    // NOTE: sets some state at the object level
    this.focusableEls = Array.from(element.querySelectorAll("a"));
    this.firstFocusableEl = this.focusableEls[0];
    this.lastFocusableEl = this.focusableEls[this.focusableEls.length - 1];
    element.addEventListener("keydown", this.menuKeyListener, false);
  };

  unTrapFocus = (element) => {
    // release event listeners added when focus trap was added
    element.removeEventListener("keydown", this.menuKeyListener, false);
  };

  menuKeyListener = (e) => {
    // when a menu is open, listen for navigation keystrokes
    if (e.key === "Tab" || e.keyCode === 9) {
      if (e.shiftKey) {
        // if this is a tab-shift, go backwards
        if (document.activeElement === this.firstFocusableEl) {
          this.lastFocusableEl.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === this.lastFocusableEl) {
          this.firstFocusableEl.focus();
          e.preventDefault();
        }
      }
    }

    // escape should close the menu
    else if (e.key === "Escape" && this.navMenuActive) {
      this.navMenuActive.querySelector("a").focus();
      this.hideNavMenu();
    }

    // arrow down should behave like tab (go forward)
    else if (e.key === "ArrowDown" && this.navMenuActive) {
      e.preventDefault();
      if (document.activeElement === this.lastFocusableEl) {
        this.firstFocusableEl.focus();
        return;
      }
      let idx = this.focusableEls.findIndex((i) => i === document.activeElement);
      if (idx === -1) idx = 0;
      this.focusableEls[idx + 1].focus();
    }

    // arrow up should behave like shift-tab (go in reverse)
    else if (e.key === "ArrowUp" && this.navMenuActive) {
      e.preventDefault();
      if (document.activeElement === this.firstFocusableEl) {
        this.lastFocusableEl.focus();
        return;
      }
      let idx = this.focusableEls.findIndex((i) => i === document.activeElement);
      if (idx === -1) idx = 1;
      this.focusableEls[idx - 1].focus();
    }
  };

  addGiftsByPrice = () => {
    const addGiftsByPriceHTML = `
      <a tabindex="0" class="level-item-2" href="/gifts">Gifts By Price</a>
      <a tabindex="0" class="level-item-3" href="/gifts#/filter:price:0:30">Under $30</a>
      <a tabindex="0" class="level-item-3" href="/gifts#/filter:price:25:50">Under $50</a>
      <a tabindex="0" class="level-item-3" href="/gifts#/filter:price:50:75">Under $75</a>
      <a tabindex="0" class="level-item-3" href="/gifts#/filter:price:75:100">Under $100</a>
    `;
    const addByPriceAfterEl = document.querySelector(
      '.dropdown-menu-container-12 [class="level-item-2"][href="/gifts/recipient"]'
    );
    if (addByPriceAfterEl) {
      addByPriceAfterEl.insertAdjacentHTML("beforebegin", addGiftsByPriceHTML);
    }
    const addByPriceGiftGuideEl = document.querySelector(
      '.bbs-tab-dropdown-menu-container [class="level-item-2"][href="/gifts/recipient?ipi=tab_recipient"]'
    );
    if (addByPriceGiftGuideEl) {
      addByPriceGiftGuideEl.insertAdjacentHTML("beforebegin", addGiftsByPriceHTML);
    }
    const addByPriceAfterElMobile = document.querySelector(
      ".mobile_categories .sub-category-gifts"
    );
    if (addByPriceAfterElMobile) {
      addByPriceAfterElMobile.insertAdjacentHTML(
        "afterend",
        `
      <div class="category-link-wrapper sub-category sub-category-by-price">
          <a class="collapsed" href="#target-XAHymrDJusb-price" data-toggle="collapse" role="button" aria-expanded="false" aria-controls="target-XAHymrDeJb-price">By Price</a>
          <div class="panel-collapse collapse" id="target-XAHymrDJusb-price" data-parent="#target-XAHymrDJusb-price" aria-expanded="false" style="">
            <div class="category-link-wrapper category">
                <a data-js="slideout-close" href="/gifts#/filter:price:0:30">Under $30</a>
            </div>
            <div class="category-link-wrapper category">
                <a data-js="slideout-close" href="/gifts#/filter:price:25:50">Under $50</a>
            </div>
            <div class="category-link-wrapper category">
                <a data-js="slideout-close" href="/gifts#/filter:price:50:75">Under $75</a>
            </div>
            <div class="category-link-wrapper category">
                <a data-js="slideout-close" href="/gifts#/filter:price:75:100">Under $100</a>
            </div>
          </div>
      </div>
      `
      );
    }

    // add event listeners to the new sub-category-by-price links
    const flyoutCloseBtn = document.querySelector(".mobile_flyout .close");
    document.querySelectorAll(".sub-category-by-price .category a").forEach((el) => {
      el.addEventListener("click", (e) => {
        flyoutCloseBtn.click();
      });
    });
  };

  stickyNav = () => {
    // keeps category nav sticky when scrolling
    const categoryNav = document.querySelector("nav.category-nav");
    if (!categoryNav) return;
    const { offsetTop } = categoryNav;
    window.addEventListener("scroll", () => {
      if (window.pageYOffset > offsetTop) {
        categoryNav.classList.add("sticky-navbar");
      } else {
        categoryNav.classList.remove("sticky-navbar");
      }
    });
  };

  navOverlay = () => {
    // darken background when a hover menu is open
    const newNavOverlay = document.querySelector(".navbar-overlay");
    const hoveredElements = document.querySelectorAll(".dropdown.menu-item");
    if (!newNavOverlay || !hoveredElements.length) return;

    // Create a single MutationObserver for all hovered elements
    const observer = new MutationObserver((mutations) => {
      const anyHovered = Array.from(hoveredElements).some((el) => el.classList.contains("hovered"));
      newNavOverlay.style.display = anyHovered ? "block" : "none";
    });

    // Observe all hovered elements
    for (const hoveredEl of hoveredElements) {
      observer.observe(hoveredEl, { attributes: true, attributeFilter: ["class"] });
    }
  };
}

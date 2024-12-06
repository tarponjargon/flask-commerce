import { copy, getFirstFocusable, isElementVisible } from "./Utils";

export default class Accessibility {
  constructor() {
    this.lastClickedEl = undefined;
    this.returnFocusEl = undefined;
    this.focusableEls = [];
    this.firstFocusableEl = undefined;
    this.lastFocusableEl = undefined;
  }
  init = () => {
    $(document).on("click", this.saveLastClicked);
    $(document).on("show.bs.modal", this.onShowModal);
    $(document).on("shown.bs.modal", this.onShownModal);
    $(document).on("hide.bs.modal", this.onHideModal);
    $(document).on("hidden.bs.modal", this.onHiddenModal);
  };

  onShowModal = (e) => {
    const modalEl = e.target;
    // if (modalEl.classList.contains("mobile_flyout")) {
    //   modalEl.querySelector(".close").classList.remove("d-none");
    // }
  };

  onShownModal = (e) => {
    /* listen for modal appearance, and add accessibility features to the document and modal */
    const modalEl = e.target;

    let topSelector = ".modal";
    // if (modalEl.classList.contains("mobile_flyout")) topSelector = ".mobile_flyout";

    if (!modalEl) return false;

    this.returnFocusEl = this.lastClickedEl || document.activeElement;

    document.body.removeAttribute("aria-haspopup");
    document.body.setAttribute("aria-haspopup", "dialog");
    modalEl.setAttribute("aria-modal", "true");
    modalEl.setAttribute("aria-hidden", "false");
    const dataAria = modalEl.getAttribute("data-aria-labelledby");
    if (dataAria) modalEl.setAttribute("aria-labelledby", dataAria);

    // if (topSelector === ".mobile_flyout") {
    //   const flyoutNav = modalEl.querySelector("nav");
    //   const closeBtn = modalEl.querySelector(".close");
    //   closeBtn.classList.remove("d-none");

    //   const closeFlyoutListener = function (e) {
    //     if (!flyoutNav.contains(e.target)) {
    //       if (closeBtn) {
    //         closeBtn.focus();
    //         closeBtn.click();
    //       }
    //     }
    //   };
    //   if (!modalEl.hasClickListener) {
    //     modalEl.hasClickListener = true;
    //     modalEl.addEventListener("click", closeFlyoutListener, false);
    //   }
    //   if (!modalEl.hasTouchListener) {
    //     modalEl.hasTouchListener = true;
    //     modalEl.addEventListener("touchstart", closeFlyoutListener, false);
    //   }
    // }

    this.trapFocus(modalEl);
    this.setInert();

    let modalFocus = modalEl.querySelector(
      `${topSelector} button, ${topSelector} a, ${topSelector} input:not([type='hidden'], ${topSelector} select, ${topSelector} textarea`
    );
    if (!modalFocus) modalFocus = getFirstFocusable(modalEl);
    modalFocus.focus();
  };

  onHiddenModal = (e) => {
    /* listen for modal hide, and dynamically remove accessibility features from the document */
    const modalEl = e.target;

    if (!modalEl) return false;
    document.body.removeAttribute("aria-haspopup");
    modalEl.removeAttribute("aria-modal");
    modalEl.removeAttribute("aria-live");
    modalEl.removeAttribute("aria-hidden", "true");
    if (modalEl.getAttribute("aria-labelledby") && modalEl.getAttribute("data-aria-labelledby")) {
      modalEl.removeAttribute("aria-labelledby");
    }

    if (this.returnFocusEl && isElementVisible(this.returnFocusEl)) {
      this.returnFocusEl.focus();
      this.returnFocusEl = undefined;
    } else {
      const focusEl = document.body || getFirstFocusable();
      focusEl.focus();
    }

    this.unTrapFocus(modalEl);
    this.unSetInert();
  };

  onHideModal = (e) => {
    const modalEl = e.target;
    // if (modalEl.classList.contains("mobile_flyout")) {
    //   modalEl.querySelector(".close").classList.add("d-none");
    // }
  };

  saveLastClicked = (e) => {
    /* save the last clicked element so I can re-focus to it after modal close */
    this.lastClickedEl = e.target;
  };

  trapFocus = (element) => {
    // limit focusable (keyboard navigable) elements to within given element
    // NOTE: sets some state at the object level
    const els = Array.from(
      element.querySelectorAll(
        'button, a, input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
    );
    els.forEach((el) => {
      if (isElementVisible(el)) {
        this.focusableEls.push(el);
      }
    });

    this.firstFocusableEl = this.focusableEls[0];
    this.lastFocusableEl = this.focusableEls[this.focusableEls.length - 1];
    element.addEventListener("keydown", this.menuKeyListener, false);
  };

  unTrapFocus = (element) => {
    // release event listeners added when focus trap was added
    element.removeEventListener("keydown", this.menuKeyListener, false);
  };

  setInert = () => {
    document.querySelectorAll("main, header, footer").forEach((el) => {
      el.setAttribute("inert", "true");
    });
  };

  unSetInert = () => {
    document.querySelectorAll("main, header, footer").forEach((el) => {
      el.removeAttribute("inert");
    });
  };

  // closeFlyout = () => {
  //   const closeBtn = document.querySelector(".mobile_flyout .close");
  //   if (!closeBtn) return;
  //   closeBtn.focus();
  //   closeBtn.click();
  // };

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
    } else if (e.key === "Escape") {
      // this.closeFlyout();
    }

    // arrow down should behave like tab (go forward)
    else if (e.key === "ArrowDown") {
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
    else if (e.key === "ArrowUp") {
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
}

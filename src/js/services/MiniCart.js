import { fetchContent } from "./Ajax";
import messages from "./Messages";
import { getBodyData, hasCartItems, spinLink, unSpinButton, unSpinLink } from "./Utils";

const onShippingSelect = function (e) {
  console.log("onShippingSelect", e);

  const spinSel = "#cart-summary-modal #ship-method-spinner";
  const el = e.target.options[e.target.selectedIndex];
  if (!el || !el.getAttribute("data-id")) return;
  const shipMethodId = el.getAttribute("data-id");
  spinLink(spinSel, "", "");
  fetch("/default?ship_method=" + shipMethodId)
    .then(() => {
      showMiniCart()
        .then(() => {
          flashMessage.show({ message: messages.itemadded });
        })
        .catch((e) => {
          console.error("minicart update failed", e);
          unSpinLink(spinSel);
        });
    })
    .catch((e) => {
      flashMessage.show({
        message: "Could not update ship method",
        alertType: "error",
      });
      console.error("minicart ship method update failed", e);
      unSpinLink(spinSel);
    });
};

const onCouponSubmit = function (e) {
  console.log("onCouponSubmit", e);
  e.preventDefault();
  const el = e.target.querySelector('#cart-summary-modal [name="coupon_code"]');
  if (!el || !el.value) return;
  const couponCode = el.value.trim();
  spinButton("cart-promo-button", "");
  showMiniCart(couponCode)
    .then(() => {
      flashMessage.show({ message: messages.itemadded });
      unSpinButton("cart-promo-button", "APPLY");
    })
    .catch((e) => {
      console.error("minicart update failed", e);
      unSpinButton("cart-promo-button", "APPLY");
    });
};

const setListeners = function () {
  // listen for ship method changes
  const shipMethods = document.querySelector('#cart-summary-modal [data-js="ship-methods-menu"]');
  if (shipMethods && !shipMethods.hasListener) {
    document.addEventListener("change", onShippingSelect, false);
    shipMethods.hasEventListener = true;
  }

  // listen for coupon code submits
  const couponForms = document.querySelectorAll(
    "#cart-summary-modal [data-js='cart-promo-submit']"
  );
  if (couponForms && couponForms.length) {
    couponForms.forEach((couponForm) => {
      if (couponForm.hasEventListener) return;
      couponForm.addEventListener("submit", onCouponSubmit, false);
      couponForm.hasEventListener = true;
    });
  }
};

export const showMiniCart = function (couponCode) {
  return new Promise((resolve, reject) => {
    const modal = document.querySelector("#cart-summary-modal .modal-content");
    const client = getBodyData("data-client-id");
    let url = "/minicart";
    if (couponCode) {
      url += "?coupon_code=" + couponCode;
    }

    const onSuccess = (content) => {
      // if the screen says there are items but the minicart says there aren't, do the request again
      // this is a hazel bug regarding persistent carts
      if (hasCartItems() && content && content.includes("cart is empty")) {
        fetchContent(url).then((data) => {
          const html = $.parseHTML($.trim(data), document, true); // will execute <script> in minicart html
          $(modal).html(html);
          $("#cart-summary-modal").modal("show");
        });
      } else {
        const html = $.parseHTML($.trim(content), document, true); // will execute <script> in minicart html
        $(modal).html(html);
        $("#cart-summary-modal").modal("show");
        resolve();

        setTimeout(() => {
          setListeners();
        }, 300);
      }
    };

    fetchContent(url)
      .then((content) => onSuccess(content))
      .catch(() => {
        console.error("minicart failed, retrying", client, url);
        fetchContent(url)
          .then((content) => {
            console.error("minicart retry succeeded", client, url);
            onSuccess(content);
          })
          .catch((e) => {
            console.error("minicart retry failed", e, client, url);
          });
      });
  });
};

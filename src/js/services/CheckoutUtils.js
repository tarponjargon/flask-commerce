export const quantityChangeListeners = function () {
  $('input[data-js="quantity-field"]').on("change", (e) => {
    const el = $(e.delegateTarget).closest('[data-js="quantity"]');
    updateQuantity(el);
  });
  $('[data-lineitem-skuid] [data-js="quantity"]').on("submit", (e) => {
    e.preventDefault();
    updateQuantity($(e.delegateTarget));
  });
};

export const updateQuantity = function (formEl) {
  if (!formEl) return false;
  const quantityEl = $(formEl).find('[data-js="quantity-field"]');
  const quantity = parseInt($(quantityEl).val());
  const maxqStr = quantityEl.attr("max");
  const maxq = maxqStr && !isNaN(maxqStr) ? parseInt(maxqStr) : 300;
  if (quantity < 0 || quantity > maxq) return false;
  const origQuantity = parseInt($(quantityEl).attr("data-orig-quantity"));
  const product = $(quantityEl).attr("name");
  const giftwrap = $(quantityEl).attr("data-gift-wrapped") || null;
  const giftwrapQuantity = giftwrap
    ? parseInt($(`[data-lineitem-skuid="${giftwrap}"] [data-js="giftwrap-quantity"]`).text())
    : null;

  let path = $("body").data("page-path") || window.location.pathname;
  let url = `${path}?${product}=${quantity}`;
  // if the item is giftwrapped, change the giftwrap item quantity to reflect qty change of this item
  if (giftwrap && giftwrapQuantity) {
    let gwq = giftwrapQuantity;
    gwq += quantity > origQuantity ? quantity - origQuantity : 0;
    gwq -= quantity < origQuantity ? origQuantity - quantity : 0;
    url += gwq !== giftwrapQuantity ? `&PRODUCT_${giftwrap}=${gwq}` : "";
  }
  window.location.href = url;
};

export const persListeners = function () {
  $('[data-js="edit-personalization"]').on("click", (e) => {
    e.preventDefault();
    const lastAdded = $(e.delegateTarget).data("last-added");
    const returnpage = $(e.delegateTarget).data("return");
    let url = `/store?action=editpersonalization&last_added=${lastAdded}&returnpage=${returnpage}`;
    $("#cart-modal .modal-content").load(url, () => {
      $("#cart-modal").modal("show");
    });
  });
};

export const giftListeners = function () {
  $('[data-lineitem-skuid] [data-js="gift-options-trigger"]').on("click", (e) => {
    e.preventDefault;
    const el = $(e.delegateTarget).closest("[data-lineitem-skuid]");
    toggleGiftOps(el);
  });
};

export const toggleGiftOps = function (el) {
  if (!el) return false;
  const skuid = $(el).data("lineitem-skuid");
  if (!skuid) return false;

  const row = $(el).find('[data-js="row"]');
  const triggerEl = $(el).find('[data-js="gift-options-trigger"]');
  const contentEl = $(el).find('[data-js="gift-options"]');

  if ($(contentEl).is(":visible")) {
    $(triggerEl).removeClass("active");
    $(row).removeClass("active");
    $(contentEl).slideUp("fast");
  } else {
    $(triggerEl).addClass("active");
    $(row).addClass("active");
    $(contentEl).slideDown("fast");
  }
};

export const addressbookListeners = () => {
  // load selected address into shipping fields
  $('[data-js="addressbook-address"]').on("change", () => {
    let address = $('[data-js="addressbook-address"]').val();
    if (address) {
      copyAddressToShip(address);
      if (!$("#reset-shipping-address-link").is(":visible")) {
        $("#reset-shipping-address-link").show();
      }
    } else {
      clearShipping();
      if ($("#reset-shipping-address-link").is(":visible")) {
        $("#reset-shipping-address-link").hide();
      }
    }
  });

  // if "reset" btn is clicked, clear shipping address fields
  $("#reset-shipping-address-link").on("click", () => {
    clearShipping();
    $('[data-js="addressbook-address"]').prop("selectedIndex", 0);
    if ($("#reset-shipping-address-link").is(":visible")) {
      $("#reset-shipping-address-link").hide();
    }
  });
};

export const copyAddressToShip = function (address) {
  $(`[data-js="addressbook-field"][data-address="${address}"]`).each(function () {
    var targetId = "#" + $(this).data("name");
    $(targetId).val($(this).val());
    $(targetId).trigger("change"); // THIS IS IMPORTANT to trigger field validation
  });
};

export const clearShipping = function () {
  $('[data-js="shipping-field"]').each(function () {
    if ($(this).is("select")) {
      $(this).prop("selectedIndex", 0);
    } else {
      $(this).val("");
    }
    $(this).trigger("change"); // THIS IS IMPORTANT to trigger field validation
  });
  if ($('[data-js="addressbook-address"]').length) {
    $('[data-js="addressbook-address"]').prop("selectedIndex", 0);
  }
};

export const checkRequired = function (selector) {
  let requiredErrors = [];
  $(selector).each(function () {
    if ($(this).attr("required") && !$(this).val()) {
      let labelText =
        $(this).attr("placeholder") ||
        $('label[for="' + $(this).attr("id") + '"]')
          .text()
          .toLowerCase()
          .replace(/ \*/g, "");
      if (labelText) {
        var prefix = null;
        if (/^BILL/.test($(this).attr("id"))) {
          prefix = "Billing ";
        }
        if (/^SHIP/.test($(this).attr("id"))) {
          prefix = "Shipping ";
        }
        requiredErrors.push(prefix + labelText);
      }
    }
  });
  return requiredErrors;
};

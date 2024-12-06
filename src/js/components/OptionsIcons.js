const renderColorsIcon = (product) => {
  if (product.colorsAvailable) {
    return `
    <div class="w-100">
      <a
        onClick="productClick(event, window.pageItemsObject['${product.itemGroupId}'])"
        class="search-product-link rec-product-link"
        href="${product.link}"
      >
        <img src="/assets/images/colorwheel2.png" alt="Multiple Colors Available">
        ${product.colorsAvailable} colors available
      </a>
    </div>
  `;
  } else {
    return "";
  }
};

const renderStylesIcon = (product) => {
  if (product.stylesAvailable) {
    return `
  <div class="w-100">
    <a
      onClick="productClick(event, window.pageItemsObject['${product.itemGroupId}'])"
      class="search-product-link rec-product-link"
      href="${product.link}"
    >
      <img src="/assets/images/option_square.png" alt="Multiple Styles Available">
      ${product.stylesAvailable} styles available
    </a>
  </div>
  `;
  } else {
    return "";
  }
};

export const renderOptionsIcons = (product) => {
  if (product.stylesAvailable || product.stylesAvailable) {
    return `<div class="options-available text-center">
    ${renderColorsIcon(product)}
    ${renderStylesIcon(product)}
  </div>`;
  } else {
    return "";
  }
};

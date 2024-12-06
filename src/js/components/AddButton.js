export const renderAddButton = (product) => {
  if (product.needsConfiguration) {
    return `
      <a
        onClick="productClick(event, window.pageItemsObject['${product.itemGroupId}'])"
        class="search-product-link rec-product-link"
        data-skuid="${product.itemGroupId}"
        href="${product.link}"
      >
        ADD <span class="d-none d-xl-inline-block">TO CART</span>
      </a>
    `;
  } else {
    return `
      <a
        class="rec-add-to-cart"
        data-skuid="${product.itemGroupId}"
        href="${product.addToCartLink}"
        onClick="directAdd('${product.itemGroupId}');return false;"
      >
        ADD <span class="d-none d-xl-inline-block">TO CART</span>
      </a>
    `;
  }
};

export const renderRating = (product) => {
  if (product.rating && !isNaN(product.rating) && parseFloat(product.rating) >= 4) {
    return `
      <div class="rating d-flex justify-content-center">
        <div class="rating-stars">
          <a
            onClick="productClick(event, window.pageItemsObject['${product.itemGroupId}'])"
            class="search-product-link rec-product-link"
            href="${product.link}"
            data-detail-item="${product.itemGroupId}"
          >
            <img
              src="/assets/images/stars/${product.rating.toFixed(1)}.png"
              alt="Product rating: ${product.rating.toFixed(1)}"
            />
          </a>
        </div>
      </div>
    `;
  } else {
    return "";
  }
};

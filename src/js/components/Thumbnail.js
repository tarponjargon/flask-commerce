import { renderAddButton } from "./AddButton";
import { renderBadge } from "./Badge";
import { renderOptionsIcons } from "./OptionsIcons";
import { renderPrice } from "./Price";
import { renderRating } from "./Rating";

export const renderThumbnail = (product, actionId) => {
  return `
    <li
      class="product--container text-center"
      data-id="${product.itemGroupId}"
      data-full-id="${product.id}"
      data-name="${product.title}"
      data-price="${product.price}"
      data-url="${product.link}"
      data-actionid="${actionId}"
      data-rec-token="${product.recToken}"
    >
    <div class="badge-wrapper">
      ${renderBadge(product)}
    </div>
    <a
      onClick="productClick(event, window.pageItemsObject['${product.itemGroupId}'])"
      class="search-product-link rec-product-link"
      href="${product.link}"
      data-skuid="${product.itemGroupId}"
    >
      <div class="product__image-container">
        <img
          class="product__image img-fluid"
          src="/assets/images/loading-dots.gif"
          data-lazy="${product.imageLink}"
          width="337"
          height="337"
          alt="${product.title}"
          onerror="imageError(this)"
        >
      </div>
    </a>
    <div class="product__data">
      <div class="product__name">
        <a
          onClick="productClick(event, window.pageItemsObject['${product.itemGroupId}'])"
          class="search-product-link"
          href="${product.link}"
          data-detail-item="${product.itemGroupId}"
        >${product.title}</a>
      </div>
      <div class="product__price">
        ${renderPrice(product)}
      </div>
      ${renderOptionsIcons(product)}
      ${renderRating(product)}
      <div class="product__links">
        <a
          onClick="productClick(event, window.pageItemsObject['${product.itemGroupId}'])"
          class="search-product-link"
          href="${product.link}"
          data-detail-item="${product.itemGroupId}"
        >(${product.itemGroupId})</a>
        |
       ${renderAddButton(product)}
      </div>
    </div>
  </li>
  `;
};

export const renderSimpleThumbnail = (product, actionId) => {
  return `
    <li
      class="popcart-related-item"
      data-id="${product.itemGroupId}"
      data-full-id="${product.id}"
      data-name="${product.title}"
      data-price="${product.price}"
      data-url="${product.link}"
      data-actionid="${actionId}"
      data-rec-token="${product.recToken}"
    >
      <a
        class="search-product-link certona_product_link"
        onclick="closeCart();productClick(event, window.pageItemsObject['${product.itemGroupId}']);"
        href="${product.link}"
        data-detail-item="${product.itemGroupId}"
      >
        <img
          class="product-thumb img-fluid"
          src="${product.imageLink}"
          alt="${product.title}"
          onerror="imageError(this)"
          width="230"
          height="230"
        >
      </a>
      ${renderRating(product)}
      <div class="product-name">
        <a
          onclick="closeCart();productClick(event, window.pageItemsObject['${
            product.itemGroupId
          }']);"
          class="search-product-link certona_product_link"
          href="${product.link}"
          data-detail-item="${product.itemGroupId}"
        >
          ${product.title}
        </a>
      </div>
      <div class="product__price">
        ${renderPrice(product)}
      </div>
    </li>
  `;
};

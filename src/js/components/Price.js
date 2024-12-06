import { formatPrice } from "../services/Utils";

export const renderPrice = (product) => {
  if (product.salePrice) {
    return `
      <span class="old">${formatPrice(product.price)}</span>
      <span class="new">${formatPrice(product.salePrice)}</span>
    `;
  } else {
    return `${formatPrice(product.price)}`;
  }
};

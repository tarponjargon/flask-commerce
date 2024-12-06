export const renderBadge = (product) => {
  // if (product.originalPrice && product.isSale) {
  //   return `<div class="badges badge-sale"></div>`;
  // }
  if (product.isClearance) {
    return `<div class="badges badge-clearance" role="img" aria-label="Clearance"></div>`;
  } else if (product.isNew) {
    return `<div class="badges badge-new" role="img" aria-label="New"></div>`;
  } else if (product.isPersonalized) {
    return `<div class="badges badge-personalized" role="img" aria-label="Personalized"></div>`;
  } else {
    return "";
  }
};

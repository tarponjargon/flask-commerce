export const trackAutoSuggest = function (mutationsList, observer) {
  let autoSuggestEl = undefined;

  for (const mutation of mutationsList) {
    if (
      mutation.type === "childList" &&
      mutation.target.tagName === "DIV" &&
      mutation.target.querySelector(".ss__results__result")
    ) {
      autoSuggestEl = mutation.target;
      break;
    }
  }
  if (autoSuggestEl) handleElements(autoSuggestEl);
};

const handleElements = function (autoSuggestEl) {
  const results = autoSuggestEl.querySelectorAll(".ss__results__result");
  const impressions = [];
  results.forEach((el, index) => {
    const impressionObj = updateAutoSuggest(el, index);
    impressions.push(impressionObj);
  });
  if (impressions.length) {
    window.dataLayer.push({
      event: "autoSuggestImpressions",
      ecommerce: {
        impressions: impressions,
      },
    });
  }
};

const updateAutoSuggest = function (autoSuggestItemEl, index) {
  const titleAnchor = autoSuggestItemEl.querySelector(".ss__result__details__title a");
  if (!titleAnchor) return false;
  const href = titleAnchor.getAttribute("href");
  let skuid = href.substring(1);
  skuid = skuid.replace(".html", "");

  // get price
  const priceEl = autoSuggestItemEl.querySelector(".ss__result__price");
  if (!priceEl) return false;
  const price = priceEl.innerText.replace(/[^0-9.]/g, "");

  const productObject = {
    id: skuid,
    name: titleAnchor.innerText,
    price: !isNaN(price) ? parseFloat(price) : undefined,
    url: `/${skuid}.html`,
    list: "Site Search",
    listId: "Auto-Suggest",
    index: index,
  };

  window.pageItemsObject = window.pageItemsObject || {};
  if (!window.pageItemsObject.hasOwnProperty(skuid)) {
    window.pageItemsObject[skuid] = productObject;
  }

  autoSuggestItemEl.querySelectorAll("a").forEach((el) => {
    el.setAttribute("onClick", `productClick(event, '${skuid}')`);
  });

  return productObject;
};

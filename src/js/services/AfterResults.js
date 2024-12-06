import { getBodyData, abbrevString, waitForSelector } from "../services/Utils";

export function ssAfterResults(paginationHash) {
  waitForSelector("#results-container h1.category-caption").then(() => {
    const ssAfterLoadEvent = new CustomEvent("ssAfterLoad", {
      bubbles: true,
      detail: {
        totalResults:
          paginationHash && paginationHash.totalResults ? paginationHash.totalResults : 0,
      },
    });
    document.dispatchEvent(ssAfterLoadEvent);
    window.dataLayer.push({
      event: "afterResultsShown",
      totalResults: paginationHash && paginationHash.totalResults ? paginationHash.totalResults : 0,
    });

    const customCanonical = getBodyData("data-custom-canonical");
    const defaultCanonical =
      window.location.origin + window.location.pathname.toLowerCase() + "?perpage=499";
    const viewAllUrl = customCanonical ? customCanonical + "?perpage=499" : defaultCanonical;

    var makeLinkUrl = function (url) {
      var customCanonical = getBodyData("data-custom-canonical");
      var newUrl = customCanonical ? customCanonical : url; // custom canonical will always take precedence
      newUrl = newUrl.split("#")[0];
      newUrl = newUrl.split("?")[0];
      newUrl = newUrl.substr(-1) === "/" ? newUrl.slice(0, -1) : newUrl;
      var regex = /[&|\?]page=(\d+)/i;
      var match = url.match(regex); // note I'm matching against the incoming ("raw") url to find page= param
      if (match && match.length > 1) {
        newUrl += "?page=" + match[1];
      }
      return newUrl;
    };

    // make the view all button search-enging friendly
    const viewAllBtns = document.querySelectorAll('[data-js="view-all-btn"]');
    if (viewAllBtns.length) {
      viewAllBtns.forEach((viewAllBtn) => {
        if (!viewAllBtn.hasListener) {
          let params = new URLSearchParams(window.location.search);
          params.delete("page");
          params.delete("perpage");
          params.append("perpage", 499);
          const url =
            window.location.origin +
            window.location.pathname +
            "?" +
            params.toString() +
            window.location.hash;
          viewAllBtn.hasListener = true;
          viewAllBtn.setAttribute("href", url);
        }
      });
    }
    // same as above but returns to pagination
    const viewLessBtns = document.querySelectorAll('[data-js="view-less-btn"]');
    if (viewLessBtns.length) {
      viewLessBtns.forEach((viewLessBtn) => {
        if (!viewLessBtn.hasListener) {
          let params = new URLSearchParams(window.location.search);
          params.delete("page");
          params.delete("perpage");
          const url =
            window.location.origin +
            window.location.pathname +
            "?" +
            params.toString() +
            window.location.hash;
          viewLessBtn.setAttribute("href", url);
          viewLessBtn.hasListener = true;
        }
      });
    }

    // inject category intro
    const $catIntroTemplate = $("#category-intro-template");
    if ($catIntroTemplate.length) {
      const catIntro = $catIntroTemplate.html();
      if (catIntro && catIntro.length) {
        const catIntroText = catIntro.replace(/<[^>]*>/g, "").trim();
        $("#results-container h1.category-caption")
          .parent()
          .removeClass("d-flex align-items-center");
        if (!$('[data-js="catintro"]').length) {
          if ($(window).width() > 1024 && catIntroText.length < 300) {
            $(`
              <div data-js="catintro">
              <p>${catIntro}</p>
              </div>
            `).insertAfter("h1.category-caption");
          } else {
            $(`
            <div class="expandable-box mb-3" data-js="catintro">
            <input type="checkbox" id="expanded">
            <p>${catIntro}</p>
            <label for="expanded" role="button"><span id="read-more">read more</span><span id="read-less">read less</span></label>
            </div>
          `).insertAfter("h1.category-caption");
          }
        }
      }
    }

    // handle updating of canonical and prev, next pagination tags and meta tags when SS updates
    // only do so if there are no user-defined filters

    // if on our default server-side category page, do not continue
    if (/page_[0-9]/.test(window.location.href)) return false;

    const baseHref = window.location.origin + window.location.pathname.toLowerCase();
    $('meta[content="noindex, nofollow"]').remove();

    if (paginationHash && paginationHash.page && paginationHash.page > 1) {
      document.title = _fcapp.defaultTitle + " - Page " + paginationHash.page;
    }

    // handle updating of canonical and preev, next pagination meta tags when SS updates

    // this will happen when the link gets indexed but the category has shrunk so that
    // paginated page no longer has produicts on it.  Ricky wants me to canonicalize to root category
    if (
      paginationHash &&
      paginationHash.page &&
      paginationHash.page > 1 &&
      paginationHash.page > paginationHash.totalPages
    ) {
      if ($('link[rel="next"]').length) {
        $('link[rel="next"]').remove();
      }
      if ($('link[rel="prev"]').length) {
        $('link[rel="prev"]').remove();
      }

      return false;
    }

    // if no page data, just return
    if (!paginationHash || !paginationHash.page) {
      return false;
    }

    // "prev" link
    if (paginationHash.page > 1) {
      const linkUrl = makeLinkUrl(`${baseHref}?page=${paginationHash.page - 1}`);

      if ($('link[rel="prev"]').length) {
        $('link[rel="prev"]').attr("href", linkUrl.toLowerCase());
      } else {
        $("<link>", {
          rel: "prev",
          href: linkUrl.toLowerCase(),
        }).insertAfter($('link[rel="canonical"]'));
      }
    } else {
      if ($('link[rel="prev"]').length) {
        $('link[rel="prev"]').remove();
      }
    }

    // "next" link
    if (paginationHash.page < paginationHash.totalPages) {
      const linkUrl = makeLinkUrl(`${baseHref}?page=${paginationHash.page + 1}`);

      if ($('link[rel="next"]').length) {
        $('link[rel="next"]').attr("href", linkUrl.toLowerCase());
      } else {
        $("<link>", {
          rel: "next",
          href: linkUrl.toLowerCase(),
        }).insertAfter($('link[rel="canonical"]'));
      }
    } else {
      if ($('link[rel="next"]').length) {
        $('link[rel="next"]').remove();
      }
    }
    createRichSnippet();

    // add gifts by price
    if (window.location.pathname === "/gifts") {
      waitForSelector('.treeview.search-filters [href="/gifts/occasion"]').then((el) => {
        if (!document.querySelector('.treeview.search-filters [data-gbp="1"]')) {
          const addGiftsByPriceHTML = `
        <li class="my-2 mx-2" data-level="0" data-gbp="1"><a class="blue-link" href="/gifts">Gifts By Price</a></li>
        <li class="my-2 mx-2" data-level="1" data-gbp="1"><a class="blue-link" href="/gifts#/filter:price:0:30">Under $30</a></li>
        <li class="my-2 mx-2" data-level="1" data-gbp="1"><a class="blue-link" href="/gifts#/filter:price:25:50">Under $50</a></li>
        <li class="my-2 mx-2" data-level="1" data-gbp="1"><a class="blue-link" href="/gifts#/filter:price:50:75">Under $75</a></li>
        <li class="my-2 mx-2" data-level="1" data-gbp="1"><a class="blue-link" href="/gifts#/filter:price:75:100">Under $100</a></li>
      `;
          const targetEl = el.parentNode;
          targetEl.insertAdjacentHTML("beforebegin", addGiftsByPriceHTML);
        }
      });
    }
  }); //end waitForSelector
} // end function export

const createRichSnippet = () => {
  // delete any prior rich snippet
  const priorRichSnippet = document.getElementById("pdp-rich-snippet");
  if (priorRichSnippet) {
    priorRichSnippet.remove();
  }

  const results = document.querySelectorAll("#product-results [data-id]");
  if (!results.length) return;
  const snippet = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    itemListElement: [],
  };
  results.forEach((result) => {
    const price = result.getAttribute("data-price");
    const pos = result.getAttribute("data-position");
    let url = result.querySelector(".search-product-link[href]")?.getAttribute("href") || "";
    if (url && !url.startsWith("http")) {
      url = window.location.origin + url;
    }
    const item = {
      "@type": "ListItem",
      position: !isNaN(pos) ? parseInt(pos) : 0,
      item: {
        "@type": "Product",
        name: result.querySelector(".product-title")?.textContent,
        image: [
          result
            .querySelector(".product-image [data-img]")
            ?.getAttribute("data-img")
            ?.replace("/small/", "/large/"),
        ],
        offers: {
          "@type": "Offer",
          price: !isNaN(price) ? parseFloat(parseFloat(price).toFixed(2)) : price,
          priceCurrency: "USD",
        },
        url: url,
      },
    };
    const rating = result.querySelector("[data-rating]")?.getAttribute("data-rating");
    const reviews = result.querySelector("[data-reviews]")?.getAttribute("data-reviews");
    if (rating && !isNaN(rating) && reviews && !isNaN(reviews)) {
      item.item.aggregateRating = {
        "@type": "AggregateRating",
        ratingValue: parseFloat(parseFloat(rating).toFixed(1)),
        reviewCount: parseInt(reviews),
      };
    }
    snippet.itemListElement.push(item);
  });

  const script = document.createElement("script");
  script.id = "pdp-rich-snippet";
  script.type = "application/ld+json";
  script.textContent = JSON.stringify(snippet);
  document.head.appendChild(script);
};

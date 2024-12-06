import { renderThumbnail, renderSimpleThumbnail } from "../components/Thumbnail";
import { createId, getBodyData, loadCarousel, removeMask, safeString } from "./Utils";

export default class Recommendations {
  constructor() {
    this.container = document.querySelector("#recs-container");
  }

  init = async () => {
    document.addEventListener("inlinePopcart", this.renderPopCartRecs, false);
    const recsEl = document.querySelector("#recs-container[data-recs]");
    if (!recsEl) return false;
    const recsData = recsEl.getAttribute("data-recs");
    const recsRes = await fetch("/api/product/recommendations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: recsData,
    });
    const recs = await recsRes.json();
    if (!recs || !recs.length) return false;
    window.kppRecs = recs; // adding to window because other processes look for this variable globally
    this.renderRecs(recs);
  };

  getHeading = (mySet) => {
    const idArr = mySet.id ? mySet.id.split("|") : [];
    const id = idArr.length >= 1 ? idArr[0].trim() : "";
    const heading = idArr.length >= 2 ? idArr[1].trim() : "";
    const link = idArr.length >= 3 ? idArr[2].trim() : "";

    return { id: safeString(id), heading: safeString(heading), link: safeString(link) };
  };

  setPageItemsObject = (mySet) => {
    window.pageItemsObject = window.pageItemsObject || {};
    const myPage = getBodyData("data-view");
    const head = this.getHeading(mySet);
    const recsProducts = [];
    mySet.recommendations.forEach((product, index) => {
      let myCats = new Array(
        product.category1,
        product.category2,
        product.category3,
        product.category4
      );
      // check if the origin in the url specified in product.link matches the origin of the current page, if not replace the origin in product
      // this allows product recommendations with a full path to production to be used in other environments.  otherwise, clicks on recs will take the user to production
      let myurl = product.link;
      if (product.link && product.link.indexOf("http") === 0) {
        const url = new URL(product.link);
        if (url.origin !== window.location.origin) {
          myurl = product.link.replace(url.origin, window.location.origin);
        }
      }
      myCats = myCats.filter((n) => n);
      const cats = myCats.join(" > ");
      window.pageItemsObject[product.itemGroupId] = {
        name: product.title,
        id: product.itemGroupId,
        price: product.salePrice ? product.salePrice : product.price,
        category: cats,
        breadcrumb: cats,
        list: "Recommendations",
        listId: head.id,
        position: index + 1,
        url: myurl,
      };
      recsProducts.push(window.pageItemsObject[product.itemGroupId]);
    });
    window.dataLayer.push({
      event: "certonaImpressions",
      ecommerce: {
        impressions: recsProducts,
      },
    });
  };

  renderCategoryLink = (link, heading) => {
    if (!link) return "";
    return `
      <span class="separator">|</span>
      <a class="view-all blue-link mt-2" href="${link}" data-test="hp-item">
        <span class="view-all-text">Show All ${heading}</span>
        <i class="fa fa-caret-right"></i>
      </a>
    `;
  };

  renderRecs = (data) => {
    const carouselProms = [];
    kppRecs.forEach((mySet, index) => {
      if (!mySet.recommendations) return false;
      const recs = mySet.recommendations;
      this.setPageItemsObject(mySet);
      const actionId = mySet.actionId;
      const rowId = createId();
      const recsDiv = document.createElement("div");
      recsDiv.style = "visibility: hidden;";
      recsDiv.setAttribute("id", `wrapper-${rowId}`);
      recsDiv.setAttribute("class", `carousel-wrapper`);
      const head = this.getHeading(mySet);
      let recsHTML = `
        <div class="fullwidth__holder">
          <div class="product__list--header">
            <h2 class="product__list--title pb-2 d-inline">${head.heading}</h2>
            ${this.renderCategoryLink(head.link, head.heading)}
          </div>
          <ul class="product__list" id="products-${rowId}">
            ${recs.map((p) => renderThumbnail(p, actionId)).join("")}
          </ul>
        </div>
      `;
      recsDiv.innerHTML = recsHTML;
      this.container.append(recsDiv);
      carouselProms.push(() => loadCarousel(`#products-${rowId}`));
    });
    Promise.all(carouselProms.map((f) => f()))
      .then(() => {
        window.dataLayer.push({
          event: "recsLoaded",
          monetateRecs: kppRecs,
        });
        Array.from(this.container.querySelectorAll(".carousel-wrapper")).map((i) =>
          removeMask(`#${i.getAttribute("id")}`)
        );
      })
      .catch((e) => {
        console.error("could not load carousel for monetate", e);
      });
  };

  renderPopCartRecs = async () => {
    const recsEl = document.querySelector("#popcart-recs-container[data-recs]");
    if (!recsEl) return false;
    const recsData = recsEl.getAttribute("data-recs");
    const recsRes = await fetch("/api/product/recommendations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: recsData,
    });
    const myRecs = await recsRes.json();
    if (!myRecs || !myRecs.length) return false;
    window.popCartRecs = myRecs; // adding to window because other processes look for this variable globally

    if (!Array.isArray(popCartRecs)) return false;
    const mySet = popCartRecs[0];
    this.setPageItemsObject(mySet);
    if (!mySet.recommendations) return false;
    const recs = mySet.recommendations;
    const rowId = createId();
    const actionId = mySet.actionId;
    const recsDiv = document.createElement("div");
    recsDiv.style = "visibility: hidden;";
    recsDiv.setAttribute("class", `popcart-wrapper`);
    recsDiv.setAttribute("id", `wrapper-${rowId}`);
    const head = this.getHeading(mySet);
    let recsHTML = `
            <div class="related__products vertical-products">
              <span class="products-list-title">${head.heading}</span>
              <ul id="popcart-${rowId}-products">
                ${recs.map((p) => renderSimpleThumbnail(p, actionId)).join("")}
                </ul>
            </div>
          `;
    recsDiv.innerHTML = recsHTML;
    document.getElementById("popcart-recs-container").append(recsDiv);
    const sel = `#popcart-${rowId}-products`;
    $(sel).on("init", (event) => {
      setTimeout(() => {
        $(sel).slick("refresh");
        removeMask(`#wrapper-${rowId}`);
        window.dataLayer.push({
          event: "popCartRecsLoaded",
          monetatePopCartRecs: popCartRecs,
        });
      }, 100);
    });
    const popCartSlick = `${sel}:not(.slick-initialized)`;
    $(popCartSlick).slick({
      infinite: true,
      slidesToShow: 3,
      slidesToScroll: 3,
    });
  };
}

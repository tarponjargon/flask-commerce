import domain from "../support/baseDomain.js";
import Cookies from "js-cookie";
const url = Cypress.env("baseUrl");
let user;

describe("productlisting", () => {
  beforeEach(function () {
    cy.fixture("user.json").then((u) => {
      user = u;
    });
    // this will either set or unset the failover cookie based on the environment
    Cookies.set(Cypress.env("failoverCookieName"), Cypress.env("failoverCookieVal"), {
      path: "/",
      expires: Cypress.env("failoverCookieExpiry"),
    });
  });

  it(`Test for failover ${url}`, function () {
    cy.visit(`${url}`);
    cy.get("body")
      .invoke("attr", "data-is-fo")
      .then((value) => {
        cy.log("data-is-fo?", value);
        expect(parseInt(value)).to.eq(Cypress.env("isFailover"));
      });
  });

  it(`Test category`, function () {
    cy.setCookie("capturewin", "capture", { secure: true, domain }); // make sure capture window doesn't appear
    cy.visit(`${url}`);

    // click on 2nd link in nav
    cy.get("a.top-category-link").eq(1).click({ force: true });

    // should have products on the page
    cy.get(".product-wrapper [data-id]").should("have.length.above", 10);

    cy.get(".page-spinner").should("not.be.visible");

    // should not have lazyload dots
    cy.get('[src="/assets/images/loading-dots.gif"]').should("have.length.of", 0);

    // should have facets
    cy.get(".search-filters .list-group-item").should("have.length.above", 8);

    // clicked facet should change the page
    cy.get(".search-filters .list-group-item").first().click({ force: true });
    cy.url().should("contain", "filter");

    // this is a way to "wait" to make sure the result set updated
    // cy.get('.list-group-item[title="View All"]').should("exist");

    cy.get("a.search-product-link")
      .first()
      .invoke("attr", "href")
      .then((href) => {
        const path = /([^/]+)$/;
        const match = href.match(path);
        cy.get("a.search-product-link").first().click({ force: true });
        cy.url().should("contain", match[1]);
      });
  });

  it(`Test search results`, function () {
    cy.setCookie("capturewin", "capture", { secure: true, domain }); // make sure capture window doesn't appear
    cy.visit(`${url}`);
    cy.get('.header_search input[name="q"]').type(user.searchTerm);
    cy.get(".header_search .submit-search-button").click({ force: true });

    // unbxd should have products on the page
    cy.get(".product-wrapper [data-id]").should("have.length.above", 10);

    cy.get(".page-spinner").should("not.be.visible");

    // should have facets
    cy.get(".search-filters .list-group-item").should("have.length.above", 5);

    // clicked facet should change the page
    cy.get(".search-filters .list-group-item").first().click({ force: true });
    cy.url().should("contain", "filter");

    // this is a way to "wait" to make sure the result set updated
    // cy.get('.list-group-item[title="View All"]').should("exist");

    cy.get("a.search-product-link")
      .first()
      .invoke("attr", "href")
      .then((href) => {
        const path = /([^/]+)$/;
        const match = href.match(path);
        cy.get("a.search-product-link").first().click({ force: true });
        cy.url().should("contain", match[1]);
      });
  });

  it(`Test indexed items`, function () {
    if (
      Cypress.env("isFailover") ||
      Cypress.env("baseUrl").includes("local") ||
      Cypress.env("baseUrl").includes("thewhiteroom")
    ) {
      cy.log("Skipping test for non-production");
      return;
    }
    const linecounterUrl = url.replace("https://", "https://misc:misc@");
    cy.request(`${linecounterUrl}/api/search_count`).then((response) => {
      const json = typeof response.body === "object" ? response.body : JSON.parse(response.body);
      const count = parseInt(json.lines);
      cy.log("linecounter count", count);
      cy.visit(`${url}/find?q=*`);
      cy.get("#facets-items-found")
        .invoke("text")
        .then((resultCount) => {
          const found = parseInt(resultCount.replace(/[^0-9]/g, ""));
          expect(found).to.be.closeTo(count, 20);
        });
    });
  });
});

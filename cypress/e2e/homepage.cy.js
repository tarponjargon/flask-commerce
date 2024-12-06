import { log } from "console";
import domain from "../support/baseDomain.js";
import Cookies from "js-cookie";
const url = Cypress.env("baseUrl");

describe("home page", () => {
  beforeEach(function () {
    cy.fixture("user.json").as("user");
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

  it(`Test homepage of ${url}`, function () {
    cy.setCookie("capturewin", "capture", { secure: true, domain }); // make sure capture window doesn't appear
    cy.visit(`${url}`);

    // visiible homepage banners image load
    cy.get('[data-test="hp-item"] img[src]').each((img) => {
      cy.wrap(img)
        .should("exist")
        .and(($img) => {
          // "naturalWidth" and "naturalHeight" are set when the image load
          expect($img[0].naturalWidth).to.be.greaterThan(0);
        });
    });

    // lazy loaded homepage banners
    cy.get('[data-test="hp-item"] img[data-lazy]').each((img) => {
      cy.wrap(img)
        .invoke("attr", "data-lazy")
        .then((href) => {
          console.log("href", href);
          if (href) {
            cy.request(href).should((response) => {
              console.log("LAZY", img);
              expect(response.status).to.eq(200);
            });
          }
        });
    });
    // cy.get('[data-test="hp-item"] img[data-lazy]').each((img) => {
    //   cy.wrap(img).invoke("attr", "src", function () {
    //     console.log("LAZY", $(this).attr("data-lazy"));
    //     return $(this).attr("data-lazy");
    //   });
    //   console.log("LAZY", img.attr("src"));
    //   cy.wrap(img)
    //     .should("exist")
    //     .and(($img) => {
    //       // "naturalWidth" and "naturalHeight" are set when the image load
    //       console.log("HEIGHT", $img[0].naturalWidth, $img[0].naturalHeight);
    //       expect($img[0].naturalWidth).to.be.greaterThan(0);
    //     });
    // });

    // homepage banners do not end up in 404 or noresults page
    cy.get('[data-test="hp-item"]').each((a) => {
      cy.wrap(a)
        .invoke("attr", "href")
        .then((href) => {
          cy.request(href).should((response) => {
            expect(response.status).to.eq(200);
            if (response.redirectedToUrl) {
              expect(response.redirectedToUrl).to.not.contain("noresults");
            }
          });
        });
    });

    // header banners do not end up in 404 or noresults page
    cy.get(".header-banner a").each((a) => {
      cy.wrap(a)
        .invoke("attr", "href")
        .then((href) => {
          cy.request(href).should((response) => {
            expect(response.status).to.eq(200);
            if (response.redirectedToUrl) {
              expect(response.redirectedToUrl).to.not.contain("noresults");
            }
          });
        });
    });

    cy.get('.category_boxes [data-test="hp-item"]').should("have.length.of", 6);

    cy.get('.small_boxes [data-test="hp-item"]').should("have.length.of", 12);

    cy.get("body").click({ force: true });
    // cy.get("section.bg-primary").scrollTo("top");
    //cy.get("#recs-container .fullwidth__holder").should("be.visible");
  });

  it(`Test mobile navigation`, function () {
    cy.viewport(550, 750);
    cy.visit(url);
    cy.get(".header_mobile .mobile_menu").first().click({ force: true });
    cy.get(".mobile_categories .top-cateogry-link-new").first().click();
    cy.get(
      '.mobile_categories > .menu-element > .panel > .panel-collapse > .panel > .sub-category > [href^="/new"]'
    )
      .first()
      .should("be.visible")
      .click();
    cy.url().should("contain", "/new");
  });
});

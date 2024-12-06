import domain from "../support/baseDomain.js";
import Cookies from "js-cookie";
const url = Cypress.env("baseUrl");

describe("product page", () => {
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

  it(`Test optioned detail page`, () => {
    cy.setCookie("capturewin", "capture", { secure: true, domain }); // make sure capture window doesn't appear
    cy.request(`${url}/api/test/testoptioned`).then((response) => {
      const json = typeof response.body === "object" ? response.body : JSON.parse(response.body);
      const skuid = json.skuid;
      cy.log(`got test SKU ${skuid}`);
      cy.visit(`${url}/${skuid}.html`);

      // select options and add to cart
      cy.selectAllMatrixOptions(skuid, `[data-js="order-form"][data-add-item="${skuid}"]`).then(
        (fullSkuid) => {
          cy.get(`#add-to-cart-btn`).click({ force: true });
          cy.get("#cart-modal .modal-body").should("contain", skuid);

          // make sure product add event fired
          cy.checkItemAddedGTM(fullSkuid);

          // check window "store"
          cy.checkCartItemsObject(fullSkuid);

          cy.get('#cart-modal .modal-body a[href="/cart"]').click({ force: true });
          cy.get(".lineitems").should("contain", fullSkuid);
        }
      );
    });
  });

  it(`Test add missing options ${url}`, () => {
    cy.setCookie("capturewin", "capture", { secure: true, domain }); // make sure capture window doesn't appear
    cy.request(`${url}/api/test/testoptioned`).then((response) => {
      const json = typeof response.body === "object" ? response.body : JSON.parse(response.body);
      const skuid = json.skuid;
      cy.log(`got test SKU ${skuid}`);
      cy.visit(`${url}/add?item=${skuid}`);

      // select options and add to cart
      cy.selectAllOptions(skuid, `[data-js="order-form"][data-add-item="${skuid}"]`).then(
        (fullSkuid) => {
          cy.get(`[data-js="order-form"][data-add-item="${skuid}"] [data-js="add-button"]`).click({
            force: true,
          });
          cy.url().should("contain", "/cart");
          cy.get(".lineitems").should("contain", fullSkuid);
        }
      );
    });
  });

  it(`Test optioned quickorder page`, () => {
    cy.setCookie("capturewin", "capture", { secure: true, domain }); // make sure capture window doesn't appear
    cy.request(`${url}/api/test/testoptioned`).then((response) => {
      const json = typeof response.body === "object" ? response.body : JSON.parse(response.body);
      const skuid = json.skuid;
      cy.log(`got test SKU ${skuid}`);
      cy.visit(`${url}/quickorder`);

      cy.get('[data-js="quick-order-form"] [data-js="quick-order-field"]').type(skuid);
      cy.get("#quick-order-add-button").click({ force: true });

      // select options and add to cart
      cy.selectAllOptions(skuid, `[data-js="order-form"][data-add-item="${skuid}"]`).then(
        (fullSkuid) => {
          cy.get(`[data-js="order-form"][data-add-item="${skuid}"] [data-js="add-button"]`).click({
            force: true,
          });
          cy.get(`[data-lineitem-skuid="${fullSkuid}"] [data-js="quantity-field"]`)
            .invoke("val")
            .should("equal", "1");
        }
      );

      // do same again and make sure qty is incremented
      cy.intercept("GET", "/quick-add?*").as("addReq");
      cy.get('[data-js="quick-order-form"] [data-js="quick-order-field"]').type(skuid);
      cy.get("#quick-order-add-button").click({ force: true });
      cy.selectAllOptions(skuid, `[data-js="order-form"][data-add-item="${skuid}"]`).then(
        (fullSkuid) => {
          cy.get(`[data-js="order-form"][data-add-item="${skuid}"]`).submit();
          cy.wait("@addReq").then(() => {
            cy.get(`[data-lineitem-skuid="${fullSkuid}"] [data-js="quantity-field"]`)
              .invoke("val")
              .should("equal", "2");
          });
        }
      );
    });
  });

  it(`Test unoptioned detail page`, () => {
    cy.request(`${url}/forgetme`).then(() => {
      cy.clearCookies();
      // for some reason session is carried over from prior test
      cy.setCookie("capturewin", "capture", { secure: true, domain }); // make sure capture window doesn't appear
      cy.request(`${url}/api/test/nonoptioned`).then((response) => {
        const json = typeof response.body === "object" ? response.body : JSON.parse(response.body);
        const skuid = json.skuid;
        cy.log(`got test SKU ${skuid}`);
        cy.visit(`${url}/${skuid}.html`);

        // /// test that certona features loaded
        // cy.get("#recs-container .product__list").should("be.visible");
        // cy.get("#recs-container .product__list .product--container").should("have.length.of", 4);

        // cy.get("#pla_rr .fullwidth__holder").should("be.visible");
        // cy.get("#pla_rr .fullwidth__holder .product__listfive").should("have.length.of", 4);

        // yotpo review widget loads
        // cy.get(".yotpo-display-wrapper").should("exist");

        // add to cart
        cy.get(`#add-to-cart-btn`).click({ force: true });
        cy.get("#cart-modal .modal-body").should("contain", skuid);

        // make sure product add event fired
        cy.checkItemAddedGTM(skuid);

        // check window "store"
        cy.checkCartItemsObject(skuid);

        cy.get('#cart-modal .modal-body a[href="/cart"]').click({ force: true });
        cy.get(".lineitems").should("contain", skuid);
      });
    });
  });

  it(`Test unoptioned quickorder page`, () => {
    cy.request(`${url}/forgetme`).then(() => {
      // for some reason session is carried over from prior test
      cy.clearCookies();
      cy.setCookie("capturewin", "capture", { secure: true, domain }); // make sure capture window doesn't appear
      cy.request(`${url}/api/test/nonoptioned`).then((response) => {
        const json = typeof response.body === "object" ? response.body : JSON.parse(response.body);
        const skuid = json.skuid;
        cy.log(`got test SKU ${skuid}`);
        cy.visit(`${url}/quickorder`);

        cy.get('[data-js="quick-order-form"] [data-js="quick-order-field"]').type(skuid);
        cy.get("#quick-order-add-button").click({ force: true });
        cy.get(`[data-lineitem-skuid="${skuid}"] [data-js="quantity-field"]`)
          .invoke("val")
          .should("equal", "1");

        // quick order the same sku, make sure qty increments
        cy.get('[data-js="quick-order-form"] [data-js="quick-order-field"]').type(skuid);
        cy.intercept("GET", `/buildorder?ADDSKUIDS=${skuid}`).as("addReq");
        cy.get('[data-js="quick-order-form"]').submit();
        cy.wait("@addReq").then(() => {
          cy.get(`[data-lineitem-skuid="${skuid}"] [data-js="quantity-field"]`)
            .invoke("val")
            .should("equal", "2");
        });
      });
    });
  });

  it(`Test qty increments ${url}`, () => {
    cy.setCookie("capturewin", "capture", { secure: true, domain }); // make sure capture window doesn't appear
    cy.request(`${url}/forgetme`).then(() => {
      cy.clearCookies();
      // for some reason session is carried over from prior test
      cy.request(`${url}/api/test/nonoptioned`).then((response) => {
        const json = typeof response.body === "object" ? response.body : JSON.parse(response.body);
        const skuid = json.skuid;
        cy.log(`got test SKU ${skuid}`);
        cy.visit(`${url}/${skuid}.html`);

        // add to cart
        cy.get(`#add-to-cart-btn`).click({ force: true });
        cy.get("#cart-modal .modal-body").should("contain", skuid);
        cy.get("#cart-modal .modal-body [data-test='added-qty']").should("have.text", "1");
        cy.get("#cart-modal [data-dismiss='modal']").click({ force: true });
        cy.get("#cart-modal .modal-body").should("not.be.visible");

        // add 2 more to the cart
        cy.get(`[data-add-item="${skuid}"] [data-js="quantity"]`)
          .clear({ force: true })
          .type("2", { force: true });
        cy.get(`#add-to-cart-btn`).click({ force: true });
        cy.get("#cart-modal .modal-body").should("contain", skuid);
        cy.get("#cart-modal .modal-body [data-test='added-qty']").should("have.text", "3");
        cy.visit(`${url}/cart`);
        cy.get(`input[name="PRODUCT_${skuid}"]`).invoke("val").should("equal", "3");
      });
    });
  });

  // it(`Test optioned upcharge`, () => {
  //   cy.request(`${url}/forgetme`).then(() => {
  //     cy.clearCookies();
  //     // for some reason session is carried over from prior test
  //     cy.setCookie("capturewin", "capture", { secure: true, domain }); // make sure capture window doesn't appear
  //     cy.request(`${url}/store?action=testupcharge`).then((response) => {
  //       const json = typeof response.body === "object" ? response.body : JSON.parse(response.body);
  //       const skuid = json.skuid;
  //       cy.log(`got test SKU ${skuid}`);
  //       cy.visit(`${url}/${skuid}.html`);

  //       // select options and add to cart

  //       cy.selectAllMatrixOptions(skuid, `[data-js="order-form"][data-add-item="${skuid}"]`).then(
  //         (fullSkuid) => {
  //           cy.get('[data-js="order-form"] [data-option-selected="1"]')
  //             .invoke("attr", "data-pricechange")
  //             .then((upcharge) => {
  //               const basePrice = Cypress.$(".product-details [data-price]")
  //                 .last() // the "last" will get the sale price, if there is one
  //                 .attr("data-price");
  //               const expectedPrice = parseFloat(
  //                 parseFloat(basePrice) + parseFloat(upcharge)
  //               ).toFixed(2);
  //               const newPrice = parseFloat(
  //                 Cypress.$(".product-details [data-price]")
  //                   .last() // the "last" will get the sale price, if there is one
  //                   .text()
  //                   .replace(/[^0-9.]+/g, "")
  //               ).toFixed(2);
  //               expect(newPrice).to.equal(expectedPrice);
  //               cy.get(`#add-to-cart-btn`).click({ force: true });
  //               cy.get("#cart-modal .modal-body").should("contain", skuid);

  //               // make sure product add event fired
  //               cy.checkItemAddedGTM(fullSkuid);

  //               // check window "store"
  //               cy.checkCartItemsObject(fullSkuid);

  //               cy.get("#cart-modal .modal-body [data-price]").should("contain", expectedPrice);
  //               cy.get('#cart-modal .modal-body a[href="/cart"]').click({ force: true });
  //               cy.get(`.lineitems [data-lineitem-skuid="${fullSkuid}"]`).should("exist");
  //               cy.get(
  //                 `.lineitems [data-lineitem-skuid="${fullSkuid}"] [data-price="${expectedPrice}"]`
  //               ).should("exist");
  //             });
  //         }
  //       );
  //     });
  //   });
  // });

  // it(`Test unoptioned preorder ${url}`, () => {
  //   cy.request(`${url}/forgetme`).then(() => {
  //     // for some reason session is carried over from prior test
  //     cy.clearCookies();
  //     cy.setCookie("capturewin", "capture", { secure: true, domain }); // make sure capture window doesn't appear
  //     cy.request(`${url}/store?action=testpreorder`).then((response) => {
  //       const json = typeof response.body === "object" ? response.body : JSON.parse(response.body);
  //       if (!json.skuid) return true;
  //       const skuid = json.skuid;
  //       cy.log(`got test SKU ${skuid}`);
  //       cy.visit(`${url}/${skuid}.html`);

  //       // product name should be prefixed with PRE-ORDER
  //       cy.get(`[data-detail-skuid="${skuid}"] .product-name`).should("contain", "PRE-ORDER");
  //       cy.get("#add-to-cart-btn").should("contain", "PRE-ORDER");
  //       cy.get(`[data-detail-skuid="${skuid}"] [data-js="detail-item-availability"]`).then((el) => {
  //         const text = el.text();
  //         expect(text).to.match(/Ships: [0-9]{1,2}\/[0-9]{1,2}/);
  //       });
  //       cy.get(`#add-to-cart-btn`).click({ force: true });
  //       cy.get("#cart-modal .modal-body").should("contain", skuid);

  //       // make sure product add event fired
  //       cy.checkItemAddedGTM(skuid);

  //       // check window "store"
  //       cy.checkCartItemsObject(skuid);

  //       cy.get('#cart-modal .modal-body a[href="/cart"]').click({ force: true });
  //       cy.get(`.lineitems [data-lineitem-skuid="${skuid}"]`).should("exist");
  //       cy.get(`.lineitems [data-lineitem-skuid="${skuid}"] .product-stock-status`).then((el) => {
  //         const text = el.text();
  //         expect(text).to.match(/PRE-ORDER: Ships [0-9]{1,2}\/[0-9]{1,2}/);
  //       });
  //     });
  //   });
  // });

  // it(`Test optioned preorder detail page`, () => {
  //   cy.request(`${url}/forgetme`).then(() => {
  //     // for some reason session is carried over from prior test
  //     cy.clearCookies();
  //     cy.setCookie("capturewin", "capture", { secure: true, domain }); // make sure capture window doesn't appear
  //     cy.request(`${url}/store?action=testpreorderoptioned`).then((response) => {
  //       const json = typeof response.body === "object" ? response.body : JSON.parse(response.body);
  //       if (!json.skuid) return true;
  //       const skuid = json.skuid;
  //       cy.log(`got test SKU ${skuid}`);
  //       cy.visit(`${url}/${skuid}.html`);

  //       // product name should be prefixed with PRE-ORDER
  //       cy.get(`[data-detail-skuid="${skuid}"] .product-name`).should("contain", "PRE-ORDER");

  //       // select options and add to cart
  //       cy.selectAllMatrixOptions(skuid, `[data-js="order-form"][data-add-item="${skuid}"]`).then(
  //         (fullSkuid) => {
  //           cy.get(`[data-detail-skuid="${skuid}"] [data-js="detail-item-availability"]`).then(
  //             (el) => {
  //               const text = el.text();
  //               expect(text).to.match(/Ships [0-9]{1,2}\/[0-9]{1,2}/);
  //             }
  //           );
  //           cy.get('[data-js="order-form"] [data-option-selected="1"]').then((el) => {
  //             const text = el.text();
  //             expect(text).to.match(/Ships [0-9]{1,2}\/[0-9]{1,2}/);
  //           });
  //           cy.get(`#add-to-cart-btn`).click({ force: true });
  //           cy.get("#cart-modal .modal-body").should("contain", skuid);

  //           // make sure product add event fired
  //           cy.checkItemAddedGTM(fullSkuid);

  //           // check window "store"
  //           cy.checkCartItemsObject(fullSkuid);

  //           cy.get('#cart-modal .modal-body a[href="/cart"]').click({ force: true });
  //           cy.get(".lineitems").should("contain", fullSkuid);
  //           cy.get(`.lineitems [data-lineitem-skuid="${fullSkuid}"]`).should("exist");
  //           cy.get(`.lineitems [data-lineitem-skuid="${fullSkuid}"] .product-stock-status`).then(
  //             (el) => {
  //               const text = el.text();
  //               expect(text).to.match(/PRE-ORDER: Ships [0-9]{1,2}\/[0-9]{1,2}/);
  //             }
  //           );
  //         }
  //       );
  //     });
  //   });
  // });

  // it(`Test personalized item AND upcharge sticks on ${url}`, () => {
  //   cy.request(`${url}/forgetme`).then(() => {
  //     // for some reason session is carried over from prior test
  //     let skuid = "GC9999";
  //     cy.setCookie("capturewin", "capture", { secure: true, domain }); // make sure capture window doesn't appear
  //     cy.visit(`${url}/${skuid}.html`);
  //     cy.log(`got test SKU ${skuid}`);
  //     cy.get('[data-option-code="250"]').click({ force: true });
  //     const fullSkuid = "GC9999-250";
  //     cy.get(`#add-to-cart-btn`).click({ force: true });
  //     cy.get('#personalization-modal input[type="text"]').eq(0).type("Ned", { force: true });
  //     cy.wait(500);
  //     cy.get('#personalization-modal input[type="text"]').eq(1).type("Flanders", { force: true });
  //     cy.wait(500);
  //     cy.get('#personalization-modal input[type="text"]')
  //       .eq(2)
  //       .type("Test Line 1", { force: true });
  //     cy.wait(500);
  //     cy.get('#personalization-modal input[type="text"]')
  //       .eq(3)
  //       .type("Test Line 2", { force: true });
  //     cy.wait(500);
  //     cy.get('#personalization-modal input[type="text"]')
  //       .eq(4)
  //       .type("Test Line 3", { force: true });
  //     cy.wait(500);
  //     cy.get("#personalization-modal-submit").click({ force: true });
  //     cy.get("#cart-modal .modal-body").should("contain", skuid);
  //     cy.get('#cart-modal .modal-body a[href="/cart"]').click({ force: true });
  //     cy.get(`.lineitems [data-lineitem-skuid="${fullSkuid}"]`)
  //       .should("exist")
  //       .and("contain", "Ned")
  //       .and("contain", "Flanders")
  //       .and("contain", "Test Line 1")
  //       .and("contain", "Test Line 2")
  //       .and("contain", "Test Line 3")
  //       .and("contain", "$250.00");
  //   });
  // });

  it(`Test group ID item ${url}`, () => {
    cy.request(`${url}/forgetme`).then(() => {
      // for some reason session is carried over from prior test
      cy.clearCookies();
      cy.setCookie("capturewin", "capture", { secure: true, domain }); // make sure capture window doesn't appear
      cy.request(`${url}/api/test/testgroupid`).then((response) => {
        const json = typeof response.body === "object" ? response.body : JSON.parse(response.body);
        const skuid = json.skuid;
        cy.log(`got test SKU ${skuid}`);
        cy.visit(`${url}/${skuid}.html`);

        // get the first unoptioned GROUP_ID, extract sku from it
        cy.get('.quick-add-detail-container [data-js="quantity"]')
          .first()
          .then((el) => {
            const itemType = el.attr("id");
            if (/^OPTIONED_QUANTITY_/.test(itemType)) {
              const skuid = itemType.replace("OPTIONED_QUANTITY_", "");
              cy.selectAllOptions(
                skuid,
                `.quick-add-detail-container[data-detail-skuid="${skuid}"]`
              ).then((fullSkuid) => {
                cy.get(
                  `.quick-add-detail-container[data-detail-skuid="${skuid}"] [data-js="add-button"]`
                ).click({ force: true });
                cy.get("#cart-modal .modal-body").should("contain", skuid);

                // make sure product add event fired
                cy.checkItemAddedGTM(fullSkuid);

                // check window "store"
                cy.checkCartItemsObject(fullSkuid);

                cy.get('#cart-modal .modal-body a[href="/cart"]').click({ force: true });
                cy.get(".lineitems").should("contain", fullSkuid);
              });
            } else {
              const skuid = itemType.replace("PRODUCT_", "");
              // add to cart
              cy.get(
                `.quick-add-detail-container[data-detail-skuid="${skuid}"] [data-js="add-button"]`
              ).click({ force: true });
              cy.get("#cart-modal .modal-body").should("contain", skuid);

              // make sure product add event fired
              cy.checkItemAddedGTM(skuid);

              // check window "store"
              cy.checkCartItemsObject(skuid);

              cy.get('#cart-modal .modal-body a[href="/cart"]').click({ force: true });
              cy.get(".lineitems").should("contain", skuid);
            }
          });
      });
    });
  });
});

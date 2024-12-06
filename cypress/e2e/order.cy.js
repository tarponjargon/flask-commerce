import domain from "../support/baseDomain.js";
import Cookies from "js-cookie";
const url = Cypress.env("baseUrl");
let user;

describe("order", () => {
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
        cy.log("data-is-fo value", value);
        expect(parseInt(value)).to.eq(Cypress.env("isFailover"));
      });
  });

  it(`Test add to cart with EMSYAY ${url}`, () => {
    // hits an endpoint that returns a sku that's non optioned, non-custom (can be added right to the cart)
    cy.setCookie("capturewin", "capture", { secure: true, domain }); // make sure capture window doesn't appear
    cy.request(`${url}/api/test/nonoptioned`).then((response) => {
      // cy.log(response);
      const json = typeof response.body === "object" ? response.body : JSON.parse(response.body);
      const skuid = json.skuid;
      cy.log(`got test SKU ${skuid}`);
      cy.visit(`${url}/add?ITEM=${skuid}&COUPON_CODE=${user.coupon}`);
      cy.get('[data-js="upsell-popup"]').should("be.visible"); // test for cart popover
      cy.wait(2000);
      cy.closeModal("#smallModal");
      cy.get(".coupon-messages").should("contain", user.coupon);
      cy.get(".coupon-messages").should("contain", "has been applied");
      cy.get(".cart-orderSummary").should("contain", "Discount:");
      cy.get(".cart-orderSummary").should("contain", "-$");
    });
  });

  it(`Make sure paypal button works`, () => {
    // hits an endpoint that returns a sku that's non optioned, non-custom (can be added right to the cart)
    cy.setCookie("capturewin", "capture", { secure: true, domain }); // make sure capture window doesn't appear
    cy.request(`${url}/api/test/nonoptioned`).then((response) => {
      const json = typeof response.body === "object" ? response.body : JSON.parse(response.body);
      const skuid = json.skuid;
      cy.log(`got test SKU ${skuid}`);
      cy.visit(`${url}/add?ITEM=${skuid}`);
      //cy.get('[data-js="upsell-popup"]').should("be.visible");
      cy.wait(2000);
      cy.closeModal("#smallModal");
      cy.get(".paypal-image").should("exist").first().click({ force: true });
      cy.url().should("contain", "paypal.com");
    });
  });

  it(`Test for session losss sequence on ${url}`, () => {
    // hits an endpoint that returns a sku that's non optioned, non-custom (can be added right to the cart)
    cy.setCookie("capturewin", "capture", { secure: true, domain }); // make sure capture window doesn't appear
    cy.request(`${url}/api/test/nonoptioned`).then((response) => {
      const json = typeof response.body === "object" ? response.body : JSON.parse(response.body);
      const skuid = json.skuid;
      cy.log(`got test SKU ${skuid}`);
      cy.visit(`${url}/${skuid}.html`);
      cy.get(`[data-detail-skuid="${skuid}"] [data-js="quantity"]`).clear().type("10");
      cy.get(`[data-detail-skuid="${skuid}"] [data-js="add-button"]`).click({ force: true });
      cy.get(`#cart-modal [data-last-added="${skuid}"] .btn[href="/checkout"]`).first().click({
        force: true,
      });
      cy.url().should("contain", "/checkout");
      cy.get("#billingPromo").type("FAKEPROMO{enter}");
      // cy.get(`.o_item .o_image a[href="/${skuid}.html"]`);
    });
  });

  it(`Test order totals`, () => {
    // this test adds two items to the cart and then manually totals up each lineitem and order line value to make sure the match all checks out
    // I'm using a CO address to also test that the CO-specific surcharge is being added
    // 7/2/24 added test to check that tax > 0 and that MN surcharge is not added if order < 100 and that it is added if order > 100
    cy.request(`${url}/api/test/nonoptioned`).then((response) => {
      const json = typeof response.body === "object" ? response.body : JSON.parse(response.body);
      const skuid1 = json.skuid;
      cy.request(`${url}/api/test/nonoptioned`).then((response2) => {
        const json2 =
          typeof response2.body === "object" ? response2.body : JSON.parse(response2.body);
        const skuid2 = json2.skuid;
        // send them straight to the confirmation page
        cy.visit(
          `${url}/confirmation?PRODUCT_${skuid1}=1&LOGINPASS=1&bill_fname=${user.firstName}&bill_lname=${user.lastName}&bill_street=${user.address1}&bill_street2=${user.address2}&bill_city=${user.city}&bill_state=${user.state}&bill_postal_code=${user.zip}&bill_zip_4=&bill_country=${user.country}&bill_email=${user.email}&bill_phone=${user.phone}&ship_fname=${user.firstName}&ship_lname=${user.lastName}&ship_street=${user.address1}&ship_street2=${user.address2}&ship_city=${user.city}&ship_state=${user.state}&ship_postal_code=${user.zip}&ship_zip_4=&ship_country=${user.country}&ship_method=24&payment_method=standard&COUPON_CODE=${user.coupon}&card_type=VI&card_month=04&card_year=28&worldpay_registration_id=2137898579424579172&worldpay_vantiv_txn_id=83993708038025121`
        );

        // total up the lineitems
        let subTotal = 0;
        cy.get(".lineitem-total")
          .each(($element) => {
            cy.wrap($element)
              .invoke("text")
              .then(($price) => {
                subTotal += parseFloat($price.match(/\d+(\.\d+)?/)[0]);
              });
          })
          .then(() => {
            let undiscounted = 0;
            let discount = 0;
            let discounted = 0;
            let shipping = 0;
            let tax = 0;
            let surcharge = 0;
            let total = 0;

            // I know this is callback hell but cypress doesn't seem to have another way
            // collect subtotal discount, tax and shipping and total them up
            cy.get('[data-test="undiscounted"]')
              .invoke("text")
              .then((text) => {
                undiscounted = parseFloat(text.match(/\d+(\.\d+)?/)[0]);
              })
              .then(() => {
                cy.wrap(undiscounted).should("be.closeTo", subTotal, 0.01);
                cy.get('[data-test="discount"]')
                  .invoke("text")
                  .then((text) => {
                    discount = parseFloat(text.match(/\d+(\.\d+)?/)[0]);
                  })
                  .then(() => {
                    cy.get('[data-test="discounted"]')
                      .invoke("text")
                      .then((text) => {
                        discounted = parseFloat(text.match(/\d+(\.\d+)?/)[0]);
                      })
                      .then(() => {
                        const discountedTotal = subTotal - discount;
                        cy.wrap(discounted).should("be.closeTo", discountedTotal, 0.01);
                        cy.get('[data-test="confirmation-tax"]')
                          .invoke("text")
                          .then((text) => {
                            tax = parseFloat(text.match(/\d+(\.\d+)?/)[0]);
                            cy.wrap(tax).should("be.greaterThan", 0);
                          })
                          .then(() => {
                            cy.get('[data-test="shipping"]')
                              .invoke("text")
                              .then((text) => {
                                shipping = parseFloat(text.match(/\d+(\.\d+)?/)[0]);
                              })
                              .then(() => {
                                cy.get('[data-test="surcharge"]')
                                  .invoke("text")
                                  .then((text) => {
                                    surcharge = parseFloat(text.match(/\d+(\.\d+)?/)[0]);
                                    cy.wrap(surcharge).should("equal", 0.29);
                                  })
                                  .then(() => {
                                    cy.get('[data-test="total"]')
                                      .invoke("text")
                                      .then((text) => {
                                        total = parseFloat(text.match(/\d+(\.\d+)?/)[0]);
                                      })
                                      .then(() => {
                                        const myTotal = discounted + tax + shipping + surcharge;
                                        cy.wrap(total).should("be.closeTo", myTotal, 0.01);
                                        cy.visit(`${url}/confirmation?ship_state=MN`);
                                        cy.get('[data-test="surcharge"]').should("not.exist");
                                        cy.visit(
                                          `${url}/confirmation?PRODUCT_${skuid1}=25&bill_state=MN`
                                        );
                                        cy.get('[data-test="surcharge"]')
                                          .invoke("text")
                                          .then((text) => {
                                            surcharge = parseFloat(text.match(/\d+(\.\d+)?/)[0]);
                                            cy.wrap(surcharge).should("equal", 0.5);
                                          });
                                      });
                                  });
                              });
                          });
                      });
                  });
              });
          });
      });
    });
  });

  it(`Test order`, () => {
    // hits an endpoint that returns a sku that's non optioned, non-custom (can be added right to the cart)
    cy.setCookie("capturewin", "capture", { secure: true, domain }); // make sure capture window doesn't appear
    cy.request(`${url}/api/test/nonoptioned`).then((response) => {
      const json = typeof response.body === "object" ? response.body : JSON.parse(response.body);
      const unoptionedSkuid = json.skuid;
      cy.log(`got test SKU ${unoptionedSkuid}`);
      cy.visit(`${url}/${unoptionedSkuid}.html?SOURCE_CODE=${user.source}`);
      cy.get(`#add-to-cart-btn`).click({ force: true });
      cy.get("#cart-modal .modal-body").should("contain", unoptionedSkuid);

      cy.request(`${url}/api/test/testoptioned`).then((response) => {
        const json = typeof response.body === "object" ? response.body : JSON.parse(response.body);
        const optionedSkuid = json.skuid;
        cy.log(`got test SKU ${optionedSkuid}`);
        cy.visit(`${url}/${optionedSkuid}.html`);

        // select options and add to cart
        cy.selectAllMatrixOptions(
          optionedSkuid,
          `[data-js="order-form"][data-add-item="${optionedSkuid}"]`
        ).then((fullSkuid) => {
          cy.get(`#add-to-cart-btn`).click({ force: true });
          cy.get("#cart-modal .modal-body").should("contain", optionedSkuid);

          // make sure product add event fired
          cy.checkItemAddedGTM(fullSkuid);

          // check window "store"
          cy.checkCartItemsObject(fullSkuid);

          // /// test that features loaded
          // cy.get("#popcart-recs-container .related__products").should("be.visible");
          // cy.get("#popcart-recs-container .related__products .popcart-related-item").should(
          //   "have.length.of",
          //   3
          // );

          cy.get('#cart-modal .modal-body a[href="/cart"]').click({ force: true });
          cy.get(".lineitems").should("contain", fullSkuid);

          cy.wait(2000);
          cy.closeModal("#smallModal");
          cy.get('[href="/checkout"]').first().click({ force: true });
          cy.url().should("contain", "/checkout");
          cy.get("input#guest-email").type(user.email);
          cy.get("#guest-checkout-button").click({ force: true });

          // modal may exist here, click body to dismiss
          cy.get('[data-js="billing-content"]').should("exist");
          cy.window().its("$").should("exist");
          cy.wait(2000);
          cy.get("body").click({ force: true });
          cy.closeModal("#smallModal");

          cy.get('[data-js="billing-form"] input[name="bill_fname"]').type(user.firstName);
          cy.get('[data-js="billing-form"] input[name="bill_lname"]').type(user.lastName);
          cy.get('[data-js="billing-form"] input[name="bill_street"]').type(user.address1);
          cy.get('[data-js="billing-form"] input[name="bill_street2"]').type(user.address2);
          cy.get('[data-js="billing-form"] input[name="bill_city"]').type(user.city);
          cy.get('[data-js="billing-form"] select[name="bill_state"]').select(user.state);
          cy.get('[data-js="billing-form"] input[name="bill_postal_code"]').type(user.zip);
          cy.get('[data-js="billing-form"] select[name="bill_country"]').select(user.country);
          cy.get('[data-js="billing-form"] input[name="bill_phone"]').type(user.phone);
          cy.get("#billing-continue-button").click({ force: true });

          // payment page
          cy.url().should("contain", "/payment");
          cy.get('[data-test="summary-billing-address"]').should("contain", user.firstName); // check address summary pane
          cy.get('[data-test="summary-billing-address"]').should("contain", user.lastName);
          cy.get('[data-test="summary-billing-address"]').should("contain", user.address1);
          cy.get('[data-test="summary-billing-address"]').should("contain", user.address2);
          cy.get('[data-test="summary-billing-address"]').should("contain", user.city);
          cy.get('[data-test="summary-billing-address"]').should("contain", user.state);
          cy.get('[data-test="summary-billing-address"]').should("contain", user.zip);
          cy.get('[data-test="summary-billing-address"]').should("contain", user.country);
          cy.get('[data-test="summary-billing-address"]').should("contain", user.phone);
          cy.get('[data-test="summary-shipping-address"]').should("contain", user.firstName);
          cy.get('[data-test="summary-shipping-address"]').should("contain", user.lastName);
          cy.get('[data-test="summary-shipping-address"]').should("contain", user.address1);
          cy.get('[data-test="summary-shipping-address"]').should("contain", user.address2);
          cy.get('[data-test="summary-shipping-address"]').should("contain", user.city);
          cy.get('[data-test="summary-shipping-address"]').should("contain", user.state);
          cy.get('[data-test="summary-shipping-address"]').should("contain", user.zip);
          cy.get('[data-test="summary-shipping-address"]').should("contain", user.country);

          // add card details
          // this is a conditional test that checks if the payframe client loads, if not the actions are different
          cy.window()
            .its("payframeClient")
            .then((payframeClient) => {
              if (typeof payframeClient === "string" && payframeClient === "fail") {
                cy.get('select[name="credit_type"]').select("VI");
                cy.get('input[name="credit_code"]').type("4111111111111111");
                cy.get('select[name="credit_month"]').select("12");
                cy.get('select[name="credit_year"]').select("2030");
                cy.get('input[name="credit_security_code"]').type("111");
                cy.get("#cc-checkout-button-payment").click({ force: true });
              } else {
                cy.get("#eProtect-iframe").iframeLoaded().as("worldpay");
                cy.get("@worldpay")
                  .its("document")
                  .getInDocument("#accountNumber")
                  .then((accountNumber) => {
                    cy.wrap(accountNumber).type("4111111111111111");
                  });
                cy.get("@worldpay")
                  .its("document")
                  .getInDocument("#expMonth")
                  .then((expMonth) => {
                    cy.wrap(expMonth).select("12");
                  });
                cy.get("@worldpay")
                  .its("document")
                  .getInDocument("#expYear")
                  .then((expYear) => {
                    cy.wrap(expYear).select("2028");
                  });
                cy.get("@worldpay")
                  .its("document")
                  .getInDocument("#cvv")
                  .then((cvv) => {
                    cy.wrap(cvv).type("111");
                  });
                cy.get("#cc-checkout-button").click({ force: true });
              }
            });

          // confirmation page
          cy.url().should("contain", "/confirmation");
          cy.get("#billing_info").should("contain", user.firstName);
          cy.get("#billing_info").should("contain", user.lastName);
          cy.get("#billing_info").should("contain", user.address1);
          cy.get("#billing_info").should("contain", user.address2);
          cy.get("#billing_info").should("contain", user.city);
          cy.get("#billing_info").should("contain", user.state);
          cy.get("#billing_info").should("contain", user.zip);
          cy.get("#billing_info").should("contain", user.email);
          cy.get("#shipping_info").should("contain", user.firstName);
          cy.get("#shipping_info").should("contain", user.lastName);
          cy.get("#shipping_info").should("contain", user.address1);
          cy.get("#shipping_info").should("contain", user.address2);
          cy.get("#shipping_info").should("contain", user.city);
          cy.get("#shipping_info").should("contain", user.state);
          cy.get("#shipping_info").should("contain", user.zip);
          cy.get(`.lineitems [data-lineitem-skuid="${unoptionedSkuid}"]`).should("exist");
          cy.get(`.lineitems [data-lineitem-skuid="${fullSkuid}"]`).should("exist");
          cy.get(`.lineitems [data-lineitem-skuid="${unoptionedSkuid}"]`).should(
            "contain",
            unoptionedSkuid
          );
          cy.get(`.lineitems [data-lineitem-skuid="${fullSkuid}"]`).should("contain", fullSkuid);
          cy.get('[data-test="confirmation-tax"]').then((el) => {
            const text = el.text();
            expect(text).to.match(/\$[0-9]{1,2}\.[0-9]{2}/);
          });

          // test updating address
          const newBillStreet2 = "Unit 123";
          cy.get('#billing_info [data-js="trigger-expand"]').click({ force: true });
          cy.get('#billing_info [name="bill_street2"]').clear().type(`${newBillStreet2}{enter}`);
          cy.get("#billing_info").should("contain", newBillStreet2);

          const newShipStreet2 = "Unit 345";
          cy.get('#shipping_info [data-js="trigger-expand"]').click({ force: true });
          cy.get('#shipping_info [name="ship_street2"]').clear().type(`${newShipStreet2}{enter}`);
          cy.get("#shipping_info").should("contain", newShipStreet2);

          if (Cypress.env("isFailover") === 0) {
            cy.get("#right-side-submit").click({ force: true });

            // receipt page
            cy.url().should("contain", "/complete");
            cy.get(".receipt-headline").should("contain", "Order Complete");
            cy.get('[data-test="receipt-billing-address"]').should("contain", user.firstName); // check address summary pane
            cy.get('[data-test="receipt-billing-address"]').should("contain", user.lastName);
            cy.get('[data-test="receipt-billing-address"]').should("contain", user.address1);
            cy.get('[data-test="receipt-billing-address"]').should("contain", newBillStreet2);
            cy.get('[data-test="receipt-billing-address"]').should("contain", user.city);
            cy.get('[data-test="receipt-billing-address"]').should("contain", user.state);
            cy.get('[data-test="receipt-billing-address"]').should("contain", user.zip);
            cy.get('[data-test="receipt-billing-address"]').should("contain", user.country);
            cy.get('[data-test="receipt-billing-address"]').should("contain", user.phone);
            cy.get('[data-test="receipt-shipping-address"]').should("contain", user.firstName);
            cy.get('[data-test="receipt-shipping-address"]').should("contain", user.lastName);
            cy.get('[data-test="receipt-shipping-address"]').should("contain", user.address1);
            cy.get('[data-test="receipt-shipping-address"]').should("contain", newShipStreet2);
            cy.get('[data-test="receipt-shipping-address"]').should("contain", user.city);
            cy.get('[data-test="receipt-shipping-address"]').should("contain", user.state);
            cy.get('[data-test="receipt-shipping-address"]').should("contain", user.zip);
            cy.get('[data-test="receipt-shipping-address"]').should("contain", user.country);
            cy.get(`.lineitems [data-lineitem-skuid="${unoptionedSkuid}"]`).should("exist");
            cy.get(`.lineitems [data-lineitem-skuid="${fullSkuid}"]`).should("exist");
            cy.get(`.lineitems [data-lineitem-skuid="${unoptionedSkuid}"]`).should(
              "contain",
              unoptionedSkuid
            );
            cy.get(`.lineitems [data-lineitem-skuid="${fullSkuid}"]`).should("contain", fullSkuid);
            cy.get('[data-test="receipt-tax"]').then((el) => {
              const text = el.text();
              expect(text).to.match(/\$[0-9]{1,2}\.[0-9]{2}/);
            });

            // test order actually is in db
            cy.get("[data-test-status]")
              .invoke("attr", "data-test-status")
              .then((orderId) => {
                cy.get('[data-js="lineitem"]').then((items) => {
                  cy.log("orderId", orderId);
                  cy.log("lineitems", items.length);
                  cy.request(
                    `${url}/api/test/otest?otest_id=${orderId}&otest_num=${items.length}`
                  ).then((response) => {
                    const json =
                      typeof response.body === "object" ? response.body : JSON.parse(response.body);
                    const success = json.success;
                    expect(success).to.be.true;
                  });
                });
              });

            cy.get("[data-test-status]").then((el) => {
              let orderId = el.attr("data-test-status");
              let href = el.attr("href");

              cy.reload();
              cy.get(".shopping-cart-header").should("contain", "Your Cart is Empty");

              cy.visit(url + href);
              cy.get(".header-title").should("contain", orderId);
              cy.get(".lineitems").should("have.length.above", 0);
            });
          } // end true for is not failover
        });
      });
    });
  });
});

import domain from "../support/baseDomain.js";
import Cookies from "js-cookie";
const url = Cypress.env("baseUrl");

function randomText() {
  var text = "";
  var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  for (var i = 0; i < 5; i++) text += possible.charAt(Math.floor(Math.random() * possible.length));
  return text;
}

function createTestEmail() {
  const username = randomText();
  return `${username}@usatestrunner.com`;
}

let user;
let testEmail = createTestEmail();

describe("Account", () => {
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

  it(`Test account`, () => {
    // if on production, don't pollute the db with test emails
    if (/www/.test(url)) {
      testEmail = user.email;
      cy.log("testemail", testEmail);
    }

    cy.setCookie("capturewin", "capture", { secure: true, domain }); // make sure capture window doesn't appear

    // test signup modal
    cy.visit(`${url}`);

    // only test signups on non-production instances.
    if (!/www/.test(url)) {
      cy.get('[data-target="#account-modal"]').first().click({ force: true });
      cy.wait(1000);
      cy.get("#nav-signup-tab").click({ force: true });
      cy.get('#user-signup-form [name="bill_email"]').type(testEmail);
      cy.get('#user-signup-form [name="bill_account_password"]').type(user.password);
      cy.get('#user-signup-form [name="bill_account_password_confirm"]').type(user.password);
      cy.get("#user-signup-form #account-signup-button").click({ force: true });

      // need to test for page refresh
      // https://github.com/cypress-io/cypress/issues/1805#issuecomment-525482440
      cy.window().then((w) => (w.beforeReload = true));
      cy.window().should("have.prop", "beforeReload", true);
      cy.window().should("not.have.prop", "beforeReload");

      // now check that dom reflects user login
      cy.get("#nav-profile-dropdown span").should("contain", "Welcome, Shopper!");

      // test account update
      cy.get("#nav-profile-dropdown").click({ force: true });
      cy.get('.dropdown.account-dropdown.open .dropdown-menu [href="/account"]').click({
        force: true,
      });
      cy.url().should("contain", "/account");
      cy.get(".account-container .user-data").should("contain", testEmail);
      cy.get('.account-container [href="#/update"]').first().click({ force: true });
      cy.get('.profile-content input[name="bill_fname"]').type(user.firstName);
      cy.get('.profile-content input[name="bill_lname"]').type(user.lastName);
      cy.get('.profile-content input[name="bill_street"]').type(user.address1);
      cy.get('.profile-content input[name="bill_street2"]').type(user.address2);
      cy.get('.profile-content input[name="bill_city"]').type(user.city);
      cy.get('.profile-content select[name="bill_state"]').select(user.state);
      cy.get('.profile-content input[name="bill_postal_code"]').type(user.zip);
      cy.get('.profile-content select[name="bill_country"]').select(user.country);
      cy.get('.profile-content input[data-test="phone"]').type(user.phone);
      cy.get('.profile-content [data-test="account-update-submit"]').click({ force: true });
      cy.url().should("not.contain", "/update");
      cy.get('[data-test="billing-address"]').should("contain", testEmail);
      cy.get('[data-test="billing-address"]').should("contain", user.firstName);
      cy.get('[data-test="billing-address"]').should("contain", user.lastName);
      cy.get('[data-test="billing-address"]').should("contain", user.address1);
      cy.get('[data-test="billing-address"]').should("contain", user.city);
      cy.get('[data-test="billing-address"]').should("contain", user.state);
      cy.get('[data-test="billing-address"]').should("contain", user.zip);

      // test logout
      cy.get('.account-container [href="/logout"]').first().click({ force: true });
      cy.url().should("contain", "/logout");
      cy.get(".header-title").should("contain", "logged out");
    } // end if for non-production

    // test sign-in
    cy.get('.sign_in [data-target="#account-modal"]').click({ force: true });
    cy.get(".loginmodal-container").should("be.visible");
    cy.get('.loginmodal-container #signin [name="bill_email"]').should("be.visible");
    cy.wait(1000);
    cy.get('.loginmodal-container #signin [name="bill_email"]').type(testEmail);
    cy.get('.loginmodal-container #signin [name="bill_account_password"]').type(user.password);
    cy.get('.loginmodal-container #signin [type="submit"]').click({ force: true });

    cy.get("#nav-profile-dropdown").should("contain", "Welcome, Rory");
    cy.get("#nav-profile-dropdown").click({ force: true });
    cy.get('.account-dropdown.open .dropdown-menu [href="/account"]').click({ force: true });
    cy.wait(2000);
    cy.get(".account-container .profile-content").should("contain", testEmail);
    cy.url().should("contain", "account");

    // test menu logout
    cy.get("#nav-profile-dropdown").click({ force: true });

    cy.get('.account-dropdown.open .dropdown-menu [href="/logout"]').click({ force: true });
    cy.url().should("contain", "logout");
    cy.get('[data-target="#account-modal"]').first().should("be.visible");
  });
});

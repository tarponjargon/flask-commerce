function randomText() {
  var text = "";
  var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  for (var i = 0; i < 5; i++) text += possible.charAt(Math.floor(Math.random() * possible.length));
  return text;
}

Cypress.Commands.add("iframeLoaded", { prevSubject: "element" }, ($iframe) => {
  const contentWindow = $iframe.prop("contentWindow");
  return new Promise((resolve) => {
    if (contentWindow && contentWindow.document.readyState === "complete") {
      resolve(contentWindow);
    } else {
      $iframe.on("load", () => {
        resolve(contentWindow);
      });
    }
  });
});

Cypress.Commands.add("checkItemAddedGTM", (skuid) => {
  cy.window().then((win) => {
    cy.wrap(win.dataLayer).should((dl) => {
      const added = dl.find((i) => i.event === "addToCart");
      expect(added.ecommerce.add.products[0].dimension1).to.equal(skuid);
    });
  });
});

Cypress.Commands.add("closeModal", (selector) => {
  cy.window()
    .should("have.property", "closeModal")
    .then((closeModal) => {
      closeModal(selector);
    });
});

Cypress.Commands.add("checkCartItemsObject", (skuid) => {
  cy.window().its("cartItemsObject").should("have.property", skuid);
});

Cypress.Commands.add("getInDocument", { prevSubject: "document" }, (document, selector) =>
  Cypress.$(selector, document)
);

Cypress.Commands.add("selectAllOptions", (skuid, sel = ".product__section") => {
  let selectedOptions = [];
  cy.get(`${sel} select`)
    .each((op, i) => {
      cy.get(`${sel} select.sel${i + 1}`).as("thisSel"); // re-get the element
      cy.get("@thisSel").should("not.have.attr", "disabled"); // wait for it to not be disabled
      cy.get("@thisSel").then((op) => {
        cy.wrap(op).should("not.have.attr", "disabled");
        const selectMenuSel = op.attr("id"); // selector for current <select>
        const currentMenu = Array.from(op[0]); // creates a JS array of the <option> nodes
        const ucIdx = currentMenu.findIndex(
          (i) =>
            i.getAttribute("data-pricechange") > 0 &&
            i.getAttribute("data-invmessage") !== "(no longer available)" &&
            i.getAttribute("value") &&
            !i.getAttribute("disabled")
        ); // get index of anyy upcharge <option>
        const enabled = currentMenu.findIndex(
          (i) =>
            !i.getAttribute("disabled") &&
            !i.classList.contains("disabled") &&
            i.getAttribute("value")
        ); // first option that's not disabled
        const selectOption = ucIdx > -1 ? currentMenu[ucIdx] : currentMenu[enabled]; // use the upcharge option (if any), or first enabled option
        const optionValue = selectOption.getAttribute("value"); // get the value of the selected option
        cy.get(`${sel} select#${selectMenuSel}`).select(optionValue); // select it with cypress (by value)
        selectedOptions.push(optionValue);
        cy.wait(2000);
      });
    })
    .then(() => {
      const fullSkuid = skuid + "-" + selectedOptions.join("-");
      cy.log("fullskuid", fullSkuid);
      cy.wrap(fullSkuid).as("fullSkuid");
    });
});

Cypress.Commands.add("selectAllMatrixOptions", (skuid, sel = '[data-js="options-matrix"]') => {
  let selectedOptions = [];
  cy.get(`${sel} [data-matrix-index]`)
    .each(($op, i) => {
      const currentMenu = Array.from($op[0].querySelectorAll("[data-option-code]")); // creates a JS array of the menu's <button> nodes
      const preSelected = $op[0].querySelector('[data-option-selected="1"]'); // if there's only one available option it is preselected, grab that element
      const ucIdx = currentMenu.findIndex(
        (i) =>
          i.getAttribute("data-pricechange") > 0 &&
          !i.getAttribute("disabled") &&
          i.getAttribute("data-option-nla") !== "1"
      ); // get index of anyy upcharge options
      const enabled = currentMenu.findIndex(
        (i) => !i.getAttribute("disabled") && !i.classList.contains("disabled")
      ); // first option that's not disabled
      const selectOption = preSelected
        ? preSelected
        : ucIdx > -1
        ? currentMenu[ucIdx]
        : currentMenu[enabled]; // use the upcharge option (if any), or first enabled option
      const optionValue = selectOption.getAttribute("data-option-code"); // get the value of the selected option
      if (!preSelected)
        cy.get(`${sel} [data-matrix-index="${i}"] [data-option-code="${optionValue}"]`).click(); // select it with cypress (by value) IF NOT PRESELECTED
      selectedOptions.push(optionValue);
      cy.wait(2000);
    })
    .then(() => {
      const fullSkuid = skuid + "-" + selectedOptions.join("-");
      cy.log("fullskuid", fullSkuid);
      cy.wrap(fullSkuid).as("fullSkuid");
    });
});

Cypress.Commands.add("apploaded", () => {
  //cy.wait(1000);
  cy.window().then((win) => {
    cy.wrap(win).should("have.property", "_fcapp");
    cy.wrap(win._fcapp, { timeout: 25000 }).should("have.property", "loaded", true);
    cy.wrap(win._fcapp).its("viewsLoaded").should("be.an", "array");
  });
  cy.window().should("have.property", "GoogleAnalyticsObject");
  cy.window().should("have.property", "google_tag_manager");
  cy.window().should("have.property", "dataLayer");
});

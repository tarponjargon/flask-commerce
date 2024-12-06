let domain = Cypress.env("baseUrl").replace(/(http.:\/\/).*:.*@(.*)$/, "$1$2");
domain = domain.replace(/https?:\/\//, "");
export default domain;

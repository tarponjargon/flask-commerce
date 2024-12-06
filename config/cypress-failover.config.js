const { defineConfig } = require("cypress");

module.exports = defineConfig({
  viewportWidth: 1440,
  viewportHeight: 900,
  pageLoadTimeout: 90000,
  defaultCommandTimeout: 15000,
  video: true,
  chromeWebSecurity: false,
  reporter: "dot",
  userAgent:
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.9.9999.999 Safari/537.36 USATestRunner",
  retries: 2,
  blockHosts: [
    "static.klaviyo.com",
    "static-tracking.klaviyo.com",
    "www.google-analytics.com",
    "cdn.attn.tv",
  ],
  e2e: {
    // We've imported your old cypress plugins here.
    // You may want to clean this up later by importing these.
    // setupNodeEvents(on, config) {
    //   return require("../cypress/plugins/index.js")(on, config);
    // },
    baseUrl: "https://flaskcommerce.thewhiteroom.com",
  },
  env: {
    baseUrl: "https://flaskcommerce.thewhiteroom.com", // NOTE: e2e.baseUrl does not seem to work locally
    isFailover: 1,
    failoverCookieName: "cloudflare_test_failover",
    failoverCookieVal: "failover",
    failoverCookieExpiry: null,
  },
});

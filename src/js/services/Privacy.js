import { getBodyData } from "./Utils";

export default class Privacy {
  constructor() {
    this.privacyId = getBodyData("data-privacy-id");
  }
  init = () => {
    if (this.privacyId) {
      this.addListener();
    }
  };

  loadPrivacyWidget = (e) => {
    e.preventDefault();
    if (window.OptanonWrapper) return; // indicator that the script is already loaded and we don't need to listen to links
    document.cookie =
      "OptanonAlertBoxClosed=; Max-Age=0; path=/; SameSite=Lax; domain=" +
      window.location.host.replace("www", "");
    document.cookie =
      "OptanonConsent=; Max-Age=0; path=/; SameSite=Lax; domain=" +
      window.location.host.replace("www", "");
    document.cookie =
      "OptanonAlertBoxClosed=; Max-Age=0; path=/; SameSite=Lax; domain=" + window.location.host;
    document.cookie =
      "OptanonConsent=; Max-Age=0; path=/; SameSite=Lax; domain=" + window.location.host;
    var consentScript = document.createElement("script");
    consentScript.type = "text/javascript";
    consentScript.src = "https://cdn.cookielaw.org/scripttemplates/otSDKStub.js";
    consentScript.setAttribute("charset", "UTF-8");
    consentScript.setAttribute("id", "ot-script");
    consentScript.setAttribute("data-domain-script", this.privacyId);
    window.OptanonWrapper = function () {};
    document.head.appendChild(consentScript);
  };

  addListener = () => {
    document.querySelectorAll(".ot-sdk-show-settings").forEach((el) => {
      if (!el.hasListener) {
        el.hasListener = true;
        el.addEventListener("click", this.loadPrivacyWidget, false);
      }
    });
  };
}

import messages from "./Messages";
import { fetchContent, fetchJson } from "./Ajax";

export function spinLink(selector, text = "PLEASE WAIT") {
  const el = selector ? document.querySelector(selector) : undefined;
  if (!el) return false;
  el.setAttribute("data-original-text", el.innerText);
  el.innerHTML = text + ' ... <i class="spinner icomoon-spinner-gray font-small"></i>';
  return true;
}

export function unSpinLink(selector, text) {
  const el = selector ? document.querySelector(selector) : undefined;
  if (!el) return false;
  const hidden = el.getAttribute("data-original-text");
  const contents = typeof text !== "undefined" ? text : hidden;
  el.innerHTML = contents;
  return true;
}

// disables the button (and shows spinner) after submit
export function spinButton(id, text = "SUBMITTING") {
  if (!id) {
    return false;
  }
  try {
    let button = document.getElementById(id);
    button.disabled = true;
    button.classList.remove("success-button");
    button.setAttribute("data-original-text", button.innerText);
    button.innerHTML = text + ` ... <i class="spinner icomoon-spinner"></i>`;
  } catch (e) {
    // console.log("problem with spinButton", e);
  }
  return true;
}

// undos the spinButton action
export function unSpinButton(id, text) {
  try {
    var button = document.getElementById(id);
    var hidden = button.getAttribute("data-original-text");
    text = typeof text !== "undefined" ? text : hidden;
    button.disabled = false;
    button.innerHTML = text;
  } catch (e) {}
  return true;
}

// remove html entities and also any non-utf8 characters
export function strip_entities(input) {
  var output = "";
  input = input.replace(/&[^\s]*;/g, "");
  for (var i = 0; i < input.length; i++) {
    if (input.charCodeAt(i) <= 127) {
      output += input.charAt(i);
    }
  }
  return output;
}

export function determineAddType(href) {
  var actionType = "DETAIL";
  var currSku = null;
  var matches = [];
  var pattern = /action=([A-Z]{3,6})&ITEM=([A-Z0-9]{6,9})/i;
  matches = pattern.exec(href);
  if (matches && matches[1] && matches[2]) {
    actionType = matches[1];
    currSku = matches[2];
  }
  return {
    actionType: actionType,
    currSku: currSku,
  };
}

export function closeModal(sel = "#cart-modal") {
  $(sel).modal("hide");
}

export function getBodyData(dataAttr) {
  const attrVal = document.body.getAttribute(dataAttr);
  return attrVal ? safeString(attrVal) : null;
}

export function getPageType() {
  return getBodyData("data-view");
}

export function getPhase() {
  // can be 'shopping' or 'checkout'
  const phase = getBodyData("data-phase");
  return phase ? phase.toLowerCase() : "shopping";
}

export function isEducationShop() {
  const val = getBodyData("data-is-education-shop");
  return val === "1" ? true : false;
}

export function vendorSearchActive() {
  const val = getBodyData("data-vendor-search");
  return val === "off" ? false : true;
}

export function isLoggedIn() {
  return document.querySelector("body[data-login='true']") ? true : false;
}

// abstraction for slecting dom elements using data-js="attr"
export function dataSelect(attr, container = document) {
  //console.log("container", container);
  if (!attr) return [];
  let nl = null;
  try {
    nl = container.querySelectorAll(`[data-js='${attr}']`);
  } catch (e) {
    //console.error("dataQS failed", e);
  }
  if (nl && nl.length === 1) {
    return nl[0];
  } else if (nl && nl.length > 1) {
    return nl;
  } else {
    return null;
  }
}

export function formatPrice(num) {
  try {
    return "$" + num.toFixed(2).replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1,");
  } catch (e) {
    return num;
  }
}

export function formatJson(obj) {
  return JSON.stringify(obj, null, "\t");
}

export function isEmpty(value) {
  if (typeof value === "undefined" || value === null) {
    return true;
  } else if (Array.isArray(value) && value.length === 0) {
    return true;
  } else if (typeof value === "object" && Object.keys(value).length === 0) {
    return true;
  } else if (typeof value === "string" && value.length === 0) {
    return true;
  } else if (typeof value == "number" && value <= 0) {
    return true;
  } else if (
    typeof value === "object" &&
    Object.keys(value)
      .map((e) => value[e])
      .every((x) => x === null || x === "")
  ) {
    // Object.keys(value).map(e => value[e]) is somewhat of a polyfill for Object.values
    return true;
  } else {
    return false;
  }
}

export function abbrevString(string, chars = 140, method = "soft") {
  let abbreviated = string;
  let removed = null;
  if (string && string.length > chars) {
    if (method === "hard") {
      abbreviated = string.substring(0, chars) + "...";
      removed = string.substring(chars);
    } else {
      const pattern = "^(.{" + chars + "}[^, ]*)(.*)";
      const re = new RegExp(pattern, "g");
      const matches = re.exec(string);
      if (matches.length > 1) {
        abbreviated = matches[1];
        removed = matches[2].trim();
      }
    }
  }
  return [abbreviated, removed];
}

export function unEscape(t) {
  if (!t) return null; // leave this
  t = decodeURIComponent(t);

  const table = {
    "&amp;(amp;)+quot;": '"',
    "&amp;quot;": '"',
    "&quot;": '"',
    "&amp;(amp;)+apos;": "'",
    "&amp;apos;": "'",
    "&apos;": "'",
  };
  Object.keys(table).forEach((key) => {
    let pattern = key;
    let re = new RegExp(pattern, "gi");
    t = t.replace(re, table[key]);
  });
  return t;
}

export function correctDoubleEscaped(t) {
  if (!t) return null; // leave this
  const table = {
    "&amp;(amp;)+quot;": "&quot;",
    "&amp;quot;": "&quot;",
    "&amp;(amp;)+apos;": "&apos;",
    "&amp;apos;": "&apos;",
    "&amp;(amp;)+": "&amp;",
    "&amp;amp;": "&amp;",
    "&amp;(amp;)+gt;": "&gt;",
    "&amp;gt;": "&gt;",
    "&amp;(amp;)+lt;": "&lt;",
    "&amp;lt;": "&lt;",
  };
  Object.keys(table).forEach((key) => {
    let pattern = key;
    let re = new RegExp(pattern, "gi");
    t = t.replace(re, table[key]);
  });
  return t;
}

export function safeString(text) {
  if (!text) return null; // leave this
  try {
    let table = {
      "<": "lt",
      ">": "gt",
      '"': "quot",
      "'": "apos",
      "&": "amp",
      "\r": "#10",
      "\n": "#13",
    };
    let t = text.toString().replace(/[<>"'\r\n&]/g, function (chr) {
      return "&" + table[chr] + ";";
    });
    t = correctDoubleEscaped(t);
    return t;
  } catch (e) {
    console.error("problem creating safeString on text", text, e);
    return null;
  }
}

export function copy(obj) {
  try {
    return JSON.parse(JSON.stringify(obj));
  } catch (e) {
    console.error("could not copy object", e);
    return null;
  }
}

export function arrayUnique(arr) {
  return arr.filter(function (item, index) {
    return arr.indexOf(item) >= index;
  });
}

export function scrollIt(element = null, duration = 1000, adjustBy = 0) {
  //console.log("Scrollit", element)
  // https://jsfiddle.net/s61x7c4e/
  var startingY = window.pageYOffset;
  var elementY = element ? element.getBoundingClientRect().top : 0;
  var targetY =
    document.body.scrollHeight - elementY < window.innerHeight
      ? document.body.scrollHeight - window.innerHeight + adjustBy
      : elementY;
  var diff = targetY - startingY;
  var easing = function (t) {
    return t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
  };
  var start;

  if (!diff) return;

  if (diff > 75) diff -= 75; // account for the sticky header

  // Bootstrap our animation - it will get called right before next frame shall be rendered.
  window.requestAnimationFrame(function step(timestamp) {
    if (!start) start = timestamp;
    var time = timestamp - start;
    var percent = Math.min(time / duration, 1);
    percent = easing(percent);
    window.scrollTo(0, startingY + diff * percent);
    if (time < duration) {
      window.requestAnimationFrame(step);
    }
  });
}

export function replaceQuotes(string) {
  return string.replace(/["]+/g, "'");
}

export function arrayParam(k, a) {
  return k && a && a.length ? a.map((i) => `${k}[]=${encodeURIComponent(i)}`).join("&") : null;
}

export function serializeToParams(obj) {
  let str = [];
  for (const p in obj)
    if (p && Object.prototype.hasOwnProperty.call(obj, p)) {
      str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
    }
  return str.join("&");
}

export function imageLoader(url) {
  return new Promise((resolve, reject) => {
    let img = new Image();
    if (!img.hasListener) {
      img.hasListener = true;
      img.addEventListener("load", () => resolve(img));
      img.addEventListener("error", () => reject(`Failed to load image: ${url}`));
      img.src = url;
    }
  });
}

export const makeFullPath = function (pathToImage) {
  if (!pathToImage) return null;
  if (/^http/i.test(pathToImage)) return pathToImage;
  return `${window.location.origin}${pathToImage}`;
};

export const elementImagesLoaded = function (selector) {
  return new Promise((resolve) => {
    const imageEls = document.querySelectorAll(`${selector} img`);
    if (!imageEls || !imageEls.length) resolve();
    const allImages = Array.prototype.slice
      .call(imageEls)
      .map((i) => makeFullPath(i.getAttribute("src")));
    if (!allImages || !allImages.length) resolve();
    allImagesLoaded(allImages).then((_log) => resolve(_log));
  });
};

export function allImagesLoaded(images) {
  if (!images || !Array.isArray(images) || !images.length) return false;
  return new Promise((resolve) => {
    // Keep the count of the verified images
    var allLoaded = 0;

    // The object that will be returned in the callback
    var _log = {
      success: [],
      error: [],
    };

    // Executed everytime an img is successfully or wrong loaded
    var verifier = function () {
      allLoaded++;

      // triggers the end callback when all images has been tested
      if (allLoaded == images.length) {
        resolve(_log);
      }
    };

    // Loop through all the images URLs
    for (var index = 0; index < images.length; index++) {
      // Prevent that index has the same value by wrapping it inside an anonymous fn
      (function (i) {
        // Image path providen in the array e.g image.png
        var imgSource = images[i];
        var img = new Image();

        if (!img.hasListener) {
          img.hasListener = true;

          img.addEventListener(
            "load",
            function () {
              _log.success.push(imgSource);
              verifier();
            },
            false
          );

          img.addEventListener(
            "error",
            function () {
              _log.error.push(imgSource);
              verifier();
            },
            false
          );
        }

        img.src = imgSource;
      })(index);
    }
  });
}

export const debounceFn = function (func, wait, immediate) {
  var timeout;
  return function () {
    var context = this,
      args = arguments;
    var later = function () {
      timeout = null;
      if (!immediate) func.apply(context, args);
    };
    var callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(context, args);
  };
};

export const validEmail = function (email) {
  return /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(
    email
  );
};

export const createId = function () {
  return Math.random().toString(36).substr(2, 8);
};

// executes promises in a series
export const promiseSerial = (funcs) =>
  funcs.reduce(
    (promise, func) => promise.then((result) => func().then(Array.prototype.concat.bind(result))),
    Promise.resolve([])
  );

// returns object of any url params.  the values will be encoded.
export const getUrlParams = (fromUrl = window.location.href) => {
  const encodeVal = function (str) {
    // pluses are getting encoded and passed thru, so we gotta s/r the +, decode, then re-encode
    return encodeURIComponent(decodeURIComponent(replacePlusSign(str)));
  };

  const replacePlusSign = function (str = "") {
    str = str.replace(/\+/g, " ");
    str = str.replace(/%2B/g, " ");
    return str;
  };

  let vars = {},
    hash = null;
  if (fromUrl.indexOf("?") > -1) {
    var hashes = fromUrl.slice(fromUrl.indexOf("?") + 1).split("&");
    for (let i = 0; i < hashes.length; i++) {
      hash = hashes[i].split("=");
      vars[hash[0].toLowerCase()] = encodeVal(hash[1]);
    }
  }

  return vars;
};

export const isLoaded = (key = "loaded") => {
  return new Promise((resolve, reject) => {
    let r = 0;
    let i = setInterval(() => {
      r += 1;
      if (r > 80) reject(clearInterval(i));
      if ("_fcapp" in window && window._fcapp[key]) {
        clearInterval(i);
        if (!_fcapp.loadingComplete.includes(key)) {
          _fcapp.loadingComplete.push(key);
        }
        resolve();
      }
    }, 100);
  });
};

export const isDesktop = () => {
  return window.innerWidth > 1240 ? true : false;
};

export const lazyLoadImages = () => {
  var lazyImages = [].slice.call(document.querySelectorAll("img.lazyload"));

  if ("IntersectionObserver" in window) {
    let lazyImageObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          let lazyImage = entry.target;
          lazyImage.src = lazyImage.dataset.src || lazyImage.getAttribute("data-img");
          lazyImage.classList.remove("lazyload");
          lazyImageObserver.unobserve(lazyImage);
        }
      });
    });

    lazyImages.forEach(function (lazyImage) {
      lazyImageObserver.observe(lazyImage);
    });
  } else {
    //console.log("NO IntersectionObserver in browser, lazyImages are:", lazyImages);
    Array.prototype.forEach.call(lazyImages, function (lazyImage) {
      lazyImage.src = lazyImage.dataset.src || lazyImage.getAttribute("data-img");
      lazyImage.classList.remove("lazyload");
    });
  }
};

export const showCapture = function () {
  // this shows the email capture form NOTE it does not add submit listener, do that on then() in caller
  return new Promise((resolve, reject) => {
    const url = "/email_capture?collect_shown=1";
    const modal = document.querySelector("#capture-modal .modal-content");
    const client = getBodyData("data-client-id");
    const startModal = (content) => {
      const html = $.parseHTML($.trim(content), document, true);
      $(modal).html(html);
      $("#capture-modal").modal("show");
    };
    fetchContent(url)
      .then((content) => {
        startModal(content);
        resolve();
      })
      .catch(() => {
        console.error("showCapture failed, retrying", client);
        fetchContent(url)
          .then((content) => {
            console.error("showCapture retry successful", client);
            startModal(content);
            resolve();
          })
          .catch((e) => {
            console.error("showCapture retry failed", e, client);
            reject(e);
          });
      });
  });
};

export const submitOptin = function (email) {
  // submits an optin.  if the capture modal is not showing, load it.
  if (!validEmail(email)) {
    flashMessage.show({ message: messages.invalidemail });
    return false;
  }

  const url = "/process_email_capture";
  const data = `bill_email=${encodeURIComponent(
    email
  )}&request=optinrequest&optin=yes&showpromo=1&capture=Y`;
  const client = getBodyData("data-client-id");
  const onSuccess = (j) => {
    var resultVar = 0;
    for (var i = 0; i < j.length; i++) {
      resultVar = j[i].result;
    }
    let prom = () => Promise.resolve();
    if (!$("#capture-modal .modal-content").is(":visible")) {
      prom = showCapture;
    }
    prom().then(() => {
      if (resultVar == 0) {
        $("#addcap").hide();
        $("#successdiv").show();
        fetchJson(`/default?IS_NEW_EMAIL=${CFG.signupCoupon}`);
        window.dataLayer.push({
          event: "trackEvent",
          eventCategory: "E-Mail Capture Complete",
          eventAction: "Modal",
          eventLabel: "New E-Mail",
        });
        window.dataLayer.push({
          event: "welcomeEmailSent",
          email: email,
          requestType: "optinrequest",
        });
      } else {
        $("#addcap").hide();
        $("#kindof-successdiv").show();
        window.dataLayer.push({
          event: "trackEvent",
          eventCategory: "E-Mail Capture Complete",
          eventAction: "Modal",
          eventLabel: "E-Mail Exists",
        });
      }
    });
  };

  fetch(url, {
    method: "POST",
    credentials: "same-origin",
    body: data,
  })
    .then((r) => r.json())
    .then((data) => onSuccess(data))
    .catch(() => {
      console.error("failed submitoptin, retrying", client);
      fetch(url, {
        method: "POST",
        credentials: "same-origin",
        body: data,
      })
        .then((r) => r.json())
        .then((data) => {
          onSuccess(data);
          console.error("submitoptin retry succeeded", client);
        })
        .catch((e) => {
          console.error("failed retry submitoptin", e, client);
        });
    });
};

export const checkZip = function (str) {
  return /^([0-9]{5})(\-([0-9]{4}))?$/.test(str);
};

export const updateMiniCart = function () {
  $.get("/store?action=ajax_carttotals", function (data) {
    if (typeof data === "string") data = JSON.parse(data);
    if (data && data.quantities) {
      $('[data-js="cart-item-quantity"]').text(data.quantities);
      $('[data-js="cart-item-container"]').toggleClass("invisible visible");
    }
  });
};

export const getEmailFromGTM = function () {
  let email = null;
  let gtmId = getBodyData("data-gtm-id");
  try {
    email = google_tag_manager[gtmId].dataLayer.get("email"); /* eslint-disable-line */
  } catch (e) {}
  return email;
};

export const removeMask = function (sel) {
  $(".page-spinner").addClass("fadeOut");
  $(sel)
    .addClass("fadeInFast")
    .css("visibility", "visible")
    .parent()
    .removeClass(
      "loading-mask mask-fixed mask-100 mask-200 mask-300 mask-400 mask-500 mask-600 mask-700 mask-800"
    );
};

export const scrollToSelector = function (sel) {
  setTimeout(function () {
    $("html, body").animate(
      {
        scrollTop: $(sel).offset().top,
      },
      100
    );
  }, 100);
};

export const waitForSelector = (sel) => {
  return new Promise((resolve, reject) => {
    if (!sel) {
      reject("no selector passed");
      return false;
    }
    let r = 0;
    let i = setInterval(() => {
      r += 1;
      if (r > 80) {
        clearInterval(i);
        reject("selector never appeared " + sel);
      }
      const el = document.querySelector(sel);
      if (el) {
        clearInterval(i);
        resolve(el);
      }
    }, 100);
  });
};

export const loadCarousel = function (sel = '[data-js="carousel-slides"]') {
  return new Promise((resolve) => {
    $(sel).on("init", (event) => {
      setTimeout(() => {
        resolve();
      }, 100);
    });
    setTimeout(() => {
      resolve();
    }, 5000);

    const slickSel = sel + ":not(.slick-initialized)";
    $(slickSel).slick({
      infinite: true,
      slidesToShow: 4,
      slidesToScroll: 4,
      lazyLoad: "ondemand",
      responsive: [
        {
          breakpoint: 991,
          settings: {
            slidesToShow: 2,
            slidesToScroll: 2,
          },
        },
        {
          breakpoint: 546,
          settings: {
            slidesToShow: 1,
            slidesToScroll: 1,
          },
        },
      ],
    });
  });
};

export const removeEmpty = function (arr) {
  if (!Array.isArray(arr)) return arr;
  return arr.filter((n) => n);
};

export const hasCartItems = function () {
  return (
    $('[data-js="cart-item-quantity"]').first() &&
    $('[data-js="cart-item-quantity"]').first().text() &&
    parseInt($('[data-js="cart-item-quantity"]').first().text()) > 0
  );
};

export const showLogin = function () {
  if (!$("body").hasClass("modal-open")) {
    $("#account-modal").modal("show");
  }
  $("#account-modal .nav-tabs .nav-link").removeClass("active");
  $('#account-modal a[href="#signin"]').tab("show");
  $("#nav-signin-tab").show().addClass("active");
};

export const showForgotPassword = function (e) {
  e.preventDefault();
  if (!$("body").hasClass("modal-open")) {
    $("#account-modal").modal("show");

    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
      event: "VirtualPageView",
      VirtualPageURL: "/forgot_password",
      VirtualPageTitle: "Forgot Password",
    });
  }
  $("#account-modal .nav-tabs .nav-link")
    .removeClass("active")
    .attr("aria-selected", false)
    .attr("tabindex", "-1");
  $('#account-modal a[href="#forgotpassword"]')
    .tab("show")
    .addClass("active")
    .attr("aria-selected", true)
    .attr("tabindex", "0");
};

export const showCreateAccount = function (e) {
  e.preventDefault();
  if (!$("body").hasClass("modal-open")) {
    $("#account-modal").modal("show");
  }
  $("#account-modal .nav-tabs .nav-link")
    .removeClass("active")
    .attr("aria-selected", false)
    .attr("tabindex", "-1");
  $('#account-modal a[href="#signup"]')
    .tab("show")
    .addClass("active")
    .attr("aria-selected", true)
    .attr("tabindex", "0");
};

export const showTrackOrder = function (e) {
  e.preventDefault();
  if (!$("body").hasClass("modal-open")) {
    $("#account-modal").modal("show");
  }
  $("#account-modal .nav-tabs .nav-link")
    .removeClass("active")
    .attr("aria-selected", false)
    .attr("tabindex", "-1");
  $('#account-modal a[href="#orderstatus"]')
    .tab("show")
    .addClass("active")
    .attr("aria-selected", true)
    .attr("tabindex", "0");
};

export const checkFieldValid = function (jqEl) {
  if (!jqEl || !$(jqEl)[0] || !("validity" in $(jqEl)[0])) return null;
  const el = $(jqEl)[0];
  el.setCustomValidity("");
  if (el.validity.valid) {
    $(jqEl).parent().addClass("isvalid");
    return true;
  } else {
    if ($(jqEl).attr("title")) el.setCustomValidity($(jqEl).attr("title"));
    if ($(jqEl).parent().hasClass("isvalid")) $(jqEl).parent().removeClass("isvalid");
    return false;
  }
};

export const fieldValidListener = function (sel) {
  // attach "live" and "custom" html5 form validation handler on each field matching selector
  if (!sel || !$(sel) || !$(sel).length) return false;

  $(sel).each((index, jqEl) => {
    // check for validity on first call
    const fieldValid = checkFieldValid(jqEl); // boolean OR null

    // fieldValid will be null if 'validity' is not on the element object (like, if it's not an input element)
    if (fieldValid !== null) {
      // listen for changes on field and reset custom invalid message, toggle validity styles
      $(jqEl).on("focusout change", function (e) {
        //console.log("event", $(this).attr("name"), e.type);
        checkFieldValid($(this));
      });

      // this dismisses any invalid messages when field is actively being used
      $(jqEl).on("keyup", function (e) {
        e.target.setCustomValidity("");
      });
    }
  });
};

export const signupHandler = function (formEl, reloadPage = false) {
  if (["/forgetme", "/logout", "/complete"].includes(window.location.pathname)) reloadPage = false;
  if ($(formEl).find(".error-card").is(":visible")) {
    $(formEl).find(".error-card").slideUp();
  }
  if (
    $(formEl).find('[name="bill_account_password"]').val() !==
    $(formEl).find('[name="bill_account_password_confirm"]').val()
  ) {
    $(formEl).find(".error-card .card-text").html("Passwords do not match");
    $(formEl).find(".error-card").slideDown();
    return false;
  }
  const btnId = $(formEl).find('button[type="submit"]').attr("id");
  spinButton(btnId, "SUBMITTING");
  $.ajax({
    url: "/store?action=ajax_newaccount",
    data: $(formEl).serialize(),
    dataType: "json",
    type: "POST",
    success: (data) => {
      if (data && data.success) {
        let message = "You are now signed up and logged in!";
        if (reloadPage) message += " Refreshing page...";
        flashMessage.show({
          message: message,
          alertType: "success",
          timeout: false,
        });
        if (["/forgetme", "/logout", "/complete"].includes(window.location.pathname)) {
          // if on one of these pages, redirect to account page.
          window.location.href = "/account";
        }
        if (reloadPage) {
          setTimeout(() => {
            window.location.reload();
          }, 1000);
        }
        unSpinButton(btnId, "SUCCESS!");
      } else {
        if ("errors" in data) {
          $(formEl).find(".error-card .card-text").html(data.errors.join(" "));
          $(formEl).find(".error-card").slideDown();
        }
        unSpinButton(btnId);
      }
    },
    error: (xhr, status, errorThrown) => {
      flashMessage.show({ message: messages.fatal });
      console.error("user signup", xhr, status, errorThrown);
      unSpinButton(btnId);
    },
  });
};

export const loginHandler = function (formEl, reloadPage = false) {
  if (["/forgetme", "/logout", "/complete"].includes(window.location.pathname)) reloadPage = false;
  if ($(formEl).find(".error-card").is(":visible")) {
    $(formEl).find(".error-card").slideUp();
  }
  const btnId = $(formEl).find('button[type="submit"]').attr("id");
  spinButton(btnId, "SUBMITTING");
  const client = getBodyData("data-client-id");
  $.ajax({
    url: `/store?action=ajax_login&client=${client}`,
    data: $(formEl).serialize(),
    dataType: "json",
    type: "POST",
    success: (data) => {
      if (data && data.success) {
        let message = "You are now logged in!";
        if (reloadPage) message += " Refreshing page...";
        flashMessage.show({
          message: message,
          alertType: "success",
          timeout: false,
        });
        if (["/forgetme", "/logout", "/complete"].includes(window.location.pathname)) {
          // if on one of these pages, redirect to account page.
          window.location.href = "/account";
        }
        if (reloadPage) {
          setTimeout(() => {
            window.location.reload();
          }, 1000);
        }
        unSpinButton(btnId, "SUCCESS!");
        setTimeout(() => {
          if ($("#account-modal").is(":visible")) $("#account-modal").modal("hide");
        }, 400);
      } else {
        if ("errors" in data) {
          $(formEl).find(".error-card .card-text").html(data.errors.join(", "));
          $(formEl).find(".error-card").slideDown();
        }
        unSpinButton(btnId);
      }
    },
    error: (xhr, status, errorThrown) => {
      flashMessage.show({ message: messages.fatal });
      console.error("user login", xhr, status, errorThrown);
      unSpinButton(btnId);
    },
  });
};

export const fullOrderId = function (orderId) {
  return /^[A-Za-z]/.test(orderId) ? `P${orderId}` : `${CFG.orderPrefix}${orderId}`;
};

export const fadeOut = function (el) {
  el.style.opacity = 1;

  (function fade() {
    if ((el.style.opacity -= 0.1) < 0) {
      el.style.display = "none";
    } else {
      requestAnimationFrame(fade);
    }
  })();
};

export const fadeIn = function (el, display) {
  el.style.opacity = 0;
  el.style.display = display || "block";

  (function fade() {
    var val = parseFloat(el.style.opacity);
    if (!((val += 0.1) > 1)) {
      el.style.opacity = val;
      requestAnimationFrame(fade);
    }
  })();
};

export const getFirstFocusable = function (scopeEl = document) {
  const focusable = scopeEl.querySelectorAll(
    'button, a, input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  return focusable[0];
};

export const isElementVisible = function (e) {
  // this is borrowed from jquery's .is(":visible")
  return !!(e.offsetWidth || e.offsetHeight || e.getClientRects().length);
};

/// apparently zendesk does not offer a close and dismiss chat button which clears the chat window AND widget icon
// here's a homebrew solution that places the close button in the chat window and listens for clicks on it
export const handleZendesk = function () {
  const closeChat = function (e) {
    zE("messenger", "close");
    zE("messenger", "hide");
    const closeBtn = document.getElementById("zd-chat-close");
    closeBtn.remove();
  };
  setTimeout(() => {
    const referenceEl = document.querySelector('[title="Messaging window"]');
    if (!referenceEl) return;

    const containerHeight = referenceEl.offsetHeight;
    const containerWidth = referenceEl.offsetWidth;
    const windowHeight = window.innerHeight || document.documentElement.clientHeight;
    const windowWidth = window.innerWidth;
    const widthAdjustment = windowWidth > containerWidth ? 0 : 10;
    const heightAdjustment = windowHeight > containerHeight ? 30 : 50;

    document.body.appendChild(
      Object.assign(document.createElement("button"), {
        id: "zd-chat-close",
        type: "button",
        className: "close",
        ariaLabel: "Close Chat",
        style: `position: fixed; bottom: ${containerHeight - heightAdjustment}px; right: ${
          22 - widthAdjustment
        }px; z-index: 9999999`,
        innerHTML: `
          <div style="width: 30px; height: 30px; border: 1px solid gray; border-radius: 50%; background-color: white; display: flex; justify-content: center; align-items: center;">
          <i class="fa fa-times" style="color: gray"></i>
        </div>
        `,
      })
    );
    const closeBtn = document.getElementById("zd-chat-close");
    if (closeBtn && !closeBtn.hasEventListener) {
      closeBtn.hasEventListener = true;
      closeBtn.addEventListener("click", closeChat, false);
    }
  }, 1000);
};

export const fetchJson = function (endpoint) {
  //console.log("trying to fetch", endpoint, createHeaders());
  return new Promise((resolve, reject) => {
    fetch(endpoint, { headers: createHeaders(), credentials: "same-origin" })
      .then((r) => {
        //console.log("R", r);
        return r.json();
      })
      .then((r) => resolve(r))
      .catch((e) => {
        //console.error("fetchJson failed for endpoint", endpoint, e);
        reject(e);
      });
  });
};

export const fetchContent = function (endpoint) {
  return new Promise((resolve, reject) => {
    fetch(endpoint, { credentials: "same-origin" })
      .then((r) => r.text())
      .then((r) => resolve(r))
      .catch((e) => {
        //console.error("fetchContent failed for endpoint", endpoint, e);
        reject(e);
      });
  });
};

export const createHeaders = function (headers = {}) {
  if (!("Content-Type" in headers)) headers["Content-Type"] = "application/json";
  headers["X-Requested-With"] = "XMLHttpRequest";
  //console.log("HEADERS", headers);
  return headers;
};

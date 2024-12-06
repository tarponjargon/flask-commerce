//import { ssAfterResults } from "../services/AfterResults";

import Recommendations from "../services/Recommendations";
import { waitForSelector } from "../services/Utils";

export default class SearchView {
  constructor() {}
  init = (view) => {
    return new Promise((resolve) => {
      // this.loadAsyncRecs();
      resolve(view);
    });
  };

  loadAsyncRecs = () => {
    // check for recs container
    waitForSelector("#recs-container")
      .then(() => {
        const oldCertonaContainer = document.querySelector(".certona-carousel");
        if (oldCertonaContainer) {
          oldCertonaContainer.remove();
        }
        if (window.afterLoad) {
          window.afterLoad("kppRecs", function () {
            let recs = new Recommendations();
            recs.init();
          });
        }
      })
      .catch((e) => {});
  };
}

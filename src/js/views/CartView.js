import CartUpsell from "../services/CartUpsell";
import { quantityChangeListeners, persListeners, giftListeners } from "../services/CheckoutUtils";

export default class CartView {
  constructor() {}
  init = (view) => {
    return new Promise((resolve) => {
      quantityChangeListeners();
      giftListeners();
      persListeners();
      this.upsell = new CartUpsell();
      this.upsell.init();
      resolve(view);
    });
  };
} // end CartView class

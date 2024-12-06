import { spinButton, unSpinButton } from "../services/Utils";

export default class ReceiptLookupView {
  constructor() {}
  init = (view) => {
    return new Promise((resolve) => {
      $(`[data-js="receipt-lookup"]`).on("submit", (e) => {
        e.preventDefault();
        this.handleSubmit(e);
      });
      resolve(view);
    });
  };

  handleSubmit = (e) => {
    if ($("#receipt-errors").is(":visible")) {
      $("#receipt-errors").slideUp();
    }
    if ($("#receipt-success").is(":visible")) {
      $("#receipt-success").slideUp();
    }
    const buttonId = $(e.currentTarget).find("button").attr("id");
    spinButton(buttonId, "");
    fetch("/api/receipt", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "content-type": "application/x-www-form-urlencoded",
      },
      body: $(e.currentTarget).serialize(),
    })
      .then((r) => r.json())
      .then((data) => {
        if ("errors" in data) {
          unSpinButton(buttonId);
          $("#receipt-errors .card-text").text(data.errors.join(", "));
          $("#receipt-errors").slideDown();
        } else if ("orderId" in data) {
          window.location.href = `/receipt/${data.orderId}`;
        } else if ("orders" in data) {
          if (data.orders.length === 1) {
            window.location.href = `/receipt/${data.orders[0].orderId}`;
          } else {
            let orderListHtml = "<ul>";
            data.orders.forEach((order) => {
              orderListHtml += `
              <li>
                <a class="text-white" href="/receipt/${order.orderId}">${order.orderId} - ${order.date}</a>
              </li>`;
            });
            orderListHtml += "</ul>";
            $("#receipt-success .card-text").html(orderListHtml);
            $("#receipt-success").slideDown();
          }
        } else {
          $("#receipt-errors .card-text").text("No orders found");
          $("#receipt-errors").slideDown();
        }
      })
      .catch((e) => {
        unSpinButton(buttonId);
        console.error("receipt lookup fail");
        $("#receipt-errors .card-text").text("Problem with order lookup");
        $("#receipt-errors").slideDown();
      });
  };
}

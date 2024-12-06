""" API routes related to customer e-mail subscriptions """

from datetime import datetime
import json
from flask import Blueprint, Response, request, current_app, render_template
from flask_app.modules.email import send_email
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import validate_email
from flask_app.modules.http import api_route_error, get_env_vars
from flask_app.modules.legacy.customer_activity import record_customer_activity
from urllib.parse import parse_qs

from flask_app.modules.subscription import update_subscription


mod = Blueprint("subscription_api", __name__)


@mod.route("/api/optchange", methods=["POST"])
def do_optchange():
    """Handle subscribe and unsubscribe form submits"""

    bill_email = request.form.get("bill_email")
    optin = request.form.get("optin")
    request_type = request.form.get("request")
    frequency = request.form.get("frequency")

    if not bill_email or not validate_email(bill_email):
        return api_route_error("Please enter a valid e-mail", 400)

    if not optin in ["yes", "no"]:
        return api_route_error("Please select a subscription preference", 400)

    exists = update_subscription(bill_email, optin, frequency)

    record_customer_activity(
        email=bill_email,
        email_exists=exists,
        optin=optin,
        request_type=request_type,
        capture="N",
        opt_only="0",
        mail_frequency=frequency,
        ins_or_upd="INSERT" if exists == "0" else "UPDATE",
        send_welcome_email="0",
    )

    return {"success": True, "error": False}


@mod.route("/process_email_capture", methods=["POST"])
def do_capture_optin():
    """A legacy endpoint for the e-mail capture modal.  Subscribes the passed email.

    Returns:
      list: List with a single element, a dict.  the dict has result key
        which is a string, "0" (email does not exist) or "1" (email does exist)

    Example:
      [ {"result":"0"} ]
    """

    # The front end /may not/ send a form header (which would result in the params being added to request.form).
    # If not, the data is parsed directly.
    form_data = {}
    if request.form:
        form_data = request.form
    else:
        if request.content_length < 2000:  # safety measure
            data = request.get_data(as_text=True)
            params = parse_qs(data)
            form_data = {k: v[0] for k, v in params.items()}

    if not form_data:
        return api_route_error("Problem opting in e-mail", 500)

    bill_email = form_data.get("bill_email")
    capture = form_data.get("capture", "Y")
    request_type = form_data.get("request") if form_data.get("request") else "optinrequest"
    email_exists = "0"
    send_welcome_email = 0
    datestr = datetime.now().strftime("%Y-%m-%d")
    datetimestr = datetime.now().strftime("%Y%m%d%H%M%S")
    ins_or_upd = ""

    if not bill_email or not validate_email(bill_email):
        return api_route_error("Please enter a valid e-mail", 400)

    existing = DB.fetch_one(
        """
          SELECT customer_id, optin
          FROM customers
          WHERE bill_email LIKE %(bill_email)s
        """,
        {"bill_email": bill_email},
    )

    if not existing:
        ins_or_upd = "INSERT"
        email_exists = "0"
        id = DB.insert_query(
            """
              INSERT INTO customers SET
              bill_email = %(bill_email)s,
              optin = 'yes',
              capture = %(capture)s,
              ins_or_upd = %(ins_or_upd)s,
              insert_date = %(datetimestr)s,
              `date` = %(datestr)s
            """,
            {
                "bill_email": bill_email,
                "capture": capture,
                "ins_or_upd": ins_or_upd,
                "datetimestr": datetimestr,
                "datestr": datestr,
            },
        )
        if id:
            send_welcome_email = 1
        else:
            return api_route_error("Problem adding e-mail", 400)

    elif existing["optin"] == "no":
        ins_or_upd = "UPDATE"
        email_exists = "0"
        success = DB.update_query(
            """
              UPDATE customers SET
              optin = 'yes',
              ins_or_upd = %(ins_or_upd)s,
              `date` = %(datestr)s
              WHERE customer_id = %(customer_id)s
              LIMIT 1
            """,
            {"ins_or_upd": ins_or_upd, "datestr": datestr, "customer_id": existing["customer_id"]},
        )
        if success:
            send_welcome_email = 1
        else:
            return api_route_error("Problem opting in e-mail", 500)

    else:
        email_exists = "1"
        ins_or_upd = "UPDATE"
        success = DB.update_query(
            """
              UPDATE customers SET
              ins_or_upd = %(ins_or_upd)s,
              `date` = %(datestr)s
              WHERE customer_id = %(customer_id)s
              LIMIT 1
            """,
            {"ins_or_upd": ins_or_upd, "datestr": datestr, "customer_id": existing["customer_id"]},
        )

    record_customer_activity(
        email=bill_email,
        email_exists=email_exists,
        optin="yes",
        request_type=request_type,
        capture=capture,
        opt_only="1",
        ins_or_upd=ins_or_upd,
        send_welcome_email=send_welcome_email,
    )

    # do not send welcome email anymore per colleen cardarella's request 7/9/24 - they go out of SNHQ
    # if send_welcome_email and not "testemail.com" in bill_email:
    #     send_email(
    #         subject=f"Welcome to {current_app.config['STORE_NAME']}",
    #         sender=current_app.config["STORE_EMAIL"],
    #         recipients=[bill_email],
    #         reply_to=current_app.config["DEFAULT_MAIL_SENDER"],
    #         text_body=render_template("emails/welcome_email.txt.j2"),
    #         html_body=render_template("emails/welcome_email.html.j2", email=bill_email),
    #     )

    # workaround for Flask not allowing lists as the top level in json
    return Response(json.dumps([{"result": email_exists}]), mimetype="application/json")

""" Contact form related API routes """

from flask import Blueprint, request, current_app, session, render_template
from flask_app.modules.extensions import DB
from flask_app.modules.http import get_env_vars
from flask_app.modules.legacy.customer_activity import record_customer_activity
from flask_app.modules.email import send_email
from flask_app.modules.subscription import update_subscription
from flask_app.modules.helpers import validate_email

mod = Blueprint("contact_api", __name__, url_prefix="/api")


@mod.route("/contact", methods=["POST"])
def do_contact_request():
    """
    Handles the contact form requests.
    """

    # honeypot.  if email_again param has a value, it's a bot.  fake a success response
    if request.form.get("email_again"):
        return {"success": True, "error": False}

    errors = []
    env_vars = get_env_vars()

    # proxy for optin, workaround for using a checkbox for subscription preference
    optpref = request.form.get("optpref")
    optin = optpref if (optpref and optpref in ["yes", "no"]) else "no"
    session["optpref"] = None

    model = [
        {"key": "bill_fname", "name": "First Name", "required": True, "value": None},
        {"key": "bill_lname", "name": "Last Name", "required": True, "value": None},
        {"key": "bill_email", "name": "E-Mail", "required": True, "value": None},
        {"key": "info_request_type", "name": "Request Type", "required": True, "value": None},
        {"key": "info_request_subject_order", "name": "Order Request", "required": False, "value": None},
        {"key": "info_request_subject_inquiry", "name": "General Request", "required": False, "value": None},
        {"key": "ordno", "name": "Order #", "required": False, "value": None},
        {"key": "request_body", "name": "Request", "required": True, "value": None},
        {"key": "optin", "name": "Opt-In", "required": False, "value": optin},
        {"key": "client", "name": "client", "required": False, "value": env_vars.get("session_id")},
        {"key": "remote_addr", "name": "IP", "required": False, "value": env_vars.get("ip_address")},
        {"key": "http_user_agent", "name": "UA", "required": False, "value": env_vars.get("user_agent")},
        {"key": "date", "name": "date", "required": False, "value": env_vars.get("date")},
    ]

    # loop model and use 'code' as key for retrieving form data.
    for field in model:
        field["value"] = request.form.get(field["key"], field["value"])
        if not field["value"] and field["required"]:
            errors.append(f"Please enter a value for {field['name']}")

    if len(errors):
        return {"success": False, "error": True, "errors": errors}

    # build the SET key = 'value' SQL from the model
    sql_values = ", ".join([f"{i['key']} = %s" for i in model])
    sql_params = [i["value"] for i in model]
    sql = f"INSERT INTO info_requests SET {sql_values}"

    id = DB.insert_query(sql, sql_params)
    if not id:
        current_app.logger.error(f"Problem inserting contact request {sql}")
        return {"success": False, "error": True, "errors": ["Problem adding request.  Please contact us."]}

    email_exists = update_subscription(request.form.get("bill_email"), optin)
    record_customer_activity(
        request_type="inforequest",
        ins_or_upd="INSERT" if email_exists == "0" else "UPDATE",
        email_exists=email_exists,
    )

    from_email = request.form.get("bill_email") if validate_email(request.form.get("bill_email")) else current_app.config["STORE_EMAIL"]
    # send email to customer service
    send_email(
        subject=f" {current_app.config['STORE_NAME']} Customer Inquiry",
        sender=from_email,
        recipients=[current_app.config["STORE_CS_EMAIL"]],
        reply_to=from_email,
        text_body=render_template("emails/contact.txt.j2", model=model),
    )

    return {"success": True, "error": False}

""" Catalog request API routes """

from flask import Blueprint, request, current_app
from flask_app.modules.extensions import DB
from flask_app.modules.http import get_env_vars, session_get
from flask_app.modules.legacy.customer_activity import record_customer_activity
from flask_app.modules.subscription import update_subscription
from flask_app.modules.user import get_id_by_email

mod = Blueprint("catalogrequest_api", __name__, url_prefix="/api")


@mod.route("/catalogrequest", methods=["POST"])
def do_catalog_request():
    """Handles the catalogrequest form requests"""

    # honeypot.  if email_again param has a value, it's a bot.  fake a success response
    if request.form.get("email_again"):
        return {"success": True, "error": False}

    errors = []
    env_vars = get_env_vars()

    model = [
        {"key": "bill_fname", "name": "First Name", "required": True, "value": None},
        {"key": "bill_lname", "name": "Last Name", "required": True, "value": None},
        {"key": "bill_street", "name": "Address 1", "required": True, "value": None},
        {"key": "bill_street2", "name": "Address 2", "required": False, "value": None},
        {"key": "bill_city", "name": "City", "required": True, "value": None},
        {"key": "bill_state", "name": "State", "required": True, "value": None},
        {"key": "bill_country", "name": "Country", "required": False, "value": "USA"},
        {"key": "bill_postal_code", "name": "Zip Code", "required": True, "value": None},
        {"key": "bill_email", "name": "E-Mail", "required": False, "value": None},
        {"key": "optin", "name": "Opt-In", "required": False, "value": None},
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

    sql = f"INSERT INTO catalog_requests SET {sql_values}"

    id = DB.insert_query(sql, sql_params)
    if not id:
        current_app.logger.error(f"Problem inserting catalog request {sql}")
        return {"success": False, "error": True, "errors": ["Problem adding catalogrequest.  Please contact us."]}

    # if the email doesn't exist in the customers table, default optin to 'yes'
    email_exists = 1 if get_id_by_email(request.form.get("bill_email")) else 0
    if not email_exists:
        update_subscription(request.form.get("bill_email"), "yes")

    record_customer_activity(
        request_type="catalogrequest",
        ins_or_upd="INSERT" if email_exists == "0" else "UPDATE",
        email_exists=email_exists,
    )

    return {"success": True, "error": False}

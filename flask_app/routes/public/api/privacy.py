""" API routes related to privacy form requests """

from flask import Blueprint, request, current_app, render_template
from flask_app.modules.extensions import DB
from flask_app.modules.http import get_env_vars
from flask_app.modules.legacy.customer_activity import record_customer_activity
from flask_app.modules.email import send_email
from flask_app.modules.http import page_not_found

mod = Blueprint("privacy_api", __name__, url_prefix="/api")


@mod.route("/ca-privacy-request", methods=["POST"])
def do_ca_privacy_request():
    """Handles the CA privacy request form requests"""

    return page_not_found(None)

    errors = []
    env_vars = get_env_vars()

    # honeypot.  if email_again param has a value, it's a bot.  fake a success response
    if request.form.get("email_again"):
        return {"success": True, "error": False}

    model = [
        {"key": "bill_fname", "name": "First Name", "required": True, "value": None},
        {"key": "bill_lname", "name": "Last Name", "required": True, "value": None},
        {"key": "bill_street", "name": "Address 1", "required": True, "value": None},
        {"key": "bill_street2", "name": "Address 2", "required": False, "value": None},
        {"key": "bill_city", "name": "City", "required": True, "value": None},
        {"key": "bill_state", "name": "State", "required": True, "value": None},
        {
            "key": "bill_postal_code",
            "name": "Zip Code",
            "required": True,
            "value": None,
        },
        {
            "key": "client",
            "name": "client",
            "required": False,
            "value": env_vars.get("session_id"),
        },
        {
            "key": "remote_addr",
            "name": "IP",
            "required": False,
            "value": env_vars.get("ip_address"),
        },
        {
            "key": "http_user_agent",
            "name": "UA",
            "required": False,
            "value": env_vars.get("user_agent"),
        },
        {
            "key": "date",
            "name": "date",
            "required": False,
            "value": env_vars.get("date"),
        },
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
    sql = "INSERT INTO privacy_requests SET " + sql_values

    id = DB.insert_query(sql, sql_params)
    if not id:
        current_app.logger.error(f"Problem inserting privacy request {sql}")
        return {
            "success": False,
            "error": True,
            "errors": ["Problem adding request.  Please contact us."],
        }

    record_customer_activity(request_type="caprivacyrequest")

    return {"success": True, "error": False}


@mod.route("/ca-subject-request", methods=["POST"])
def do_ca_subject_request():
    """Handles the CA privacy act request form requests."""

    return page_not_found(None)

    # honeypot.  if email_again param has a value, it's a bot.  fake a success response
    if request.form.get("email_again"):
        return {"success": True, "error": False}

    errors = []
    env_vars = get_env_vars()

    # honeypot.  if email_again param has a value, it's a bot.  fake a success response
    if request.form.get("email_again"):
        return {"success": True, "error": False}

    model = [
        {"key": "bill_fname", "name": "First Name", "required": True, "value": None},
        {"key": "bill_lname", "name": "Last Name", "required": True, "value": None},
        {"key": "bill_street", "name": "Address 1", "required": True, "value": None},
        {"key": "bill_street2", "name": "Address 2", "required": False, "value": None},
        {"key": "bill_city", "name": "City", "required": True, "value": None},
        {"key": "bill_state", "name": "State", "required": True, "value": None},
        {
            "key": "bill_postal_code",
            "name": "Zip Code",
            "required": True,
            "value": None,
        },
        {
            "key": "disclosure_request",
            "name": "Disclosure Request",
            "required": False,
            "value": None,
        },
        {
            "key": "specific_disclosure_request",
            "name": "Specific Disclosure Request",
            "required": False,
            "value": None,
        },
        {
            "key": "correction_request",
            "name": "Correction Request",
            "required": False,
            "value": None,
        },
        {
            "key": "deletion_request",
            "name": "Deletion Request",
            "required": False,
            "value": None,
        },
        {
            "key": "client",
            "name": "client",
            "required": False,
            "value": env_vars.get("session_id"),
        },
        {
            "key": "remote_addr",
            "name": "IP",
            "required": False,
            "value": env_vars.get("ip_address"),
        },
        {
            "key": "http_user_agent",
            "name": "UA",
            "required": False,
            "value": env_vars.get("user_agent"),
        },
        {
            "key": "date",
            "name": "date",
            "required": False,
            "value": env_vars.get("date"),
        },
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
    sql = "INSERT INTO subject_requests SET " + sql_values

    id = DB.insert_query(sql, sql_params)
    if not id:
        current_app.logger.error(f"Problem inserting CA subject request {sql}")
        return {
            "success": False,
            "error": True,
            "errors": ["Problem adding request.  Please contact us."],
        }

    record_customer_activity(request_type="casubjectrequest")

    return {"success": True, "error": False}


@mod.route("/data-request-appeal", methods=["POST"])
def do_data_request_appeal_request():
    """Handles the data request appeal form"""

    return page_not_found(None)

    errors = []
    env_vars = get_env_vars()

    # honeypot.  if email_again param has a value, it's a bot.  fake a success response
    if request.form.get("email_again"):
        return {"success": True, "error": False}

    model = [
        {"key": "bill_fname", "name": "First Name", "required": True, "value": None},
        {"key": "bill_lname", "name": "Last Name", "required": True, "value": None},
        {"key": "bill_street", "name": "Address 1", "required": True, "value": None},
        {"key": "bill_street2", "name": "Address 2", "required": False, "value": None},
        {"key": "bill_city", "name": "City", "required": True, "value": None},
        {"key": "bill_state", "name": "State", "required": True, "value": None},
        {
            "key": "bill_postal_code",
            "name": "Zip Code",
            "required": True,
            "value": None,
        },
        {
            "key": "client",
            "name": "client",
            "required": False,
            "value": env_vars.get("session_id"),
        },
        {
            "key": "remote_addr",
            "name": "IP",
            "required": False,
            "value": env_vars.get("ip_address"),
        },
        {
            "key": "http_user_agent",
            "name": "UA",
            "required": False,
            "value": env_vars.get("user_agent"),
        },
        {
            "key": "date",
            "name": "date",
            "required": False,
            "value": env_vars.get("date"),
        },
    ]

    # loop model and use 'code' as key for retrieving form data.
    for field in model:
        field["value"] = request.form.get(field["key"], field["value"])
        if not field["value"] and field["required"]:
            errors.append(f"Please enter a value for {field['name']}")

    if len(errors):
        return {"success": False, "error": True, "errors": errors}

    sql_values = ", ".join([f"{i['key']} = %s" for i in model])
    sql_params = [i["value"] for i in model]
    sql = "INSERT INTO data_request_appeal SET " + sql_values

    id = DB.insert_query(sql, sql_params)
    if not id:
        current_app.logger.error(f"Problem inserting data-request-appeal {sql}")
        return {
            "success": False,
            "error": True,
            "errors": ["Problem adding request.  Please contact us."],
        }

    record_customer_activity(request_type="datarequestappeal")

    return {"success": True, "error": False}


@mod.route("/do-not-rent", methods=["POST"])
def do_not_rent_request():
    """Handles the "do not rent" form"""

    return page_not_found(None)

    errors = []
    env_vars = get_env_vars()

    # honeypot.  if email_again param has a value, it's a bot.  fake a success response
    if request.form.get("email_again"):
        return {"success": True, "error": False}

    model = [
        {"key": "bill_fname", "name": "First Name", "required": True, "value": None},
        {"key": "bill_lname", "name": "Last Name", "required": True, "value": None},
        {"key": "bill_street", "name": "Address 1", "required": True, "value": None},
        {"key": "bill_street2", "name": "Address 2", "required": False, "value": None},
        {"key": "bill_city", "name": "City", "required": True, "value": None},
        {"key": "bill_state", "name": "State", "required": True, "value": None},
        {
            "key": "bill_postal_code",
            "name": "Zip Code",
            "required": True,
            "value": None,
        },
        {
            "key": "client",
            "name": "client",
            "required": False,
            "value": env_vars.get("session_id"),
        },
        {
            "key": "remote_addr",
            "name": "IP",
            "required": False,
            "value": env_vars.get("ip_address"),
        },
        {
            "key": "http_user_agent",
            "name": "UA",
            "required": False,
            "value": env_vars.get("user_agent"),
        },
        {
            "key": "date",
            "name": "date",
            "required": False,
            "value": env_vars.get("date"),
        },
    ]

    # loop model and use 'code' as key for retrieving form data.
    for field in model:
        field["value"] = request.form.get(field["key"], field["value"])
        if not field["value"] and field["required"]:
            errors.append(f"Please enter a value for {field['name']}")

    if len(errors):
        return {"success": False, "error": True, "errors": errors}

    sql_values = ", ".join([f"{i['key']} = %s" for i in model])
    sql_params = [i["value"] for i in model]
    sql = "INSERT INTO donotrent_requests SET " + sql_values

    id = DB.insert_query(sql, sql_params)
    if not id:
        current_app.logger.error(f"Problem inserting do-not-rent {sql}")
        return {
            "success": False,
            "error": True,
            "errors": ["Problem adding request.  Please contact us."],
        }

    record_customer_activity(request_type="donotrent")

    return {"success": True, "error": False}


@mod.route("/accessibility-request", methods=["POST"])
def do_accessibility_request():
    """Handles the "do not rent" form"""

    return page_not_found(None)

    errors = []
    env_vars = get_env_vars()

    # honeypot.  if email_again param has a value, it's a bot.  fake a success response
    if request.form.get("email_again"):
        return {"success": True, "error": False}

    model = [
        {"key": "bill_fname", "name": "First Name", "required": True, "value": None},
        {"key": "bill_lname", "name": "Last Name", "required": True, "value": None},
        {"key": "bill_email", "name": "E-Mail", "required": True, "value": None},
        {"key": "request_body", "name": "Request", "required": True, "value": None},
        {
            "key": "client",
            "name": "client",
            "required": False,
            "value": env_vars.get("session_id"),
        },
        {
            "key": "remote_addr",
            "name": "IP",
            "required": False,
            "value": env_vars.get("ip_address"),
        },
        {
            "key": "http_user_agent",
            "name": "UA",
            "required": False,
            "value": env_vars.get("user_agent"),
        },
        {
            "key": "date",
            "name": "date",
            "required": False,
            "value": env_vars.get("date"),
        },
    ]

    # loop model and use 'code' as key for retrieving form data.
    for field in model:
        field["value"] = request.form.get(field["key"], field["value"])
        if not field["value"] and field["required"]:
            errors.append(f"Please enter a value for {field['name']}")

    if len(errors):
        return {"success": False, "error": True, "errors": errors}

    sql_values = ", ".join([f"{i['key']} = %s" for i in model])
    sql_params = [i["value"] for i in model]
    sql = "INSERT INTO accessibility_requests SET " + sql_values

    id = DB.insert_query(sql, sql_params)
    if not id:
        current_app.logger.error(f"Problem inserting accessibility request {sql}")
        return {
            "success": False,
            "error": True,
            "errors": ["Problem adding request.  Please contact us."],
        }

    record_customer_activity(request_type="accessibilityrequest")

    # send email to customer service
    send_email(
        subject=f" {current_app.config['STORE_NAME']} Digital Accessibility Request",
        sender=current_app.config["STORE_EMAIL"],
        recipients=[current_app.config["STORE_ACCESSIBILITY_CONTACT"]],
        reply_to=current_app.config["DEFAULT_MAIL_SENDER"],
        text_body=render_template("emails/contact.txt.j2", model=model),
    )

    return {"success": True, "error": False}

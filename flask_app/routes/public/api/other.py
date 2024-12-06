""" API rotues that don't fit anywhere else """
import os
from flask_app.modules.extensions import DB
from flask_app.modules.email import send_email
from flask import Blueprint, render_template, Response, request, current_app
from flask_app.modules.regions import get_countries, get_states
from flask_app.modules.extensions import cache
from flask_app.modules.helpers import do_cache_clear, do_category_count, do_file_sync, validate_email, do_search_feed_count
from flask_app.modules.legacy.customer_activity import record_customer_activity
from flask_app.modules.http import get_env_vars, api_route_error
from flask_app.modules.product.slugify import slugify_all_products

mod = Blueprint("other_api", __name__, url_prefix="/api")


@mod.route("/states")
def do_get_states():
    """Returns a list of state objects as JSON"""
    return {"states": get_states(), "countries": get_countries()}


@mod.route("/countries")
def do_get_countries():
    """Returns a list of country objects as JSON"""
    return {"countries": get_countries()}


@mod.route("/moonglow")
def do_moonglow_json():
    """Returns a list of moonglow jewelry dates-to-images"""
    return Response(render_template("includes/moonglow.json"), mimetype="application/json")


@mod.route("/clear_cache")
def do_get_clear_cache():
    """clears the memoized/cached items"""
    resp = do_cache_clear()
    resp2 = slugify_all_products()

    return {
        "cache": resp,
        "slugify": {
          "new paths": resp2[0],
          "errors": resp2[1],
        }
    }




@mod.route("/category_count")
def do_get_category_count():
    """counts items in categories and calcs bestsellers"""
    resp = do_category_count()

    return resp

@mod.route("/search_count")
def do_get_do_search_feed_count():
    """counts lines in search feed for testing purposes.  also used for monitoring."""
    return {
      "lines": do_search_feed_count(),
    }


@mod.route("/sync")
def do_get_file_sync():
    """syncs files from fileserver to webserver(s)"""
    resp = do_file_sync()

    return resp

@mod.route("/reader-review", methods=["POST"])
def do_add_reder_review():
    """Handles the "reader review" form"""
    if current_app.config.get("STORE_CODE") != 'basbleu2':
      return api_route_error("Not found")
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
        {"key": "bill_postal_code", "name": "Zip Code", "required": True, "value": None},
        {"key": "your_book_title", "name": "Book Title", "required": True, "value": None},
        {"key": "your_book_author", "name": "Book Author", "required": True, "value": None},
        {"key": "your_review", "name": "Your Review", "required": True, "value": None},
        {"key": "date", "name": "date", "required": False, "value": env_vars.get("date")},
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
    sql = "INSERT INTO your_review SET " + sql_values

    id = DB.insert_query(sql, sql_params)
    if not id:
        current_app.logger.error(f"Problem inserting your review {sql}")
        return {"success": False, "error": True, "errors": ["Problem adding request.  Please contact us."]}

    record_customer_activity(request_type="readerreview")

    from_email = request.form.get("bill_email") if validate_email(request.form.get("bill_email")) else current_app.config["STORE_EMAIL"]
    # send email to customer service
    send_email(
        subject=f" {current_app.config['STORE_NAME']} Reader Review",
        sender=from_email,
        recipients=['editors@basbleu.com'],
        reply_to=from_email,
        text_body=render_template("emails/contact.txt.j2", model=model),
    )

    return {"success": True, "error": False}
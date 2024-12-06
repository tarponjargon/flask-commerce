""" Functions related to e-mail subscriptions """

from flask import current_app
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import validate_email
from flask_app.modules.http import get_env_vars


def update_subscription(bill_email, optin, frequency=None):
    """Updates the customer subscription preference in the customers table.  Inserts if not existing.

    Args:
      bill_email (str): The email address to update
      optin (str): The preference, "yes" or "no"
      frequency (str): if passed, one of "1W", "2M", "PO", "All"

    Returns:
      str: "0" if the email did not exist and was inserted.  "1" if the email was updated

    TODO: Figure out a way to properly return errors
    """

    email_exists = "0"
    env_vars = get_env_vars()

    if not bill_email or not isinstance(bill_email, str) or not bill_email.strip() or not validate_email(bill_email.strip()):
        return None

    bill_email = bill_email.strip()

    if not optin in ["yes", "no"]:
        return None

    existing = DB.fetch_one(
        """
          SELECT customer_id, optin, mail_frequency
          FROM customers
          WHERE bill_email LIKE %(bill_email)s
        """,
        {"bill_email": bill_email},
    )

    # set frequency, if available
    if not frequency and existing and existing["mail_frequency"]:
        frequency = existing["mail_frequency"]

    if not frequency or not frequency in ["1W", "2M", "PO", "All"]:
        frequency = "All"

    if not existing:
        ins_or_upd = "INSERT"
        email_exists = "0"
        id = DB.insert_query(
            """
              INSERT INTO customers SET
              bill_email = %(bill_email)s,
              optin = %(optin)s,
              capture = 'N',
              ins_or_upd = %(ins_or_upd)s,
              mail_frequency = %(frequency)s,
              insert_date = %(ts)s,
              `date` = %(dt)s
            """,
            {
                "bill_email": bill_email,
                "optin": optin,
                "ins_or_upd": ins_or_upd,
                "frequency": frequency,
                "ts": env_vars.get("timestamp"),
                "dt": env_vars.get("date"),
            },
        )
        if not id:
            current_app.logger.error(f"problem inserting {bill_email} into customers")
            return None

    else:
        email_exists = "1"
        ins_or_upd = "UPDATE"
        success = DB.update_query(
            """
              UPDATE customers SET
              optin = %(optin)s,
              capture = 'N',
              ins_or_upd = %(ins_or_upd)s,
              mail_frequency = %(frequency)s,
              timestamp = NOW(),
              `date` = %(dt)s
              WHERE customer_id = %(customer_id)s
              LIMIT 1
            """,
            {
                "optin": optin,
                "ins_or_upd": ins_or_upd,
                "frequency": frequency,
                "dt": env_vars.get("date"),
                "customer_id": existing["customer_id"],
            },
        )
        if not success:
          # this is LIKELY due to a dupe request for which no rows will be updated (sesscess is Falsey)
          # as a backstop, query customers and make sure the optin value is the same as what was chosen
          customer = DB.fetch_one("SELECT optin FROM customers WHERE bill_email = %(bill_email)s", { 'bill_email': bill_email })
          if not customer or not customer.get('optin') or not optin == customer.get('optin'):
            current_app.logger.error(f"problem updating {bill_email} opt preference to {optin}")
            return None

    return email_exists

""" Functions related to recording customer actions on the site """

from flask import request, current_app, session
from flask_app.modules.extensions import DB
from flask_app.modules.http import get_env_vars, session_get


def record_customer_activity(**kwargs):
    """Records the customer action.  Like, optinrequest, optoutrequest, etc.  Also associated data
    like IP addr, customer id, utm params.

    Args:
      dict: the keyword args

    Returns:
      None
    """

    env_vars = get_env_vars()

    request_type = kwargs.get("request_type") if kwargs.get("request_type") else session_get("request")
    email = kwargs.get("email") if kwargs.get("email") else session_get("bill_email")
    optin = kwargs.get("optin") if kwargs.get("optin") else session_get("optin")
    opt_only = kwargs.get("opt_only") if kwargs.get("opt_only") else session_get("opt_only")
    mail_frequency = kwargs.get("mail_frequency") if kwargs.get("mail_frequency") else session_get("frequency")
    email_exists = kwargs.get("email_exists") if kwargs.get("email_exists") else ""
    ins_or_upd = kwargs.get("ins_or_upd") if kwargs.get("ins_or_upd") else ""
    capture = kwargs.get("capture") if kwargs.get("capture") else ""
    new_account = kwargs.get("new_account") if kwargs.get("new_account") else ""
    send_welcome_email = kwargs.get("send_welcome_email") if kwargs.get("send_welcome_email") else ""

    q = """
      INSERT INTO customer_activity SET
        customer_id = %(customer_id)s,
        uid = '',
        universal_uid = '',
        bill_email = %(email)s,
        email_exists = %(email_exists)s,
        optin = %(optin)s,
        ins_or_upd = %(ins_or_upd)s,
        capture = %(capture)s,
        request = %(request_type)s,
        new_account = %(new_account)s,
        opt_only = %(opt_only)s,
        mail_frequency = %(mail_frequency)s,
        send_welcome_email = %(send_welcome_email)s,
        howfound = %(howfound)s,
        howfound2 = %(howfound2)s,
        remote_addr = %(remote_addr)s,
        http_user_agent = %(user_agent)s,
        utm_source = %(utm_source)s,
        utm_medium = %(utm_medium)s,
        utm_campaign = %(utm_campaign)s,
        utm_term = %(utm_term)s,
        utm_content = %(utm_content)s,
        referer = %(referer)s,
        current_url = %(current_url)s,
        client = %(client)s,
        action_history = %(action_history)s
    """
    params = {
        "customer_id": session_get("customer_id", ""),
        "email": email,
        "email_exists": email_exists,
        "optin": optin,
        "ins_or_upd": ins_or_upd,
        "capture": capture,
        "request_type": request_type,
        "new_account": new_account,
        "opt_only": opt_only,
        "mail_frequency": mail_frequency,
        "send_welcome_email": send_welcome_email,
        "howfound": session_get("howfound", ""),
        "howfound2": session_get("howfound2"),
        "remote_addr": env_vars.get("ip_address", ""),
        "user_agent": env_vars.get("user_agent", ""),
        "utm_source": session_get("utm_source", ""),
        "utm_medium": session_get("utm_medium", ""),
        "utm_campaign": session_get("utm_campaign", ""),
        "utm_term": session_get("utm_term", ""),
        "utm_content": session_get("utm_content", ""),
        "referer": session_get("referer", ""),
        "current_url": request.path,
        "client": env_vars.get("session_id", ""),
        "action_history": session_get("action_history", ""),
    }
    id = DB.insert_query(q, params)
    if not id:
        current_app.logger.error(f"Could not add record to customer_activity")

    return None

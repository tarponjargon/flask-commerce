""" General content-related views """

from flask import Blueprint, render_template, request
from flask_app.modules.cart.shipping import get_shipping_chart
from flask_app.modules.extensions import DB


mod = Blueprint("content_view", __name__)


@mod.route("/about")
def do_about_page():
    """'About us' View"""
    return render_template("content/about.html.j2")


@mod.route("/reviews")
def do_reviews_page():
    """Reviews Page View"""
    return render_template("content/reviews.html.j2")


@mod.route("/customerservice")
def do_customerservice_page():
    """Customer service / shipping information view"""
    shipping_chart = get_shipping_chart()
    canadafee = shipping_chart[0].get("canadafee") if len(shipping_chart) else 21.95
    return render_template(
        "content/customerservice.html.j2",
        shipping_chart=shipping_chart,
        canadafee=canadafee,
    )


@mod.route("/contact")
def do_contact_form():
    """Contact form view"""
    return render_template("content/contact.html.j2")


@mod.route("/catalogrequest")
def do_catalogrequest_form():
    """Catalog request form view"""
    return render_template("content/catalogrequest.html.j2")


@mod.route("/optout")
def do_optout_form():
    """Opt-out (unsubscribe) form view"""
    return render_template("content/optout.html.j2")


@mod.route("/optin")
def do_optin_form():
    """Opt-in (subscribe) form view"""
    return render_template("content/optin.html.j2")


@mod.route("/privacy")
def do_privacy():
    """Privacy policy view"""
    return render_template("content/privacy.html.j2")


@mod.route("/notice-at-collection")
def do_nac():
    """Notice at Collection View"""
    return render_template("content/notice-at-collection.html.j2")


@mod.route("/ca-privacy")
def do_ca_privacy():
    """California privacy rights view"""
    return render_template("content/ca-privacy.html.j2")


@mod.route("/ca-do-not-sell")
def do_ca_do_not_sell_form():
    """California do-not-sell view"""
    return render_template("content/ca-do-not-sell.html.j2")


@mod.route("/do-not-rent")
def do_not_rent_form():
    """Do not rent view"""
    return render_template("content/donotrent.html.j2")


@mod.route("/ca-consumer-privacy")
def do_ca_consumer_privacy_form():
    """California consumer privacy act form view"""
    return render_template("content/ca-consumer-privacy.html.j2")


@mod.route("/data-request-appeal")
def do_data_request_appeal():
    """Privacy data request appeal form"""
    return render_template("content/data-request-appeal.html.j2")


@mod.route("/termsofuse")
def do_termsofuse_page():
    """Terms of use view"""
    return render_template("content/termsofuse.html.j2")


@mod.route("/accessibility-statement")
def do_accessibility_statement():
    """Accessibility statement view"""
    return render_template("content/accessibility-statement.html.j2")


@mod.route("/vip-insider-info")
def do_vip_insider_page():
    """Loyalty program information view"""
    return render_template("content/vipinsider.html.j2")


@mod.route("/lakes")
def do_lake_personalization():
    """HTML fragment/app for vendor named 'coasterstone' who sells 'personalized lake' items and requires a custom personaliztion UI"""
    return render_template("content/lakes.html.j2")


@mod.route("/coupons")
def do_coupons_page():
    """Coupons and Deals page"""

    coupons = DB.fetch_all(
        """
      SELECT * FROM promo_listing
      WHERE start_timestamp <= NOW()
      AND end_timestamp > NOW()
      ORDER BY sort_order ASC
    """
    )["results"]
    return render_template("content/coupons.html.j2", coupons=coupons)


@mod.route("/lp")
def do_landing_page():
    """Landing page"""
    lp_id = request.args.get("lp_id", 1)
    lp = DB.fetch_one(
        "SELECT heading,content FROM landing_pages WHERE id = %(lp_id)s",
        {"lp_id": lp_id},
    )
    return render_template("content/landing_page.html.j2", lp=lp)

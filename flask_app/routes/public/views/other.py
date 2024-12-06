""" View routes that don't fit anywhere else """

from flask import Blueprint, request, redirect, render_template, g, current_app, session, Response
from flask_app.modules.cart import Cart
from flask_app.modules.cart.shipping import get_shipping_chart
from flask_app.modules.extensions import DB, cache
from flask_app.modules.helpers import match_uuid
from flask_app.modules.preload import get_flip_catalog
from flask_app.modules.http import page_not_found, error_500

mod = Blueprint("other_view", __name__)


@mod.route("/store", methods=["GET", "POST"])
def do_store_view():
    """/store is a legacy all-purpose URL used on hazel sites.  Functionality depends on query parameters sent.
    TODO: update front-end application to use the /api endpoints so the redirects below are not necessary"""

    if request.args.get("action") == "editpersonalization":
        return redirect(
            current_app.config["STORE_URL"] + "/editpersonalization?" + request.query_string.decode("utf8")
        )

    if request.args.get("action") == "ajax_orderstatus":
        return redirect(current_app.config["STORE_URL"] + "/api/orderstatus?" + request.query_string.decode("utf8"))

    elif request.args.get("action") == "multi_option":
        return redirect(current_app.config["STORE_URL"] + "/api/multioption?" + request.query_string.decode("utf8"))

    elif request.args.get("action") == "get_cart":
        return redirect(current_app.config["STORE_URL"] + "/get-cart?" + request.query_string.decode("utf8"))

    elif request.args.get("action") == "ajax_carttotals":
        return redirect(current_app.config["STORE_URL"] + "/api/cart/totals", code=307)

    elif request.args.get("action") == "ajax_optchange":
        return redirect(current_app.config["STORE_URL"] + "/api/optchange", code=307)

    elif request.args.get("action") == "ajax_caprivacyrequest":
        return redirect(current_app.config["STORE_URL"] + "/api/ca-privacy-request", code=307)

    elif request.args.get("action") == "ajax_accessibility":
        return redirect(current_app.config["STORE_URL"] + "/api/accessibility-request", code=307)

    elif request.args.get("action") == "ajax_requestappeal":
        return redirect(current_app.config["STORE_URL"] + "/api/data-request-appeal", code=307)

    elif request.args.get("action") == "ajax_subjectrequest":
        return redirect(current_app.config["STORE_URL"] + "/api/ca-subject-request", code=307)

    elif request.args.get("action") == "ajax_donotrent":
        return redirect(current_app.config["STORE_URL"] + "/api/do-not-rent", code=307)

    elif request.args.get("action") == "ajax_readerreview":
        return redirect(current_app.config["STORE_URL"] + "/api/reader-review", code=307)

    elif request.args.get("action") == "ajax_contact":
        return redirect(current_app.config["STORE_URL"] + "/api/contact", code=307)

    elif request.args.get("action") == "ajax_catalog":
        return redirect(current_app.config["STORE_URL"] + "/api/catalogrequest", code=307)

    elif request.args.get("action") == "ajax_newaccount":
        return redirect(current_app.config["STORE_URL"] + "/api/newaccount", code=307)

    elif request.args.get("action") == "ajax_login":
        return redirect(current_app.config["STORE_URL"] + "/api/login", code=307)

    elif request.args.get("action") == "ajax_account":
        return redirect(current_app.config["STORE_URL"] + "/api/account", code=307)

    elif request.args.get("action") == "ajax_getwishlist":
        return redirect(current_app.config["STORE_URL"] + "/api/wishlist?" + request.query_string.decode("utf8"))

    elif request.args.get("action") == "ajax_wishlistshare":
        return redirect(current_app.config["STORE_URL"] + "/api/wishlist-share", code=307)

    elif request.args.get("action") == "ajax_updateaccount":
        return redirect(current_app.config["STORE_URL"] + "/api/updateaccount", code=307)

    elif request.args.get("action") == "ajax_editaddress":
        return redirect(current_app.config["STORE_URL"] + "/api/updateaddress", code=307)

    elif request.args.get("action") == "ajax_newaddress":
        return redirect(current_app.config["STORE_URL"] + "/api/newaddress", code=307)

    elif request.args.get("action") == "ajax_deleteaddress":
        return redirect(current_app.config["STORE_URL"] + "/api/deleteaddress", code=307)

    elif request.args.get("action") == "ajax_states":
        return redirect(current_app.config["STORE_URL"] + "/api/states")

    elif request.args.get("action") == "ajax_countries":
        return redirect(current_app.config["STORE_URL"] + "/api/countries")

    elif request.args.get("action") == "ajax_checkpassword":
        return redirect(current_app.config["STORE_URL"] + "/api/checkpassword", code=307)

    elif request.args.get("action") == "ajax_updatepassword":
        return redirect(current_app.config["STORE_URL"] + "/api/updatepassword", code=307)

    elif request.args.get("action") == "forgotpassword_ajax":
        return redirect(current_app.config["STORE_URL"] + "/api/forgotpassword", code=307)

    elif request.args.get("action") == "ajax_billinginfo":
        return redirect(current_app.config["STORE_URL"] + "/api/checkout/billingshipping", code=307)

    elif request.args.get("action") == "ajax_payment":
        return redirect(current_app.config["STORE_URL"] + "/api/checkout/payment", code=307)

    elif request.args.get("action") == "ajax_gc":
        return redirect(current_app.config["STORE_URL"] + "/api/checkout/gc", code=307)

    elif request.args.get("action") == "nonoptioned":
        return redirect(current_app.config["STORE_URL"] + "/api/test/nonoptioned")

    elif request.args.get("action") == "testpreorder":
        return redirect(current_app.config["STORE_URL"] + "/api/test/testpreorder")

    elif request.args.get("action") == "testgroupid":
        return redirect(current_app.config["STORE_URL"] + "/api/test/testgroupid")

    elif request.args.get("action") == "testpreorderoptioned":
        return redirect(current_app.config["STORE_URL"] + "/api/test/testpreorderoptioned")

    elif request.args.get("action") == "testupcharge":
        return redirect(current_app.config["STORE_URL"] + "/api/test/testupcharge")

    elif request.args.get("action") == "testoptioned":
        return redirect(current_app.config["STORE_URL"] + "/api/test/testoptioned")

    elif request.args.get("action") == "otest":
        return redirect(current_app.config["STORE_URL"] + "/api/test/otest?" + request.query_string.decode("utf8"))

    elif request.args.get("action") == "default":
        # the purpose is to just set variables to the session (see params.py)
        return {}
    else:
        return redirect("/")


@mod.route("/shippinginfo")
def do_shippinginfo():
    """render the shipping cart and information HTML fragment (usually in a modal)"""
    return render_template("includes/shipping.html.j2", shipping_chart=get_shipping_chart())


@mod.route("/default")
@mod.route("/keepalive")
def do_keepalive():
    """Periodically called by setInterval function on the front-end for keeping the session alive for open browsers"""
    return {}


@mod.route(f"/u/<string:hashid>")
def do_url_short_lookup(hashid):
    """Looks up urls that have been shortened.

    Args:
      str: the id of the shortened URL

    Returns:
      redirect: A flask redirect object.  To the found url or "/? if none found
    """
    url = "/"
    res = DB.fetch_one("SELECT url FROM url_translations WHERE hashid = %(hashid)s", {"hashid": hashid})
    if res and "url" in res:
        url = res["url"]
    return redirect(url)


@mod.route("/forgetme")
def do_forgetme():
    """Clears the session, cart. Generally, for internal use only"""
    session.clear()

    resp = Response(render_template("forgetme.html.j2"), mimetype="text/html")
    resp.set_cookie(
        current_app.config["CART_COOKIE_NAME"],
        value="",
        max_age=0,
        expires=0,
        secure=True,
        httponly=True,
        samesite="Lax",
    )
    resp.set_cookie("capturewin", "", expires=0)
    resp.set_cookie("cloudflare_test_failover", "", expires=0)

    return resp


@mod.route("/get-cart")
def do_get_cart():
    """Allows an existing cart to be discoverable via a link"""
    cart_id = request.values.get("cart")
    if cart_id and match_uuid(cart_id):
        cart_json = Cart.load_cart_from_redis(cart_id)
        if cart_json:
            g.cart = Cart.from_json(cart_json)
    return redirect(current_app.config["STORE_URL"] + "/cart")


@mod.route("/flipcatalog-modal")
def do_get_flipcatalog_modal():
    """Serves the content for the flip catalog, usually in a modal"""
    return render_template("partials/flip_catalog_modal.html.j2", flip_catalog=get_flip_catalog())


@mod.route("/flipcatalog")
def do_get_flipcatalog():
    """Serves the content for the flip catalog"""
    return render_template("flip_catalog.html.j2")

@mod.route("/bbslogin")
def do_get_bbslogin():
    """Serves the content for the club login modal"""
    if current_app.config.get("STORE_CODE") != 'basbleu2':
      return page_not_found(None)
    return render_template("partials/bbs_login.html.j2")

@mod.route("/member-popup")
def do_get_member_popup():
    """Serves marketing content for clubs in a modal"""
    if current_app.config.get("STORE_CODE") != 'basbleu2':
      return page_not_found(None)
    return render_template("partials/member_popup.html.j2")

@mod.route("/member-popup-mobile")
def do_get_member_popup_mobile():
    """Serves marketing content for clubs in a modal for a mobile view"""
    if current_app.config.get("STORE_CODE") != 'basbleu2':
      return page_not_found(None)
    return render_template("partials/member_popup_mobile.html.j2")

@mod.route("/member-checkout-popup")
def do_get_member_checkout_popup():
    """Serves marketing content for clubs in a modal at checkout"""
    if current_app.config.get("STORE_CODE") != 'basbleu2':
      return page_not_found(None)
    return render_template("partials/member_checkout_popup.html.j2")

@mod.route("/error")
def do_error():
    """ just render the error template"""
    return error_500(None)

@mod.route("/reader-review")
def do_reader_review():
    """for bas bleu only, customers submit reader review"""
    if current_app.config.get("STORE_CODE") != 'basbleu2':
      return page_not_found(None)
    return render_template("content/reader_review.html.j2")

@cache.cached()
@mod.route("/blog")
def do_blog():
    """Serves the blog homepage"""
    posts = DB.fetch_all("""
      SELECT slug,thumbnail,title
      FROM blog_content ORDER BY id DESC
    """)['results']
    return render_template("content/blog.html.j2", posts=posts)

@cache.cached()
@mod.route("/blog/<path:subpath>")
def do_blog_view(subpath):
    """Serves a blog post"""
    post = DB.fetch_one("""
      SELECT id,slug,thumbnail,title,content,author
      FROM blog_content WHERE slug = %(subpath)s
    """, { 'subpath': subpath })
    if not post:
      return page_not_found(None)
    posts = DB.fetch_all("""
      SELECT slug,thumbnail,title
      FROM blog_content ORDER BY id DESC
    """)['results']
    return render_template("content/blog_article.html.j2", post=post, posts=posts)
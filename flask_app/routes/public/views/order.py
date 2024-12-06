""" Order view routes """

from flask import Blueprint, render_template

mod = Blueprint("order_view", __name__)


@mod.route("/orderstatus")
def do_orderstatus_view():
    """Order status view"""
    return render_template("orderstatus.html.j2")

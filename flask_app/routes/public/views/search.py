""" Search route Blueprint

Flask Blueprint for rendering search result HTML
"""


from flask import Blueprint, render_template, request, current_app, g
from flask_app.modules.search import Search
from flask_app.modules.helpers import sanitize
from flask_app.modules.preload import get_search_state
from flask_app.modules.banners import get_plp_banner

mod = Blueprint("search_view", __name__)


@mod.route("/find")
def search_view():
    """Render search results view"""


    term = ""
    if request.args.get("q"):
      term = sanitize(request.args.get("q"))
    if not term or not term.strip():
        return render_template("searchresults.html.j2", search={}, errors=["Please enter a search term"])

    results = {}
    if not get_search_state():
      search = Search.from_term(term)
      results = search.get_search()

    plp_banner = get_plp_banner()
    return render_template(
      "searchresults.html.j2",
      search=results, errors=[],
      plp_banner=plp_banner
    )


@mod.route("/tools/no_results.hzml")
def no_results_view():
    """Render 'no results' view"""
    return render_template("no_results.html.j2")

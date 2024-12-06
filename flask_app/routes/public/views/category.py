""" Category route Blueprint

Flask Blueprint for rendering Category (PLP) HTML
"""


from flask import Blueprint, current_app, render_template, request
from flask_app.modules.extensions import DB, cache
from flask_app.modules.category import Category
from flask_app.modules.category.categories import get_root_categories
from flask_app.modules.banners import get_plp_banner

mod = Blueprint("category_view", __name__)


def get_root_category_str():
    """Creates a pipe-delimited list of root-level category codes

    Background:
    USA does not have a prefix for category routes.  They are formatted like: /tshirts
    The server has to watch for any root path matching one of the top-level category slugs and handle it as a category.
    I'm accomplishing that by creating a list of slugs, pipe delimiting them using that as the regex value for route matching

    Returns:
      str: Pipe-delimited list meant to be used for regex.  The same list (only uppercased for uppercase-matching) is concatenated

    Example:
      new|home|outdoor|clothing|NEW|HOME|OUTDOOR|CLOTHING
    """
    root_list = get_root_categories()
    root_list_str = "|".join(root_list) + '|' + "|".join(root_list).upper()
    return root_list_str


root_str = get_root_category_str()

@cache.memoize()
def get_highlighted_category_reviews(category_code):
    """ Returns a list of highlighted reviews for a given category
    Args:
      category_code (str): The category code to get reviews for

    Returns:
      list: A list of highlighted reviews for the category
    """
    if not category_code:
        return []
    q = DB.fetch_all(
        """
        SELECT
          highlighted_reviews.id AS review_id,
          highlighted_reviews.name,
          LEFT(highlighted_reviews.name, 1) as user_letter,
          highlighted_reviews.title,
          highlighted_reviews.review,
          highlighted_reviews.category_code,
          highlighted_reviews.rating,
          highlighted_reviews.skuid,
          products.NAME AS product_name
        FROM
        highlighted_reviews, products
        WHERE review_type = 'category'
        AND highlighted_reviews.category_code = %(category_code)s
        AND highlighted_reviews.skuid = products.SKUID
        GROUP BY highlighted_reviews.id
        ORDER BY highlighted_reviews.sort_order
        """,
        {"category_code": category_code},
    )
    return q["results"] if q and "results" in q else []


@mod.route(f'/<regex("{root_str}"):rootpath>')
@mod.route(f'/<regex("{root_str}"):rootpath>/<path:child_path>')
def category_view(rootpath, child_path=None):
    """Returns the category view"""
    category_code = request.path.split("/")[-1]
    category_code = category_code.lower()
    category = Category.from_code(category_code, True)
    if not category or not category.get_category():
        return render_template("404.html.j2"), 404
    highlighted_reviews = get_highlighted_category_reviews(category_code)
    plp_banner = get_plp_banner()
    return render_template(
      "category.html.j2",
      category=category.get_category(),
      highlighted_reviews=highlighted_reviews,
      plp_banner=plp_banner
    )

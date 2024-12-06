""" Functions related to shipping calculation """

from flask_app.modules.extensions import DB, cache


@cache.memoize()
def get_method_descriptions():
    """Gets all data for all available shipping methods

    Returns:
      list: A list of dictionaries, each a shipping method
    """
    q = DB.fetch_all(
        """SELECT
          ship_method_code,
          ship_method_key,
          ship_method_name,
          ship_method_short_name,
          ship_method_delivery_desc,
          ship_method_delivery_desc
        FROM ship_methods_loop
        WHERE is_active = 1
        ORDER BY sort_order ASC
        """
    )
    return q.get("results")

@cache.memoize()
def get_shipping_chart():
    """Gets the shipping chart as a list

    Returns:
      list: A list of dictionaries, each a tier of the shipping chart
    """
    q = DB.fetch_all(
        """
          SELECT
            order_min,
            order_max,
            shipping_cost,
            rush,2day,
            overnight,
            canada,
            modifier,
            (canada - shipping_cost) as canadafee
          FROM standard_rates_loop
          WHERE order_min > 0
          ORDER BY order_min ASC
        """
    )
    return q.get("results")

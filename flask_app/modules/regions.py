""" Functions related to location data (like states, countries)  """

from flask import current_app
from flask_app.modules.extensions import DB, cache
import re

@cache.memoize()
def get_states():
    """Get a list of state codes

    Returns:
      list: A list of dictionaries, each containing state code and state name
    """
    states = []
    q = DB.fetch_all(f"SELECT state_code AS code,state_name AS name FROM states_loop")
    if q and "results" in q:
        states = q["results"]
    return states

@cache.memoize()
def get_canada_provinces():
    """Get a list of canadian provinces

    Returns:
      list: a list of strings
    """
    provinces = []
    q = DB.fetch_all(f"SELECT province FROM canada_tax_residential")
    if q and "results" in q:
        for result in q["results"]:
          provinces.append(result.get('province'))

    return provinces

@cache.memoize()
def get_countries():
    """Get a list of countries

    Returns:
      list: A list of dictionaries, each containing a country code an country name
    """
    countries = []
    q = DB.fetch_all(f"SELECT country_code AS code,country_name AS name FROM countries_loop")
    if q and "results" in q:
        countries = q["results"]
    return countries

@cache.memoize()
def get_state_from_zip(zip):
    """Get a state code given a zip

    Args:
      zip (str): The zip code

    Returns:
      str: The state for the given zip code
    """
    if not zip or not re.match("^[0-9]{5}", zip):
        return None

    state = None
    query = """
      SELECT Destination_State AS state
      FROM masterzip_us WHERE Destination_Zip = %(zip)s
      GROUP BY Destination_State
    """
    result = DB.fetch_one(query, {"zip": zip})
    if result and "state" in result:
        state = result["state"]

    return state


@cache.memoize()
def get_tax_rate(zip):
    """get the tax rate for given zip

    Args:
      zip (str): the 5-digit zip code

    Returns:
      dict: A dictionary containing tax info for given zip
    """
    if not zip or not re.match("^[0-9]{5}", zip):
        return None

    rate_object = {}
    query = """
      SELECT Combined_Rate+0 AS rate,
      Shipping_Taxable AS shipping_taxable
      FROM masterzip_us WHERE Destination_Zip = %(zip)s
      GROUP BY Combined_Rate
    """
    result = DB.fetch_one(query, {"zip": zip})
    if result and "rate" in result:
        rate_object = result

    return rate_object

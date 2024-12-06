""" Functions related to tax calcuation"""

import re
from flask import current_app
from flask_app.modules.extensions import DB
from flask_app.modules.regions import get_canada_provinces


def get_taxtable():
    """Returns a list of states that collect sales tax, whether shipping is taxable, and the tax rate

    Returns:
      list: a list of dictionaries, each a state and it's associated tax info
    """
    taxtable = []
    q = DB.fetch_all(
        """
          SELECT tax_states.state,
          'Yes' as merch_taxable,
          IF(tax_states.shipping_taxable = 'YES', 'Yes', 'No') AS shipping_taxable,
          rates.combined_rate as rate FROM tax_states
          LEFT JOIN (
            SELECT  a.state AS state,
            IF(COUNT(a.state) = 1, ROUND(a.combined_rate*100, 2), NULL) AS combined_rate,
            COUNT(a.state) AS localities
            FROM (
              SELECT
              masterzip_us.Destination_State AS state,
              masterzip_us.Combined_rate AS combined_rate,
              COUNT(masterzip_us.Combined_Rate) AS localities_with_rate FROM masterzip_us
              GROUP BY masterzip_us.Destination_State, masterzip_us.Combined_Rate
              ORDER BY masterzip_us.Destination_State ASC ) AS a
              GROUP BY a.state ORDER BY a.state ASC
            ) AS rates ON tax_states.state = rates.state
          GROUP BY tax_states.state ORDER BY tax_states.state ASC
        """
    )
    if q and "results" in q:
        taxtable = q["results"]
    return taxtable


def get_tax_rate(zip):
    """Gets the tax rate for a given zip code.  US only

    Args:
      zip (str): The zip code to get the tax rate for

    Returns:
      dict: The tax data for the zip code
    """
    if not zip or not re.match("^[0-9]{5}", zip):
        return None

    rate_object = {}
    zip = zip[:5]
    query = """
      SELECT Combined_Rate+0 AS rate,
      Shipping_Taxable AS shipping_taxable
      FROM masterzip_us
      WHERE Destination_Zip = %(zip)s
      GROUP BY Combined_Rate
    """
    params = {"zip": zip}
    result = DB.fetch_one(query, params)
    if result and "rate" in result:
        rate_object = result

    return rate_object


def get_taxable_states():
    """Gets a list of states store collects sales tax for

    Returns:
      list: A list of strings, each a 2-letter state code
    """
    taxable_states = []
    query = "SELECT state FROM tax_states GROUP BY state"
    q = DB.fetch_all(query)
    if q and "results" in q:
        taxable_states = [r["state"] for r in q["results"]]
    return taxable_states

def get_canada_tax_rate(province):
  """ returns a canadian residential tax rate for given province and taxable amount

  Args:
    province (str): 2-char code for Canadian province
    taxable (float): The taxable amount

  Returns:
    float: Canadian tax rate
  """

  if not province in get_canada_provinces():
    return 0.00

  gst = 0.00
  pst = 0.00
  hst = 0.00

  tax_rate = 0.00

  query = """
    SELECT
      gst,pst,hst
    FROM canada_tax_residential
    WHERE province = %(province)s
  """
  result = DB.fetch_one(query, { "province": province} )
  if result:
      gst = result.get('gst', 0.00)
      pst = result.get('pst', 0.00)
      hst = result.get('hst', 0.00)

  current_app.logger.debug("TAX RATES FOR " + province)
  current_app.logger.debug(result)

  # if there's an HST value, just return it as the tax rate
  if hst > 0:
    return hst

  # if pst is 0.00, return GST as the tax rate
  if pst == 0.0:
    return gst

  # if pst has a value, perform calculation
  tax_rate = (((1+gst)*pst)+gst)

  return tax_rate



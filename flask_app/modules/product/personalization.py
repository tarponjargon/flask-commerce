""" Functions related to product personalization data """

from flask import current_app
from flask_app.modules.extensions import DB
from flask_app.modules.helpers import get_alphabet, split_to_list


def get_personalization_prompts(pers_ref):
    """Load personalization prompts/requirements into a list

    Args:
      pres_ref (str): The key to the product's personalization data (usually stored in products.CUSTOM)

    Returns:
      list: The personalization prompts/requirements
    """
    personalized = []

    if not pers_ref:
        return personalized

    query = """
                SELECT
                    id,
                    custom,
                    data,
                    prompt,
                    maxlength,
                    list,
                    required,
                    '' AS value
                FROM personalization_loop
                WHERE custom = %(pers_ref)s
                ORDER BY REPLACE(data,'DATA','')+0 ASC
            """

    pers = DB.fetch_all(query, {"pers_ref": pers_ref})

    if pers and "results" in pers and pers["results"]:
        personalized = pers["results"]

        # if the 'list' field is not empty, it's a semicolon-delim list of allowed values
        # split it into a python list
        for p in personalized:
            if "list" in p and p["list"]:
                p["list"] = split_to_list(p["list"])

        # exception for GC9999 + DATA1, it needs to be in the "schema" but not shown or collected
        # remove it from the list
        if pers_ref == "GC9999":
            x = next((i for (i, d) in enumerate(personalized) if d["custom"] == "GC9999" and d["data"] == "DATA1"), -1)
            if x > -1:
                i = personalized.pop(x)

    return personalized


def get_lakes(letter="A"):
    """Get lakes beginning with given letter.
    To support the 'personalized lake' items offered by vender 'coasterstone'

    Args:
      letter (str): The first letter of the lakes to return.  Default "A"

    Returns:
      list: A list of the lakes that start with the given letter

    """
    lakes = []
    alphabet = get_alphabet()
    if not letter or letter.upper() not in alphabet:
        letter = "A"
    query = """
              SELECT * FROM lake_translation
              WHERE LEFT(lake_name,1) = %(letter)s
              AND vendor = 'COASTERSTONE'
              ORDER BY lake_name ASC
            """
    q = DB.fetch_all(query, {"letter": letter})
    if q and "results" in q:
        lakes = q["results"]
    return lakes

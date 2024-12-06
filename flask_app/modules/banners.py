""" Functions related promotional banners """

from urllib.parse import urlparse
from flask_app.modules.extensions import DB, cache, current_app
from flask_app.modules.helpers import split_to_list, image_size
from flask_app.modules.http import session_get


@cache.memoize()
def get_catalog_image():
    """Get the most recent catalog cover image and its dimensions.  If none found, revert to a default

    Returns:
      dict: An object containing the full URL to the catalog cover, the image width and height
    """

    catalog_image = {
        "path": current_app.config["IMAGE_BASE"] + "/assets/images/catalog-request.png",
        "width": "",
        "height": "",
    }
    mydims = None
    mypath = None

    q = DB.fetch_one("SELECT cover_image FROM flip_catalog ORDER BY ID DESC LIMIT 1")
    if q and q.get("cover_image"):
        try:
            mypath = urlparse(q.get("cover_image")).path
            mydims = image_size(mypath)
        except Exception as e:
            current_app.logger.error(f"Could not parse path from catalog image url {q.get('cover_image')}")

    if mypath and mydims and len(mydims) == 2 and mydims[0]:
        catalog_image["path"] = current_app.config["IMAGE_BASE"] + mypath
        catalog_image["width"] = mydims[0]
        catalog_image["height"] = mydims[1]
    else:
        dims = image_size(catalog_image["path"])
        if dims and len(dims) == 2 and dims[0]:
            catalog_image["width"] = dims[0]
            catalog_image["height"] = dims[1]

    return catalog_image


def get_homepage_slides():
    """Get homepage carousel slides

    when there are multiple slides with the same sort_order value, if
    homepage_slides.websource = session.websource, choose that one.  if not, choose the one that
    does not have a websource value

    Returns:
      list: A list of slide dictionaries
    """

    banners = []
    banner_ids = []
    banner_limit = 4
    websource = session_get("websource").upper()
    current_q = DB.fetch_all(
        """
          SELECT id,websource,sort_order,count(*) AS num_banners
          FROM homepage_slides
          WHERE start_date < NOW() AND end_date > NOW()
          GROUP BY sort_order
          ORDER BY sort_order ASC;
        """
    )

    # loop all current banners
    for res in current_q.get("results"):
        if res.get("num_banners") == 1:
            if websource and res.get('websource') and res.get('websource').upper() == websource:
              banner_ids.append(res.get("id"))
            if not res.get('websource'):
              banner_ids.append(res.get("id"))

        else:
            # if there are multiple banners returned for this sort order slot, check if there's
            # a matching source in any of them.  if so that is the winner
            group_winner_id = None
            q="""
                  SELECT id AS winner_id
                  FROM homepage_slides
                  WHERE sort_order = %(sort_order)s
                  AND start_date < NOW() AND end_date > NOW()
                  AND websource = %(websource)s LIMIT 1
                """
            #current_app.logger.debug(f"q: {q}")
            ws_winner_q = DB.fetch_one(
                q,
                {"sort_order": res.get("sort_order"), "websource": websource},
            )
            if ws_winner_q and ws_winner_q.get("winner_id"):
                group_winner_id = ws_winner_q.get("winner_id")

            if not group_winner_id:
                winner_q = DB.fetch_one(
                    """
                      SELECT id AS winner_id
                      FROM homepage_slides
                      WHERE sort_order = %(sort_order)s
                      AND (websource IS NULL OR websource = '')
                      AND start_date < NOW() AND end_date > NOW()
                      ORDER BY id ASC LIMIT 1
                    """,
                    {"sort_order": res.get("sort_order")},
                )
                if winner_q and winner_q.get("winner_id"):
                    group_winner_id = winner_q.get("winner_id")

            if group_winner_id:
                banner_ids.append(group_winner_id)

    if banner_ids:
        banners_list = split_to_list(banner_ids)
        banners_q = DB.fetch_all(
            """
              SELECT id, filename, mobile_filename, link, title, imagemap, imagemap_mobile
              FROM homepage_slides
              WHERE id IN %(banners_list)s
              AND start_date < NOW() AND end_date > NOW()
              ORDER BY sort_order ASC
              LIMIT %(banner_limit)s
            """,
            {"banners_list": tuple(banners_list), "banner_limit": banner_limit},
        )
        if banners_q and banners_q.get("results"):
            banners = banners_q.get("results")

    return banners


def get_heading_banners():
    """Get banners that appear in the heading of the template, usually as slides.

    shows banenrs in slideshow format, ordered by sort_order in the heading_banners table.
    when there are multiple banners with the same sort_order value, if
    heading_banners.websource = session.websource, choose that one.  if not, choose the one that
    does not have a websource value

    Returns:
      list: A list of banner dictionaries
    """

    banners = []
    banner_ids = []
    banner_limit = 4
    websource = session_get("websource").upper()
    current_q = DB.fetch_all(
        """
          SELECT id,websource,sort_order,count(*) AS num_banners
          FROM heading_banners
          WHERE start_date < NOW() AND end_date > NOW()
          GROUP BY sort_order
          ORDER BY sort_order ASC;
        """
    )

    # loop all current banners
    for res in current_q.get("results"):
        if res.get("num_banners") == 1:
            banner_ids.append(res.get("id"))

        else:
            # if there are multiple banners returned for this sort order slot, check if there's
            # a matching source in any of them.  if so that is the winner
            group_winner_id = None
            ws_winner_q = DB.fetch_one(
                """
                  SELECT id AS winner_id
                  FROM heading_banners
                  WHERE sort_order = %(sort_order)s
                  AND start_date < NOW() AND end_date > NOW()
                  AND websource = %(websource)s LIMIT 1
                """,
                {"sort_order": res.get("sort_order"), "websource": websource},
            )
            if ws_winner_q and ws_winner_q.get("winner_id"):
                group_winner_id = ws_winner_q.get("winner_id")

            if not group_winner_id:
                winner_q = DB.fetch_one(
                    """
                      SELECT id AS winner_id
                      FROM heading_banners
                      WHERE sort_order = %(sort_order)s
                      AND (websource IS NULL OR websource = '')
                      AND start_date < NOW() AND end_date > NOW()
                      ORDER BY id ASC LIMIT 1
                    """,
                    {"sort_order": res.get("sort_order")},
                )
                if winner_q and winner_q.get("winner_id"):
                    group_winner_id = winner_q.get("winner_id")

            if group_winner_id:
                banner_ids.append(group_winner_id)

    if banner_ids:
        banners_list = split_to_list(banner_ids)
        banners_q = DB.fetch_all(
            """
              SELECT id, banner_text, banner_mobile_text, banner_link, link_is_external
              FROM heading_banners
              WHERE id IN %(banners_list)s
              AND start_date < NOW() AND end_date > NOW()
              ORDER BY sort_order ASC
              LIMIT %(banner_limit)s
            """,
            {"banners_list": tuple(banners_list), "banner_limit": banner_limit},
        )
        if banners_q and banners_q.get("results"):
            for banner in banners_q.get("results"):
                banners.append(
                    {
                        "banner_text": banner.get("banner_text"),
                        "banner_mobile_text": banner.get("banner_mobile_text"),
                        "banner_link": banner.get("banner_link"),
                        "link_is_external": banner.get("link_is_external"),
                    }
                )
    return banners


def get_plp_banner():
    """
    Get PLP banner by websource.  If no websource, just return.
    Intent is to override searchspring inline banner.


    Returns:
      dict: A dictionary of containing filename, link, title
    """

    banner = {}
    if not session_get("websource"):
        return banner

    websource = session_get("websource").upper()
    banner_q = DB.fetch_one(
        """
          SELECT filename, link, title
          FROM plp_banners
          WHERE start_date < NOW() AND end_date > NOW()
          AND websource = %(websource)s LIMIT 1
        """,
        {"websource": websource}
    )
    return banner_q
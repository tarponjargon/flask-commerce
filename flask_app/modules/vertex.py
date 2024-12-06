""" Vertex methods for calculating tax """

import requests
import socket
from datetime import datetime
import json
from flask import current_app, g, session, current_app
from flask_app.modules.http import session_get
from flask_app.modules.extensions import cache


class Vertex:
    """Contains what's needed for calls to Vertex"""

    def __init__(self):
        """Initialize Vertex"""
        self.access_token = ""
        self.token_endpoint = current_app.config["VERTEX_TOKEN_ENDPOINT"]
        self.rest_endpoint = current_app.config["VERTEX_REST_ENDPOINT"] + current_app.config["VERTEX_SALE_URI"]
        self.token_creds = self._set_token_creds()
        # TODO: check age of any existing token in session
        tres = self._get_newtoken()
        tresdata = tres.get("data", None)
        if tresdata:
            self.access_token = tresdata.get("access_token")

    def _set_token_creds(self):
        """Sets the token credentials"""
        return {
            "client_id": current_app.config["VERTEX_CLIENT_ID"],
            "client_secret": current_app.config["VERTEX_CLIENT_SECRET"],
            "username": current_app.config["VERTEX_API_KEY"],
            "password": current_app.config["VERTEX_API_PASS"],
            "scope": current_app.config["VERTEX_SCOPE"],
            "grant_type": current_app.config["VERTEX_GRANT_TYPE"],
        }

    def _get_newtoken(self):
        """Get a New Vertex Bearer Token"""
        reqs = None
        requests_error = ""
        resultdata = {}
        current_app.logger.debug("VERTEX GET NEW TOKEN")
        current_app.logger.debug(self.token_creds)
        try:
            reqs = requests.post(self.token_endpoint, data=self.token_creds, timeout=10)
        except requests.exceptions.RequestException as err:
            requests_error = "POST exception error to " + self.token_endpoint + ": " + str(err)
        except socket.timeout as err:
            requests_error = str(err)
        try:
            reqs.raise_for_status()
        except requests.exceptions.HTTPError as err:
            requests_error = "POST HTTP error " + str(err)
        except AttributeError as err:
            requests_error = "POST HTTP failure " + str(err)
        if reqs:
            if reqs.status_code == 200 or reqs.status_code == 201 or reqs.status_code == 202:
                resultdata = reqs.json()
                if len(resultdata) > 0:
                    requests_error = ""
                else:
                    requests_error = "POST success but blank response"
            else:
                requests_error = "POST connect but error status: [" + str(reqs.status_code) + "] " + reqs.text
        else:
            if requests_error == "":
                requests_error = "POST unknown connect error to " + self.token_endpoint
        current_app.logger.debug(resultdata)
        return {"error": requests_error, "data": resultdata}

    def get_sale_query(self):
        """Returns the QUOTATION Sale Query JSON"""
        sellerdata = {
            "company": current_app.config["VERTEX_COMPANY_CODE"],
            "physicalOrigin": {
                "streetAddress1": current_app.config["VERTEX_SELLER_ADDRESS1"],
                "streetAddress2": "",
                "city": current_app.config["VERTEX_SELLER_CITY"],
                "mainDivision": current_app.config["VERTEX_SELLER_STATE"],
                "postalCode": current_app.config["VERTEX_SELLER_ZIP"],
                "country": current_app.config["VERTEX_SELLER_COUNTRY"],
            },
            "administrativeOrigin": {
                "streetAddress1": current_app.config["VERTEX_SELLER_ADDRESS1"],
                "streetAddress2": "",
                "city": current_app.config["VERTEX_SELLER_CITY"],
                "mainDivision": current_app.config["VERTEX_SELLER_STATE"],
                "postalCode": current_app.config["VERTEX_SELLER_ZIP"],
                "country": current_app.config["VERTEX_SELLER_COUNTRY"],
            },
        }
        idx = 0
        lineItems = []
        for item in g.cart.get_items():
            idx += 1
            product = item.get("product", {})
            lineItems.append(
                {
                    "customer": {
                        "destination": {
                            "streetAddress1": session_get("ship_street"),
                            "streetAddress2": session_get("ship_street2"),
                            "city": session_get("ship_city"),
                            "mainDivision": session_get("ship_state"),
                            "postalCode": session_get("ship_postal_code"),
                            "country": session_get("ship_country"),
                        },
                    },
                    "product": {
                        "productClass": product.get("product_class"),
                        "value": item.get("skuid"),
                    },
                    "quantity": {"value": item.get("quantity"), "unitOfMeasure": "EA"},
                    "extendedPrice": item.get("price"),
                    "lineItemNumber": idx,
                }
            )

        # Return immediately if no line items added above (i.e. an empty cart)
        if not lineItems:
            current_app.logger.debug("VERTEX NO ITEMS IN CART")
            return {}

        shipping_cost = g.cart.get_shipping()
        if shipping_cost > 0:
            lineItems.append(
                {
                    "customer": {
                        "destination": {
                            "streetAddress1": session_get("ship_street"),
                            "streetAddress2": session_get("ship_street2"),
                            "city": session_get("ship_city"),
                            "mainDivision": session_get("ship_state"),
                            "postalCode": session_get("ship_postal_code"),
                            "country": session_get("ship_country"),
                        },
                    },
                    "product": {
                        "productClass": "FRGT",
                        "value": "FREIGHT",
                    },
                    "quantity": {"value": 1, "unitOfMeasure": "EA"},
                    "extendedPrice": shipping_cost,
                    "lineItemNumber": idx + 1,
                }
            )

        return {
            "saleMessageType": "QUOTATION",  # always QUOTATION
            "postingDate": "",  # intentionally blank
            "documentNumber": "",  # intentionally blank
            "documentDate": datetime.now().strftime("%Y-%m-%d"),
            "transactionId": session_get("client") + " " + datetime.now().strftime("%H:%M:%S"),
            "transactionType": "SALE",  # always SALE
            "seller": sellerdata,
            "lineItems": lineItems,
        }

    def do_sale_query(self, qdata):
        """Makes Vertex Sale Call with Query Data"""
        reqs = None
        requests_error = ""
        resultdata = {}
        current_app.logger.debug("VERTEX SALE QUERY")
        current_app.logger.debug(qdata)
        headers = {
            "Authorization": "Bearer " + self.access_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        jsondata = {}
        try:
            jsondata = json.dumps(qdata)
        except:
            pass
        try:
            reqs = requests.post(self.rest_endpoint, data=jsondata, headers=headers, timeout=10)
        except requests.exceptions.RequestException as err:
            requests_error = "POST exception error to " + self.rest_endpoint + ": " + str(err)
        except socket.timeout as err:
            requests_error = str(err)
        try:
            reqs.raise_for_status()
        except requests.exceptions.HTTPError as err:
            requests_error = "POST HTTP error " + str(err)
        except AttributeError as err:
            requests_error = "POST HTTP failure " + str(err)
        if reqs:
            if reqs.status_code == 200 or reqs.status_code == 201 or reqs.status_code == 202:
                resultdata = reqs.json()
                if len(resultdata) > 0:
                    requests_error = ""
                else:
                    requests_error = "POST success but blank response"
            else:
                requests_error = "POST connect but error status: [" + str(reqs.status_code) + "] " + reqs.text
        else:
            if requests_error == "":
                requests_error = "POST unknown connect error to " + self.rest_endpoint
        current_app.logger.debug(requests_error)
        current_app.logger.debug(resultdata)
        return {"error": requests_error, "data": resultdata}

    def process_query_results(self, qres):
        """Process the sale query data and determine tax"""
        vertex_line_items = None
        try:
            vertex_line_items = qres["data"]["lineItems"]
        except KeyError as err:
            # Problem parsing line items
            current_app.logger.debug("VERTEX PROBLEM PARSING RETURNED VERTEX LINE ITEMS: "+str(err))
            pass

        # Just return if there's a problem getting the line items
        if not vertex_line_items:
            return {}

        total_combined_rate = float(0.0)
        combined_rates = {}
        combined_rates_list = []
        vertex_tax_shipping = False
        vertex_tax_shipping_amt = float(0.0)
        session["nontaxable_items"] = []
        # Loop through TAXABLE Vertex line items
        for line_item in vertex_line_items:
            is_state_taxed = False
            is_county_taxed = False
            product_obj = line_item.get("product", None)
            if product_obj:
                product = product_obj.get("value", None)
            lineno = line_item.get("lineItemNumber", 1)
            totaltax = float(line_item.get("totalTax", 0.0))
            line_item_taxable = ""
            line_item_taxable_amt = float(0.0)
            line_item_combined_rates = float(0.0)
            state_taxed_amt = float(0.0)
            county_taxed_amt = float(0.0)
            vertex_taxes_items = line_item.get("taxes", None)
            combined_rates[lineno] = {}
            # Loop through taxes array to pick out effective rates
            # Count them up for the "total" combined rate
            if vertex_taxes_items:
                for vertex_taxes_item in vertex_taxes_items:
                    line_item_taxable = vertex_taxes_item.get("taxResult", "")
                    line_item_taxable_amt = float(vertex_taxes_item.get("taxable", 0.0))
                    line_item_combined_rate = float(vertex_taxes_item.get("effectiveRate", 0.0))
                    jurisdiction = vertex_taxes_item.get("jurisdiction", None)
                    if jurisdiction:
                        jurisdiction_level = jurisdiction.get("jurisdictionLevel", "")
                        jurisdiction_value = jurisdiction.get("value", "")
                        if (jurisdiction_level == "STATE") and (line_item_taxable == "TAXABLE"):
                            is_state_taxed = True
                            state_taxed_amt = line_item_taxable_amt
                        if (jurisdiction_level == "COUNTY") and (line_item_taxable == "TAXABLE"):
                            is_county_taxed = True
                            county_taxed_amt = line_item_taxable_amt
                        current_app.logger.debug(
                            "Line: {}, Product: {}, Jurisdiction Lvl: {}, Jurisdiction Val: {}, Total Tax: {}, Taxable: {}, Taxable Amt: {}, Combined Rate: {}".format(
                                lineno,
                                product,
                                jurisdiction_level,
                                jurisdiction_value,
                                totaltax,
                                line_item_taxable,
                                line_item_taxable_amt,
                                line_item_combined_rate,
                            )
                        )

                        # Keep track of effective rates for each jurisdiction level
                        # Only keep *one* rate per level.  Add rates together if:
                        #   * For STATE or COUNTY - there are different rates for same jurisdiction level
                        #   * For others (DISTRICT) - there are additional rates at the level
                        if len(jurisdiction_level) > 0:
                            current_rate = combined_rates[lineno].get(jurisdiction_level, None)
                            if current_rate is None:
                                combined_rates[lineno][jurisdiction_level] = line_item_combined_rate
                            else:
                                if (current_rate != line_item_combined_rate) or (
                                    (jurisdiction_level != "STATE") and (jurisdiction_level != "COUNTY")
                                ):
                                    combined_rates[lineno][jurisdiction_level] = current_rate + line_item_combined_rate

                # Product is considered TAXABLE if either a STATE or COUNTY jurisdiction level was flagged TAXABLE
                if is_state_taxed:
                    line_item_taxable = "TAXABLE"
                    line_item_taxable_amt = state_taxed_amt
                elif is_county_taxed:
                    line_item_taxable = "TAXABLE"
                    line_item_taxable_amt = county_taxed_amt

            # Determine the combined rate (effective rate) for this item
            if combined_rates[lineno]:
                for j in combined_rates[lineno]:
                    line_item_combined_rates += combined_rates[lineno][j]

            # Check if shipping (FREIGHT) was taxed.
            if (product == "FREIGHT") and (line_item_taxable == "TAXABLE"):
                vertex_tax_shipping = True
                vertex_tax_shipping_amt = line_item_taxable_amt

            # Identify and tag "NONTAXABLE" line item product SKUIDs
            if (product != "FREIGHT") and (line_item_taxable == "NONTAXABLE" or line_item_taxable == "DEFERRED"):
                session["nontaxable_items"].append(product)

            # Hold all the line_item_combined_rates
            combined_rates_list.append(line_item_combined_rates)

        # The largest of the effective rates is the total_combined_rate.  This is what we came for!
        total_combined_rate = float(max(combined_rates_list))

        shipping_taxable_val = 0
        if vertex_tax_shipping:
            shipping_taxable_val = 1
        return {"rate": total_combined_rate, "shipping_taxable": shipping_taxable_val}


@cache.memoize()
def get_vtax_rate(addr_cache_key=None):
    """Get the sales tax from Vertex"""
    V = Vertex()
    sale_query = V.get_sale_query()
    if sale_query:
        sale_query_results = V.do_sale_query(sale_query)
        sale_query_errors = sale_query_results.get("error", None)
        sale_query_data = sale_query_results.get("data", None)
        if sale_query_errors:
            current_app.logger.error(sale_query_errors)
            return {}
        else:
            tax_rate = V.process_query_results(sale_query_data)
        return tax_rate
    else:
        return {}

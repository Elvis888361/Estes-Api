# from zeep import Client
# from zeep.exceptions import Fault
import frappe
from frappe import _
import requests

@frappe.whitelist(allow_guest=True)
def get_total_prices(data):
    estes_user=frappe.db.get_single_value("Estes API", "estes_user")
    estes_password=frappe.db.get_single_value("Estes API", "estes_password")
    estes_account_number=frappe.db.get_single_value("Estes API", "estes_account_number")
    wsdl_url = "https://www.estes-express.com/tools/rating/ratequote/v4.0/services/RateQuoteService?wsdl"

    client = Client(wsdl_url)

    try:
        request_data = frappe.parse_json(data)

        header = {
            "authentication": {
                "user": estes_user,
                "password": estes_password
            }
        }

        response = client.service.getQuote(_soapheaders=header, **request_data)
        
        quotes = response["quoteInfo"]["quote"]
    
        quoted_info = []

        for quote in quotes:                       
            if quote["quoteNumber"] and quote["serviceLevel"]["text"] == "LTL Standard Transit":
                total_price = quote["pricing"]["totalPrice"]
                quote_number = quote["quoteNumber"]
                service_level = quote["serviceLevel"]["text"]
                
                accessorial_code = None
                accessorial_charge = None
                
                if "accessorialInfo" in quote:
                    accessorial_info = quote["accessorialInfo"]
                    accessorial_list = accessorial_info["accessorial"]
                    
                    if accessorial_list:
                        first_accessorial = accessorial_list[0]
                        accessorial_code = first_accessorial["code"]
                        accessorial_charge = first_accessorial["charge"]
                
                quoted_dict = {
                    "total_price": str(total_price),
                    "quote_number": quote_number,
                    "service_level": service_level,
                    "accessorial_code": accessorial_code,
                    "accessorial_charge": accessorial_charge
                }
                
                quoted_info.append(quoted_dict)

    except Fault as e:
        if e.code == 400:
            return "Missing or invalid body params. Data object will be empty."
        elif e.code == 401:
            return "Not authenticated. Data object will be empty."
        elif e.code == 500:
            return "Internal server error. Data object will be empty."
        elif e.code == 503:
            return "Service unavailable. Response body will be empty."
        else:
            return f"An error occurred while retrieving rate quotes: {e}"

    return quoted_info

# Whitelist the autocomplete function
@frappe.whitelist(allow_guest=True)
def autocomplete(query):
    apis=frappe.db.get_single_value("GeoApify Address Validation", "geoapify_api_key")
    print(f"""/n/n/n/{apis}""")
    apiUrl = f"https://api.geoapify.com/v1/geocode/autocomplete?text={query}&format=json&apiKey={apis}"
    response = requests.get(apiUrl)
    data = response.json()
    # print(data)
    # for result in data['results']:
    #     print(result['address_line1'])
    return data

@frappe.whitelist(allow_guest=True)
def get_autocomplete(query):
    # print(f"""/n/n/n/{query}""")
    if query:
        suggestions = autocomplete(query)
        return suggestions
    else:
        return frappe.as_json([])
from langchain_core.tools import tool
import requests
from config.settings import fb_base_url, fb_access_token


@tool
def get_facebook_catalogs(business_account_id: str) -> str:
    """Fetches the product catalogs for a specific business account which can get by using the get_facebook_business_accounts tool
    and shows them to the user with their name and id."""
    print(f"Tool Called: get_facebook_catalogs")
    url = f"{fb_base_url}{business_account_id}/owned_product_catalogs"

    try:
        response = requests.get(url, params={"access_token": fb_access_token})
        response.raise_for_status()
        data = response.json()

        catalogs = data.get("data", [])
        if not catalogs:
            return "No product catalogs found for this business account."

        # return "Here are the product catalogs:\n" + "\n".join(
        #     [f"- {cat.get('name', 'Unnamed')} (ID: {cat['id']})" for cat in catalogs]
        # )
        return catalogs

    except requests.exceptions.HTTPError as http_err:
        return f"Facebook API error: {http_err.response.json().get('error', {}).get('message', str(http_err))}"

    except requests.exceptions.RequestException as e:
        return f"Network error while contacting Facebook: {str(e)}"

    except Exception as e:
        return f"Unexpected error: {str(e)}"


@tool
def create_facebook_catalog(business_id: str, catalog_name: str) -> str:
    """Create a new product catalog under a Facebook business account."""
    url = f'{fb_base_url}{business_id}/owned_product_catalogs'
    data = {
        'name': catalog_name,
        'access_token': fb_access_token
    }

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        return f"Catalog created with ID: {response.json().get('id')}"
    except requests.exceptions.RequestException as e:
        return f"Error creating catalog: {str(e)}"

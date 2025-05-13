from langchain_core.tools import tool
from config.settings import fb_access_token, fb_base_url
import requests

# --- TOOL DEFINITION ---
@tool
def get_facebook_business_accounts() -> str:
    """Fetches Facebook Business Accounts connected to the authenticated user."""
    url = f"{fb_base_url}me/businesses"

    try:
        response = requests.get(url, params={"access_token": fb_access_token})
        response.raise_for_status()
        data = response.json()

        businesses = data.get("data", [])
        if not businesses:
            return "No business accounts found for this user."

        # return "Here are your business accounts:\n" + "\n".join(
        #     [f"- {b.get('name', 'Unnamed')} (ID: {b['id']})" for b in businesses]
        # )
        return businesses

    except requests.exceptions.HTTPError as http_err:
        return f"Facebook API error: {http_err.response.json().get('error', {}).get('message', str(http_err))}"

    except requests.exceptions.RequestException as e:
        return f"Network error while contacting Facebook: {str(e)}"

    except Exception as e:
        return f"Unexpected error: {str(e)}"



@tool
def get_facebook_ad_accounts() -> str:
    """Fetches Facebook Ad Accounts connected to the authenticated user."""
    url = f"{fb_base_url}me/adaccounts"

    try:
        response = requests.get(url, params={"access_token": fb_access_token})
        response.raise_for_status()
        data = response.json()

        ad_accounts = data.get("data", [])
        if not ad_accounts:
            return "No ad accounts found for this user."

        # return "Here are your ad accounts:\n" + "\n".join(
        #     [f"- {acc.get('name', 'Unnamed')} (ID: {acc['id']})" for acc in ad_accounts]
        # )
        return ad_accounts

    except requests.exceptions.HTTPError as http_err:
        return f"Facebook API error: {http_err.response.json().get('error', {}).get('message', str(http_err))}"

    except requests.exceptions.RequestException as e:
        return f"Network error while contacting Facebook: {str(e)}"

    except Exception as e:
        return f"Unexpected error: {str(e)}"

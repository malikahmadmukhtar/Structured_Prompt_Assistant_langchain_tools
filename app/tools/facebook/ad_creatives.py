import streamlit as st
from langchain.tools import tool
import requests

from config.settings import fb_access_token, fb_base_url


@tool
def fetch_existing_creatives(ad_account_id: str):
    """
    Fetch existing ad creatives for the given Facebook ad account.

    Parameters:
    - ad_account_id: Facebook Ad Account ID

    Returns:
    - List of tuples (creative_id, creative_name) or error message.
    """
    st.sidebar.info("Used Fetch Creatives Tool")

    url = f"{fb_base_url}{ad_account_id}/adcreatives"
    params = {
        'access_token': fb_access_token,
        'fields': 'id,name,object_story_spec'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        creatives = data.get('data', [])
        if not creatives:
            return "No ad creatives found for this account."

        # Format output nicely
        creative_list = [(c['id'], c.get('name', '')) for c in creatives]
        return creative_list

    except requests.exceptions.RequestException as e:
        return f"Error fetching creatives: {str(e)}"



@tool
def start_creative_creation(
    ad_account_id: str,
    page_id: str,
    name: str | None = None,
    message: str | None = None,
    link: str | None = None,
    cta_type: str | None = None,
) -> str:
    """
    Initiates ad creative creation by saving required data to session and prompting for image upload.
    Don't call this tool before collecting all the below parameters and remember this rule for every other tool.

    Parameters:
    - ad_account_id: Facebook Ad Account ID
    - page_id: Facebook Page ID that owns the ad.
    - name: Name of the creative (e.g., "Summer Sale Ad").
    - message: The text shown above the ad creative.
    - link: URL the ad should link to.
    - cta_type: Call-to-action type (e.g., "SHOP_NOW", "LEARN_MORE").

    Returns:
    - Message prompting image upload or error if any field is missing.
    """
    st.sidebar.info("Used Start Creative creation tool")
    fields = {
        "ad_account_id": ad_account_id,
        "page_id": page_id,
        "name": name,
        "message": message,
        "link": link,
        "cta_type": cta_type
    }

    missing = [k for k, v in fields.items() if not v]
    if missing:
        return f"Missing required creative fields: {', '.join(missing)}."
    else:
        st.session_state.pending_creative = fields
        return "Creative details saved. Please upload an image to complete the process."


@tool
def delete_facebook_ad_creative(creative_id: str) -> str:
    """
    Deletes a Facebook Ad Creative.

    Parameters:
    - creative_id (str): The ID of the Ad Creative to delete.

    Returns:
    - Success or error message as a string.
    """
    try:
        url = f"{fb_base_url}{creative_id}"
        response = requests.delete(url, params={"access_token": fb_access_token})
        response.raise_for_status()
        result = response.json()

        if result.get("success"):
            return f"Ad Creative `{creative_id}` deleted successfully."
        else:
            return f"Failed to delete Ad Creative `{creative_id}`. Response: {result}"
    except requests.RequestException as e:
        return f"Error deleting Ad Creative: {str(e)}"

import requests
from langchain_core.tools import tool
from config.settings import fb_access_token, fb_base_url


@tool
def fetch_ad_sets(ad_account_id: str, campaign_id: str) -> str:
    """
    Fetch all ad sets for a given Facebook ad account using the get_facebook_ad_accounts tool and asking user for confirmation.
    Optionally filters by a specific campaign ID by asking the user first.
    """
    base_url = f"{fb_base_url}{ad_account_id}/adsets"
    params = {
        "fields": "name,id,daily_budget,billing_event,optimization_goal,bid_strategy,status,targeting",
        "access_token": fb_access_token,
    }

    if campaign_id:
        params["filtering"] = f'[{{"field":"campaign.id","operator":"IN","value":["{campaign_id}"]}}]'

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        ad_sets = response.json().get("data", [])

        if not ad_sets:
            return "No ad sets found for this account or campaign."

        # summaries = [
        #     f"- {ad['name']} (ID: {ad['id']}, Status: {ad['status']})"
        #     for ad in ad_sets
        # ]
        # return "Here are the ad sets:\n" + "\n".join(summaries)
        return ad_sets

    except requests.exceptions.RequestException as e:
        return f"Error fetching ad sets: {str(e)}"

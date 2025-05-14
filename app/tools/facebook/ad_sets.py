import json

import requests
from langchain_core.tools import tool
from config.settings import fb_access_token, fb_base_url


@tool
def fetch_ad_sets(ad_account_id: str, campaign_id: str) -> str:
    """
    Fetch all ad sets for a given Facebook ad account using the get_facebook_ad_accounts tool and asking user for confirmation.
    Optionally filters by a specific campaign ID by asking the user first.
    """
    print("Fetch ad sets called")
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


@tool
def create_ad_set(
    ad_account_id: str,
    name: str,
    daily_budget: int,
    billing_event: str,
    optimization_goal: str,
    bid_strategy: str,
    status: str,
    campaign_id: str,
    countries: list,
    age_min: int,
    age_max: int,
    interests: list = None,
    behaviors: list = None
) -> str:
    """
    Create an ad set with targeting under the selected ad account and campaign.

    DO NOT hardcode ad account IDs, campaign IDs, interest or behavior IDs directly.
    Instead:
    - Use the 'get_facebook_ad_accounts' tool and select the first or most relevant ad account.
    - Use the 'get_facebook_campaigns' tool to get a campaign from that account.
    - Use the 'search_interests' tool to get interest objects (with id and name) from keywords.
    - Use the 'get_behaviour_ids' tool to get behavior objects (with id and name) from keywords.
    - Ask the user at each step if unsure what information to use.

    Parameters:
    - ad_account_id: ID of the ad account (get this from 'get_facebook_ad_accounts')
    - name: Name of the ad set
    - daily_budget: Budget in cents (min 1000)
    - billing_event: "IMPRESSIONS" or "LINK_CLICKS"
    - optimization_goal: "LINK_CLICKS", "REACH", or "IMPRESSIONS"
    - bid_strategy: "LOWEST_COST_WITHOUT_CAP", "COST_CAP", or "BID_CAP"
    - status: "PAUSED" or "ACTIVE"
    - campaign_id: ID of the campaign (get this from 'fetch_campaigns')
    - countries: List of country codes (e.g., ["US", "GB"])
    - age_min: Minimum age (13–65)
    - age_max: Maximum age (13–65)
    - interests: List of interest dicts with `id` and `name` (use 'search_interests')
    - behaviors: List of behavior dicts with `id` and `name` (use 'search_behaviors')

    Returns:
    - ID of the created ad set or an error message if failed.
    """
    print("crate ad set called")
    url = f'{fb_base_url}{ad_account_id}/adsets'

    # Normalize country codes (e.g., UK → GB)
    countries = ['GB' if c.upper() == 'UK' else c.upper() for c in countries]

    # Build targeting
    targeting_spec = {
        'geo_locations': {'countries': countries},
        'age_min': age_min,
        'age_max': age_max
    }

    # Flexible spec only if needed
    flexible_spec = []

    if interests:
        flexible_spec.append({'interests': interests})

    if behaviors:
        if flexible_spec:
            flexible_spec[0]['behaviors'] = behaviors
        else:
            flexible_spec.append({'behaviors': behaviors})

    if flexible_spec:
        targeting_spec['flexible_spec'] = flexible_spec # type: ignore

    # Ensure daily budget is valid
    if daily_budget < 1000:
        daily_budget = 1000

    payload = {
        'name': name,
        'daily_budget': daily_budget,
        'billing_event': billing_event,
        'optimization_goal': optimization_goal,
        'bid_strategy': bid_strategy,
        'status': status,
        'campaign_id': campaign_id,
        'targeting': json.dumps(targeting_spec),
        'access_token': fb_access_token
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json().get('id')
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err} - {response.text}"
    except requests.exceptions.RequestException as req_err:
        return f"Request error: {req_err}"
    except Exception as e:
        return f"Unexpected error: {e}"
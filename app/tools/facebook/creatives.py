import requests
import streamlit as st
import json
from langchain.tools import tool


### not implemented yet
@tool
def create_facebook_creative(
    ad_account_id: str,
    page_id: str,
    name: str,
    message: str,
    link: str,
    cta_type: str = "SHOP_NOW"
) -> str:
    """
    Creates a Facebook ad creative by:
    1. Asking the user to upload an image using Streamlit
    2. Uploading the image to Facebook to get an image hash
    3. Creating an ad creative using the image hash and inputs

    Parameters:
    - ad_account_id: Facebook Ad Account ID (no 'act_' prefix)
    - page_id: Facebook Page ID
    - name: Name of the creative
    - message: Ad text
    - link: URL the ad points to
    - cta_type: Call to action type (e.g. SHOP_NOW, SIGN_UP)

    Returns:
    - Creative ID if successful, or error message if failed.
    """

    st.info("📤 Please upload an image to use in the ad creative")
    image_file = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"])

    if not image_file:
        return "Waiting for image upload..."

    # Upload the image to Facebook
    image_file.seek(0)
    upload_url = f"https://graph.facebook.com/v18.0/act_{ad_account_id}/adimages"

    files = {
        'file': ('ad_image.jpg', image_file, 'image/jpeg')
    }
    data = {
        'access_token': ACCESS_TOKEN
    }

    response = requests.post(upload_url, files=files, data=data)
    if response.status_code != 200:
        return f"❌ Image upload failed: {response.text}"

    try:
        image_hash = list(response.json()['images'].values())[0]['hash']
    except Exception as e:
        return f"⚠️ Failed to extract image hash: {str(e)}"

    # Create ad creative using the image hash
    creative_url = f"https://graph.facebook.com/v18.0/act_{ad_account_id}/adcreatives"

    link_data = {
        'message': message,
        'link': link,
        'image_hash': image_hash,
        'call_to_action': {
            'type': cta_type,
            'value': {'link': link}
        }
    }

    creative_data = {
        'name': name,
        'object_story_spec': json.dumps({
            'page_id': page_id,
            'link_data': link_data
        }),
        'access_token': ACCESS_TOKEN
    }

    creative_response = requests.post(creative_url, data=creative_data)
    if creative_response.status_code == 200:
        creative_id = creative_response.json().get('id')
        return f"✅ Creative created successfully. ID: {creative_id}"
    else:
        return f"❌ Error creating creative: {creative_response.text}"
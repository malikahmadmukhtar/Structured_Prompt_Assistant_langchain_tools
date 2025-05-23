from config.settings import fb_access_token, fb_base_url
import json
import requests
import streamlit as st

def finalize_creative_upload(creative_info, image_hash):
    """Create a Facebook ad creative after image upload."""
    url = f"{fb_base_url}{creative_info['ad_account_id']}/adcreatives"

    link_data = {
        "message": creative_info["message"],
        "link": creative_info["link"],
        "image_hash": image_hash,
        "call_to_action": {
            "type": creative_info["cta_type"],
            "value": {
                "link": creative_info["link"]
            }
        }
    }

    payload = {
        "name": creative_info["name"],
        "object_story_spec": json.dumps({
            "page_id": creative_info["page_id"],
            "link_data": link_data
        }),
        "access_token": fb_access_token
    }

    try:
        res = requests.post(url, data=payload)
        res.raise_for_status()
        return res.json().get("id")
    except requests.RequestException as e:
        return f"Error creating creative: {str(e)}"

def upload_image_to_facebook(ad_account_id, image_file):
    """Upload image directly to Facebook and return image_hash."""
    url = f"{fb_base_url}{ad_account_id}/adimages"
    image_file.seek(0)

    files = {'file': ('ad_image.jpg', image_file, 'image/jpeg')}
    data = {'access_token': fb_access_token}

    res = requests.post(url, files=files, data=data)
    if res.status_code == 200:
        try:
            return list(res.json()['images'].values())[0]['hash']
        except Exception:
            st.error("❌ Invalid image upload response.")
            return None
    else:
        st.error(f"❌ Facebook upload failed: {res.text}")
        return None

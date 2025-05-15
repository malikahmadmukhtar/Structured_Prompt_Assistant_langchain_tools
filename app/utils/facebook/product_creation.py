import uuid
import requests
import streamlit as st
import cloudinary.uploader
import os
from dotenv import load_dotenv
from config.settings import fb_base_url, fb_access_token

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_NAME"),
    api_key=os.getenv("CLOUDINARY_KEY"),
    api_secret=os.getenv("CLOUDINARY_SECRET")
)


def upload_image_to_cloudinary(image_file):
    try:
        result = cloudinary.uploader.upload(image_file)
        return result["secure_url"]
    except Exception as e:
        st.error(f"Cloudinary Error: {str(e)}")
        return None


def finalize_product_upload(product_info, image_url):
    """Send the final product creation request to Facebook"""
    try:
        price_minor = int(float(str(product_info['price']).replace(',', '').replace('PKR', '').strip()) * 100)
    except ValueError:
        return "Invalid price format."

    try:
        account_url = f"{fb_base_url}{product_info['ad_account_id']}?fields=currency"
        res = requests.get(account_url, params={'access_token': fb_access_token})
        res.raise_for_status()
        currency = res.json().get("currency", "USD")
    except requests.RequestException as e:
        return f"Error getting currency: {str(e)}"

    payload = {
        "name": product_info["name"],
        "description": product_info["description"],
        "price": price_minor,
        "currency": currency,
        "url": product_info["url"],
        "image_url": image_url,
        "availability": product_info["availability"],
        "retailer_id": str(uuid.uuid4()),
        "access_token": fb_access_token
    }

    try:
        post_url = f"{fb_base_url}{product_info['catalog_id']}/products"
        res = requests.post(post_url, data=payload)
        res.raise_for_status()
        return res.json().get("id")
    except requests.RequestException as e:
        return f"Error creating product: {str(e)}"

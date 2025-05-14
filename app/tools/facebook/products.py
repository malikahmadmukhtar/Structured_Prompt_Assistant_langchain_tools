import uuid
import requests
from langchain_core.tools import tool
from config.settings import fb_base_url, fb_access_token
import streamlit as st

@tool
def fetch_products_from_catalog(catalog_id: str) -> str:
    """Fetches all products from a Facebook catalog by catalog ID not the name which can get using the get_facebook_catalogs tool while following its structure.
    Show the list of catalogs and let the user choose the catalog then fetch based on user choice.
    Products will be shown to user with their name, description, price and image URL.
    """
    st.sidebar.info("Used Fetch Products Tool")

    print(f"Tool Called: fetch_products_from_catalog")
    base_url = f"{fb_base_url}{catalog_id}/products"
    print(f"Base URL: {base_url}")
    products = []
    params = {
        'access_token': fb_access_token,
        'fields': 'id,name,description,price,image_url,url,availability',
        'limit': 100
    }

    try:
        while True:
            response = requests.get(base_url, params=params)
            print(response.json())
            data = response.json()

            if 'error' in data:
                error = data['error']
                return f"Facebook API Error: {error['message']}"

            products.extend(data.get('data', []))

            next_page = data.get('paging', {}).get('next')
            if not next_page:
                break

            # For next page, use full URL (Graph API includes access_token in it)
            base_url = next_page

        if not products:
            return "No products found in this catalog."

        print(f"\nproducts are {str(products)}")
        return str(products)
        # return f"Fetched {len(products)} products from catalog {catalog_id} which are {products}."

    except Exception as e:
        return f"An error occurred: {str(e)}"



@tool
def delete_catalog_product(product_id: str) -> str:
    """
    Deletes a product from a Facebook catalog by its product ID.
    First show the products with their ids and then ask user to choose which product to delete.
    """
    st.sidebar.info("Used Delete Product Tool")

    url = f'{fb_base_url}{product_id}'
    params = {
        'access_token': fb_access_token
    }

    try:
        response = requests.delete(url, params=params)
        response.raise_for_status()
        success = response.json().get('success', False)
        if success:
            return f"Product {product_id} deleted successfully."
        else:
            return f"Product deletion request was received but not confirmed."
    except requests.exceptions.RequestException as e:
        return f"Error deleting product: {str(e)}"




# @tool
# def create_catalog_product(
#     catalog_id: str,
#     ad_account_id: str,
#     name: str,
#     description: str,
#     price: float,
#     url: str,
#     availability: str
# ) -> str:
#     """
#     Creates a product in the specified Facebook catalog.
#     Prompts the user to upload an image using Streamlit UI and uploads it to Cloudinary.
#
#     Args:
#         catalog_id: Facebook catalog ID.
#         ad_account_id: Ad account ID (to fetch currency).
#         name: Product name.
#         description: Product description.
#         price: Product price (float).
#         url: Product page URL.
#         availability: ["in stock", "out of stock", "available for order", "discontinued"].
#
#     Returns:
#         The ID of the created product or an error message.
#     """
#     st.info("Please upload an image for the product below:")
#
#     image_file = st.file_uploader("Upload Product Image", type=["jpg", "jpeg", "png"])
#     if not image_file:
#         st.stop()  # Pause execution until image is uploaded
#
#     image_url = upload_image_to_cloudinary(image_file)
#     if not image_url:
#         return "Image upload failed. Cannot proceed."
#
#     # Convert price to minor units (e.g., cents)
#     try:
#         price_minor = int(float(str(price).replace(',', '').replace('PKR', '').strip()) * 100)
#     except ValueError:
#         return "Invalid price format. Please enter a numeric value."
#
#     # Get currency from ad account
#     try:
#         account_url = f'{fb_base_url}{ad_account_id}?fields=currency'
#         account_response = requests.get(account_url, params={'access_token': fb_access_token})
#         account_response.raise_for_status()
#         currency = account_response.json().get('currency', 'USD')
#     except requests.RequestException as e:
#         return f"Failed to get ad account currency: {str(e)}"
#
#     product_data = {
#         'name': name,
#         'description': description,
#         'price': price_minor,
#         'currency': currency,
#         'url': url,
#         'image_url': image_url,
#         'availability': availability,
#         'retailer_id': str(uuid.uuid4()),
#         'access_token': fb_access_token
#     }
#
#     # Create product in Facebook catalog
#     try:
#         post_url = f'{fb_base_url}{catalog_id}/products'
#         response = requests.post(post_url, data=product_data)
#         response.raise_for_status()
#         return response.json().get('id')
#     except requests.RequestException as e:
#         return f"Error creating product: {str(e)}"


@tool
def create_catalog_product(
    catalog_id: str,
    ad_account_id: str,
    name: str,
    description: str,
    price: float,
    url: str,
    image_url: str,
    availability: str
) -> str:
    """
    Creates a product in the specified Facebook catalog.

    Args:
        catalog_id: The ID of the Facebook catalog(not the name).
        ad_account_id: The ad account ID (not business account ID) to fetch currency info.
        name: Name of the product.
        description: Product description.
        price: Product price (in local currency as float).
        url: Product page URL.
        image_url: Public URL of the product image.
        availability: Product availability status ["in stock", "out of stock", "available for order", "discontinued"].

    Returns:
        The ID of the created product or an error message.
    """
    st.sidebar.info("Used Create Product Tool")

    # Prepare and convert price to minor units (e.g., cents)
    try:
        price_minor = int(float(str(price).replace(',', '').replace('PKR', '').strip()) * 100)
    except ValueError:
        return "Invalid price format. Please enter a numeric value."

    # Get currency from ad account
    try:
        account_url = f'{fb_base_url}{ad_account_id}?fields=currency'
        account_response = requests.get(account_url, params={'access_token': fb_access_token})
        account_response.raise_for_status()
        currency = account_response.json().get('currency', 'USD')
    except requests.RequestException as e:
        return f"Failed to get ad account currency: {str(e)}"

    if not image_url:
        return "Product image URL is required."

    # Prepare product payload
    product_data = {
        'name': name,
        'description': description,
        'price': price_minor,
        'currency': currency,
        'url': url,
        'image_url': image_url,
        'availability': availability,
        'retailer_id': str(uuid.uuid4()),
        'access_token': fb_access_token
    }

    # Create product
    try:
        url = f'{fb_base_url}{catalog_id}/products'
        response = requests.post(url, data=product_data)
        response.raise_for_status()
        return response.json().get('id')
    except requests.RequestException as e:
        return f"Error creating product: {str(e)}"
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

        print(f"\nproducts tool output {str(products)}")
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


@tool
def start_catalog_product_creation(
    catalog_id: str,
    ad_account_id: str,
    name: str,
    description: str,
    price: float,
    url: str,
    availability: str,
) -> str:
    """
    Creates a new product in the selected Facebook catalog and collects all required information via user prompts.

    DO NOT hardcode any data or assume values. Instead:
    - Ask the user for all the data like (name, description, price and availability) before using this tool.
    - Use the 'get_facebook_catalogs' tool to get the catalog ID (ask the user to select from the results).
    - Use the 'get_facebook_ad_accounts' tool to fetch the currency (based on ad_account_id).

    Parameters:
    - catalog_id: ID of the Facebook catalog (fetched using 'get_facebook_catalogs'; do not use the name).
    - ad_account_id: The ad account ID (not business ID) used to retrieve currency info.
    - name: Name of the product (ask the user).
    - description: Description of the product (ask the user).
    - price: Product price (as a float, in the currency of the ad account; ask the user).
    - url: Product page URL (ask the user).
    - availability: Product availability status. Must be one of:
      ["in stock", "out of stock", "available for order", "discontinued"].

    Returns:
    - Message to upload image after calling this tool with correct data or an error if data is invalid.
    """

    required_fields = {
        "catalog_id": catalog_id,
        "ad_account_id": ad_account_id,
        "name": name,
        "description": description,
        "price": price,
        "url": url,
        "availability": availability,
    }

    # Check for any missing or invalid fields
    missing = [field for field, value in required_fields.items() if not value]
    if missing:
        return f"Missing required product fields: {', '.join(missing)}. Please provide all required data."

    # Validate availability field
    valid_availability = ["in stock", "out of stock", "available for order", "discontinued"]
    if availability.lower() not in valid_availability:
        return f"Invalid availability: '{availability}'. Must be one of: {', '.join(valid_availability)}."

    # All good — store in session
    st.session_state.pending_product = {
        "catalog_id": catalog_id,
        "ad_account_id": ad_account_id,
        "name": name,
        "description": description,
        "price": price,
        "url": url,
        "availability": availability.lower()
    }

    return "Product details received. Please upload a product image to complete catalog product creation."




# @tool
# def create_catalog_product(
#     catalog_id: str,
#     ad_account_id: str,
#     name: str,
#     description: str,
#     price: float,
#     url: str,
#     image_url: str,
#     availability: str
# ) -> str:
#     """
#     Creates a product in the specified Facebook catalog.
#
#     Args:
#         catalog_id: The ID of the Facebook catalog(not the name).
#         ad_account_id: The ad account ID (not business account ID) to fetch currency info.
#         name: Name of the product.
#         description: Product description.
#         price: Product price (in local currency as float).
#         url: Product page URL.
#         image_url: Public URL of the product image.
#         availability: Product availability status ["in stock", "out of stock", "available for order", "discontinued"].
#
#     Returns:
#         The ID of the created product or an error message.
#     """
#     st.sidebar.info("Used Create Product Tool")
#
#     # Prepare and convert price to minor units (e.g., cents)
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
#     if not image_url:
#         return "Product image URL is required."
#
#     # Prepare product payload
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
#     # Create product
#     try:
#         url = f'{fb_base_url}{catalog_id}/products'
#         response = requests.post(url, data=product_data)
#         response.raise_for_status()
#         return response.json().get('id')
#     except requests.RequestException as e:
#         return f"Error creating product: {str(e)}"
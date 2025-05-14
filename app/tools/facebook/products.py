import requests
from langchain_core.tools import tool
from config.settings import fb_base_url, fb_access_token


@tool
def fetch_products_from_catalog(catalog_id: str) -> str:
    """Fetches all products from a Facebook catalog by catalog ID not the name which can get using the get_facebook_catalogs tool while following its structure.
    Show the list of catalogs and let the user choose the catalog then fetch based on user choice.
    Products will be shown to user with their name, description, price and image URL.
    """
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

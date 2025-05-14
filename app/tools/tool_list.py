from app.tools.facebook.accounts import get_facebook_business_accounts, get_facebook_ad_accounts
from app.tools.facebook.ad_sets import fetch_ad_sets
from app.tools.facebook.campaigns import get_facebook_campaigns, create_fb_campaign
from app.tools.facebook.catalogs import get_facebook_catalogs, create_facebook_catalog
from app.tools.facebook.products import fetch_products_from_catalog, delete_catalog_product

declared_tool_list=[
    get_facebook_business_accounts,
    get_facebook_ad_accounts,
    get_facebook_catalogs,
    fetch_products_from_catalog,
    get_facebook_campaigns,
    fetch_ad_sets,
    create_fb_campaign,
    create_facebook_catalog,
    delete_catalog_product
]
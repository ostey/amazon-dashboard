import os
from dotenv import load_dotenv
from sp_api.api import Inventories
from sp_api.base import Marketplaces
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()

credentials = {
    "lwa_app_id": os.getenv("SP_API_CLIENT_ID"),
    "lwa_client_secret": os.getenv("SP_API_CLIENT_SECRET"),
    "refresh_token": os.getenv("SP_API_REFRESH_TOKEN"),
}

print("CLIENT_ID loaded:", credentials["lwa_app_id"] is not None)
print("CLIENT_SECRET loaded:", credentials["lwa_client_secret"] is not None)
print("REFRESH_TOKEN loaded:", credentials["refresh_token"] is not None)

inventory_api = Inventories(
    marketplace=Marketplaces.US,
    credentials=credentials
)

response = inventory_api.get_inventory_summary_marketplace(
    details=True,
    marketplaceIds=["ATVPDKIKX0DER"]
)

now_kr = datetime.now(ZoneInfo("Asia/Seoul"))
now_pt = datetime.now(ZoneInfo("America/Los_Angeles"))

print("=" * 60)
print("Account: EIGHTEEN H")
print("Marketplace: Amazon US")
print("Updated (KST):", now_kr.strftime("%Y-%m-%d %H:%M:%S"))
print("Updated (PDT):", now_pt.strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 60)

items = response.payload.get("inventorySummaries", [])

for item in items:
    sku = item.get("sellerSku")
    asin = item.get("asin")
    details = item.get("inventoryDetails", {})

    available = details.get("fulfillableQuantity", 0)
    reserved = details.get("reservedQuantity", {}).get("totalReservedQuantity", 0)
    inbound_working = details.get("inboundWorkingQuantity", 0)
    inbound_shipped = details.get("inboundShippedQuantity", 0)
    inbound_receiving = details.get("inboundReceivingQuantity", 0)

    inbound_total = (
        inbound_working +
        inbound_shipped +
        inbound_receiving
    )

    print("--------------------------------")
    print("SKU:", sku)
    print("ASIN:", asin)
    print("Available:", available)
    print("Reserved:", reserved)
    print("Inbound:", inbound_total)
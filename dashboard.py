import os
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sp_api.api import Inventories
from sp_api.base import Marketplaces

load_dotenv()

st.set_page_config(
    page_title="EIGHTEEN H Amazon Dashboard",
    layout="wide"
)

st.title("EIGHTEEN H Amazon Dashboard")

credentials = {
    "lwa_app_id": os.getenv("SP_API_CLIENT_ID"),
    "lwa_client_secret": os.getenv("SP_API_CLIENT_SECRET"),
    "refresh_token": os.getenv("SP_API_REFRESH_TOKEN"),
}

inventory_api = Inventories(
    marketplace=Marketplaces.US,
    credentials=credentials
)

items = []
next_token = None

while True:
    if next_token:
        response = inventory_api.get_inventory_summary_marketplace(
            details=True,
            marketplaceIds=["ATVPDKIKX0DER"],
            nextToken=next_token
        )
    else:
        response = inventory_api.get_inventory_summary_marketplace(
            details=True,
            marketplaceIds=["ATVPDKIKX0DER"]
        )

    payload = response.payload





    items.extend(payload.get("inventorySummaries", []))

    next_token = payload.get("pagination", {}).get("nextToken")

    if not next_token:
        break
# SKU → 상품명 매핑
sku_names = {
    "BLACKT-EU6035501-LAUNCHMONITOR": "SHOT5 런치모니터",
    "BLACKT-RANGEFINDER": "골프 레이저 거리측정기",
    "PROIMPACTOR": "프로임팩터",
}

rows = []

for item in items:
    sku = item.get("sellerSku")
    asin = item.get("asin")
    details = item.get("inventoryDetails", {})

    available = details.get("fulfillableQuantity", 0)
    reserved = details.get("reservedQuantity", {}).get("totalReservedQuantity", 0)

    inbound_working = details.get("inboundWorkingQuantity", 0)
    inbound_shipped = details.get("inboundShippedQuantity", 0)
    inbound_receiving = details.get("inboundReceivingQuantity", 0)

    inbound_total = inbound_working + inbound_shipped + inbound_receiving

    rows.append({
    "Product": sku_names.get(sku, sku),
    "ASIN": asin,
    "Available": available,
    "Reserved": reserved,
    "Inbound": inbound_total,
    })

df = pd.DataFrame(rows)

df = df.sort_values(
    by="Available",
    ascending=False
)

kr_time = datetime.now(
    ZoneInfo("Asia/Seoul")
).strftime("%Y-%m-%d %H:%M:%S")

pdt_time = datetime.now(
    ZoneInfo("America/Los_Angeles")
).strftime("%Y-%m-%d %H:%M:%S")

st.caption(
    f"Last Updated | KST: {kr_time} | PDT: {pdt_time}"
)

col1, col2, col3 = st.columns(3)

col1.metric("Total SKUs", len(df))
col2.metric("Total Available", int(df["Available"].sum()) if not df.empty else 0)
col3.metric("Total Inbound", int(df["Inbound"].sum()) if not df.empty else 0)




st.subheader("FBA Inventory")

st.dataframe(
    df,
    width="stretch",
    height=1200
)

csv = df.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="📥 Download Inventory CSV",
    data=csv,
    file_name="inventory.csv",
    mime="text/csv"
)
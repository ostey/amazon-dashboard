import os
import time
import json
import gzip
import io
import requests
from dotenv import load_dotenv
from sp_api.api import Reports
from sp_api.base import Marketplaces

load_dotenv()

credentials = {
    "lwa_app_id": os.getenv("SP_API_CLIENT_ID"),
    "lwa_client_secret": os.getenv("SP_API_CLIENT_SECRET"),
    "refresh_token": os.getenv("SP_API_REFRESH_TOKEN"),
}

reports_api = Reports(
    marketplace=Marketplaces.US,
    credentials=credentials
)

report_type = "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL"

create_response = reports_api.create_report(
    reportType=report_type,
    marketplaceIds=["ATVPDKIKX0DER"],
    dataStartTime="2026-06-01T00:00:00-07:00",
    dataEndTime="2026-06-16T23:59:59-07:00",
)

report_id = create_response.payload["reportId"]
print("Report ID:", report_id)

while True:
    report_response = reports_api.get_report(report_id)
    status = report_response.payload["processingStatus"]
    print("Status:", status)

    if status == "DONE":
        document_id = report_response.payload["reportDocumentId"]
        break

    if status in ["CANCELLED", "FATAL"]:
        print(report_response.payload)
        raise SystemExit("Report failed")

    time.sleep(20)

document_response = reports_api.get_report_document(document_id)
document_url = document_response.payload["url"]
compression = document_response.payload.get("compressionAlgorithm")

download_response = requests.get(document_url)

if compression == "GZIP":
    compressed_file = io.BytesIO(download_response.content)
    with gzip.GzipFile(fileobj=compressed_file, mode="rb") as gz:
        content = gz.read().decode("utf-8")
else:
    content = download_response.text

print(content[:3000])

with open("order_report_raw.txt", "w", encoding="utf-8") as f:
    f.write(content)

print("Saved: order_report_raw.txt")
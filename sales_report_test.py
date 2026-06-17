import os
import time
import json
import requests
import pandas as pd
import gzip
import io
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

# PDT 기준으로 나중에 자동화할 예정.
# 우선 테스트용: 2026-06-01 ~ 2026-06-16
report_type = "GET_SALES_AND_TRAFFIC_REPORT"

create_response = reports_api.create_report(
    reportType=report_type,
    marketplaceIds=["ATVPDKIKX0DER"],
    dataStartTime="2026-06-01T00:00:00-07:00",
    dataEndTime="2026-06-16T23:59:59-07:00",
    reportOptions={
        "dateGranularity": "DAY",
        "asinGranularity": "CHILD"
    }
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

download_response = requests.get(document_url)

compressed_file = io.BytesIO(download_response.content)

with gzip.GzipFile(fileobj=compressed_file, mode="rb") as gz:
    decoded_content = gz.read().decode("utf-8")

data = json.loads(decoded_content)

print(json.dumps(data, indent=2, ensure_ascii=False))

with open("sales_report_raw.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Saved: sales_report_raw.json")

print(json.dumps(data, indent=2, ensure_ascii=False))

with open("sales_report_raw.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Saved: sales_report_raw.json")
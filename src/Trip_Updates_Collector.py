from datetime import datetime
from pathlib import Path
import ssl
import time
import requests
from requests.adapters import HTTPAdapter

TRIP_UPDATES_URL = "https://webapps.regionofwaterloo.ca/api/grt-routes/api/tripupdates/1"
RAW_FOLDER = Path("GRT_GTFS/Trip_Updates")
INTERVAL_SECONDS = 60

class GRTSSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.set_ciphers("DEFAULT@SECLEVEL=1")
        kwargs["ssl_context"] = context
        return super().init_poolmanager(*args, **kwargs)

def download_snapshot(session):
    response = session.get(TRIP_UPDATES_URL, timeout=30)
    response.raise_for_status()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    file_path = RAW_FOLDER / f"trip_updates_{timestamp}.pb"

    file_path.write_bytes(response.content)

    print(f"Saved: {file_path}")

RAW_FOLDER.mkdir(parents=True, exist_ok=True)

session = requests.Session()
session.mount("https://webapps.regionofwaterloo.ca", GRTSSLAdapter())

print("Press Control + C to stop.")

try:
    while True:
        try:
            download_snapshot(session)
        except requests.RequestException as error:
            print(f"Download failed: {error}")

        time.sleep(INTERVAL_SECONDS)

finally:
    session.close()
import urllib.request
import urllib.error
import zipfile
import io
import shutil
from pathlib import Path

STATIC_FEED_URL = "https://webapps.regionofwaterloo.ca/api/grt-routes/api/staticfeeds/1"
RAW_FOLDER = Path("GRT_GTFS/Static_Feed")

try:
    if RAW_FOLDER.exists():
        shutil.rmtree(RAW_FOLDER)

    RAW_FOLDER.mkdir(parents=True, exist_ok=True)

    with urllib.request.urlopen(STATIC_FEED_URL) as response:
        with zipfile.ZipFile(io.BytesIO(response.read())) as z:
            z.extractall(RAW_FOLDER)

    print(f"Successfully extracted files to: {RAW_FOLDER}")

except urllib.error.URLError as error:
    print(f"Download failed: {error}")
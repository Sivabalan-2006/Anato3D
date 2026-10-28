import urllib.request
import zipfile
import time
from pathlib import Path

# Series Instance UID
SERIES_UID = "1.3.6.1.4.1.14519.5.2.1.8700.9668.150726169700362683111630632617"

# Determine path
if Path("data").exists() or Path("backend").exists():
    target_dir = Path("data/dicom/sample")
elif Path("../data").exists():
    target_dir = Path("../data/dicom/sample")
else:
    target_dir = Path("Anato3D/data/dicom/sample")

target_dir.mkdir(parents=True, exist_ok=True)
zip_path = target_dir / "series.zip"
api_url = f"https://nbia.cancerimagingarchive.net/nbia-api/v1/getImage?SeriesInstanceUID={SERIES_UID}"

# Header to prevent TCIA / Windows network resets
req = urllib.request.Request(
    api_url, 
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
)

print(f"Downloading DICOM series from TCIA API...\nUID: {SERIES_UID}")

max_retries = 3
for attempt in range(1, max_retries + 1):
    try:
        with urllib.request.urlopen(req, timeout=60) as response, open(zip_path, "wb") as out_file:
            downloaded = 0
            while True:
                chunk = response.read(1024 * 1024)  # 1MB buffer
                if not chunk:
                    break
                out_file.write(chunk)
                downloaded += len(chunk)
                print(f"\rDownloaded: {downloaded / (1024 * 1024):.2f} MB", end="", flush=True)
        print("\nDownload finished.")
        break
    except Exception as e:
        print(f"\n[Attempt {attempt}/{max_retries}] Download interrupted: {e}")
        if attempt < max_retries:
            print("Retrying in 5 seconds...")
            time.sleep(5)
        else:
            raise

print("Extracting DICOM files...")
with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall(target_dir)

zip_path.unlink()
print(f"Success! DICOM files extracted to: {target_dir.resolve()}")
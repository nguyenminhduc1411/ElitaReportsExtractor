import requests
import os
import tempfile
import subprocess
from packaging.version import Version
from version import (
    APP_VERSION,
    GITHUB_OWNER,
    GITHUB_REPO
)

API_URL = (
    f"https://api.github.com/repos/"
    f"{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
)


def check_latest():

    r = requests.get(API_URL, timeout=10)

    r.raise_for_status()

    data = r.json()

    latest = data["tag_name"].lstrip("v")

    return {
        "latest": latest,
        "current": APP_VERSION,
        "is_newer": Version(latest) > Version(APP_VERSION),
        "notes": data["body"],
        "url": data["html_url"],
        "download": data["assets"][0]["browser_download_url"]
        if data["assets"] else None
    }

def download_update(url, progress_callback=None):

    temp_folder = os.path.join(
        tempfile.gettempdir(),
        "ElitaReportsExtractor"
    )

    os.makedirs(
        temp_folder,
        exist_ok=True
    )

    filename = os.path.basename(url)

    save_path = os.path.join(
        temp_folder,
        filename
    )

    r = requests.get(
        url,
        stream=True,
        timeout=30
    )

    r.raise_for_status()

    total = int(
        r.headers.get(
            "content-length",
            0
        )
    )

    downloaded = 0

    with open(save_path, "wb") as f:

        for chunk in r.iter_content(8192):

            if not chunk:
                continue

            f.write(chunk)

            downloaded += len(chunk)

            if progress_callback and total:

                progress_callback(
                    downloaded,
                    total
                )

    return save_path
    
def run_installer(installer):

    subprocess.Popen([installer])
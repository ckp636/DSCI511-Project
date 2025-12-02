import json
import re
import requests
from bs4 import BeautifulSoup

COUNTY_CLASS_URL = "https://datausa.io/about/classifications/Geography/County"
BASE = "https://datausa.io"


def extract_county_master():
    print("[INFO] Fetching County classification page...")

    resp = requests.get(COUNTY_CLASS_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract window.__INITIAL_STATE__
    script_tag = soup.find("script", string=re.compile("window.__INITIAL_STATE__"))
    if not script_tag:
        raise RuntimeError("INITIAL_STATE not found")

    m = re.search(
        r"window.__INITIAL_STATE__\s*=\s*JSON\.parse\('(.+?)'\);",
        script_tag.string,
        re.DOTALL,
    )
    if not m:
        raise RuntimeError("Could not extract JSON payload")

    json_str = m.group(1).encode().decode("unicode_escape")
    payload = json.loads(json_str)

    results = payload["data"]["search"]["results"]

    # County entries only
    counties = [
        r for r in results
        if r.get("hierarchy") == "County"
    ]

    print(f"[INFO] Total counties found: {len(counties)}")
    return counties


def merge_into_master(new_data: dict, master_path="data-master.json"):
    try:
        with open(master_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing = {}

    for k, v in new_data.items():
        if k not in existing:
            existing[k] = v

    with open(master_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=4, ensure_ascii=False)

    print("[INFO] Merged into data-master.json")


if __name__ == "__main__":
    counties = extract_county_master()
    dataset = {}

    for c in counties:
        geo_id = c.get("id")
        slug = c.get("slug")

        # SAFE name extraction
        name = (
            c.get("label")
            or c.get("name")
            or c.get("display_name")
            or c.get("title")
            or c.get("profile_label")
            or (slug.replace("-", " ").title() if slug else geo_id)
        )

        url = f"{BASE}/profile/geo/{slug}"

        dataset[geo_id] = {
            "id": geo_id,
            "name": name,
            "type": "County",
            "slug": slug,
            "url": url,
        }

    merge_into_master(dataset)
    print("[DONE] County master data saved.")


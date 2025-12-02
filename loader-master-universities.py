import json
import re
import requests
from bs4 import BeautifulSoup

UNIVERSITY_CLASS_URL = "https://datausa.io/about/classifications/University/University"
BASE = "https://datausa.io"


def extract_university_master():
    print("[INFO] Fetching University classification page...")

    resp = requests.get(UNIVERSITY_CLASS_URL)
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

    # University entries only
    universities = [
        r for r in results
        if r.get("hierarchy") == "University"
    ]

    print(f"[INFO] Total universities found: {len(universities)}")
    return universities


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
    unis = extract_university_master()
    dataset = {}

    for u in unis:
        geo_id = u.get("id")
        slug = u.get("slug")

        # SAFE and CLEAN name extraction
        name = (
            u.get("label")
            or u.get("name")
            or u.get("title")
            or u.get("display_name")
            or u.get("profile_label")
            or (slug.replace("-", " ").title() if slug else geo_id)
        )

        url = f"{BASE}/profile/university/{slug}"

        dataset[geo_id] = {
            "id": geo_id,
            "name": name,
            "type": "University",
            "slug": slug,
            "url": url,
        }

    merge_into_master(dataset)
    print("[DONE] University master data saved.")


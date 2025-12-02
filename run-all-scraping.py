import json
import os
import time
import requests
from bs4 import BeautifulSoup

DETAIL_FILE = "data-detail.json"
MASTER_FILE = "data-master.json"
BASE = "https://datausa.io"

STATE_COUNTY_FIELDS = {
    "population": ["2023 Population", "2022 Population", "Population"],
    "median_age": ["2023 Median Age", "Median Age"],
    "income": ["2023 Median Household Income", "Median Household Income"],
    "poverty_rate": ["2023 Poverty Rate", "Poverty Rate"],
    "property_value": ["2023 Median Property Value", "Median Property Value"],
}

UNIVERSITY_FIELDS = {
    "tuition": ["2023 Undergraduate Tuition"],
    "enrolled": ["2023 Enrolled Students"],
    "net_price": ["2023 Average Net Price"],
    "growth": ["1 Year Growth"],
    "acceptance_rate": ["Acceptance Rate in 2023"],
    "full_time": ["Full-Time Enrollment"],
}

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def extract_from_profile(url, fields):
    print(f"[INFO] Scraping: {url}")
    time.sleep(0.5)

    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Failed request: {e}")
        return {}

    soup = BeautifulSoup(resp.text, "html.parser")
    stats_div = soup.find("div", {"class": "profile-stats"})
    if not stats_div:
        print("[WARN] No profile-stats found")
        return {}

    results = {}
    for key, labels in fields.items():
        value = None
        for label in labels:
            node = stats_div.find(string=label)
            if node:
                value_el = node.find_next()
                if value_el:
                    value = value_el.get_text(strip=True)
                    break
        results[key] = value

    return results

def main():
    master = load_json(MASTER_FILE)
    detail = load_json(DETAIL_FILE)

    print(f"[INFO] Master entries: {len(master)}")
    print(f"[INFO] Detail entries already loaded: {len(detail)}")

    for item_id, obj in master.items():
        if item_id in detail:
            print(f"[SKIP] Already have detail for {obj['name']}")
            continue

        print(f"\n[LOAD] Getting detail for: {obj['name']} ({obj['type']})")

        if obj["type"] in ["State", "County"]:
            stats = extract_from_profile(obj["url"], STATE_COUNTY_FIELDS)

        elif obj["type"] == "University":
            stats = extract_from_profile(obj["url"], UNIVERSITY_FIELDS)

        else:
            print("[WARN] Unknown type, skipping")
            continue

        detail[item_id] = {
            "id": item_id,
             "name": obj["name"],
            "type": obj["type"],
            "slug": obj["slug"],
            "url": obj["url"],
            **stats
        }

        save_json(DETAIL_FILE, detail)
        print("[SAVE] Updated data-detail.json")

    print("\n[DONE] All detail loading complete!")

if __name__ == "__main__":
    main()

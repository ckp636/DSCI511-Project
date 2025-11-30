import json
import re
import time
import requests
from bs4 import BeautifulSoup

BASE = "https://datausa.io"

# Which classifications to fetch
TYPES = {
    "Geography": ["State", "County"],
    "University": ["University"],
}

# Labels we look for inside the profile-stats block
FIELD_LABELS = {
    "population": [
        "2023 Population",
        "2022 Population",
        "Population",
    ],
    "median_age": [
        "2023 Median Age",
        "Median Age",
    ],
    "income": [
        "2023 Median Household Income",
        "Median Household Income",
    ],
    "poverty_rate": [
        "2023 Poverty Rate",
        "Poverty Rate",
    ],
    "property_value": [
        "2023 Median Property Value",
        "Median Property Value",
    ],
}

def construct_url(base: str, segments):
    """Join a base URL with path segments."""
    return "/".join([base.rstrip("/")] + [s.strip("/") for s in segments])

def get_initial_state(url: str):
    """Extract window.__INITIAL_STATE__ JSON from a DataUSA page."""
    resp = requests.get(url)
    resp.raise_for_status()
    html = resp.text
    soup = BeautifulSoup(html, "html.parser")

    script_tag = soup.find("script", string=re.compile(r"window\.__INITIAL_STATE__"))
    if not script_tag or not script_tag.string:
        raise ValueError(f"INITIAL_STATE not found at {url}")

    m = re.search(
        r"window\.__INITIAL_STATE__\s*=\s*JSON\.parse\('(.+?)'\);",
        script_tag.string,
        re.DOTALL,
    )
    if not m:
        raise ValueError(f"Could not extract JSON payload at {url}")

    json_str = m.group(1).encode().decode("unicode_escape")
    payload = json.loads(json_str)
    return payload

def get_classification_results():
    """Get all entries for the configured TYPES."""
    all_results = []
    for category, hier_list in TYPES.items():
        for hier in hier_list:
            url = construct_url(BASE, ["about", "classifications", category, hier])
            print(f"[INFO] Fetching classification: {category}/{hier} -> {url}")
            payload = get_initial_state(url)
            results = payload["data"]["search"]["results"]
            print(f"  Found {len(results)} results")
            all_results.extend(results)
    print(f"[INFO] Total classification objects: {len(all_results)}")
    return all_results

def build_geo_index(results):
    """Build a dict keyed by id with profile info and profile URL."""
    index = {}
    for obj in results:
        geo_id = obj.get("id")
        if not geo_id:
            continue

        hierarchy = obj.get("hierarchy")
        profile = obj.get("profile")
        slug = obj.get("slug")
        label = obj.get("label") or (slug.replace("-", " ").title() if slug else geo_id)

        if not profile or not slug:
            continue

        profile_url = construct_url(BASE, ["profile", profile, slug])

        if hierarchy in ("State", "County", "University"):
            type_name = hierarchy
        else:
            type_name = hierarchy or "Unknown"

        index[geo_id] = {
            "id": geo_id,
            "name": label,
            "type": type_name,
            "profile": profile,
            "slug": slug,
            "url": profile_url,
        }

    print(f"[INFO] Built geo index entries: {len(index)}")
    return index

def extract_stats_from_profile(url: str, delay: float = 0.5):
    """Fetch a profile page and extract key stats from the 'profile-stats' area.

    Returns a dict with string values as shown on the site.
    """
    print(f"[INFO] Scraping profile: {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    stats_div = soup.find("div", {"class": "profile-stats"})
    if not stats_div:
        print("  [WARN] profile-stats not found")
        time.sleep(delay)
        return {}

    stats = {}
    for field, labels in FIELD_LABELS.items():
        value = None
        for label in labels:
            node = stats_div.find(string=label)
            if node:
                value_el = node.find_next()
                if value_el:
                    value = value_el.get_text(strip=True)
                    break
        stats[field] = value

    time.sleep(delay)
    return stats

def build_dataset(limit_per_type=None):
    """Full pipeline: classifications -> index -> scrape stats -> dataset dict.

    limit_per_type: if set to an int, only scrape up to that many of each type
                    (State / County / University). Use None for no limit.
    """
    results = get_classification_results()
    index = build_geo_index(results)

    dataset = {}
    counts_by_type = {}

    for geo_id, info in index.items():
        t = info["type"]
        counts_by_type.setdefault(t, 0)

        if limit_per_type is not None and counts_by_type[t] >= limit_per_type:
            continue

        try:
            stats = extract_stats_from_profile(info["url"])
        except Exception as e:
            print(f"  [ERROR] Failed to scrape {info['url']}: {e}")
            stats = {}

        counts_by_type[t] += 1

        dataset[geo_id] = {
            "id": geo_id,
            "name": info["name"],
            "type": info["type"],
            "slug": info["slug"],
            "url": info["url"],
            "population": stats.get("population"),
            "median_age": stats.get("median_age"),
            "income": stats.get("income"),
            "poverty_rate": stats.get("poverty_rate"),
            "property_value": stats.get("property_value"),
        }

    print("[INFO] Scraping complete. Counts by type:", counts_by_type)
    return dataset

def main():
    # For a small test run, set limit_per_type to a small number (e.g., 3).
    # For the full scrape, change to None (may take a long time).
    dataset = build_dataset(limit_per_type=5)

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=4, ensure_ascii=False)

    print("[INFO] Saved data-master.json and data.json")

if __name__ == "__main__":
    main()

import json
from scrape_core import build_dataset

def merge_into_master(new_data: dict, master_path: str = "data-master.json") -> None:
    try:
        with open(master_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing = {}

    # Add only new keys
    for k, v in new_data.items():
        if k not in existing:
            existing[k] = v

    with open(master_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    data = build_dataset(limit_per_type=100, only_type="State")
    merge_into_master(data)

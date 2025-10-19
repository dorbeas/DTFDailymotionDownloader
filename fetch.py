import os
import time
import requests

# === CONFIG ===
channel_names = [
    "upbulk", "upbulk1", "upbulk2", "upbulk3", "upbulk4", "upbulk5", "upbulk6", "upbulk7", "upbulk8", "upbulk9",
    "upbulk10", "upbulk11", "upbulk12", "upbulk13", "upbulk14", "upbulk15", "upbulk16", "upbulk17", "upbulk18",
    "upbulk22", "upbulk23", "upbulk24", "upbulk25", "upbulk26", "upbulk27"
]

expected_counts = {
    "upbulk": 6, "upbulk1": 1856, "upbulk2": 1032, "upbulk3": 1663, "upbulk4": 866,
    "upbulk5": 1481, "upbulk6": 895, "upbulk7": 1021, "upbulk8": 605, "upbulk9": 1451,
    "upbulk10": 570, "upbulk11": 1131, "upbulk12": 1803, "upbulk13": 929, "upbulk14": 594,
    "upbulk15": 867, "upbulk16": 713, "upbulk17": 565, "upbulk18": 563,
    "upbulk22": 269, "upbulk23": 285, "upbulk24": 207, "upbulk25": 183,
    "upbulk26": 249, "upbulk27": 287
}

log2_dir = "log2"
archive_dir = "archive"
base_api = "https://api.dailymotion.com/user/{}/videos"

# === SETUP ===
def ensure_folders():
    os.makedirs(log2_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)

def fetch_all_videos(channel_name):
    seen = set()
    all_entries = []
    created_before = int(time.time())
    while True:
        params = {
            "fields": "url,created_time",
            "limit": 100,
            "created_before": created_before
        }
        try:
            resp = requests.get(base_api.format(channel_name), params=params)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("list", [])
            if not items:
                break
            new_entries = []
            for item in items:
                url = item.get("url")
                ts = item.get("created_time")
                key = (url, ts)
                if key not in seen:
                    seen.add(key)
                    new_entries.append(key)
            if not new_entries:
                break
            all_entries.extend(new_entries)
            created_before = min(ts for _, ts in new_entries) - 1
            print(f"✅ {channel_name}: {len(new_entries)} new videos (total: {len(all_entries)})")
            time.sleep(0.5)
        except Exception as e:
            print(f"❌ Error fetching {channel_name}: {e}")
            break
    return [url for url, _ in sorted(all_entries, key=lambda x: x[1], reverse=True)]

def load_archive(channel_name):
    archive_path = os.path.join(archive_dir, f"{channel_name}.txt")
    if not os.path.exists(archive_path):
        return set()
    with open(archive_path, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_log2(channel_name, urls):
    path = os.path.join(log2_dir, f"{channel_name}.txt")
    with open(path, "w", encoding="utf-8") as f:
        for url in urls:
            f.write(f"{url}\n")
    print(f"📁 Saved {len(urls)} URLs to {path}")

def update_archive(channel_name, urls):
    archive_path = os.path.join(archive_dir, f"{channel_name}.txt")
    existing = load_archive(channel_name)
    new_urls = [url for url in urls if url not in existing]
    if new_urls:
        with open(archive_path, "a", encoding="utf-8") as f:
            for url in new_urls:
                f.write(f"{url}\n")
        print(f"🗃️ Added {len(new_urls)} new URLs to archive/{channel_name}.txt")
    else:
        print(f"🗃️ No new URLs for {channel_name}")

def recover_missing(channel_name, fetched_urls):
    archive_urls = load_archive(channel_name)
    missing = [url for url in archive_urls if url not in fetched_urls]
    if missing:
        print(f"🔁 Recovering {len(missing)} missing URLs from archive")
        combined = fetched_urls + missing
        save_log2(channel_name, combined)
        return combined
    return fetched_urls

def recursive_recovery(channel_name):
    expected = expected_counts.get(channel_name)
    attempt = 1
    urls = fetch_all_videos(channel_name)
    update_archive(channel_name, urls)

    while attempt <= 5:
        recovered = recover_missing(channel_name, urls)
        actual = len(recovered)
        print(f"🔍 Attempt {attempt}: {channel_name} has {actual}/{expected} videos")
        if expected and actual >= expected:
            print(f"✅ Final count for {channel_name}: {actual} (matches expected)")
            break
        if actual == len(urls):
            print(f"⚠️ No new recoveries found. Still short by {expected - actual}")
        urls = recovered
        attempt += 1
    else:
        print(f"❌ Max recovery attempts reached for {channel_name}. Final count: {len(urls)}")

# === MAIN ===
def main():
    ensure_folders()
    for channel in channel_names:
        recursive_recovery(channel)

if __name__ == "__main__":
    main()

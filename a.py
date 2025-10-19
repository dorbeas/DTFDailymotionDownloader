from yt_dlp import YoutubeDL

archive_path = "archive/DTFvideos16.txt"
log_path = "logs/DTFvideos16.txt"
start_line = 100  # 0-based index for line 600

# Load logged titles
with open(log_path, "r", encoding="utf-8") as f:
    logged_titles = [line.strip() for line in f if line.strip()]

# Load archive URLs
with open(archive_path, "r", encoding="utf-8") as f:
    archive_urls = [line.strip() for line in f if line.strip()]

# Prepare yt-dlp
ydl_opts = {
    'quiet': True,
    'skip_download': True,
    'noplaylist': True
}

print(f"🔍 Comparing titles from line {start_line + 1} onward...\n")

with YoutubeDL(ydl_opts) as ydl:
    for i in range(start_line, min(len(archive_urls), len(logged_titles))):
        url = archive_urls[i]
        expected_title = logged_titles[i]

        try:
            info = ydl.extract_info(url, download=False)
            actual_title = info.get("title", "").strip()

            if actual_title == expected_title:
                print(f"✅ Line {i+1}: Title matches")
            else:
                print(f"❌ Line {i+1}: Title mismatch")
                print(f"   Archive title: {actual_title}")
                print(f"   Log title    : {expected_title}")
        except Exception as e:
            print(f"❌ Line {i+1}: Failed to extract title from URL")
            print(f"   URL: {url}")
            print(f"   Error: {e}")

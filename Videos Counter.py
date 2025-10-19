import requests

input_file = "DTFvideos Channels List.txt"
output_file = "DTFvideos Video Counts.txt"

with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
    for line in infile:
        url = line.strip()
        if not url:
            continue

        username = url.split("/")[-1]
        api_url = f"https://api.dailymotion.com/user/{username}?fields=videos_total"

        try:
            response = requests.get(api_url, timeout=5)
            data = response.json()

            if "videos_total" in data:
                count = data["videos_total"]
                print(f"{username} → {count} videos")
                outfile.write(f"{username} → {count} videos\n")
            else:
                print(f"{username} → Channel not found or no videos")
                outfile.write(f"{username} → Channel not found or no videos\n")

        except Exception as e:
            print(f"⚠️ Error checking {username}: {e}")
            outfile.write(f"{username} → Error\n")

print(f"\n✅ Done! Video counts saved to '{output_file}'")

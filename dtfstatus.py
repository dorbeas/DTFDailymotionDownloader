import requests

output_file = "DTFvideos Channel Status.txt"

with open(output_file, "w", encoding="utf-8") as file:
    for i in range(1, 200):
        username = f"DTFvideos{i}"
        api_url = f"https://api.dailymotion.com/user/{username}?fields=videos_total"

        try:
            response = requests.get(api_url, timeout=5)
            data = response.json()

            if "videos_total" in data:
                count = data["videos_total"]
                if count > 0:
                    status = f"{username} → ✅ {count} videos"
                else:
                    status = f"{username} → ⚠️ Channel exists but no videos"
                print(status)
                file.write(status + "\n")

            elif "error" in data and data["error"]["type"] == "not_found":
                print(f"{username} → ❌ Channel not found")
                # Do not write to file

            else:
                status = f"{username} → ⚠️ Unknown response"
                print(status)
                file.write(status + "\n")

        except Exception as e:
            error_msg = f"{username} → ⚠️ Error: {e}"
            print(error_msg)
            file.write(error_msg + "\n")

print(f"\n✅ Done! Results saved to '{output_file}'")

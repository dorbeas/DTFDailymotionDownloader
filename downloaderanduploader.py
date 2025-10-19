import os
from pyrogram import Client, filters
from pyrogram.types import Message

# === CONFIG ===
api_id = 25936332
api_hash = "143ce1fde47f1ff58807200919d5d980"
bot_token = "8432002920:AAEz9GroO0aybXj317I_tx-doyqiVJJX52w"
upload_channel_id = -1002957212621

download_dir = "downloads"
log_dir = "logs"
archive_dir = "archive"
batch_size = 1000  # ✅ Updated to process 1000 videos per batch

channel_names = [
    # DTFvideos channels
    "DTFvideos", "DTFvideos12", "DTFvideos13", "DTFvideos14", "DTFvideos15", "DTFvideos16", "DTFvideos17",
    "DTFvideos18", "DTFvideos19", "DTFvideos20", "DTFvideos21", "DTFvideos22", "DTFvideos23", "DTFvideos24",
    "DTFvideos25", "DTFvideos26", "DTFvideos31", "DTFvideos32", "DTFvideos34", "DTFvideos36", "DTFvideos37",
    "DTFvideos38", "DTFvideos39", "DTFvideos40", "DTFvideos41", "DTFvideos46", "DTFvideos50", "DTFvideos52",
    "DTFvideos102", "DTFvideos103", "DTFvideos104", "DTFvideos105", "DTFvideos107", "DTFvideos108", "DTFvideos109",
    "DTFvideos110", "DTFvideos112", "DTFvideos114", "DTFvideos117", "DTFvideos119", "DTFvideos120", "DTFvideos190",

    # upbulk channels
    "upbulk", "upbulk1", "upbulk2", "upbulk3", "upbulk4", "upbulk5", "upbulk6", "upbulk7", "upbulk8", "upbulk9",
    "upbulk10", "upbulk11", "upbulk12", "upbulk13", "upbulk14", "upbulk15", "upbulk16", "upbulk17", "upbulk18",
    "upbulk22", "upbulk23", "upbulk24", "upbulk25", "upbulk26", "upbulk27"
]

app = Client("dtf_uploader_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# === SETUP ===
def ensure_folders():
    os.makedirs(download_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)

def clean_downloads():
    for f in os.listdir(download_dir):
        os.remove(os.path.join(download_dir, f))

def get_log_path(channel_name):
    return os.path.join(log_dir, f"{channel_name}.txt")

def get_archive_path(channel_name):
    return os.path.join(archive_dir, f"{channel_name}.txt")

def get_last_uploaded_index(channel_name):
    log_path = get_log_path(channel_name)
    if not os.path.exists(log_path):
        return -1
    with open(log_path, "r", encoding="utf-8") as f:
        return len([line for line in f if line.strip()]) - 1

def log_video(channel_name, title):
    with open(get_log_path(channel_name), "a", encoding="utf-8") as f:
        f.write(f"{title}\n")

def get_urls_to_process(channel_name):
    archive_path = get_archive_path(channel_name)
    if not os.path.exists(archive_path):
        return []
    with open(archive_path, "r", encoding="utf-8") as f:
        all_urls = [line.strip() for line in f if line.strip()]
    start_index = get_last_uploaded_index(channel_name) + 1
    return all_urls[start_index:]

def download_video(url):
    import yt_dlp
    ydl_opts = {
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'quiet': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)
            title = info.get("title")
            return filepath, title
    except Exception as e:
        print(f"❌ Download failed for {url}: {e}")
        return None

async def process_channel(channel_name):
    urls = get_urls_to_process(channel_name)
    if not urls:
        return

    log_path = get_log_path(channel_name)
    already_started = os.path.exists(log_path) and os.path.getsize(log_path) > 0

    if not already_started:
        try:
            pin_msg = await app.send_message(upload_channel_id, f"📌 Now uploading from: **{channel_name}**")
            await app.pin_chat_message(upload_channel_id, pin_msg.id, disable_notification=True)
        except Exception as e:
            print(f"⚠️ Failed to send pin message for {channel_name}: {e}")

    total = len(urls)
    for batch_start in range(0, total, batch_size):
        clean_downloads()
        batch = urls[batch_start:batch_start + batch_size]
        downloaded = []

        for url in batch:
            result = download_video(url)
            if result:
                downloaded.append(result)

        for i, (filepath, title) in enumerate(downloaded, start=1):
            if not os.path.exists(filepath):
                print(f"⚠️ File missing: {filepath}")
                continue
            try:
                percent = int((i / len(downloaded)) * 100)
                print(f"📤 Uploading {i}/{len(downloaded)} ({percent}%) → {title}")
                await app.send_video(upload_channel_id, video=filepath, caption=title)
                log_video(channel_name, title)
                os.remove(filepath)
            except Exception as e:
                print(f"❌ Upload failed for {title}: {e}")
                await app.send_message(upload_channel_id, f"❌ Error uploading `{title}`: {e}")
                continue

# === MAIN WORKFLOW ===
async def process_channels():
    ensure_folders()
    clean_downloads()

    started = any(
        os.path.exists(get_log_path(name)) and os.path.getsize(get_log_path(name)) > 0
        for name in channel_names
    )
    if not started:
        await app.send_message(upload_channel_id, "🚀 Starting DTFvideos upload process...")

    for channel_name in channel_names:
        await process_channel(channel_name)

    if not started:
        await app.send_message(upload_channel_id, "✅ All channels processed!")

# === COMMAND HANDLER ===
@app.on_message(filters.command("start") & filters.text)
async def start_handler(client: Client, message: Message):
    await process_channels()

# === RUN ===
if __name__ == "__main__":
    ensure_folders()
    app.run()

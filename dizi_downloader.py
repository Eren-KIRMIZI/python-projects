import asyncio
import subprocess
import os
import requests
from playwright.async_api import async_playwright

URL = "https://www.diziyou.io/mr-robot-1-sezon-7-bolum/"
SAVE_DIR = r"C:\Users\Eren\Desktop\dene"

os.makedirs(SAVE_DIR, exist_ok=True)

m3u8_found = None
subs_found = []

async def run():
    global m3u8_found, subs_found

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="msedge",
            headless=False
        )
        context = await browser.new_context()
        page = await context.new_page()

        def handle_request(request):
            global m3u8_found, subs_found
            url = request.url

            if ".m3u8" in url and not m3u8_found:
                print("M3U8 bulundu:", url)
                m3u8_found = url

            if url.endswith(".vtt") or url.endswith(".srt"):
                if url not in subs_found:
                    print("Altyazı bulundu:", url)
                    subs_found.append(url)

        page.on("request", handle_request)

        await page.goto(URL)
        await page.wait_for_timeout(15000)  # 15 sn bekle

        await browser.close()

asyncio.run(run())

# Video indir
if m3u8_found:
    subprocess.run([
        "python", "-m", "yt_dlp",
        "--referer", URL,
        "--merge-output-format", "mp4",
        "-o", os.path.join(SAVE_DIR, "video.%(ext)s"),
        m3u8_found
    ])

# Altyazı indir
for sub in subs_found:
    r = requests.get(sub)
    name = sub.split("/")[-1]
    with open(os.path.join(SAVE_DIR, name), "wb") as f:
        f.write(r.content)

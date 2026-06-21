import os
import asyncio
import subprocess
from flask import Flask, jsonify
from playwright.async_api import async_playwright

app = Flask(__name__)

TARGET_URL = "https://www.bigmumbaia.com/#/saasLottery/WinGo?gameCode=WinGo_1M&lottery=WinGo"

# यह फंक्शन चेक करेगा और ज़रूरत पड़ने पर क्रोमियम खुद डाउनलोड कर लेगा
def install_playwright_browsers():
    try:
        print("Playwright क्रोमियम ब्राउज़र इंस्टॉल करने की कोशिश कर रहे हैं...")
        subprocess.run(["playwright", "install", "chromium"], check=True)
        print("क्रोमियम सफलतापूर्वक इंस्टॉल हो गया!")
    except Exception as e:
        print(f"ब्राउज़र इंस्टॉलेशन में एरर आया (शायद पहले से इंस्टॉल हो): {e}")

async def scrape_wingo_history():
    try:
        async with async_playwright() as p:
            # क्रोमियम को बिना सैंडबॉक्स और पूरी तरह से स्टेबल मोड में चलाना
            try:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-blink-features=AutomationControlled"
                    ]
                )
            except Exception as launch_error:
                # अगर ब्राउज़र गायब होने की एरर दोबारा आए, तो रनटाइम पर इंस्टॉल मारो
                if "Executable doesn't exist" in str(launch_error):
                    install_playwright_browsers()
                    browser = await p.chromium.launch(
                        headless=True,
                        args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
                    )
                else:
                    raise launch_error
            
            # असली मोबाइल ब्राउज़र जैसा दिखने के लिए User-Agent बदलना
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
            )
            
            page = await context.new_page()
            print("Big Mumbai URL पर जा रहे हैं...")
            
            # वेबसाइट लोड होने का इंतज़ार
            await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000) # 5 सेकंड का होल्ड
            
            # पेज का टाइटल चेक करना
            title = await page.title()
            
            await browser.close()
            return {
                "status": "connected",
                "page_title": title,
                "message": "सर्वर सफलतापूर्वक वेबसाइट से जुड़ गया है और ब्राउज़र रेडी है!"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error_details": str(e)
        }

@app.route('/')
def home():
    return "<h1>AI Predictor Engine Operational</h1><p>Use <b>/fetch-data</b></p>"

@app.route('/fetch-data')
def fetch_data():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(scrape_wingo_history())
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "flask_error", "message": str(e)})

if __name__ == '__main__':
    # पहली बार सर्वर स्टार्ट होते ही बैकग्राउंड में ब्राउज़र सेटअप ट्रिगर करना
    install_playwright_browsers()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

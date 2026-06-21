import os
import asyncio
from flask import Flask, jsonify
from playwright.async_api import async_playwright

app = Flask(__name__)

TARGET_URL = "https://www.bigmumbaia.com/#/saasLottery/WinGo?gameCode=WinGo_1M&lottery=WinGo"

async def scrape_wingo_history():
    # एरर को पकड़ने के लिए ब्लॉक
    try:
        async with async_playwright() as p:
            # क्रोमियम को बिना सैंडबॉक्स और पूरी तरह से स्टेबल मोड में चलाना
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled"
                ]
            )
            
            # असली मोबाइल ब्राउज़र जैसा दिखने के लिए User-Agent बदलना
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
            )
            
            page = await context.new_page()
            print("Big Mumbai URL पर जा रहे हैं...")
            
            # वेबसाइट लोड होने का इंतज़ार
            await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000) # 5 सेकंड का एक्स्ट्रा होल्ड
            
            # पेज का टाइटल चेक करना
            title = await page.title()
            
            await browser.close()
            return {
                "status": "connected",
                "page_title": title,
                "message": "सर्वर सफलतापूर्वक वेबसाइट से जुड़ गया है!"
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
    # बिना एरर के एसिंक फंक्शन को रन करना
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(scrape_wingo_history())
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "flask_error", "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

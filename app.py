import os
import asyncio
from flask import Flask, jsonify
from playwright.async_api import async_playwright

app = Flask(__name__)

TARGET_URL = "https://www.bigmumbaia.com/#/saasLottery/WinGo?gameCode=WinGo_1M&lottery=WinGo"

async def scrape_wingo_data():
    async with async_playwright() as p:
        # बिना स्क्रीन/हेडलेस मोड में ब्राउज़र खोलना
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        page = await browser.new_page()
        
        try:
            print("Target URL पर जा रहे हैं...")
            await page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            
            # वेबसाइट को पूरी तरह लोड होने के लिए 5 सेकंड का वेट
            await asyncio.sleep(5)
            
            # यहाँ हम पेज का टाइटल चेक कर रहे हैं ताकि पता चले पेज खुला या नहीं
            title = await page.title()
            
            # TODO: अगले स्टेप में हम यहाँ Big Mumbai के सटीक HTML क्लास/आईडी एलिमेंट्स डालकर 
            # लाइव टाइमर और पिछले कलर्स का डेटा निकालेंगे।
            
            await browser.close()
            return {"status": "success", "page_title": title, "message": "सफलतापूर्वक कनेक्ट हो गया!"}
            
        except Exception as e:
            await browser.close()
            return {"status": "failed", "error": str(e)}

@app.route('/')
def home():
    return "AI Predictor Backend Server is Running!"

@app.route('/fetch-data')
def fetch_data():
    # स्क्रैपिंग फंक्शन को रन करना
    result = asyncio.run(scrape_wingo_data())
    return jsonify(result)

if __name__ == '__main__':
    # रेंडर के पोर्ट पर ऐप को रन करना
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

import os
import asyncio
from flask import Flask, jsonify
from playwright.async_api import async_playwright

app = Flask(__name__)

TARGET_URL = "https://www.bigmumbaia.com/#/saasLottery/WinGo?gameCode=WinGo_1M&lottery=WinGo"

async def scrape_wingo_history():
    async with async_playwright() as p:
        # रेंडर सर्वर के लिए क्रोमियम सेटिंग्स
        browser = await p.chromium.launch(
            headless=True, 
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        page = await browser.new_page()
        
        try:
            print("Big Mumbai पेज पर जा रहे हैं...")
            await page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            
            # टेबल और डेटा लोड होने के लिए थोड़ा एक्स्ट्रा वेट
            await page.wait_for_timeout(7000)
            
            # स्क्रीनशॉट में दिखने वाली 'Game history' टेबल के रोज़ (Rows) को सेलेक्ट करना
            # ये कसी诺 वेबसाइट्स आमतौर पर 'van-row' या टेबल टैग्स का इस्तेमाल करती हैं
            rows_selector = ".game-list .van-row, table tbody tr, .history-list .item"
            
            # अगर सेलेक्टर मिलने में टाइम लगे तो बैकअप चेकिंग
            rows = await page.query_selector_all(rows_selector)
            
            history_data = []
            
            if not rows:
                # अगर डायरेक्ट क्लास नहीं मिली, तो हम पेज से टेक्स्ट निकालने की कोशिश करेंगे
                page_text = await page.inner_text("body")
                if "Period" in page_text or "Game history" in page_text:
                    return {"status": "connected", "message": "वेबसाइट लोड हो गई है, डेटा पार्सिंग चालू है।"}
                return {"status": "empty", "message": "पेज लोड हुआ पर हिस्ट्री टेबल नहीं दिखी। लॉगिन या कैप्चा की ज़रूरत हो सकती है।"}

            # टॉप 5 रिकॉर्ड्स निकालना
            for row in rows[:5]:
                text = await row.inner_text()
                # टेक्स्ट को साफ करके लिस्ट बनाना (Period, Number, Size, Color)
                clean_text = [item.strip() for item in text.split("\n") if item.strip()]
                if clean_text:
                    history_data.append(clean_text)
                    
            await browser.close()
            return {
                "status": "success",
                "game": "WinGo 1M",
                "latest_history": history_data
            }
            
        except Exception as e:
            await browser.close()
            return {"status": "failed", "error": str(e)}

@app.route('/')
def home():
    return "<h1>AI Predictor Engine Operational</h1><p>Use <b>/fetch-data</b> to trigger scraper.</p>"

@app.route('/fetch-data')
def fetch_data():
    result = asyncio.run(scrape_wingo_history())
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

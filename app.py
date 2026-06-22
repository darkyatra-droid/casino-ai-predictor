import os
from flask import Flask, jsonify
import cloudscraper
from bs4 import BeautifulSoup

app = Flask(__name__)

TARGET_URL = "https://www.bigmumbaia.com/#/saasLottery/WinGo?gameCode=WinGo_1M&lottery=WinGo"

def scrape_wingo_with_scraper():
    try:
        # Cloudflare की सिक्योरिटी को बाईपास करने वाला एडवांस स्क्रैपर
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'android',
                'desktop': False
            }
        )
        
        print("Big Mumbai से डेटा सीधे फेच कर रहे हैं...")
        response = scraper.get(TARGET_URL, timeout=30)
        
        if response.status_code == 200:
            # HTML को पार्स करना
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # पेज का टाइटल चेक करना
            title = soup.title.string if soup.title else "No Title Found"
            
            return {
                "status": "success",
                "page_title": title,
                "message": "सर्वर बिना ब्राउज़र के सीधे वेबसाइट से जुड़ गया!",
                "raw_html_snippet": response.text[:500]  # चेक करने के लिए थोड़ा सा HTML कोड
            }
        else:
            return {
                "status": "failed",
                "status_code": response.status_code,
                "message": "वेबसाइट ने रिक्वेस्ट ब्लॉक कर दी या रिस्पॉन्स नहीं दिया।"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error_details": str(e)
        }

@app.route('/')
def home():
    return "<h1>AI Predictor Engine - Cloud Powered</h1><p>Use <b>/fetch-data</b></p>"

@app.route('/fetch-data')
def fetch_data():
    result = scrape_wingo_with_scraper()
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

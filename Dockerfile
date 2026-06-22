# प्लेराइट का ऑफिशियल इमेज जिसमें क्रोम और सारी लाइब्रेरी पहले से हैं
FROM mcr.microsoft.com/playwright:v1.44.0-jammy

# पायथन इंस्टॉल करना
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv

# वर्किंग डायरेक्टरी सेट करना
WORKDIR /app

# वर्चुअल एनवायरनमेंट बनाना और एक्टिव करना
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# डिपेंडेंसी कॉपी और इंस्टॉल करना
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# बाकी का कोड कॉपी करना
COPY . .

# पोर्ट सेट करना
EXPOSE 8080

# ऐप को ग्यूनिकॉर्न से चलाना
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]

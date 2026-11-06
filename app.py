import requests

# १. तुझा अचूक डेटा (इथे तुझे डिटेल्स टाक)
BOT_TOKEN = "9037885219:AAEO4b4NQXu5eM7Ijwmnt1CuS7tPHFjCvRI"
CHAT_ID = "तुझा_USERINFO_कडुन_मिळालेला_नंबर"  # उदा. 567891234

# जुन्या ३-४ लाईन्स काढून फक्त एवढंच लिहा:
BOT_TOKEN = "9037885219:AAEO4b4NQXu5eM7Ijwmnt1CuS7tPHFjCvRI"
CHAT_ID = "तुमचा_अचूक_नंबर_इथे_टाका"  # (उदा. "123456789" अवतरण चिन्हात)

# ही लिंक जशी आहे तशीच कॉपी-पेस्ट कर भाऊ, यात कोणतीही स्पेस नसावी
url = f"https://telegram.org{BOT_TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": "भाऊ, अखेर आपला टेलिग्राम मेसेज चालू झाला! 🚀"}

response = requests.post(url, json=payload)

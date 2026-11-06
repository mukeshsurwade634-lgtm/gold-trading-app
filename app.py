import requests

# १. तुझा अचूक डेटा (इथे तुझे डिटेल्स टाक)
BOT_TOKEN = "9037885219:AAEO4b4NQXu5eM7Ijwmnt1CuS7tPHFjCvRI"
CHAT_ID = "तुझा_USERINFO_कडुन_मिळालेला_नंबर"  # उदा. 567891234

# २. एकदम सोपा आणि अचूक मेसेज पाठवणारा कोड
url = f"https://telegram.org{BOT_TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": "भाऊ, अखेर आपला टेलिग्राम मेसेज चालू झाला! 🚀"}

# ३. मेसेज पाठवणे
response = requests.post(url, json=payload)

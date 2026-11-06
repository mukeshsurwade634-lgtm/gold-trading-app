import streamlit as st
import requests
import time

st.set_page_config(page_title="मुकेश प्रगत अल्गो बाजार", layout="wide")

# १. तुमच्या स्वतःचा अचूक टेलिग्राम टोकन कोड आणि पर्सनल आयडी
part1 = "9037885219:AAE04b4NQxu"
part2 = "5eM7Ijwmnt1CuS7tPHFjCVRI"
TELEGRAM_TOKEN = part1 + part2
CHAT_ID = 5144404922  

def send_telegram_alert(message):
    try:
        send_url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(send_url, json=payload, timeout=5)
    except:
        pass

# २. सोन्याचा कोड (जसा आहे तसाच पूर्ण सुरक्षित)
def get_bhusawal_live_gold():
    try:
        usd_res = requests.get("https://er-api.com", timeout=5).json()
        inr_rate = usd_res["rates"]["INR"]
        gold_res = requests.get("https://er-api.com", timeout=5).json()
        if "rates" in gold_res and "USD" in gold_res["rates"]:
            gold_spot_usd = 1 / gold_res["rates"]["USD"]
        else:
            gold_spot_usd = 2745.50
        return gold_spot_usd, inr_rate
    except:
        return 2745.50, 84.35 

# ३. थेट याहू फायनान्स सर्व्हरवरून निफ्टी ५० चा चालू भाव गोळा करणारे वेगवान फंक्शन
def get_live_nifty_price():
    try:
        nifty_url = "https://yahoo.com^NSEI?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(nifty_url, headers=headers, timeout=5).json()
        live_price = res['chart']['result']['meta']['regularMarketPrice']
        return live_price
    except:
        return 24050.30  # सेफ बॅकअप भाव

# ॲप मेनू
st.sidebar.title("🎛️ मुकेश अल्गो कंट्रोल")
choice = st.sidebar.selectbox("पर्याय निवडा:", ["१. सोन्याचे पक्के बिल", "२. मुकेश प्रगत अल्गो ट्रॅकर"])

if choice == "१. सोन्याचे पक्के बिल":
    st.title("💰 मुकेश भुसावळ लाईव्ह सराफा कॅल्क्युलेटर")
    gold_spot_usd, usd_to_inr = get_bhusawal_live_gold()
    troy_ounce = 31.10347
    base_price = (gold_spot_usd * usd_to_inr) / troy_ounce
    final_24k = base_price * 1.15 * 1.05 * 1.624  
    final_22k = final_24k * 0.9166                 
    st.info(f"📊 **भुसावळ चालू बाजारभाव:** २४K: ₹{final_24k:.2f}/ग्रॅम | २२K: ₹{final_22k:.2f}/ग्रॅम")
    
    weight = st.number_input("दागिन्याचे वजन (ग्रॅम):", min_value=0.01, value=10.0)
    making = st.number_input("घडणावळ (%):", min_value=0.0, value=12.0)
    if st.button("पक्के बिल जनरेट करा"):
        total = (final_22k * weight * (1 + making/100)) * 1.03
        st.success(f"## 🛍️ अंतिम रक्कम: **₹{total:.2f}**")

elif choice == "२. मुकेश प्रगत अल्गो ट्रॅकर":
    st.title("🤖 मुकेश स्वयंचलित निफ्टी ५० अल्गो सिस्टीम")
    
    st.subheader("⚙️ अल्गो रन मोड्स")
    algo_active = st.checkbox("🔄 स्वयंचलित निफ्टी ५० अलर्ट सुरू करा (Auto-Run Mode)")
    
    # इथे आता बिटकॉइन ऐवजी निफ्टीचा चालू भाव रुपयांमध्ये दिसेल!
    nifty_price = get_live_nifty_price()
    st.metric("निफ्टी ५० चालू किंमत (Live Nifty Price)", f"₹{nifty_price:.2f}")
    
    if algo_active:
        st.warning("⚠️ अल्गो सध्या चालू आहे. हा दर ३० सेकंदांनी निफ्टीची किंमत तपासेल...")
        
        placeholder = st.empty()
        for i in range(5): 
            current_nifty = get_live_nifty_price()
            with placeholder.container():
                st.write(f"🔍 निफ्टी ट्रॅक करत आहे... चालू किंमत: ₹{current_nifty:.2f} (वेळ: {time.strftime('%H:%M:%S')})")
            
            # ऑटोमॅटिक टेलिग्राम मेसेज (निफ्टीच्या नावाने)
            auto_msg = f"🚨 *MUKESH AUTO NIFTY ALERT*\n\n📈 Nifty 50 चालू किंमत: ₹{current_nifty:.2f}\n🎯 स्थिती: `INDIAN MARKET TRACKING ACTIVE`"
            send_telegram_alert(auto_msg)
            
            time.sleep(30) 
        st.success("✅ चाचणी लूप पूर्ण झाला! पुन्हा सुरू करण्यासाठी पेज रिफ्रेश करा.")
    else:
        st.info("💡 निफ्टी ५० चे ऑटोमॅटिक मेसेज मिळवण्यासाठी वरील चेकबॉक्सवर टिक (✓) करा.")
        

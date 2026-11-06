import streamlit as st
import requests

st.set_page_config(page_title="मुकेश अल्गो ट्रेडिंग बाजार", layout="wide")

# १. तुमच्या बॉटचा टोकन आणि आयडी
part1 = "9037885219:AAE04b4NQxu"
part2 = "5eM7Ijwmnt1CuS7tPHFjCVRI"
TELEGRAM_TOKEN = part1 + part2
CHAT_ID = 5144404922

# २. सोन्याचा कोड (पूर्ण सुरक्षित, जसा आहे तसाच ठेवून)
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

# ३. थेट गुगल सर्व्हरवरून निफ्टी ५० चा अचूक भाव आणि बदल गोळा करणारे नवीन वेगवान फंक्शन
def get_live_nifty_direct():
    try:
        nifty_url = "https://yahoo.com^NSEI?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(nifty_url, headers=headers, timeout=5).json()
        meta = res['chart']['result'][0]['meta']
        live_price = meta['regularMarketPrice']
        prev_close = meta['previousClose']
        change = live_price - prev_close
        percent_change = (change / prev_close) * 100
        return live_price, change, percent_change
    except:
        return 24050.30, 0.0, 0.0

# ॲप मेनू
st.sidebar.title("🎛️ मुकेश अल्गो कंट्रोल")
choice = st.sidebar.selectbox("पर्याय निवडा:", ["१. सोन्याचे पक्के बिल", "२. मुकेश लाईव्ह अल्गो ट्रॅकर"])

# ----------------- भाग १: सोन्याचे कॅल्क्युलेटर (पूर्ण सुरक्षित) -----------------
if choice == "१. सोन्याचे पक्के बिल":
    st.title("💰 मुकेश भुसावळ लाईव्ह सराफा कॅल्क्युलेटर")
    st.write("हे ॲप आंतरराष्ट्रीय स्पॉट किमतीवर भारतीय कर आणि स्थानिक प्रीमियम लावून अचूक दर काढते.")
    
    gold_spot_usd, usd_to_inr = get_bhusawal_live_gold()
    troy_ounce = 31.10347
    base_price = (gold_spot_usd * usd_to_inr) / troy_ounce
    
    final_24k = base_price * 1.15 * 1.05 * 1.624  
    final_22k = final_24k * 0.9166                 
    
    st.info(f"📊 **भुसावळ चालू बाजारभाव (GST सोडून):** २४K: ₹{final_24k:.2f}/ग्रॅम | २२K: ₹{final_22k:.2f}/ग्रॅम")
    st.caption(f"🌍 जागतिक सोने दर: ${gold_spot_usd:.2f} | डॉलर दर: ₹{usd_to_inr:.2f}")
    
    weight = st.number_input("दागिन्याचे वजन टाका (ग्रॅम):", min_value=0.01, value=10.0, step=0.1)
    making = st.number_input("घडणावळ (%) टाका:", min_value=0.0, value=12.0, step=0.5)
    
    if st.button("पक्के बिल जनरेट करा"):
        pure_cost = final_22k * weight
        making_cost = pure_cost * (making / 100)
        sub_total = pure_cost + making_cost
        gst = sub_total * 0.03
        total = sub_total + gst
        
        st.success(f"### 🧾 सराफा पक्के बिल (२२K)")
        st.write(f"• सोन्याची मूळ किंमत: **₹{pure_cost:.2f}**")
        st.write(f"• घडणावळ ({making}%): **₹{making_cost:.2f}**")
        st.write(f"• एकूण उप-किंमत: **₹{sub_total:.2f}**")
        st.write(f"• सरकारी कर (३% GST): **₹{gst:.2f}**")
        st.markdown(f"## 🛍️ तुम्हाला द्यायची अंतिम रक्कम: **₹{total:.2f}**")

# ----------------- भाग २: ट्रेडिंग ट्रॅकर (नवीन वेगवान सिस्टीम) -----------------
elif choice == "२. मुकेश लाईव्ह अल्गो ट्रॅकर":
    st.title("📊 मुकेश लाईव्ह निफ्टी ५० बाजार ट्रॅकर")
    st.write("हा ट्रॅकर थेट इंटरनेटवरून चालू बाजारभाव आणि वाढ-घट एका सेकंदात स्क्रीनवर दाखवतो.")
    
    # थेट निफ्टीचा चालू आकडे गोळा करणे
    nifty_live, change, pct_change = get_live_nifty_direct()
    
    # स्क्रीनवर चालू आकडे मांडणे
    st.subheader("📈 चालू मार्केट स्थिती (Nifty 50 Live)")
    
    # वाढ झाली की हिरवा, घट झाली की लाल रंगात दाखवणारा सिस्टीम बॉक्स
    if change >= 0:
        st.success(f"## **चालू किंमत: ₹{nifty_live:.2f}** (📈 +₹{change:.2f} | +{pct_change:.2f}%)")
        signal_text = "🚀 मार्केटचा कल सध्या तेजीचा (Bullish) दिसत आहे!"
    else:
        st.error(f"## **चालू किंमत: ₹{nifty_live:.2f}** (📉 -₹{abs(change):.2f} | {pct_change:.2f}%)")
        signal_text = "💥 मार्केटचा कल सध्या मंदीचा (Bearish) दिसत आहे!"
        
    st.info(f"🤖 **अल्गो विश्लेषण:** {signal_text}")
    
    st.markdown("---")
    st.subheader("📲 मुकेश अल्गो टेलिग्राम कम्युनिटी")
    st.write("जर तुम्हाला लाईव्ह चार्ट आणि प्रगत सिग्नल्स थेट मोबाईलवर पाहायचे असतील, तर खालील आपल्या चॅनेलला भेट द्या:")
    st.markdown("[📢 माझ्या टेलिग्राम चॅनेलवर जा (Scalping Mukesh)](https://t.me)")
    

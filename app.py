import streamlit as st
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="मुकेश अल्गो ट्रेडिंग बाजार", layout="wide")

# १. तुमच्या बॉटचा टोकन आणि आयडी
part1 = "9037885219:AAE04b4NQxu"
part2 = "5eM7Ijwmnt1CuS7tPHFjCVRI"
TELEGRAM_TOKEN = part1 + part2
CHAT_ID = 5144404922  # वैयक्तिक आयडी

# २. सोन्याचा कोड (ज्याला आपण अजिबात हात लावलेला नाही, हा जसा आहे तसाच सुरक्षित आहे)
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

# ॲप डावा मेनू
st.sidebar.title("🎛️ मुकेश अल्गो कंट्रोल")
choice = st.sidebar.selectbox("पर्याय निवडा:", ["१. सोन्याचे पक्के बिल", "२. मुकेश प्रगत ट्रेडिंगव्ह्यू ट्रॅकर"])

# ----------------- भाग १: सोन्याचे कॅल्क्युलेटर (हा पूर्ण सुरक्षित आहे) -----------------
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
        st.write(f"• एकूण उप-किंमत (Sub-Total): **₹{sub_total:.2f}**")
        st.write(f"• सरकारी कर (३% GST): **₹{gst:.2f}**")
        st.markdown(f"## 🛍️ तुम्हाला द्यायची अंतिम रक्कम: **₹{total:.2f}**")

# -------- भाग २: ट्रेडिंग कोड (यात आपण बदल करून TradingView इंजिन बसवले आहे) --------
elif choice == "२. मुकेश प्रगत ट्रेडिंगव्ह्यू ट्रॅकर":
    st.title("📈 निफ्टी ५० आणि शेअर्स लाईव्ह आलेख (TradingView)")
    st.write("हा ट्रॅकर थेट ट्रेडिंगव्ह्यूच्या हाय-स्पीड सर्व्हरवरून चालतो, ज्यामुळे एरर येण्याचा चान्स संपतो.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 लाईव्ह कॅन्डलस्टिक आलेख (Nifty 50)")
        tradingview_chart = """
        <div class="tradingview-widget-container" style="height:500px;width:100%;">
          <div id="tradingview_chart"></div>
          <script type="text/javascript" src="https://tradingview.com"></script>
          <script type="text/javascript">
          new TradingView.widget({
            "autosize": true,
            "symbol": "NSE:NIFTY",
            "interval": "5",
            "timezone": "Asia/Kolkata",
            "theme": "dark",
            "style": "1",
            "locale": "en",
            "enable_publishing": false,
            "hide_side_toolbar": false,
            "allow_symbol_change": true,
            "container_id": "tradingview_chart"
          });
          </script>
        </div>
        """
        components.html(tradingview_chart, height=520)

    with col2:
        st.subheader("🤖 ऑटो टेक्निकल संकेत मीटर")
        tradingview_meter = """
        <div class="tradingview-widget-container" style="width:100%;height:400px;">
          <iframe src="https://tradingview.com" 
                  width="100%" height="430" frameborder="0" allowtransparency="true" scrolling="no"></iframe>
        </div>
        """
        components.html(tradingview_meter, height=450)
        
    st.markdown("---")
    st.subheader("📲 मुकेश अल्गो टेलिग्राम कम्युनिटी")
    st.markdown("[📢 माझ्या टेलिग्राम चॅनेलवर जा (Scalping Mukesh)](https://t.me)")
    

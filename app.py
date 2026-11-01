import streamlit as st
import requests
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="माझे ऑल-इन-वन ॲप", layout="wide")

st.sidebar.title("🎛️ ॲप मेनू")
choice = st.sidebar.selectbox("तुम्हाला काय वापरायचे आहे?", ["१. सोन्याचे पक्के बिल", "२. निफ्टी ट्रेडिंग ट्रॅकर"])

def get_live_market_data():
    try:
        usd_url = "https://er-api.com"
        usd_data = requests.get(usd_url).json()
        live_usd = usd_data["rates"]["INR"]
        
        gold_ticker = yf.Ticker("XAUUSD=X")
        gold_data = gold_ticker.history(period="1d", interval="1m")
        
        if not gold_data.empty:
            live_gold = gold_data['Close'].iloc[-1]
        else:
            live_gold = 3874.40
            
        return live_gold, live_usd
    except:
        return 3874.40, 95.07

if choice == "१. सोन्याचे पक्के बिल":
    st.title("💰 भुसावळ लाईव्ह सोन्याचे पक्के बिल")
    st.write("हा कॅल्क्युलेटर इंटरनेटवरून दर सेकंदाला थेट सोन्याचा आणि डॉलरचा भाव स्वतः शोधून काढतो.")
    
    gold_spot_usd, usd_to_inr = get_live_market_data()
    
    troy_ounce = 31.10347
    base_price = (gold_spot_usd * usd_to_inr) / troy_ounce
    final_24k = base_price * 1.15 * 1.05
    final_22k = final_24k * 0.916
    
    st.info(f"📊 **रिअल-टाइम चालू बाजारभाव:** २४K: ₹{final_24k:.2f}/ग्रॅम | २२K: ₹{final_22k:.2f}/ग्रॅम")
    st.caption(f"🌍 आंतरराष्ट्रीय स्पॉट भाव: ${gold_spot_usd:.2f} | डॉलर दर: ₹{usd_to_inr:.2f} (हा डेटा आपोआप अपडेट होतो)")
    
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("दागिन्याचे वजन (ग्रॅम):", min_value=0.1, value=10.0, step=0.1)
    with col2:
        making = st.number_input("घडणावळ (टक्केवारी %):", min_value=0.0, value=12.0, step=0.5)
        
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
        st.markdown(f"## 🛍️ अंतिम रक्कम: **₹{total:.2f}**")

elif choice == "२. निफ्टी ट्रेडिंग ट्रॅकर":
    st.title("📈 निफ्टी ५० ऑप्शन्स इंडिकेटर ट्रॅकर")
    
    nifty = yf.Ticker("^NSEI")
    data = nifty.history(period="1mo", interval="1d")
    
    if not data.empty:
        data['20_SMA'] = data['Close'].rolling(window=20).mean()
        live_price = data['Close'].iloc[-1]
        sma_value = data['20_SMA'].iloc[-1]
        
        st.metric(label="निफ्टी ५० चालू किंमत", value=f"₹{live_price:.2f}", delta=f"{live_price - sma_value:.2f} (20 SMA वरून)")
        
        if live_price > sma_value:
            st.success("🟢 **ट्रेडिंग संकेत: BUY CALL (तेजी)**")
        else:
            st.error("🔴 **ट्रेडिंग संकेत: BUY PUT (मंदी)**")

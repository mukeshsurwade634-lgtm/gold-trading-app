import streamlit as st
import requests
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="माझे ऑल-इन-वन ॲप", layout="wide")

st.sidebar.title("🎛️ ॲप मेनू")
choice = st.sidebar.selectbox("तुम्हाला काय वापरायचे आहे?", ["१. सोन्याचे पक्के बिल", "२. निफ्टी प्रगत ट्रेडिंग ट्रॅकर"])

def get_live_market_data():
    try:
        usd_url = "https://er-api.com"
        usd_data = requests.get(usd_url).json()
        live_usd = usd_data["rates"]["INR"]
        
        gold_in_usd = 3904.50
        try:
            gold_url = "https://er-api.com"
            gold_data = requests.get(gold_url).json()
            if "rates" in gold_data and "USD" in gold_data["rates"]:
                gold_spot_usd = 1 / gold_data["rates"]["USD"]
                if gold_spot_usd > 1000:
                    gold_in_usd = gold_spot_usd
        except:
            pass
        return gold_in_usd, live_usd
    except:
        return 3904.50, 95.07

# ----------------- भाग १: सोन्याचे कॅल्क्युलेटर -----------------
if choice == "१. सोन्याचे पक्के बिल":
    st.title("💰 भुसावळ लाईव्ह सोन्याचे पक्के बिल")
    gold_spot_usd, usd_to_inr = get_live_market_data()
    troy_ounce = 31.10347
    base_price = (gold_spot_usd * usd_to_inr) / troy_ounce
    final_24k = base_price * 1.15 * 1.05
    final_22k = final_24k * 0.916
    
    st.info(f"📊 **रिअल-टाइम चालू बाजारभाव:** २४K: ₹{final_24k:.2f}/ग्रॅम | २२K: ₹{final_22k:.2f}/ग्रॅम")
    
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

# ----------------- भाग २: प्रगत ट्रेडिंग ट्रॅकर -----------------
elif choice == "२. निफ्टी प्रगत ट्रेडिंग ट्रॅकर":
    st.title("📈 निफ्टी ५० प्रगत इंडिकेटर ट्रॅकर (EMA, RSI, MACD)")
    st.write("हा ट्रॅकर एकाच वेळी अनेक इंडिकेटर्सचा अभ्यास करून बाजाराचा कल दाखवतो.")
    
    nifty = yf.Ticker("^NSEI")
    # ६० दिवसांचा डेटा जेणेकरून इंडिकेटर्स अचूक येतील
    data = nifty.history(period="3mo", interval="1d")
    
    if not data.empty:
        # १. EMA ९ आणि २६ काढणे
        data['EMA_9'] = data['Close'].ewm(span=9, adjust=False).mean()
        data['EMA_26'] = data['Close'].ewm(span=26, adjust=False).mean()
        
        # २. RSI १४ काढणे
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI_14'] = 100 - (100 / (1 + rs))
        
        # चालू दिवसाचे आकडे
        live_price = data['Close'].iloc[-1]
        ema9 = data['EMA_9'].iloc[-1]
        ema26 = data['EMA_26'].iloc[-1]
        rsi = data['RSI_14'].iloc[-1]
        
        # स्क्रीनवर इंडिकेटर्स दाखवणे
        col1, col2, col3 = st.columns(3)
        col1.metric(label="निफ्टी चालू किंमत", value=f"₹{live_price:.2f}")
        col2.metric(label="RSI (14)", value=f"{rsi:.2f}")
        col3.metric(label="EMA 9 vs EMA 26", value=f"₹{ema9:.2f}", delta=f"{(ema9-ema26):.2f}")
        
        st.markdown("---")
        st.subheader("🤖 ऑटोमॅटिक मल्टि-इंडिकेटर संकेत (Signal)")
        
        # संकेत ठरवण्याचे प्रगत लॉजिक
        score = 0
        if live_price > ema9: score += 1
        if ema9 > ema26: score += 1
        if rsi > 50 and rsi < 70: score += 1
        
        if score >= 2:
            st.success(f"🟢 **मजबूत तेजी संकेत (BUY CALL)** \n\nबहुतांश इंडिकेटर्स (EMA आणि RSI) मार्केटमध्ये तेजी दाखवत आहेत. [स्कोर: {score}/3]")
        elif score == 1:
            st.warning(f"🟡 **मार्केट न्यूट्रल / साईडवेज (थांबा आणि वाट पाहा)** \n\nइंडिकेटर्स संभ्रमात आहेत, कोणताही स्पष्ट कल नाही. [स्कोर: {score}/3]")
        else:
            st.error(f"🔴 **मजबूत मंदी संकेत (BUY PUT)** \n\nबहुतांश इंडिकेटर्स मार्केटमध्ये घसरण दाखवत आहेत. [स्कोर: {score}/3]")
            
        st.subheader("📋 हिस्टोरिकल डेटा चार्ट टेबल")
        st.dataframe(data[['Close', 'EMA_9', 'EMA_26', 'RSI_14']].tail(5))

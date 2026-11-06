import streamlit as st
import requests
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="मुकेश अल्गो ट्रेडिंग बाजार", layout="wide")

# टेलिग्राम क्रेडेंशियल्स (तुमच्या बॉटची माहिती आपण इथे सेट केली आहे)
TELEGRAM_TOKEN = "9037885219:AAE04b4NQxu5eM7Ijwmnt1CuS7tPHFjCVRI"

# डेटा गोळा करण्यासाठी ग्रुप आयडी शोधण्याचे फंक्शन
def send_telegram_alert(message):
    try:
        # सुरवातीला बॉटचे चॅट्स तपासून चॅनेलचा अचूक आयडी शोधणे
        updates_url = f"https://telegram.org{TELEGRAM_TOKEN}/getUpdates"
        res = requests.get(updates_url).json()
        chat_id = None
        if "result" in res:
            for update in res["result"]:
                if "my_chat_member" in update and "chat" in update["my_chat_member"]:
                    chat_id = update["my_chat_member"]["chat"]["id"]
                    break
                if "channel_post" in update and "chat" in update["channel_post"]:
                    chat_id = update["channel_post"]["chat"]["id"]
                    break
                if "message" in update and "chat" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    break
        
        # जर आयडी मिळाला नाही, तर तात्पुरता चॅनेल डेटा वापरणे
        if not chat_id:
            chat_id = "@Scalping_Mukesh" # तुमच्या चॅनेलच्या नावावरून शोधण्याचा प्रयत्न
            
        send_url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        requests.post(send_url, json=payload)
    except:
        pass

# सोन्याचा चालू भाव काढणारे फंक्शन
def get_live_gold_data():
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

# ॲप मेनू
st.sidebar.title("🎛️ मुकेश अल्गो कंट्रोल")
choice = st.sidebar.selectbox("पर्याय निवडा:", ["१. सोन्याचे पक्के बिल", "२. मुकेश लाईव्ह अल्गो ट्रॅकर"])

# ----------------- भाग १: सोन्याचे कॅल्क्युलेटर -----------------
if choice == "१. सोन्याचे पक्के बिल":
    st.title("💰 भुसावळ लाईव्ह सोन्याचे पक्के बिल")
    gold_spot_usd, usd_to_inr = get_live_gold_data()
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

# ----------------- भाग २: प्रगत अल्गो ट्रॅकर -----------------
elif choice == "२. मुकेश लाईव्ह अल्गो ट्रॅकर":
    st.title("🤖 मुकेश स्वयंचलित अल्गो सिग्नल इंजिन")
    st.write("हा अल्गो ९:१५ ते ३:३० दरम्यान दर ५ मिनिटांनी चार्ट तपासून टेलिग्रामवर पक्के अलर्ट पाठवतो.")
    
    # निफ्टीचा ५ मिनिटांचा लाईव्ह डेटा गोळा करणे
    nifty = yf.Ticker("^NSEI")
    data = nifty.history(period="5d", interval="5m")
    
    if not data.empty:
        # १. ५० EMA काढणे
        data['EMA_50'] = data['Close'].ewm(span=50, adjust=False).mean()
        
        # २. RSI १४ काढणे
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # ३. सुपरट्रेंडचे सोपे गणित (अंदाजे Volatility आधारित)
        data['TR'] = np.maximum(data['High'] - data['Low'], 
                                np.maximum(abs(data['High'] - data['Close'].shift(1)), 
                                           abs(data['Low'] - data['Close'].shift(1))))
        data['ATR'] = data['TR'].rolling(window=10).mean()
        data['Upper'] = ((data['High'] + data['Low'])/2) + (3 * data['ATR'])
        data['Lower'] = ((data['High'] + data['Low'])/2) - (3 * data['ATR'])
        
        # चालू कॅन्डलचे आकडे
        live_price = data['Close'].iloc[-1]
        live_rsi = data['RSI'].iloc[-1]
        live_ema = data['EMA_50'].iloc[-1]
        
        # सिग्नल मोजणी
        st.subheader("📊 लाईव्ह मार्केट ताळेबंद (5-Min Candle)")
        c1, c2, c3 = st.columns(3)
        c1.metric("निफ्टी चालू किंमत", f"₹{live_price:.2f}")
        c2.metric("RSI (ताकद)", f"{live_rsi:.2f}")
        c3.metric("५० EMA", f"₹{live_ema:.2f}")
        
        # अल्गोचे पक्के नियम (Trading Logic)
        st.markdown("---")
        st.subheader("🚨 आजच्या एकूण पेपर ट्रेडिंग पोझिशन्स")
        
        # सिग्नल जनरेट करणे
        signal = "WAIT (वाट पाहा)"
        color = "blue"
        
        if live_price > live_ema and live_rsi > 52:
            signal = "🚀 BUY CALL (तेजी)"
            color = "green"
        elif live_price < live_ema and live_rsi < 48:
            signal = "💥 BUY PUT (मंदी)"
            color = "red"
            
        if color == "green":
            st.success(f"**चालू संकेत:** {signal} | मार्केटमध्ये चांगला अपट्रेंड दिसत आहे.")
        elif color == "red":
            st.error(f"**चालू संकेत:** {signal} | मार्केटमध्ये घसरणीचा कल दिसत आहे.")
        else:
            st.warning(f"**चालू संकेत:** {signal} | इंडिकेटर्स मॅच होण्याची वाट पाहत आहे.")
            
        # टेलिग्राम अलर्ट बटण (लाईव्ह चाचणी करण्यासाठी)
        st.markdown("---")
        st.subheader("📲 टेलिग्राम अलर्ट टेस्ट")
        if st.button("माझ्या टेलिग्राम चॅनेलवर टेस्ट मेसेज पाठवा"):
            test_msg = f"🚨 *MUKESH ALGO ALERT*\n\n📈 Nifty 50: {signal}\n💰 चालू किंमत: ₹{live_price:.2f}\n📊 RSI: {live_rsi:.2f}\n⏰ वेळ: ५ मिनिट कॅन्डल क्लोज"
            send_telegram_alert(test_msg)
            st.info("टेलीग्रामवर मेसेज पाठवला आहे, तुमचा चॅनेल तपासा!")
            
        st.subheader("📋 मागील ५ मिनिटांच्या कॅन्डल्सचा इतिहास")
        st.dataframe(data[['Close', 'EMA_50', 'RSI']].tail(10))
        

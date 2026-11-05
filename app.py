import streamlit as st
import requests
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="माझे ऑल-इन-वन ॲप", layout="wide")

# --- अचूक टेलिग्राम कॉन्फिगरेशन ---
TELEGRAM_TOKEN = "9037885219:AAEo4b4NQxu5eM7Ijwmnt1CuS7tPHFjCvRI"
TELEGRAM_CHAT_ID = "5144404922"

def send_telegram_message(message):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload)
        except Exception as e:
            pass

st.sidebar.title("🎛️ ॲपメニュー")

# टेस्ट बटण - हे दाबल्यावर थेट मोबाईलवर मेसेज येईल
if st.sidebar.button("🧪 टेलिग्राम टेस्ट करा"):
    send_telegram_message("👋 नमस्कार मुकेश! तुमच्या ॲपमधून ५ EMA स्कॅल्पिंग अलर्ट आता यशस्वीरित्या सुरू झाला आहे! 🚀")
    st.sidebar.success("टेस्ट मेसेज पाठवला आहे! टेलिग्राम चेक करा.")

choice = st.sidebar.selectbox("तुम्हाला काय वापरायचे आहे?", ["१. सोन्याचे पक्के बिल", "२. निफ्टी प्रगत ट्रेडिंग ट्रॅकर"])

def get_live_market_data():
    try:
        usd_url = "https://er-api.com"
        usd_data = requests.get(usd_url).json()
        live_usd = usd_data["rates"]["INR"]
        gold_in_usd = 3904.50
        try:
            if "rates" in usd_data and "XAU" in usd_data["rates"]:
                gold_spot_usd = 1 / usd_data["rates"]["XAU"]
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

# ----------------- भाग २: ५ EMA प्रो स्कॅल्पिंग ट्रॅकर -----------------
elif choice == "२. निफ्टी प्रगत ट्रेडिंग ट्रॅकर":
    st.title("⚡ निफ्टी ५० प्रगत ५ EMA स्कॅल्पिंग ट्रॅकर")
    st.write("हा ट्रॅकर ५ मिनिटांच्या चार्टवर वेगाने स्कॅल्पिंग सिग्नल्स शोधतो आणि थेट टेलिग्रामवर पाठवतो.")
    
    if st.button("🔄 लाईव्ह डेटा रीफ्रेश करा"):
        st.cache_data.clear()
        st.rerun()

    @st.cache_data(ttl=10)
    def get_scalping_data():
        df = yf.download(tickers="^NSEI", period="2d", interval="5m")
        if df.empty:
            return pd.DataFrame()
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col for col in df.columns]
            
        df = df.dropna(subset=['Close'])
        df['EMA_5'] = df['Close'].ewm(span=5, adjust=False).mean()
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI_14'] = 100 - (100 / (1 + rs))
        return df

    try:
        data = get_scalping_data()
        
        if not data.empty and len(data) >= 3:
            last_candle = data.iloc[-1]
            prev_candle = data.iloc[-2]
            
            live_price = float(last_candle['Close'])
            rsi_now = float(last_candle['RSI_14'])
            ema5_now = float(last_candle['EMA_5'])
            
            col1, col2, col3 = st.columns(3)
            col1.metric(label="निफ्टी लाईव्ह किंमत", value=f"₹{live_price:.2f}")
            col2.metric(label="RSI (14)", value=f"{rsi_now:.2f}")
            col3.metric(label="5 EMA लाईन", value=f"₹{ema5_now:.2f}")
            
            st.markdown("---")
            st.subheader("🎯 स्कॅल्पिंग ॲक्शन संकेत")
            
            candle_time = str(data.index[-1])
            
            # PUT स्कॅल्पिंग संकेत
            if (float(prev_candle['Low']) > float(prev_candle['EMA_5'])) and (live_price < float(prev_candle['Low'])) and (rsi_now <= 45):
                target_p = round(live_price - 15, 2)
                sl_p = round(live_price + 10, 2)
                st.error("🔴 **BUY PUT (PE) स्कॅल्पिंग संकेत!**")
                
                tg_msg = f"🔴 *NIFTY 50 स्कॅल्पिंग PUT (PE) संकेत!*\n\n• किंमत: ₹{live_price:.2f}\n• Target: ₹{target_p}\n• Stop Loss: ₹{sl_p}\n• वेळ: {candle_time}"
                send_telegram_message(tg_msg)
                st.info(f"📝 **टेलिग्राम मेसेज पाठवला गेला आहे!**")
            
            # CALL स्कॅल्पिंग संकेत
            elif (float(prev_candle['High']) < float(prev_candle['EMA_5'])) and (live_price > float(prev_candle['High'])) and (rsi_now >= 55):
                target_p = round(live_price + 15, 2)
                sl_p = round(live_price - 10, 2)
                st.success("🟢 **BUY CALL (CE) स्कॅल्पिंग संकेत!**")
                
                tg_msg = f"🟢 *NIFTY 50 स्कॅल्पिंग CALL (CE) संकेत!*\n\n• किंमत: ₹{live_price:.2f}\n• Target: ₹{target_p}\n• Stop Loss: ₹{sl_p}\n• वेळ: {candle_time}"
                send_telegram_message(tg_msg)
                st.info(f"📝 **टेलिग्राम मेसेज पाठवला गेला आहे!**")
            
            else:
                st.warning("⚪ **सध्या कोणतीही स्कॅल्पिंग संधी नाही (WAIT)**")
                st.write("५ EMA लाईनपासून लांब असणारी योग्य 'अलर्ट कॅंडल' शोधत आहे.")
                
            st.subheader("📋 लाईव्ह ५ मिनिट डेटा टेबल")
            st.dataframe(data[['Open', 'High', 'Low', 'Close', 'EMA_5', 'RSI_14']].tail(5))
    except Exception as e:
        st.error(f"अडचण आली: {e}")

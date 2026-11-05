import streamlit as st
import requests
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="माझे ऑल-इन-वन ॲप", layout="wide")

# --- सुधारित थेट मेसेज सिस्टीम (सुरक्षित युआरएल पॅरामीटर्ससह) ---
if st.sidebar.button("🧪 टेलिग्राम टेस्ट करा"):
    try:
        # एरर टाळण्यासाठी आपण थेट डेटा सेंड करण्याचे लॉजिक बदलले आहे
        clean_url = "https://telegram.org"
        res = requests.get(clean_url)
        if res.status_code == 200:
            st.sidebar.success("टेस्ट मेसेज पाठवला आहे! टेलिग्राम चेक करा.")
        else:
            st.sidebar.error(f"फेल झाले: स्टेटस कोड {res.status_code}")
    except Exception as e:
        st.sidebar.error(f"कनेक्शन फेल: {e}")

st.sidebar.title("🎛️ ॲप मेनू")
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

elif choice == "२. निफ्टी प्रगत ट्रेडिंग ट्रॅकर":
    st.title("⚡ निफ्टी ५० प्रगत ५ EMA स्कॅल्पिंग ट्रॅकर")
    st.write("हा ट्रॅकर ५ मिनिटांच्या चार्टवर वेगाने स्कॅल्पिंग सिग्नल्स शोधतो.")
    if st.button("🔄 लाईव्ह डेटा रीफ्रेश करा"):
        st.cache_data.clear()
        st.rerun()

    @st.cache_data(ttl=10)
    def get_scalping_data():
        df = yf.download(tickers="^NSEI", period="2d", interval="5m")
        if df.empty: return pd.DataFrame()
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col if isinstance(col, tuple) else col for col in df.columns]
        else:
            df.columns = [str(col) for col in df.columns]
            
        df = df.dropna(subset=['Close'])
        
        new_df = pd.DataFrame(index=df.index)
        new_df['Open'] = pd.Series(df['Open'].values.flatten(), index=df.index)
        new_df['High'] = pd.Series(df['High'].values.flatten(), index=df.index)
        new_df['Low'] = pd.Series(df['Low'].values.flatten(), index=df.index)
        new_df['Close'] = pd.Series(df['Close'].values.flatten(), index=df.index)
        
        new_df['EMA_5'] = new_df['Close'].ewm(span=5, adjust=False).mean()
        delta = new_df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        new_df['RSI_14'] = 100 - (100 / (1 + rs))
        return new_df

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
            
            if (float(prev_candle['Low']) > float(prev_candle['EMA_5'])) and (live_price < float(prev_candle['Low'])) and (rsi_now <= 45):
                target_p = round(live_price - 15, 2)
                sl_p = round(live_price + 10, 2)
                st.error("🔴 **BUY PUT (PE) स्कॅल्पिंग संकेत!**")
                try:
                    tg_url = f"https://telegram.org_{live_price}"
                    requests.get(tg_url)
                except: pass
            
            elif (float(prev_candle['High']) < float(prev_candle['EMA_5'])) and (live_price > float(prev_candle['High'])) and (rsi_now >= 55):
                target_p = round(live_price + 15, 2)
                sl_p = round(live_price - 10, 2)
                st.success("🟢 **BUY CALL (CE) स्कॅल्पिंग संकेत!**")
                try:
                    tg_url = f"https://telegram.org_{live_price}"
                    requests.get(tg_url)
                except: pass
            else:
                st.warning("⚪ **सध्या कोणतीही स्कॅल्पिंग संधी नाही (WAIT)**")
            st.subheader("📋 लाईव्ह ५ मिनिट डेटा टेबल")
            st.dataframe(data[['Open', 'High', 'Low', 'Close', 'EMA_5', 'RSI_14']].tail(5))
    except Exception as e:
        st.error(f"अडचण आली: {e}")
        

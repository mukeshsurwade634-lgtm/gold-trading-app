import streamlit as st
import requests
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="माझे ऑल-इन-वन ॲप", layout="wide")

st.sidebar.title("🎛️ ॲप मेनू")
choice = st.sidebar.selectbox("तुम्हाला काय वापरायचे आहे?", ["१. सोन्याचे पक्के बिल", "२. निफ्टी प्रगत ट्रेडिंग ट्रॅकर"])

def get_live_market_data():
    try:
        # ExchangeRate-API चा वापर करून लाईव्ह USD ते INR दर मिळवणे
        usd_url = "https://er-api.com"
        usd_data = requests.get(usd_url).json()
        live_usd = usd_data["rates"]["INR"]
        
        # गोल्ड स्पॉट प्राईससाठी डिफॉल्ट किंवा API डेटा
        gold_in_usd = 3904.50
        try:
            # गोल्ड प्राईससाठी एक्सचेंज रेट किंवा योग्य API एंडपॉईंट वापरणे
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

# ----------------- भाग २: प्रगत ट्रेडिंग ट्रॅकर (नवीन बदल केलेला भाग) -----------------
elif choice == "२. निफ्टी प्रगत ट्रेडिंग ट्रॅकर":
    st.title("📈 निफ्टी ५० प्रगत इंट्राडे ट्रॅकर (EMA क्रॉसओवर आणि पेपर ट्रेडिंग)")
    st.write("हा ट्रॅकर ५/१५ मिनिटांच्या कॅंडलचा अभ्यास करून अचूक खरेदी (CALL) आणि विक्री (PUT) चे संकेत देतो.")
    
    # मोबाईल युझर्ससाठी साईडबारमध्ये पॅरामीटर्स बदलण्याची सोय (लॉजिक टेस्ट करण्यासाठी)
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ पेपर ट्रेडिंग सेटिंग्ज")
    timeframe = st.sidebar.selectbox("कॅंडल टाईमफ्रेम", ["5m", "15m", "1h", "1d"], index=0)
    ema_fast_len = st.sidebar.number_input("लहान EMA (Fast)", min_value=1, max_value=50, value=9)
    ema_slow_len = st.sidebar.number_input("मोठा EMA (Slow)", min_value=5, max_value=100, value=26)
    rsi_buy_level = st.sidebar.slider("CALL साठी किमान RSI", 50, 70, 55)
    rsi_sell_level = st.sidebar.slider("PUT साठी कमाल RSI", 30, 50, 45)

    @st.cache_data(ttl=60)
    def get_intraday_data(tf, fast, slow):
        # period="5d" मुळे शनिवार-रविवार किंवा मार्केट बंद असतानाही मागील ५ दिवसांचा डेटा लोड होईल
        df = yf.download(tickers="^NSEI", period="5d", interval=tf)
        
        # मल्टि-इंडेक्स कॉलम असल्यास ते साधे करणे
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
            
        # EMA ९ आणि २६ ची गणना
        df['EMA_Fast'] = df['Close'].ewm(span=fast, adjust=False).mean()
        df['EMA_Slow'] = df['Close'].ewm(span=slow, adjust=False).mean()
        
        # RSI १४ ची गणना
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI_14'] = 100 - (100 / (1 + rs))
        return df

    try:
        data = get_intraday_data(timeframe, ema_fast_len, ema_slow_len)
        
        if not data.empty:
            # शेवटच्या दोन पूर्ण झालेल्या कॅंडल्सचा डेटा (क्रॉसओवर ओळखण्यासाठी)
            last_candle = data.iloc[-1]
            prev_candle = data.iloc[-2]
            
            live_price = float(last_candle['Close'])
            rsi = float(last_candle['RSI_14'])
            ema_fast_now = float(last_candle['EMA_Fast'])
            ema_slow_now = float(last_candle['EMA_Slow'])
            
            ema_fast_prev = float(prev_candle['EMA_Fast'])
            ema_slow_prev = float(prev_candle['EMA_Slow'])
            
            # स्क्रीनवर इंडिकेटर्स दाखवणे
            col1, col2, col3 = st.columns(3)
            col1.metric(label="निफ्टी शेवटची किंमत", value=f"₹{live_price:.2f}")
            col2.metric(label="RSI (14)", value=f"{rsi:.2f}")
            col3.metric(label=f"EMA {ema_fast_len} vs {ema_slow_len}", value=f"₹{ema_fast_now:.2f}", delta=f"{(ema_fast_now-ema_slow_now):.2f}")
            
            st.markdown("---")
            st.subheader("🎯 पेपर ट्रेडिंग ॲक्शन संकेत (Action Signal)")
            
            # अचूक क्रॉसओवर लॉजिक आणि CALL / PUT निर्णय
            signal = "WAIT"
            
            # BUY CALL अट: Fast EMA ने Slow EMA ला खालून वर क्रॉस केले आणि RSI ५५+ आहे
            if (ema_fast_prev <= ema_slow_prev) and (ema_fast_now > ema_slow_now) and (rsi >= rsi_buy_level):
                signal = "BUY CALL"
                target_price = live_price + 40
                sl_price = live_price - 20
                st.success(f"🟢 **मजबूत तेजी संकेत (BUY CALL - CE)**")
                st.info(f"📝 **पेपर ट्रेड नोंद घ्या:** \n\n• **खरेदी झोन:** ₹{live_price:.2f} च्या वर \n\n• **🎯 Target (+40 pts):** ₹{target_price:.2f} \n\n• **🛑 Stop Loss (-20 pts):** ₹{sl_price:.2f}")
            
            # BUY PUT अट: Fast EMA ने Slow EMA ला वरून खाली क्रॉस केले आणि RSI ४५- आहे
            elif (ema_fast_prev >= ema_slow_prev) and (ema_fast_now < ema_slow_now) and (rsi <= rsi_sell_level):
                signal = "BUY PUT"
                target_price = live_price - 40
                sl_price = live_price + 20
                st.error(f"🔴 **मजबूत मंदी संकेत (BUY PUT - PE)**")
                st.info(f"📝 **...पेपर ट्रेड नोंद घ्या:** \n\n• **खरेदी झोन:** ₹{live_price:.2f} च्या खाली \n\n• **🎯 Target (-40 pts):** ₹{target_price:.2f} \n\n• **🛑 Stop Loss (+20 pts):** ₹{sl_price:.2f}")
            
            else:
                st.warning("⚪ **सध्या कोणताही स्पष्ट क्रॉसओवर सिग्नल नाही (NO SIGNAL / WAIT)**")
                st.write("बाजार सध्या तुमच्या पॅरामीटर्सनुसार कन्सॉलिडेशन किंवा शांत मोडमध्ये आहे. नवीन कॅंडल पूर्ण होण्याची वाट पहा.")
                
            st.subheader("📋 हिस्टोरिकल इंट्राडे डेटा टेबल (शेवटच्या ५ कॅंडल्स)")
            st.dataframe(data[['Close', 'EMA_Fast', 'EMA_Slow', 'RSI_14']].tail(5))
    except Exception as e:
        st.error(f"डेटा लोड करताना तांत्रिक अडचण आली: {e}")

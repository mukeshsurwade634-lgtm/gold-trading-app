import streamlit as st
import plotly.graph_objects as go
import requests
import yfinance as yf

st.set_page_config(page_title="मुकेश अल्गो ट्रेडिंग बाजार", layout="wide")

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

def get_live_nifty_direct():
    try:
        # अधिकृत यफायनान्स लायब्ररी द्वारे अचूक निफ्टी ५० ट्रॅकर
        nifty = yf.Ticker("^NSEI")
        todays_data = nifty.history(period='1d')
        if not todays_data.empty:
            live_price = todays_data['Close'].iloc[-1]
            return live_price
        else:
            return 24864.05
    except:
        return 24864.05

st.sidebar.title("🎛️ मुकेश अल्गो CONTROL")
choice = st.sidebar.selectbox("पर्याय निवडा:", ["१. सोन्याचे पक्के bill", "२. निफ्टी लाईव्ह निकष स्क्रीन"])

if choice == "१. सोन्याचे पक्के bill":
    st.title("💰 मुकेश भुसावळ लाईव्ह सराफा कॅल्क्युलेटर")
    st.write("हे ॲप आंतरराष्ट्रीय SPOT किमतीवर भारतीय कर आणि स्थानिक प्रीमियम लावून अचूक दर काढते.")
    
    gold_spot_usd, usd_to_inr = get_bhusawal_live_gold()
    troy_ounce = 31.10347
    base_price = (gold_spot_usd * usd_to_inr) / troy_ounce
    
    final_24k = base_price * 1.15 * 1.05 * 1.624  
    final_22k = final_24k * 0.9166                 
    
    st.info(f"📊 **भुसावळ चालू बाजारभाव:** २४K: ₹{final_24k:.2f}/ग्रॅम | २२K: ₹{final_22k:.2f}/ग्रॅम")
    
    weight = st.number_input("दागिन्याचे वजन टाका (ग्रॅम):", min_value=0.01, value=10.0, step=0.1)
    making = st.number_input("घडणावळ (%) टाका:", min_value=0.0, value=12.0, step=0.5)
    
    if st.button("पक्के बिल जनरेट करा"):
        pure_cost = final_22k * weight
        making_cost = pure_cost * (making / 100)
        sub_total = pure_cost + making_cost
        gst = sub_total * 0.03
        total = sub_total + gst
        st.success(f"### 🧾 सराफा पक्के बिल (२२K)\n• मूळ किंमत: ₹{pure_cost:.2f}\n• घडणावळ: ₹{making_cost:.2f}\n• एकूण रक्कम GST सह: **₹{total:.2f}**")

elif choice == "२. निफ्टी लाईव्ह निकष स्क्रीन":
    st.title("📈 निफ्टी ५० इंट्राडे अल्गो (5m चार्ट आणि बाण)")
    
    # १. ५ मिनिटांचा (5m) लाईव्ह डेटा ओढणे
    nifty = yf.Ticker("^NSEI")
    df = nifty.history(period="2d", interval="5m")
    
    if not df.empty:
        # इंडिकेटर्स मोजणे
        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # आजचा शेवटचा भाग (शेवटच्या ६० कॅंडल्स) चार्टवर दाखवण्यासाठी वेगळा करणे
        df_chart = df.tail(60).copy()
        
        # BUY आणि SELL चे बाण (Arrows) शोधण्याचे लॉजिक
        buy_signals = []
        sell_signals = []
        
        for i in range(1, len(df_chart)):
            # जेव्हा ९ EMA ने २१ EMA ला खालून वर क्रॉस केले (BUY बाण)
            if df_chart['EMA_9'].iloc[i] > df_chart['EMA_21'].iloc[i] and df_chart['EMA_9'].iloc[i-1] <= df_chart['EMA_21'].iloc[i-1]:
                buy_signals.append(df_chart['Low'].iloc[i] - 10) # कॅंडलच्या थोडे खाली बाण दिसेल
                sell_signals.append(None)
            # जेव्हा ९ EMA ने २१ EMA ला वरून खाली क्रॉस केले (SELL बाण)
            elif df_chart['EMA_9'].iloc[i] < df_chart['EMA_21'].iloc[i] and df_chart['EMA_9'].iloc[i-1] >= df_chart['EMA_21'].iloc[i-1]:
                sell_signals.append(df_chart['High'].iloc[i] + 10) # कॅंडलच्या थोडे वर बाण दिसेल
                buy_signals.append(None)
            else:
                buy_signals.append(None)
                sell_signals.append(None)
                
        # पहिल्या कॅंडलसाठी रिकामी जागा
        buy_signals.insert(0, None)
        sell_signals.insert(0, None)

        nifty_live = df_chart['Close'].iloc[-1]
        ema_9 = df_chart['EMA_9'].iloc[-1]
        ema_21 = df_chart['EMA_21'].iloc[-1]
        live_rsi = df_chart['RSI'].iloc[-1]

        # चालू भाव आणि इंडिकेटर्स दाखवणे
        st.metric(label="निफ्टी ५० चालू भाव (5m)", value=f"₹{nifty_live:.2f}")
        
        # २. कॅंडलस्टिक चार्ट आणि बाण तयार करणे
        fig = go.Figure()
        
        # कॅंडल्स (Candlesticks)
        fig.add_trace(go.Candlestick(
            x=df_chart.index, open=df_chart['Open'], high=df_chart['High'],
            low=df_chart['Low'], close=df_chart['Close'], name='Nifty 5m'
        ))
        
        # ९ आणि २१ EMA रेषा
        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['EMA_9'], line=dict(color='cyan', width=1.5), name='9 EMA'))
        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['EMA_21'], line=dict(color='orange', width=1.5), name='21 EMA'))
        
        # हिरवा BUY बाण (वरच्या दिशेने तोंड असलेला त्रिकोण)
        fig.add_trace(go.Scatter(
            x=df_chart.index, y=buy_signals, mode='markers',
            marker=dict(symbol='triangle-up', size=14, color='#00ff00'), name='BUY संकेत'
        ))
        
        # लाल SELL बाण (खालच्या दिशेने तोंड असलेला त्रिकोण)
        fig.add_trace(go.Scatter(
            x=df_chart.index, y=sell_signals, mode='markers',
            marker=dict(symbol='triangle-down', size=14, color='#ff0000'), name='SELL संकेत'
        ))
        
        fig.update_layout(
            template="plotly_dark", xaxis_rangeslider_visible=False,
            height=450, margin=dict(l=10, r=10, t=30, b=10)
        )
        
        # स्क्रीनवर चार्ट दाखवणे
        st.plotly_chart(fig, use_container_width=True)
        
        # ३. अल्गो फायनल निर्णय बॉक्स
        st.subheader("💡 अल्गो फायनल निर्णय (इंट्राडे)")
        ema_diff = abs(ema_9 - ema_21)
        
        if ema_diff < 15:
            st.warning("⏸️ **WAIT / NO TRADE (मार्केट साईडवेज आहे):** एकाच रेंजमध्ये मार्केट फिरत आहे, नवीन ट्रेड टाळा.")
        elif ema_9 > ema_21 and live_rsi > 55:
            st.success("🚀 **BUY CALL (तेजी):** चार्टवर हिरवा बाण आला आहे आणि मार्केट मजबूत आहे!")
        elif ema_9 < ema_21 and live_rsi < 45:
            st.error("💥 **BUY PUT (मंदी):** चार्टवर लाल बाण आला आहे आणि विक्रीचा दबाव आहे!")
        else:
            st.info("⚖️ **प्रतीक्षा करा:** इंडिकेटर्स पूर्णपणे जुळण्याची वाट पहा.")
    else:
        st.error("सध्या मार्केट डेटा उपलब्ध नाही, थोड्या वेळाने प्रयत्न करा.")
        

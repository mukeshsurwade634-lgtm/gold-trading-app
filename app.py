import streamlit as st
import requests
import yfinance as yf
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="मुकेश अल्गो ट्रेडिंग बाजार", layout="wide")

# दर ६० सेकंदांनी (1 मिनिटाने) ॲप आपोआप रिफ्रेश होईल
st_autorefresh(interval=60000, key="algo_auto_refresh")

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

st.sidebar.title("🎛️ मुकेश अल्गो CONTROL")
choice = st.sidebar.selectbox("पर्याय निवडा:", [
    "१. सोन्याचे पक्के bill", 
    "२. निफ्टी लाईव्ह निकष स्क्रीन", 
    "३. बिटकॉइन (BTC/USD) लाईव्ह चार्ट"
])

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
    
    nifty = yf.Ticker("^NSEI")
    df = nifty.history(period="1d", interval="5m")
    
    if not df.empty:
        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        df_chart = df.tail(60).copy()
        buy_signals = []
        sell_signals = []
        
        for i in range(1, len(df_chart)):
            if df_chart['EMA_9'].iloc[i] > df_chart['EMA_21'].iloc[i] and df_chart['EMA_9'].iloc[i-1] <= df_chart['EMA_21'].iloc[i-1]:
                buy_signals.append(df_chart['Low'].iloc[i] - 10)
                sell_signals.append(None)
            elif df_chart['EMA_9'].iloc[i] < df_chart['EMA_21'].iloc[i] and df_chart['EMA_9'].iloc[i-1] >= df_chart['EMA_21'].iloc[i-1]:
                sell_signals.append(df_chart['High'].iloc[i] + 10)
                buy_signals.append(None)
            else:
                buy_signals.append(None)
                sell_signals.append(None)
                
        buy_signals.insert(0, None)
        sell_signals.insert(0, None)

        nifty_live = df_chart['Close'].iloc[-1]
        ema_9 = df_chart['EMA_9'].iloc[-1]
        ema_21 = df_chart['EMA_21'].iloc[-1]
        live_rsi = df_chart['RSI'].iloc[-1]

        st.metric(label="निफ्टी ५० चालू भाव (5m)", value=f"₹{nifty_live:.2f}")
        
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df_chart.index.strftime('%H:%M'), open=df_chart['Open'], high=df_chart['High'],
            low=df_chart['Low'], close=df_chart['Close'], name='Nifty 5m'
        ))
        fig.add_trace(go.Scatter(x=df_chart.index.strftime('%H:%M'), y=df_chart['EMA_9'], line=dict(color='cyan', width=1.5), name='9 EMA'))
        fig.add_trace(go.Scatter(x=df_chart.index.strftime('%H:%M'), y=df_chart['EMA_21'], line=dict(color='orange', width=1.5), name='21 EMA'))
        fig.add_trace(go.Scatter(
            x=df_chart.index.strftime('%H:%M'), y=buy_signals, mode='markers',
            marker=dict(symbol='triangle-up', size=14, color='#00ff00'), name='BUY संकेत'
        ))
        fig.add_trace(go.Scatter(
            x=df_chart.index.strftime('%H:%M'), y=sell_signals, mode='markers',
            marker=dict(symbol='triangle-down', size=14, color='#ff0000'), name='SELL संकेत'
        ))
        
        fig.update_layout(
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            xaxis_type="category",
            height=450,
            margin=dict(l=10, r=10, t=30, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
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

elif choice == "३. बिटकॉइन (BTC/USD) लाईव्ह चार्ट":
    st.title("🪙 बिटकॉइन (BTC/USD) फिबोनाची अल्गो सेटअप")
    
    btc = yf.Ticker("BTC-USD")
    df_btc = btc.history(period="1d", interval="5m")
    
    if not df_btc.empty:
        df_chart = df_btc.tail(60).copy()
        btc_live = df_chart['Close'].iloc[-1]
        
        swing_high = df_chart['High'].max()
        swing_low = df_chart['Low'].min()
        diff = swing_high - swing_low
        
        fib_0 = swing_high
        fib_382 = swing_high - (0.382 * diff)
        fib_500 = swing_high - (0.500 * diff)
        fib_618 = swing_high - (0.618 * diff)
        fib_100 = swing_low

        st.metric(label="बिटकॉइन चालू भाव (BTC/USD)", value=f"${btc_live:,.2f}")
        
        fig_fib = go.Figure()
        fig_fib.add_trace(go.Candlestick(
            x=df_chart.index.strftime('%H:%M'), open=df_chart['Open'], high=df_chart['High'],
            low=df_chart['Low'], close=df_chart['Close'], name='BTC-USD'
        ))
        
        fig_fib.add_hline(y=fib_0, line_dash="dash", line_color="red", annotation_text=f"0.0% High (${fib_0:,.0f})")
        fig_fib.add_hline(y=fib_382, line_dash="dot", line_color="cyan", annotation_text=f"38.2% (${fib_382:,.0f})")
        fig_fib.add_hline(y=fib_500, line_dash="dash", line_color="yellow", annotation_text=f"50.0% (${fib_500:,.0f})")
        fig_fib.add_hline(y=fib_618, line_dash="solid", line_color="#00ff00", annotation_text=f"61.8% Golden (${fib_618:,.0f})")
        fig_fib.add_hline(y=fib_100, line_dash="dash", line_color="white", annotation_text=f"100% Low (${fib_100:,.0f})")
        
        fig_fib.update_layout(
            template="plotly_dark", 
            xaxis_rangeslider_visible=False, 
            xaxis_type="category", 
            height=480, 
            margin=dict(l=10, r=10, t=30, b=10)
        )
        
        st.plotly_chart(fig_fib, use_container_width=True)
        
        st.subheader("💡 फिबोनाची स्ट्रॅटेजी निरीक्षण")
        
        if fib_618 <= btc_live <= fib_500:
            st.success(f"🎯 **गोल्डन झोन अलर्ट (BUY संधी):** \n\nबिटकॉइनची किंमत सध्या **५०% (${fib_500:,.0f}) ते ६१.८% (${fib_618:,.0f})** या मजबूत सपोर्ट झोनमध्ये आहे! इथून वर रिव्हर्सल होण्याची शक्यता तपासा.")
        elif btc_live > fib_382:
            st.info("📈 **मजबूत तेजी (Strong Uptrend):** किंमत ३८.२% च्या वर आहे, मार्केट तेजीत आहे.")
        elif btc_live < fib_618:
            st.error("⚠️ **सपोर्ट तुटला (Breakdown):** किंमत ६१.८% च्या गोल्डन रेषेच्या खाली गेली आहे, खरेदी करणे टाळा.")
        else:
            st.warning("⚖️ **प्रतीक्षा करा:** किंमत फिबोनाचीच्या मुख्य रेषेजवळ येण्याची वाट पहा.")
    else:
        st.error("सध्या बिटकॉइन डेटा उपलब्ध नाही.")
        

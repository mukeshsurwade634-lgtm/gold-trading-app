import streamlit as st
import requests
import yfinance as yf
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="मुकेश अल्गो ट्रेडिंग बाजार", layout="wide")

# लाईव्ह मार्केटमध्ये दर ३० सेकंदांनी ॲप आपोआप रिफ्रेश होईल
st_autorefresh(interval=30000, key="algo_fast_refresh")

def get_bhusawal_live_gold():
    try:
        # १. आंतरराष्ट्रीय सोन्याचा थेट लाईव्ह भाव (Gold Futures - USD per Troy Ounce)
        gold_ticker = yf.Ticker("GC=F")
        gold_data = gold_ticker.history(period="1d")
        gold_spot_usd = gold_data['Close'].iloc[-1] if not gold_data.empty else 2745.50
        
        # २. अमेरिकन डॉलरचा थेट भारतीय रुपयातील भाव (USD to INR)
        inr_ticker = yf.Ticker("INR=X")
        inr_data = inr_ticker.history(period="1d")
        inr_rate = inr_data['Close'].iloc[-1] if not inr_data.empty else 84.40
        
        return float(gold_spot_usd), float(inr_rate)
    except Exception:
        return 2745.50, 84.40
     

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
    st.title("📈 निफ्टी ५० तंतोतंत अल्गो (पेपर ट्रेडिंग बेस)")
    
    nifty = yf.Ticker("^NSEI")
    df = nifty.history(period="1d", interval="5m")
    
    if not df.empty:
        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        df_chart = df.tail(60).copy()
        buy_signals, sell_signals = [], []
        
                # ==========================================
        # खिचडी थांबवणारे अचूक क्रॉसओव्हर (Clean Arrows) लॉजिक
        # ==========================================
        buy_signals, sell_signals = [], []
        last_signal = None  # शेवटचा सिग्नल कोणता होता हे लक्षात ठेवण्यासाठी
        
        for i in range(1, len(df_chart)):
            ema9_curr = df_chart['EMA_9'].iloc[i]
            ema21_curr = df_chart['EMA_21'].iloc[i]
            ema9_prev = df_chart['EMA_9'].iloc[i-1]
            ema21_prev = df_chart['EMA_21'].iloc[i-1]
            close_curr = df_chart['Close'].iloc[i]
            
            # १. अचूक BUY बाण: लाल रेषेने निळ्या रेषेला वर क्रॉस केले + कॅंडल दोन्हीच्या वर बंद झाली
            if (ema9_curr > ema21_curr) and (ema9_prev <= ema21_prev) and (close_curr > ema9_curr) and (last_signal != "BUY"):
                buy_signals.append(df_chart['Low'].iloc[i] - 15)
                sell_signals.append(None)
                last_signal = "BUY"
                
            # २. अचूक SELL बाण: लाल रेषेने निळ्या रेषेला खाली क्रॉस केले + कॅंडल दोन्हीच्या खाली बंद झाली
            elif (ema9_curr < ema21_curr) and (ema9_prev >= ema21_prev) and (close_curr < ema9_curr) and (last_signal != "SELL"):
                sell_signals.append(df_chart['High'].iloc[i] + 15)
                buy_signals.append(None)
                last_signal = "SELL"
                
            else:
                buy_signals.append(None)
                sell_signals.append(None)
                
        buy_signals.insert(0, None)
        sell_signals.insert(0, None)
        

        nifty_live = df_chart['Close'].iloc[-1]
        current_ema9 = df_chart['EMA_9'].iloc[-1]
        current_ema21 = df_chart['EMA_21'].iloc[-1]
        last_low = df_chart['Low'].iloc[-1]
        last_high = df_chart['High'].iloc[-1]

        st.metric(label="निफ्टी ५० चालू भाव (5m Live)", value=f"₹{nifty_live:.2f}")
        
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df_chart.index.strftime('%H:%M'), open=df_chart['Open'], high=df_chart['High'],
            low=df_chart['Low'], close=df_chart['Close'], name='Nifty 5m'
        ))
        fig.add_trace(go.Scatter(x=df_chart.index.strftime('%H:%M'), y=df_chart['EMA_9'], line=dict(color='red', width=1.5), name='9 EMA'))
        fig.add_trace(go.Scatter(x=df_chart.index.strftime('%H:%M'), y=df_chart['EMA_21'], line=dict(color='cyan', width=1.5), name='21 EMA'))
        fig.add_trace(go.Scatter(
            x=df_chart.index.strftime('%H:%M'), y=buy_signals, mode='markers',
            marker=dict(symbol='triangle-up', size=15, color='#00ff00'), name='BUY एंट्री'
        ))
        fig.add_trace(go.Scatter(
            x=df_chart.index.strftime('%H:%M'), y=sell_signals, mode='markers',
            marker=dict(symbol='triangle-down', size=15, color='#ff0000'), name='SELL एंट्री'
        ))
        
        fig.update_layout(
            template="plotly_dark", xaxis_rangeslider_visible=False,
            xaxis_type="category", height=450, margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # तंतोतंत पेपर ट्रेडिंग एंट्री आणि स्टॉपलॉस बॉक्स
        st.subheader("🎯 तंतोतंत पेपर ट्रेडिंग लेव्हल्स (Live Action)")
        
        if nifty_live > current_ema9 and nifty_live > current_ema21:
            sl_call = min(last_low, current_ema21) - 10
            target_call = nifty_live + (nifty_live - sl_call) * 1.5
            st.success(f"🟢 **LIVE BUY CALL (तेजी संकेत)**\n\n"
                       f"• **तंतोतंत एंट्री (Entry):** ₹{nifty_live:.2f}\n"
                       f"• **स्टॉपलॉस (Stop Loss):** ₹{sl_call:.2f}\n"
                       f"• **पहिले टार्गेट (Target):** ₹{target_call:.2f}")
                       
        elif nifty_live < current_ema9 and nifty_live < current_ema21:
            sl_put = max(last_high, current_ema21) + 10
            target_put = nifty_live - (sl_put - nifty_live) * 1.5
            st.error(f"🔴 **LIVE BUY PUT / SELL (मंदी संकेत)**\n\n"
                     f"• **तंतोतंत एंट्री (Entry):** ₹{nifty_live:.2f}\n"
                     f"• **स्टॉपलॉस (Stop Loss):** ₹{sl_put:.2f}\n"
                     f"• **पहिले टार्गेट (Target):** ₹{target_put:.2f}")
        else:
            st.warning("🟡 **प्रतीक्षा करा (No Trade Zone):** कॅंडल दोन्ही रेषांच्या मध्ये आहे, स्पष्ट ब्रेकआऊटची वाट पहा.")
    else:
        st.error("सध्या मार्केट डेटा उपलब्ध नाही.")

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
        
        fig_fib.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, xaxis_type="category", height=480, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_fib, use_container_width=True)
        
        if fib_618 <= btc_live <= fib_500:
            st.success(f"🎯 **गोल्डन झोन अलर्ट (BUY संधी):** किंमत ५०% (${fib_500:,.0f}) ते ६१.८% (${fib_618:,.0f}) झोनमध्ये आहे!")
        elif btc_live > fib_382:
            st.info("📈 **मजबूत तेजी:** किंमत ३८.२% च्या वर आहे.")
        elif btc_live < fib_618:
            st.error("⚠️ **सपोर्ट तुटला:** किंमत ६१.८% च्या खाली गेली आहे.")
        else:
            st.warning("⚖️ **प्रतीक्षा करा:** किंमत मुख्य रेषेजवळ येण्याची वाट पहा.")
            

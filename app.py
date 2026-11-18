import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="मुकेश अल्गो ट्रेडिंग टर्मिनल", layout="wide")

# लाईव्ह मार्केटमध्ये दर ३० सेकंदांनी ॲप आपोआप रिफ्रेश होईल
st_autorefresh(interval=30000, key="algo_trading_refresh")

st.sidebar.title("🎛️ मुकेश अल्गो CONTROL")
choice = st.sidebar.selectbox("ट्रेडिंग मार्केट निवडा:", [
    "१. निफ्टी ५० अल्गो (Golden Trio + Options)", 
    "२. बिटकॉइन (BTC/USD) फिबोनाची सेटअप"
])

if choice == "१. निफ्टी ५० अल्गो (Golden Trio + Options)":
    st.title("📈 निफ्टी ५० 'गोल्डन ट्रिओ' अल्गो टर्मिनल")
    
    nifty = yf.Ticker("^NSEI")
    df = nifty.history(period="2d", interval="5m")
    
    if not df.empty:
        # १. EMA मोजणे
        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
        
        # २. RSI (14) मोजणे
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        df_chart = df.tail(65).copy()
        buy_signals, sell_signals = [], []
        last_trade = None
        
        for i in range(1, len(df_chart)):
            c_open = df_chart['Open'].iloc[i]
            c_close = df_chart['Close'].iloc[i]
            p_open = df_chart['Open'].iloc[i-1]
            
            ema9 = df_chart['EMA_9'].iloc[i]
            ema21 = df_chart['EMA_21'].iloc[i]
            rsi_val = df_chart['RSI'].iloc[i]
            
            is_bullish_candle = (c_close > c_open) and (c_close > p_open)
            is_bearish_candle = (c_close < c_open) and (c_close < p_open)
            
            # तिन्ही नियम जुळल्यावरच BUY बाण
            if (ema9 > ema21) and (c_close > ema9) and is_bullish_candle and (rsi_val > 55) and (last_trade != "BUY"):
                buy_signals.append(df_chart['Low'].iloc[i] - 15)
                sell_signals.append(None)
                last_trade = "BUY"
                
            # तिन्ही नियम जुळल्यावरच SELL बाण
            elif (ema9 < ema21) and (c_close < ema9) and is_bearish_candle and (rsi_val < 45) and (last_trade != "SELL"):
                sell_signals.append(df_chart['High'].iloc[i] + 15)
                buy_signals.append(None)
                last_trade = "SELL"
            else:
                buy_signals.append(None)
                sell_signals.append(None)
                
        buy_signals.insert(0, None)
        sell_signals.insert(0, None)

        nifty_live = df_chart['Close'].iloc[-1]
        curr_ema9 = df_chart['EMA_9'].iloc[-1]
        curr_ema21 = df_chart['EMA_21'].iloc[-1]
        curr_rsi = df_chart['RSI'].iloc[-1]
        last_low = df_chart['Low'].iloc[-1]
        last_high = df_chart['High'].iloc[-1]

        # वरती महत्त्वाचे आकडे दाखवणे
        c1, c2, c3 = st.columns(3)
        c1.metric("निफ्टी चालू भाव (5m)", f"₹{nifty_live:.2f}")
        c2.metric("RSI (14) ताकद", f"{curr_rsi:.1f}")
        c3.metric("ट्रेंड (9 vs 21 EMA)", "तेजी (Bull)" if curr_ema9 > curr_ema21 else "मंदी (Bear)")
        
        # चार्ट तयार करणे
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=df_chart.index.strftime('%H:%M'), open=df_chart['Open'], high=df_chart['High'],
            low=df_chart['Low'], close=df_chart['Close'], name='Nifty 5m'
        ))
        fig.add_trace(go.Scatter(x=df_chart.index.strftime('%H:%M'), y=df_chart['EMA_9'], line=dict(color='red', width=1.5), name='9 EMA'))
        fig.add_trace(go.Scatter(x=df_chart.index.strftime('%H:%M'), y=df_chart['EMA_21'], line=dict(color='cyan', width=1.5), name='21 EMA'))
        fig.add_trace(go.Scatter(
            x=df_chart.index.strftime('%H:%M'), y=buy_signals, mode='markers',
            marker=dict(symbol='triangle-up', size=16, color='#00ff00'), name='पक्का BUY'
        ))
        fig.add_trace(go.Scatter(
            x=df_chart.index.strftime('%H:%M'), y=sell_signals, mode='markers',
            marker=dict(symbol='triangle-down', size=16, color='#ff0000'), name='पक्का SELL'
        ))
        
        fig.update_layout(
            template="plotly_dark", xaxis_rangeslider_visible=False,
            xaxis_type="category", height=450, margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # ATM आणि ITM स्ट्राईक प्राईस गणित
        atm_strike = round(nifty_live / 50) * 50
        
        st.subheader("🎯 ३-नियमांचा फायनल पेपर ट्रेड आणि ऑप्शन निवड")
        
        if (curr_ema9 > curr_ema21) and (nifty_live > curr_ema9) and (curr_rsi > 55):
            sl = min(last_low, curr_ema21) - 10
            tgt = nifty_live + (nifty_live - sl) * 1.5
            itm_call = atm_strike - 100
            
            st.success(f"🟢 **पक्का BUY CALL (तेजी सिग्नल)**\n\n"
                       f"• **इंडेक्स एंट्री:** ₹{nifty_live:.2f} | **स्टॉपलॉस (SL):** ₹{sl:.2f} | **टार्गेट:** ₹{tgt:.2f}\n\n"
                       f"👉 **कोणता ऑप्शन निवडावा?**\n"
                       f"• **ATM (बेस्ट):** `NIFTY {atm_strike} CE`\n"
                       f"• **ITM (सेफ):** `NIFTY {itm_call} CE`")
                       
        elif (curr_ema9 < curr_ema21) and (nifty_live < curr_ema9) and (curr_rsi < 45):
            sl = max(last_high, curr_ema21) + 10
            tgt = nifty_live - (sl - nifty_live) * 1.5
            itm_put = atm_strike + 100
            
            st.error(f"🔴 **पक्का BUY PUT (मंदी सिग्नल)**\n\n"
                     f"• **इंडेक्स एंट्री:** ₹{nifty_live:.2f} | **स्टॉपलॉस (SL):** ₹{sl:.2f} | **टार्गेट:** ₹{tgt:.2f}\n\n"
                     f"👉 **कोणता ऑप्शन निवडावा?**\n"
                     f"• **ATM (बेस्ट):** `NIFTY {atm_strike} PE`\n"
                     f"• **ITM (सेफ):** `NIFTY {itm_put} PE`")
        else:
            st.warning(f"🟡 **प्रतीक्षा करा (No Trade):** सध्या तिन्ही निकष (EMA + Candle + RSI {curr_rsi:.1f}) जुळलेले नाहीत. (सध्याचा ATM स्ट्राईक: {atm_strike})")
    else:
        st.error("सध्या मार्केट डेटा उपलब्ध नाही.")

elif choice == "२. बिटकॉइन (BTC/USD) फिबोनाची सेटअप":
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
            template="plotly_dark", xaxis_rangeslider_visible=False, 
            xaxis_type="category", height=480, margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig_fib, use_container_width=True)
        
        st.subheader("💡 फिबोनाची स्ट्रॅटेजी निरीक्षण")
        
        if fib_618 <= btc_live <= fib_500:
            st.success(f"🎯 **गोल्डन झोन अलर्ट (BUY संधी):** किंमत ५०% (${fib_500:,.0f}) ते ६१.८% (${fib_618:,.0f}) या मजबूत सपोर्ट झोनमध्ये आहे!")
        elif btc_live > fib_382:
            st.info("📈 **मजबूत तेजी:** किंमत ३८.२% च्या वर आहे, मार्केट तेजीत आहे.")
        elif btc_live < fib_618:
            st.error("⚠️ **सपोर्ट तुटला:** किंमत ६१.८% च्या गोल्डन रेषेच्या खाली गेली आहे, खरेदी करणे टाळा.")
        else:
            st.warning("⚖️ **प्रतीक्षा करा:** किंमत फिबोनाचीच्या मुख्य रेषेजवळ येण्याची वाट पहा.")
    else:
        st.error("सध्या बिटकॉइन डेटा उपलब्ध नाही.")
        

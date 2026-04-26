import streamlit as st
import pandas as pd
import time
import os
from datetime import datetime
import streamlit.components.v1 as components

# ==========================================
# ⚙️ SYSTEM INITIALIZATION
# ==========================================
st.set_page_config(
    page_title="OMNIX CORE", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# Internal Modules Check
try:
    from brokers.fin_provider import FinProvider
    from core.engine import TradeEngine
except ImportError:
    st.error("Missing Files: core/engine.py or brokers/fin_provider.py not found.")
    st.stop()

# Persistent Ledger File
HISTORY_FILE = 'trade_history.csv'
COLS = ['Timestamp', 'Asset', 'Signal', 'Price', 'SL', 'TP', 'Confidence', 'Status']

def clear_ledger():
    pd.DataFrame(columns=COLS).to_csv(HISTORY_FILE, index=False)

if not os.path.exists(HISTORY_FILE):
    clear_ledger()

# ==========================================
# 🎨 UI STYLING & OVERLAP OC LOGO
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Rajdhani', sans-serif; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0A0A0A !important;
        border-right: 1px solid #1A1A1A;
    }

    /* THE OVERLAP OC LOGO */
    .oc-logo-box {
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        display: inline-block;
        line-height: 1;
        position: relative;
    }
    .oc-logo-box .o { color: #FFFFFF; position: relative; z-index: 2; }
    .oc-logo-box .c { color: #666666; margin-left: -0.35em; position: relative; z-index: 1; }
    
    .sidebar-branding {
        text-align: center;
        padding: 20px 0;
        border-bottom: 1px solid #1A1A1A;
        margin-bottom: 20px;
    }

    /* Main Header Styling - 100% match with Sidebar Sub-Header Style */
    .main-header-flex {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin-bottom: 30px;
        padding: 40px;
    }

    .brand-title-style {
        color: #FFFFFF; 
        font-family: 'Orbitron', sans-serif; 
        text-align: center; 
        font-size: 32px; /* Adjusted for Header Visibility */
        letter-spacing: 12px; /* Sidebar style spacing logic */
        text-transform: uppercase;
        margin: 0;
    }
    
    .core-highlight { color: #666666; }

    /* Dashboard Components */
    .card-container { background: #050505; border: 2px solid #1A1A1A; border-radius: 12px; padding: 20px; min-height: 480px; display: flex; flex-direction: column; justify-content: space-between; }
    .card-header { font-family: 'Rajdhani', sans-serif; color: #444; text-transform: uppercase; letter-spacing: 2px; text-align: center; font-size: 0.9rem; }
    .card-signal { font-family: 'Orbitron', sans-serif; font-size: 2.5rem; font-weight: bold; text-align: center; margin: 15px 0; letter-spacing: 4px; }
    .info-row { background: rgba(255,255,255,0.02); padding: 10px; border-radius: 6px; margin-bottom: 8px; border-left: 4px solid #333; }
    .info-label { font-size: 0.7rem; color: #666; text-transform: uppercase; font-weight: bold; }
    .info-val { font-family: 'Orbitron', sans-serif; font-size: 1rem; color: #EEE; }
    
    .stButton>button {
        width: 100%;
        background-color: #1a1a1a !important;
        color: #ff3333 !important;
        border: 1px solid #333 !important;
        font-family: 'Orbitron', sans-serif;
    }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 📋 SIDEBAR NAVIGATION
# ==========================================
ASSET_DB = {
    "BINARY OPTIONS": ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD"],
    "FOREX INSTITUTIONAL": ["EURUSD=X", "GBPUSD=X", "USDJPY=X"],
    "GLOBAL STOCKS": ["NVDA", "TSLA", "AAPL"]
}

with st.sidebar:
    st.markdown("""
        <div class="sidebar-branding">
            <div class="oc-logo-box" style="font-size: 40px;">
                <span class="o">O</span><span class="c">C</span>
            </div>
            <div style="color:#FFF; font-family:'Orbitron'; font-size:10px; letter-spacing:4px; margin-top:10px;">OMNIX CORE</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ENVIRONMENT")
    category = st.radio("Market Selection", list(ASSET_DB.keys()), label_visibility="collapsed")
    st.markdown("### INSTRUMENT")
    selected_asset = st.selectbox("Asset Selection", ASSET_DB[category], label_visibility="collapsed")
    
    st.write("---")
    if st.button("RESET LEDGER"):
        clear_ledger()
        st.success("Ledger Reset!")
        time.sleep(1)
        st.rerun()

# ==========================================
# ⚡ MAIN INTERFACE
# ==========================================
st.markdown("""
    <div class="main-header-flex">
        <div class="oc-logo-box" style="font-size: 65px;">
            <span class="o">O</span><span class="c">C</span>
        </div>
        <div style="height: 60px; width: 2px; background: #222; margin: 0 10px;"></div>
        <div class="brand-title-style">OMNIX <span class="core-highlight">CORE</span></div>
    </div>
""", unsafe_allow_html=True)

try:
    provider = FinProvider()
    engine = TradeEngine()
    
    data_df = provider.get_data(selected_asset)
    if data_df is not None and not data_df.empty:
        data_df.columns = [c.lower() for c in data_df.columns]
        signal, confidence = engine.generate_signal(data_df)
        
        last_row = data_df.iloc[-1]
        current_price = round(float(last_row['close']), 5)
        rsi_val = last_row['rsi'] if 'rsi' in data_df.columns else 50.0

        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("PRICE", f"{current_price:,}")
        m2.metric("RSI", round(rsi_val, 2))
        m3.metric("STATUS", "STABLE" if 40 < rsi_val < 60 else "VOLATILE")
        m4.metric("AI CONF", f"{confidence}%")

        st.write("---")

        # Chart & Signal Workspace
        col_left, col_right = st.columns([2.5, 1])

        with col_left:
            tv_symbol = selected_asset.replace("=X", "").replace("-", "")
            if category == "FOREX INSTITUTIONAL": tv_symbol = f"FX:{tv_symbol}"
            elif category == "GLOBAL STOCKS": tv_symbol = f"NASDAQ:{tv_symbol}"
            else: tv_symbol = f"BINANCE:{tv_symbol.replace('USD', 'USDT')}"
            
            chart_html = f"""
            <div style="height:480px; border-radius:10px; overflow:hidden; border:1px solid #1A1A1A;">
                <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                <script type="text/javascript">
                new TradingView.widget({{"autosize": true, "symbol": "{tv_symbol}", "interval": "1", "theme": "dark", "style": "1", "container_id": "tv-div", "hide_side_toolbar": true, "backgroundColor": "#000000", "gridColor": "#0D0D0D"}});
                </script>
                <div id="tv-div" style="height:100%;"></div>
            </div>
            """
            components.html(chart_html, height=485)

        with col_right:
            is_active = signal in ["CALL", "PUT"]
            sig_color = "#00FF88" if signal == "CALL" else "#FF3333" if signal == "PUT" else "#333"
            sl = round(current_price * (0.998 if signal == "CALL" else 1.002), 5) if is_active else 0
            tp = round(current_price * (1.006 if signal == "CALL" else 0.994), 5) if is_active else 0

            st.markdown(f"""
                <div class="card-container" style="border-color: {sig_color if is_active else '#1A1A1A'};">
                    <div>
                        <div class="card-header">Signal Engine</div>
                        <div class="card-signal" style="color: {sig_color};">{signal}</div>
                        <div style="text-align:center; color:{sig_color}; font-size:0.7rem; font-family:Orbitron;">
                            {f'VERIFIED {confidence}%' if is_active else 'ANALYZING...'}
                        </div>
                    </div>
                    <div>
                        <div class="info-row" style="border-left-color: {sig_color};">
                            <div class="info-label">Entry</div><div class="info-val">{current_price if is_active else '---'}</div>
                        </div>
                        <div class="info-row" style="border-left-color: #FF3333;">
                            <div class="info-label">Stop Loss</div><div class="info-val">{sl if is_active else '---'}</div>
                        </div>
                        <div class="info-row" style="border-left-color: #00FF88;">
                            <div class="info-label">Take Profit</div><div class="info-val">{tp if is_active else '---'}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if is_active:
                ts = datetime.now().strftime("%H:%M:%S")
                with open(HISTORY_FILE, "a") as f:
                    f.write(f"{ts},{selected_asset},{signal},{current_price},{sl},{tp},{confidence}%,ACTIVE\n")

        # Ledger Table
        st.write("")
        st.markdown('<p style="text-align:center; color:#444; font-family:Orbitron; letter-spacing:5px;">INSTITUTIONAL LEDGER</p>', unsafe_allow_html=True)
        if os.path.exists(HISTORY_FILE):
            history_df = pd.read_csv(HISTORY_FILE, on_bad_lines='skip')
            if not history_df.empty:
                st.table(history_df.tail(10).iloc[::-1])

        time.sleep(2)
        st.rerun()

except Exception as e:
    st.error(f"Engine Error: {e}")
    time.sleep(3)
    st.rerun()
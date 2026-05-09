import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# --- 1. INITIALIZATION & DATA SETUP ---
if "vibe_data" not in st.session_state:
    st.session_state.vibe_data = {}
if "chat" not in st.session_state:
    st.session_state.chat = []

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

DB_FILE = "sentiment_history.csv"
TICKERS = ["AAPL", "TSLA", "AMZN", "MSFT", "GOOGL", "NFLX", "META", "NVDA"]
STOCK_NAMES = {
    "AAPL": "Apple Inc.", "TSLA": "Tesla Inc.", "AMZN": "Amazon.com", 
    "MSFT": "Microsoft", "GOOGL": "Google", "NFLX": "Netflix", 
    "META": "Meta", "NVDA": "Nvidia"
}
STOCK_LOGOS = {
    "AAPL": "https://www.vectorlogo.zone/logos/apple/apple-icon.svg",
    "TSLA": "https://www.vectorlogo.zone/logos/tesla/tesla-icon.svg",
    "AMZN": "https://www.vectorlogo.zone/logos/amazon/amazon-icon.svg",
    "MSFT": "https://www.vectorlogo.zone/logos/microsoft/microsoft-icon.svg",
    "GOOGL": "https://www.vectorlogo.zone/logos/google/google-icon.svg",
    "NFLX": "https://www.vectorlogo.zone/logos/netflix/netflix-icon.svg",
    "META": "https://www.vectorlogo.zone/logos/facebook/facebook-icon.svg",
    "NVDA": "https://www.vectorlogo.zone/logos/nvidia/nvidia-icon.svg"
}

st.set_page_config(page_title="Novus Solutions", layout="wide", page_icon="💹")

if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["Timestamp", "Ticker", "Score"]).to_csv(DB_FILE, index=False)

# --- 2. DARK MODE STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #ffffff; }
    .stApp { background: #0f172a; }
    [data-testid="stSidebar"] { background-color: #020617; border-right: 1px solid #1e293b; }
    
    /* Style "View Why" Button as a blue link */
    div.stButton > button {
        background-color: transparent; color: #38bdf8; border: none;
        padding: 0; text-decoration: underline; font-size: 0.8rem; font-weight: 600;
    }
    div.stButton > button:hover { color: #7dd3fc; background-color: transparent; }

    .stock-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px; padding: 20px; backdrop-filter: blur(10px);
    }
    .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; }
    .hyped { background-color: #064e3b; color: #34d399; }
    .optimistic { background-color: #14532d; color: #4ade80; }
    .neutral { background-color: #1e293b; color: #94a3b8; }
    .worried { background-color: #7c2d12; color: #fb923c; }
</style>
""", unsafe_allow_html=True)

# --- 3. DIALOG POPUP ---
@st.dialog("Sentiment Drivers")
def show_drivers(ticker, headlines):
    st.write(f"### Why is {ticker} showing this vibe?")
    for h in headlines:
        st.markdown(f"**•** {h}")
    st.info("Scores are derived from a real-time analysis of the last 24h of news headlines.")

# --- 4. DATA HELPERS ---
def get_label_meta(score):
    if score >= 0.4: return "HYPED", "hyped", "#10b981"
    if score >= 0.1: return "OPTIMISTIC", "optimistic", "#22c55e"
    if score <= -0.1: return "WORRIED", "worried", "#f97316"
    return "NEUTRAL", "neutral", "#94a3b8"

@st.cache_data(ttl=1800)
def fetch_headlines(ticker):
    url = f"https://news.google.com/rss/search?q={ticker}+stock+when:1d"
    try:
        response = requests.get(url, timeout=5)
        root = ET.fromstring(response.content)
        return [item.find("title").text for item in root.findall("./channel/item")[:5]]
    except: return []

def analyze_vibe(text_list):
    if not text_list or not VADER_AVAILABLE: return 0.0
    return round(sum(analyzer.polarity_scores(t)["compound"] for t in text_list) / len(text_list), 3)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#38bdf8;'>Novus Solutions</h1>", unsafe_allow_html=True)
    st.button("🏠 Dashboard", use_container_width=True)
    st.markdown("---")
    if st.button("Refresh Market Data", type="primary", use_container_width=True):
        results = {}
        history_entries = []
        for t in TICKERS:
            h = fetch_headlines(t)
            s = analyze_vibe(h)
            results[t] = {"score": s, "headlines": h}
            history_entries.append({"Timestamp": datetime.now(), "Ticker": t, "Score": s})
        
        st.session_state.vibe_data = results
        hist_df = pd.read_csv(DB_FILE)
        pd.concat([hist_df, pd.DataFrame(history_entries)]).to_csv(DB_FILE, index=False)
        st.rerun()

# --- 6. OVERALL GAUGE & CARDS ---
if st.session_state.vibe_data:
    avg_score = sum(v["score"] for v in st.session_state.vibe_data.values()) / len(TICKERS)
    label, _, color = get_label_meta(avg_score)
    
    st.markdown("<h2 style='text-align:center; color:#f8fafc;'>Overall Market Vibe</h2>", unsafe_allow_html=True)
    
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = avg_score,
        title = {'text': f"{label}", 'font': {'size': 24, 'color': color}},
        gauge = {'axis': {'range': [-1, 1], 'tickcolor': "#94a3b8"}, 'bar': {'color': "#38bdf8"}, 'bgcolor': "rgba(30, 41, 59, 0.5)"}
    ))
    fig_gauge.update_layout(height=280, margin=dict(t=50, b=0), paper_bgcolor='rgba(0,0,0,0)', font={'color': "#ffffff"})
    st.plotly_chart(fig_gauge, use_container_width=True)

    for row in [TICKERS[:4], TICKERS[4:]]:
        cols = st.columns(4)
        for i, ticker in enumerate(row):
            d = st.session_state.vibe_data[ticker]
            lbl, l_class, _ = get_label_meta(d['score'])
            with cols[i]:
                st.markdown(f"""
                <div class="stock-card">
                    <div style="display:flex; justify-content:space-between;">
                        <img src="{STOCK_LOGOS[ticker]}" width="24" style="filter: brightness(0) invert(1);">
                        <span class="status-badge {l_class}">{lbl}</span>
                    </div>
                    <div style="font-weight:700; margin-top:10px;">{ticker}</div>
                    <div style="color:#38bdf8; font-size:1.8rem; font-weight:800;">{d['score']:+.2f}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("View Why", key=f"btn_{ticker}"):
                    show_drivers(ticker, d['headlines'])

# --- 7. HISTORICAL TRAJECTORY & CHAT ---
st.markdown("---")
col_g, col_c = st.columns([1.6, 1])

with col_g:
    st.subheader("Historical Trajectory")
    df = pd.read_csv(DB_FILE)
    if not df.empty:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        fig = go.Figure()
        # Specific High-Contrast colors for lines
        colors = ['#60a5fa', '#facc15', '#fb923c', '#c084fc', '#4ade80', '#22d3ee', '#f472b6', '#fb7185']
        
        for idx, t in enumerate(TICKERS):
            t_df = df[df['Ticker'] == t]
            if not t_df.empty:
                fig.add_trace(go.Scatter(
                    x=t_df['Timestamp'], y=t_df['Score'], 
                    name=t, mode='lines', 
                    line=dict(width=2, color=colors[idx % len(colors)]),
                    connectgaps=True
                ))
        fig.update_layout(
            template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            margin=dict(t=10, l=0, r=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

with col_c:
    st.subheader("Vibe Analyst Chat")
    chat_container = st.container(height=350)
    with chat_container:
        if not st.session_state.chat:
            st.markdown("<p style='color: #64748b;'>Ask about a stock vibe...</p>", unsafe_allow_html=True)
        for m in st.session_state.chat:
            with st.chat_message("assistant" if m["sender"] == "Bot" else "user"):
                st.markdown(m["text"])
    
    if prompt := st.chat_input("Ask about a stock vibe..."):
        st.session_state.chat.append({"sender": "You", "text": prompt})
        response = "Please sync market data first."
        if st.session_state.vibe_data:
            match = next((t for t in TICKERS if t.lower() in prompt.lower()), None)
            if match:
                data = st.session_state.vibe_data[match]
                label, _, _ = get_label_meta(data['score'])
                response = f"**{match}** is **{label}** (`{data['score']:+.2f}`). \n\n**Driver:** {data['headlines'][0]}"
            else:
                response = "I track AAPL, TSLA, AMZN, MSFT, GOOGL, NFLX, META, and NVDA. Mention one to get an analysis!"
        st.session_state.chat.append({"sender": "Bot", "text": response})
        st.rerun()
        

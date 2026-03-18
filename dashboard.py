import streamlit as st
import base64
import time
import cv2
import numpy as np
import urllib.request
from pathlib import Path
from prediction_graph import build_chart
from emergency import check_emergency
from ai_assistant import get_ai_tip
from decision_engine import DecisionEngine
from traffic_predictor import TrafficPredictor
from vehicle_detection import VehicleDetector

# ── Download demo video if not present ────────────────────────────────────────
VIDEO_PATH = Path("traffic.mp4")
VIDEO_ID   = "1zAXvb6mMMi0FrXFxo9oqYeFrdvXAvBoj"

if not VIDEO_PATH.exists():
    with st.spinner("Downloading demo video..."):
        try:
            import gdown
            gdown.download(id=VIDEO_ID, output=str(VIDEO_PATH), quiet=True)
        except Exception:
            urllib.request.urlretrieve(
                f"https://drive.google.com/uc?export=download&id={VIDEO_ID}",
                VIDEO_PATH
            )

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AURA Smart City",
    page_icon="AURA",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600&display=swap');

:root {
    --bg:      #020b18;
    --surface: #041428;
    --card:    #071e36;
    --border:  #0d3a5c;
    --cyan:    #00d4ff;
    --blue:    #0077ff;
    --green:   #00ff88;
    --orange:  #ff8c00;
    --red:     #ff3b5c;
    --text:    #cce8ff;
    --muted:   #4a7fa5;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif;
}

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,212,255,.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,.04) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }

.aura-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
    transition: transform .2s, box-shadow .2s;
}
.aura-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(0,212,255,.15);
}
.aura-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--cyan), var(--blue));
}

.metric-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.metric-card .label {
    font-size: .72rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--muted);
    font-family: 'Orbitron', sans-serif;
}
.metric-card .value {
    font-size: 2rem;
    font-weight: 700;
    font-family: 'Orbitron', sans-serif;
    line-height: 1.1;
    margin: 4px 0;
}
.metric-card .sub { font-size: .78rem; color: var(--muted); }

@keyframes glow {
    0%,100% { text-shadow: 0 0 8px currentColor; }
    50%      { text-shadow: 0 0 22px currentColor, 0 0 40px currentColor; }
}
.metric-card .value { animation: glow 3s ease-in-out infinite; }

.cyan   { color: var(--cyan)   !important; }
.green  { color: var(--green)  !important; }
.orange { color: var(--orange) !important; }
.red    { color: var(--red)    !important; }
.blue   { color: var(--blue)   !important; }

.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: .72rem;
    font-family: 'Orbitron', sans-serif;
    letter-spacing: .08em;
    font-weight: 700;
}
.badge-green  { background: rgba(0,255,136,.12); color: var(--green);  border: 1px solid var(--green); }
.badge-orange { background: rgba(255,140,0,.12);  color: var(--orange); border: 1px solid var(--orange); }
.badge-red    { background: rgba(255,59,92,.12);  color: var(--red);    border: 1px solid var(--red); }
.badge-cyan   { background: rgba(0,212,255,.12);  color: var(--cyan);   border: 1px solid var(--cyan); }

.section-title {
    font-family: 'Orbitron', sans-serif;
    font-size: .8rem;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: var(--cyan);
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border), transparent);
}

.alert-box {
    background: rgba(255,59,92,.08);
    border: 1px solid var(--red);
    border-radius: 12px;
    padding: 14px 18px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: .88rem;
}
.alert-box.info {
    background: rgba(0,212,255,.06);
    border-color: var(--cyan);
}

.ai-tip {
    background: linear-gradient(135deg, rgba(0,119,255,.08), rgba(0,212,255,.06));
    border: 1px solid var(--blue);
    border-radius: 12px;
    padding: 14px 18px;
    font-size: .88rem;
    line-height: 1.6;
}

div[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 10px;
    color: #4a7fa5;
    font-family: 'Inter', sans-serif;
    font-size: .88rem;
    text-align: left;
    padding: 10px 14px;
    margin-bottom: 4px;
    transition: all .2s;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(0,212,255,.08);
    color: #00d4ff;
    border-color: rgba(0,212,255,.3);
}
div[data-testid="stSidebar"] .stButton > button:focus { box-shadow: none; }
.nav-active > button {
    background: rgba(0,212,255,.12) !important;
    color: #00d4ff !important;
    border-color: #00d4ff !important;
    border-left: 3px solid #00d4ff !important;
    font-weight: 600;
}

[data-testid="stMetric"] { display: none; }
div[data-testid="column"] > div { gap: 0 !important; }
.stPlotlyChart { border-radius: 14px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def logo_b64():
    p = Path("Smart city evolution logo.png")
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return None

def video_b64():
    if VIDEO_PATH.exists():
        return base64.b64encode(VIDEO_PATH.read_bytes()).decode()
    return None

def congestion_color(level):
    return {"Low": "green", "Medium": "orange", "High": "red"}.get(level, "cyan")

def signal_color(decision):
    if "Green" in decision: return "green"
    if "Red"   in decision: return "red"
    return "orange"


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    logo = logo_b64()
    if logo:
        st.markdown(
            f'<div style="text-align:center;padding:16px 0 8px">'
            f'<img src="data:image/png;base64,{logo}" style="width:160px;filter:drop-shadow(0 0 12px #00d4ff88)"/>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        '<div style="text-align:center;font-family:Orbitron,sans-serif;'
        'font-size:.65rem;letter-spacing:.25em;color:#4a7fa5;padding-bottom:20px">'
        'SMART CITY INTELLIGENCE</div>',
        unsafe_allow_html=True,
    )

    if "page" not in st.session_state:
        st.session_state.page = "Live Dashboard"

    st.markdown('<div style="margin-bottom:8px;font-family:Orbitron,sans-serif;font-size:.65rem;letter-spacing:.18em;color:#4a7fa5">NAVIGATION</div>', unsafe_allow_html=True)
    for label in ["Live Dashboard", "Analytics", "Route Map", "Emergency", "AI Assistant"]:
        is_active = st.session_state.page == label
        if is_active:
            st.markdown('<div class="nav-active">', unsafe_allow_html=True)
        if st.button(label, key=f"nav_{label}"):
            st.session_state.page = label
            st.rerun()
        if is_active:
            st.markdown('</div>', unsafe_allow_html=True)

    page = st.session_state.page

    st.markdown("<hr style='border-color:#0d3a5c;margin:16px 0'/>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">System Status</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    col_a.markdown('<div style="font-size:.75rem;color:#4a7fa5">AI Engine</div>'
                   '<span class="badge badge-green">ONLINE</span>', unsafe_allow_html=True)
    col_b.markdown('<div style="font-size:.75rem;color:#4a7fa5">Camera Feed</div>'
                   '<span class="badge badge-cyan">ACTIVE</span>', unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    run = st.toggle("Start Live Feed", value=False)


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="display:flex;align-items:center;gap:16px;padding:8px 0 24px">'
    '<div>'
    '<div style="font-family:Orbitron,sans-serif;font-size:1.8rem;font-weight:900;'
    'background:linear-gradient(90deg,#00d4ff,#0077ff);-webkit-background-clip:text;'
    '-webkit-text-fill-color:transparent">AURA</div>'
    '<div style="font-size:.72rem;letter-spacing:.22em;color:#4a7fa5;'
    'font-family:Orbitron,sans-serif">AUTONOMOUS URBAN RESPONSE ARCHITECTURE</div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: LIVE DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if "Live Dashboard" in page:

    engine    = DecisionEngine()
    predictor = TrafficPredictor()
    detector  = VehicleDetector()

    if "history" not in st.session_state:
        st.session_state.history = [10, 12, 14, 18, 20]

    history = st.session_state.history

    # ── Static metric placeholders (rendered once) ─────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    slot_v  = m1.empty()
    slot_c  = m2.empty()
    slot_d  = m3.empty()
    slot_p  = m4.empty()

    feed_col, chart_col = st.columns([3, 2], gap="medium")
    feed_slot  = feed_col.empty()
    chart_slot = chart_col.empty()

    alert_col, tip_col = st.columns(2, gap="medium")
    alert_slot = alert_col.empty()
    tip_slot   = tip_col.empty()

    def render_metric(slot, label, value, sub, color):
        slot.markdown(
            f'<div class="metric-card">'
            f'<div class="label">{label}</div>'
            f'<div class="value {color}">{value}</div>'
            f'<div class="sub">{sub}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    if "chart_key" not in st.session_state:
        st.session_state.chart_key = 0

    def render_chart_slot(h):
        st.session_state.chart_key += 1
        chart_slot.markdown('<div class="section-title">Vehicle Count Trend</div>', unsafe_allow_html=True)
        chart_slot.plotly_chart(build_chart(h), use_container_width=True,
                                config={"displayModeBar": False}, key=f"trend_{st.session_state.chart_key}")

    def render_alert_tip(congestion, vehicles):
        alert = check_emergency(congestion, vehicles)
        if alert:
            alert_slot.markdown(
                f'<div class="alert-box"><div><b>EMERGENCY ALERT</b><br/>{alert}</div></div>',
                unsafe_allow_html=True)
        else:
            alert_slot.markdown(
                '<div class="alert-box info"><div><b>All Clear</b><br/>'
                'No incidents detected. System operating normally.</div></div>',
                unsafe_allow_html=True)
        tip_slot.markdown(
            f'<div class="section-title">AI Recommendation</div>'
            f'<div class="ai-tip">{get_ai_tip(congestion, vehicles)}</div>',
            unsafe_allow_html=True)

    # ── Initial render ─────────────────────────────────────────────────────────
    render_metric(slot_v, "Vehicles Detected", "0",    "active now", "cyan")
    render_metric(slot_c, "Congestion Level",  "Low",  "real-time",  "green")
    render_metric(slot_d, "Signal Decision",   "Green Light", "AI control", "green")
    render_metric(slot_p, "Next Prediction",   "0 veh", "forecast",  "blue")
    feed_slot.markdown(
        '<div style="background:#041428;border:1px solid #0d3a5c;border-radius:12px;'
        'height:260px;display:flex;align-items:center;justify-content:center;'
        'color:#4a7fa5;font-family:Orbitron,sans-serif;font-size:.75rem;'
        'letter-spacing:.15em">FEED INACTIVE — TOGGLE TO START</div>',
        unsafe_allow_html=True)
    render_chart_slot(history)
    render_alert_tip("Low", 0)

    # ── Live loop ──────────────────────────────────────────────────────────────
    if run:
        cap = cv2.VideoCapture(str(VIDEO_PATH))
        if not cap.isOpened():
            st.error("Could not open video file.")
        else:
            feed_slot.markdown('<div class="section-title">Live Camera Feed</div>', unsafe_allow_html=True)
            frame_slot = feed_slot.empty()
            frame_idx  = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue

                frame, vehicle_count, _ = detector.detect(frame)
                congestion = engine.analyze(vehicle_count)
                decision   = engine.signal_decision(congestion)
                history.append(vehicle_count)
                if len(history) > 30:
                    history.pop(0)
                prediction = predictor.predict(history)
                st.session_state.history = history

                cc = congestion_color(congestion)
                sc = signal_color(decision)

                frame_slot.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)

                # Update metrics and chart every 10 frames only
                if frame_idx % 10 == 0:
                    render_metric(slot_v, "Vehicles Detected", str(vehicle_count), "active now", "cyan")
                    render_metric(slot_c, "Congestion Level",  congestion, "real-time", cc)
                    render_metric(slot_d, "Signal Decision",   decision,   "AI control", sc)
                    render_metric(slot_p, "Next Prediction",   str(prediction)+" veh", "forecast", "blue")
                    render_chart_slot(history)
                    render_alert_tip(congestion, vehicle_count)

                frame_idx += 1

            cap.release()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif "Analytics" in page:
    import plotly.graph_objects as go

    st.markdown('<div class="section-title">Traffic Analytics Overview</div>', unsafe_allow_html=True)

    hours          = list(range(24))
    avg_vehicles   = [5,3,2,2,3,8,18,32,28,22,20,24,26,23,21,25,30,35,28,20,15,12,9,6]
    congestion_pct = [10,5,3,3,5,15,45,80,70,55,50,60,65,58,52,62,75,88,70,50,38,30,22,15]

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hours, y=avg_vehicles, fill='tozeroy',
            line=dict(color='#00d4ff', width=2),
            fillcolor='rgba(0,212,255,0.08)', name='Avg Vehicles'
        ))
        fig.update_layout(
            title=dict(text="Avg Vehicles per Hour", font=dict(color='#cce8ff', size=13)),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#4a7fa5'),
            xaxis=dict(gridcolor='#0d3a5c', title='Hour'),
            yaxis=dict(gridcolor='#0d3a5c', title='Vehicles'),
            margin=dict(l=10, r=10, t=40, b=10), height=260,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="analytics_vehicles")

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=hours, y=congestion_pct,
            marker=dict(color=congestion_pct,
                        colorscale=[[0,'#00ff88'],[0.5,'#ff8c00'],[1,'#ff3b5c']]),
            name='Congestion %'
        ))
        fig2.update_layout(
            title=dict(text="Congestion % by Hour", font=dict(color='#cce8ff', size=13)),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#4a7fa5'),
            xaxis=dict(gridcolor='#0d3a5c', title='Hour'),
            yaxis=dict(gridcolor='#0d3a5c', title='%'),
            margin=dict(l=10, r=10, t=40, b=10), height=260,
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False}, key="analytics_congestion")

    st.markdown('<div class="section-title">Key Metrics</div>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    for col, label, val, color in [
        (s1, "Peak Hour",       "17:00", "cyan"),
        (s2, "Max Vehicles",    "35",    "blue"),
        (s3, "Avg Congestion",  "42%",   "orange"),
        (s4, "Incidents Today", "2",     "red"),
    ]:
        col.markdown(
            f'<div class="metric-card">'
            f'<div class="label">{label}</div>'
            f'<div class="value {color}">{val}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: ROUTE MAP
# ══════════════════════════════════════════════════════════════════════════════
elif "Route Map" in page:
    import plotly.graph_objects as go
    import random

    st.markdown('<div class="section-title">Emergency Route Intelligence</div>', unsafe_allow_html=True)

    # ── Simulated city routes (lat/lon pairs) ────────────────────────────────────
    # Centre: Nairobi CBD
    CENTER = (-1.2921, 36.8219)

    routes = [
        {
            "name": "Route A — Uhuru Highway",
            "coords": [(-1.2921,36.8219),(-1.2950,36.8150),(-1.2980,36.8080),(-1.3010,36.8010)],
            "congestion": "High",
            "eta": "18 min",
            "distance": "4.2 km",
        },
        {
            "name": "Route B — Mombasa Road",
            "coords": [(-1.2921,36.8219),(-1.3000,36.8300),(-1.3080,36.8380),(-1.3150,36.8450)],
            "congestion": "Low",
            "eta": "7 min",
            "distance": "3.1 km",
        },
        {
            "name": "Route C — Ngong Road",
            "coords": [(-1.2921,36.8219),(-1.2860,36.8150),(-1.2800,36.8080),(-1.2740,36.8010)],
            "congestion": "Medium",
            "eta": "12 min",
            "distance": "3.8 km",
        },
        {
            "name": "Route D — Thika Road",
            "coords": [(-1.2921,36.8219),(-1.2800,36.8300),(-1.2680,36.8380),(-1.2560,36.8450)],
            "congestion": "Low",
            "eta": "9 min",
            "distance": "3.5 km",
        },
        {
            "name": "Route E — Waiyaki Way",
            "coords": [(-1.2921,36.8219),(-1.2880,36.8350),(-1.2840,36.8480),(-1.2800,36.8600)],
            "congestion": "High",
            "eta": "22 min",
            "distance": "5.0 km",
        },
    ]

    color_map = {"Low": "#00ff88", "Medium": "#ff8c00", "High": "#ff3b5c"}

    # ── Best route highlight ─────────────────────────────────────────────────────────
    low_routes  = [r for r in routes if r["congestion"] == "Low"]
    best_route  = min(low_routes, key=lambda r: int(r["eta"].split()[0])) if low_routes else routes[0]

    # ── Top summary cards ─────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, color in [
        (c1, "Best Route",     best_route["name"].split(" — ")[1], "green"),
        (c2, "ETA",            best_route["eta"],                   "cyan"),
        (c3, "Distance",       best_route["distance"],              "blue"),
        (c4, "Routes Blocked", str(sum(1 for r in routes if r["congestion"]=="High")), "red"),
    ]:
        col.markdown(
            f'<div class="metric-card">'
            f'<div class="label">{label}</div>'
            f'<div class="value {color}">{val}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br/>", unsafe_allow_html=True)
    map_col, info_col = st.columns([3, 1], gap="medium")

    with map_col:
        st.markdown('<div class="section-title">Live Route Congestion Map</div>', unsafe_allow_html=True)

        fig = go.Figure()

        for route in routes:
            lats = [c[0] for c in route["coords"]]
            lons = [c[1] for c in route["coords"]]
            color = color_map[route["congestion"]]
            is_best = route["name"] == best_route["name"]
            fig.add_trace(go.Scattermapbox(
                lat=lats, lon=lons,
                mode="lines+markers",
                line=dict(width=6 if is_best else 4, color=color),
                marker=dict(size=8 if is_best else 5, color=color),
                name=route["name"],
                hovertemplate=(
                    f"<b>{route['name']}</b><br>"
                    f"Congestion: {route['congestion']}<br>"
                    f"ETA: {route['eta']}<br>"
                    f"Distance: {route['distance']}"
                    "<extra></extra>"
                ),
            ))

        # Origin marker
        fig.add_trace(go.Scattermapbox(
            lat=[CENTER[0]], lon=[CENTER[1]],
            mode="markers+text",
            marker=dict(size=16, color="#00d4ff", symbol="circle"),
            text=["DISPATCH"], textposition="top right",
            textfont=dict(color="#00d4ff", size=11),
            name="Dispatch",
            hovertemplate="<b>Dispatch Center</b><extra></extra>",
        ))

        # Best route pulse marker at destination
        dest = best_route["coords"][-1]
        fig.add_trace(go.Scattermapbox(
            lat=[dest[0]], lon=[dest[1]],
            mode="markers+text",
            marker=dict(size=18, color="#00ff88", symbol="circle"),
            text=["TARGET"], textposition="top right",
            textfont=dict(color="#00ff88", size=11),
            name="Target",
            hovertemplate="<b>Incident Location</b><extra></extra>",
        ))

        fig.update_layout(
            mapbox=dict(
                style="carto-darkmatter",
                center=dict(lat=CENTER[0], lon=CENTER[1]),
                zoom=12,
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=0, b=0),
            height=500,
            legend=dict(
                bgcolor="rgba(4,20,40,0.9)",
                bordercolor="#0d3a5c",
                borderwidth=1,
                font=dict(color="#cce8ff", size=11),
            ),
            font=dict(color="#cce8ff"),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="route_map")

    with info_col:
        st.markdown('<div class="section-title">Route Status</div>', unsafe_allow_html=True)
        for route in routes:
            color     = color_map[route["congestion"]]
            badge_cls = f"badge-{route['congestion'].lower()}"
            is_best   = route["name"] == best_route["name"]
            border    = "#00ff88" if is_best else "#0d3a5c"
            bg        = "rgba(0,255,136,.05)" if is_best else "rgba(7,30,54,1)"
            st.markdown(
                f'<div style="background:{bg};border:1px solid {border};border-radius:12px;'
                f'padding:12px 14px;margin-bottom:10px">'
                f'<div style="font-family:Orbitron,sans-serif;font-size:.72rem;color:#cce8ff;margin-bottom:6px">'
                f'{"RECOMMENDED " if is_best else ""}{route["name"]}'
                f'</div>'
                f'<div style="display:flex;justify-content:space-between;align-items:center">'
                f'<span class="badge {badge_cls}">{route["congestion"]}</span>'
                f'<span style="font-size:.78rem;color:#4a7fa5">{route["eta"]} &bull; {route["distance"]}</span>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Legend</div>', unsafe_allow_html=True)
        for label, color in [("Low Congestion","#00ff88"),("Medium Congestion","#ff8c00"),("High Congestion","#ff3b5c")]:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;font-size:.82rem">'
                f'<div style="width:28px;height:4px;background:{color};border-radius:2px"></div>'
                f'<span style="color:#cce8ff">{label}</span></div>',
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: EMERGENCY
# ══════════════════════════════════════════════════════════════════════════════
elif "Emergency" in page:
    st.markdown('<div class="section-title">Emergency Management</div>', unsafe_allow_html=True)

    e1, e2, e3 = st.columns(3, gap="medium")
    for col, title, loc, status, color in [
        (e1, "Fire Alert", "Zone A - Main St",   "ACTIVE",     "red"),
        (e2, "Medical",    "Zone C - Park Ave",  "RESOLVED",   "green"),
        (e3, "Accident",   "Zone B - Highway 1", "MONITORING", "orange"),
    ]:
        col.markdown(
            f'<div class="aura-card">'
            f'<div style="font-family:Orbitron,sans-serif;font-size:.9rem;margin:8px 0 4px">{title}</div>'
            f'<div style="font-size:.8rem;color:#4a7fa5;margin-bottom:10px">{loc}</div>'
            f'<span class="badge badge-{color}">{status}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Report New Incident</div>', unsafe_allow_html=True)
    with st.form("incident_form"):
        c1, c2 = st.columns(2)
        itype    = c1.selectbox("Incident Type", ["Fire", "Accident", "Medical", "Flood", "Other"])
        zone     = c2.selectbox("Zone", ["Zone A", "Zone B", "Zone C", "Zone D"])
        st.text_area("Description", placeholder="Describe the incident...")
        severity = st.select_slider("Severity", ["Low", "Medium", "High", "Critical"])
        if st.form_submit_button("Submit Incident Report"):
            st.markdown(
                f'<div class="alert-box info"><div><b>Incident Reported</b><br/>'
                f'{itype} in {zone} — Severity: {severity}</div></div>',
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE: AI ASSISTANT
# ══════════════════════════════════════════════════════════════════════════════
elif "AI Assistant" in page:
    st.markdown('<div class="section-title">AURA AI Assistant</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="aura-card" style="margin-bottom:20px">'
        '<div style="font-family:Orbitron,sans-serif;font-size:.85rem;color:#00d4ff;margin-bottom:8px">'
        'AURA Intelligence Engine</div>'
        '<div style="font-size:.88rem;color:#4a7fa5;line-height:1.7">'
        'Ask me anything about traffic conditions, signal optimization, '
        'emergency routing, or city analytics.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for role, msg in st.session_state.chat_history:
        align  = "right" if role == "user" else "left"
        bg     = "rgba(0,119,255,.12)" if role == "user" else "rgba(0,212,255,.06)"
        border = "#0077ff" if role == "user" else "#00d4ff"
        label  = "You" if role == "user" else "AURA"
        st.markdown(
            f'<div style="display:flex;justify-content:{align};margin-bottom:10px">'
            f'<div style="max-width:75%;background:{bg};border:1px solid {border};'
            f'border-radius:12px;padding:10px 14px;font-size:.88rem">'
            f'<div style="font-size:.7rem;color:#4a7fa5;margin-bottom:4px">{label}</div>'
            f'{msg}</div></div>',
            unsafe_allow_html=True,
        )

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("", placeholder="Ask AURA something...", label_visibility="collapsed")
        if st.form_submit_button("Send") and user_input.strip():
            st.session_state.chat_history.append(("user", user_input))
            st.session_state.chat_history.append(("aura", get_ai_tip("Medium", 20, query=user_input)))
            st.rerun()

import os
import streamlit as st
import folium
from streamlit_folium import st_folium

from schemas import AnomalyDetectionEvent
from agent_core import (
    run_hydrodynamic_agent,
    run_biogeochemical_agent,
    run_synthesizer_agent,
)

st.set_page_config(
    page_title="ORCA Tactical Oceanic Sentry",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aerospace & Tactical Maritime HUD Styling
st.markdown("""
<style>
    @import url("https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Inter:wght@300;400;500;600;700&display=swap");
    
    * {
        font-family: "Inter", -apple-system, sans-serif;
    }
    
    code, .mono-font, [class*="stCode"] {
        font-family: "JetBrains Mono", monospace !important;
    }
    
    .stApp {
        background-color: #040813;
        color: #D1D5DB;
    }
    
    /* Top Global Header */
    .orca-nav {
        background: linear-gradient(180deg, #0A1324 0%, #060B17 100%);
        border: 1px solid #16263D;
        border-top: 3px solid #00E5FF;
        border-radius: 4px;
        padding: 16px 22px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
    }
    
    .orca-title {
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: 2.5px;
        color: #F8FAFC;
        text-transform: uppercase;
    }
    
    .orca-subtitle {
        font-size: 0.75rem;
        letter-spacing: 1.2px;
        color: #64748B;
        text-transform: uppercase;
        margin-top: 3px;
    }
    
    /* Radar Live Pulse Indicator */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-family: "JetBrains Mono", monospace;
        font-size: 0.72rem;
        padding: 4px 10px;
        background: rgba(0, 229, 255, 0.05);
        border: 1px solid rgba(0, 229, 255, 0.3);
        border-radius: 2px;
        color: #00E5FF;
        letter-spacing: 1px;
    }
    
    .pulse-dot {
        width: 7px;
        height: 7px;
        background: #00E5FF;
        border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(0, 229, 255, 0.7);
        animation: pulse-ring 2s infinite;
    }
    
    @keyframes pulse-ring {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 229, 255, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(0, 229, 255, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 229, 255, 0); }
    }
    
    /* Telemetry Quick Cards */
    .telemetry-card {
        background: #070F1E;
        border: 1px solid #132238;
        border-radius: 3px;
        padding: 12px 14px;
        text-align: left;
        position: relative;
        overflow: hidden;
    }
    
    .telemetry-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(0, 229, 255, 0.4), transparent);
    }
    
    .telemetry-label {
        font-size: 0.68rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #64748B;
        font-family: "JetBrains Mono", monospace;
    }
    
    .telemetry-val {
        font-size: 1.25rem;
        font-weight: 700;
        color: #F1F5F9;
        font-family: "JetBrains Mono", monospace;
        margin-top: 4px;
    }
    
    /* Agent Execution Log Containers */
    .agent-box {
        background: #08101F;
        border: 1px solid #14233A;
        border-radius: 3px;
        padding: 16px;
        margin-bottom: 14px;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    
    .agent-box:hover {
        border-color: #1F3A60;
    }
    
    .agent-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #122035;
        padding-bottom: 10px;
        margin-bottom: 12px;
    }
    
    .agent-title {
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        font-family: "JetBrains Mono", monospace;
    }
    
    .agent-badge {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.7rem;
        padding: 2px 7px;
        border-radius: 2px;
        background: #0E1D33;
        border: 1px solid #1E385D;
    }
    
    .agent-row {
        font-size: 0.85rem;
        line-height: 1.6;
        color: #94A3B8;
        margin-bottom: 6px;
    }
    
    .agent-row strong {
        color: #E2E8F0;
        font-weight: 600;
    }
    
    /* Downlink Hex Frame Monospace */
    .downlink-terminal {
        background: #02050B;
        border: 1px solid #13243C;
        border-left: 3px solid #00E5FF;
        border-radius: 2px;
        padding: 14px 16px;
        margin-top: 10px;
    }
    
    .downlink-title {
        font-size: 0.68rem;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: #64748B;
        font-family: "JetBrains Mono", monospace;
        margin-bottom: 6px;
    }
    
    .downlink-payload {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.92rem;
        color: #00E5FF;
        letter-spacing: 2px;
        word-break: break-all;
    }
</style>
""", unsafe_allow_html=True)

# Navigation Header
st.markdown("""
<div class="orca-nav">
    <div>
        <div class="orca-title">Project ORCA &bull; Naval Oceanic Sentry</div>
        <div class="orca-subtitle">Multi-Agent Hydrodynamic & Biogeochemical Autonomous Disaster Network</div>
    </div>
    <div style="display:flex; gap:12px; align-items:center;">
        <div class="status-badge">
            <div class="pulse-dot"></div>
            <span>SENTINEL TELEMETRY ONLINE</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Configuration & Sector Select
st.sidebar.markdown("<div style=\"font-size:0.75rem; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:#64748B; margin-bottom:12px; font-family:'JetBrains Mono';\">Surveillance Sector</div>", unsafe_allow_html=True)

selected_preset = st.sidebar.selectbox(
    "Observation Domain",
    [
        "Malabar Upwelling Zone (Arabian Sea)",
        "Gulf of Mannar Biological Sanctuary (Bay of Bengal)",
        "Konkan Basin Shelf (Central Arabian Sea)",
        "Manual Spatial Coordinate Ingestion"
    ]
)

presets = {
    "Malabar Upwelling Zone (Arabian Sea)": {
        "lat": 11.25, "lon": 74.80, "sst": 25.8, "chl": 9.85, "wind": 8.2, "z": 3.42,
        "desc": "Active southwest coastal upwelling zone characterized by high Ekman transport and dense chlorophyll plumes."
    },
    "Gulf of Mannar Biological Sanctuary (Bay of Bengal)": {
        "lat": 8.95, "lon": 79.15, "sst": 29.4, "chl": 4.12, "wind": 5.1, "z": 2.18,
        "desc": "Shallow reef corridor with elevated thermal profiles and localized biogenic organic accumulation."
    },
    "Konkan Basin Shelf (Central Arabian Sea)": {
        "lat": 15.50, "lon": 73.65, "sst": 28.1, "chl": 1.45, "wind": 3.4, "z": 0.85,
        "desc": "Stable stratified marine shelf exhibiting baseline seasonal nutrient dynamics."
    },
    "Manual Spatial Coordinate Ingestion": {
        "lat": 12.00, "lon": 75.00, "sst": 26.0, "chl": 6.50, "wind": 7.0, "z": 2.80,
        "desc": "Custom injection matrix for testing edge threshold responses."
    }
}

p = presets[selected_preset]

if selected_preset == "Manual Spatial Coordinate Ingestion":
    c_lat = st.sidebar.number_input("Latitude Coordinate (N)", 5.0, 25.0, p["lat"], 0.05)
    c_lon = st.sidebar.number_input("Longitude Coordinate (E)", 65.0, 90.0, p["lon"], 0.05)
    c_sst = st.sidebar.slider("Sea Surface Temperature (C)", 20.0, 34.0, p["sst"], 0.1)
    c_chl = st.sidebar.slider("Chlorophyll-a Concentration (mg/m3)", 0.1, 25.0, p["chl"], 0.1)
    c_wind = st.sidebar.slider("10m Surface Wind Velocity (m/s)", 0.0, 25.0, p["wind"], 0.1)
    c_z = st.sidebar.slider("Spatial Anomaly Significance (Sigma)", 0.0, 5.0, p["z"], 0.05)
else:
    c_lat, c_lon, c_sst, c_chl, c_wind, c_z = p["lat"], p["lon"], p["sst"], p["chl"], p["wind"], p["z"]

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style="font-size:0.75rem; color:#64748B; font-family:'JetBrains Mono'; line-height:1.6;">
    <span style="color:#94A3B8; font-weight:600;">SENSOR SUITE:</span> Oceansat-3 OCM / MODIS-Aqua<br>
    <span style="color:#94A3B8; font-weight:600;">COORDINATES:</span> {c_lat:.2f}&deg;N, {c_lon:.2f}&deg;E<br>
    <span style="color:#94A3B8; font-weight:600;">SECTOR BRIEF:</span> {p["desc"]}
</div>
""", unsafe_allow_html=True)

telemetry = AnomalyDetectionEvent(
    event_id=f"ORCA-2026-T-{int(c_lat*100)}",
    center_lat=c_lat,
    center_lon=c_lon,
    peak_chlorophyll=c_chl,
    mean_sst=c_sst,
    wind_speed=c_wind,
    z_score=c_z
)

col_map, col_analysis = st.columns([5, 6], gap="large")

with col_map:
    st.markdown("<div style=\"font-size:0.8rem; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:#94A3B8; margin-bottom:8px; font-family:'JetBrains Mono';\">Geospatial Tactical Projection</div>", unsafe_allow_html=True)
    
    tactical_map = folium.Map(
        location=[c_lat, c_lon],
        zoom_start=7,
        tiles="CartoDB dark_matter",
        control_scale=False,
        attributionControl=False
    )
    
    tier_color = "#FF3366" if c_z >= 3.0 else ("#FFB020" if c_z >= 1.5 else "#00E5FF")
    
    folium.Circle(
        location=[c_lat, c_lon],
        radius=40000,
        color=tier_color,
        weight=1.5,
        fill=True,
        fill_color=tier_color,
        fill_opacity=0.22,
        tooltip=f"Vector {telemetry.event_id} | Z-Score: {c_z} Sigma"
    ).add_to(tactical_map)

    folium.CircleMarker(
        location=[c_lat, c_lon],
        radius=4,
        color="#FFFFFF",
        weight=2,
        fill=True,
        fill_color=tier_color,
        fill_opacity=1.0
    ).add_to(tactical_map)
    
    st_folium(tactical_map, height=440, use_container_width=True)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="telemetry-card">
            <div class="telemetry-label">SST Depr.</div>
            <div class="telemetry-val" style="color:#38BDF8;">{c_sst:.1f}&deg;C</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="telemetry-card">
            <div class="telemetry-label">Chl-a Peak</div>
            <div class="telemetry-val" style="color:#34D399;">{c_chl:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="telemetry-card">
            <div class="telemetry-label">Wind Vec.</div>
            <div class="telemetry-val" style="color:#FACC15;">{c_wind:.1f}</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="telemetry-card">
            <div class="telemetry-label">Z-Sigma</div>
            <div class="telemetry-val" style="color:{tier_color};">+{c_z:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

with col_analysis:
    st.markdown("<div style=\"font-size:0.8rem; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; color:#94A3B8; margin-bottom:8px; font-family:'JetBrains Mono';\">Multi-Agent Reasoning Core</div>", unsafe_allow_html=True)
    
    run_button = st.button("RUN DISTRIBUTED DELIBERATION PIPELINE", use_container_width=True, type="primary")
    
    if run_button or "current_event_id" not in st.session_state or st.session_state.current_event_id != telemetry.event_id:
        st.session_state.current_event_id = telemetry.event_id
        
        with st.status("Executing Multi-Agent Telemetry Ingestion...", expanded=True) as status_box:
            st.write("Node 1: Physical Oceanographer verifying wind stress divergence and isotherm shoaling...")
            hydro_report = run_hydrodynamic_agent(telemetry)
            
            st.write("Node 2: Marine Biogeochemist modeling bloom taxa senescence and BOD consumption...")
            bio_report = run_biogeochemical_agent(telemetry, hydro_report)
            
            st.write("Node 3: Tactical Operations Synthesizer computing tier directives and NavIC S-band frame...")
            tactical_report = run_synthesizer_agent(telemetry, hydro_report, bio_report)
            
            status_box.update(label="Deliberation Sequence Finalized &bull; Consensus Achieved", state="complete", expanded=False)
            
            st.session_state.hydro = hydro_report
            st.session_state.bio = bio_report
            st.session_state.tactical = tactical_report

    if "tactical" in st.session_state:
        hydro = st.session_state.hydro
        bio = st.session_state.bio
        tactical = st.session_state.tactical
        
        st.markdown(f"""
        <div class="agent-box" style="border-left: 3px solid #0284C7;">
            <div class="agent-header">
                <span class="agent-title" style="color: #38BDF8;">Node 1 &bull; Physical Oceanographer</span>
                <span class="agent-badge" style="color: #38BDF8;">CONFIDENCE: {hydro.physical_confidence_score * 100:.0f}%</span>
            </div>
            <div class="agent-row"><strong>Upwelling Signature:</strong> {"Active Dynamic Divergence" if hydro.upwelling_detected else "Quiescent / Stratified"}</div>
            <div class="agent-row"><strong>Ekman Transport Mechanics:</strong> {hydro.ekman_transport_assessment}</div>
            <div class="agent-row"><strong>Thermocline Vertical Displacement:</strong> {hydro.thermocline_dynamics}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="agent-box" style="border-left: 3px solid #059669;">
            <div class="agent-header">
                <span class="agent-title" style="color: #34D399;">Node 2 &bull; Marine Biogeochemist</span>
                <span class="agent-badge" style="color: #F43F5E; border-color: #881337;">HYPOXIA TIER: {bio.hypoxia_risk_level}</span>
            </div>
            <div class="agent-row"><strong>Dominant Bloom Taxa:</strong> <em>{bio.primary_taxa_identified}</em></div>
            <div class="agent-row"><strong>BOD Remineralization Trajectory:</strong> {bio.bod_trajectory}</div>
            <div class="agent-row"><strong>Biogeochemical Threat Summary:</strong> {bio.ecological_threat_narrative}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="agent-box" style="border-left: 3px solid #E11D48;">
            <div class="agent-header">
                <span class="agent-title" style="color: #FB7185;">Node 3 &bull; Crisis Operations Synthesizer</span>
                <span class="agent-badge" style="color: #FB7185; border-color: #881337;">{tactical.alert_tier}</span>
            </div>
            <div class="agent-row"><strong>Designated Sector:</strong> {tactical.target_geography}</div>
            <div class="agent-row" style="margin-top: 8px;"><strong>Tactical Directives:</strong></div>
        </div>
        """, unsafe_allow_html=True)
        
        for directive in tactical.operational_directives:
            st.markdown(f"""
            <div style="font-size:0.82rem; color:#CBD5E1; padding-left:14px; margin-bottom:5px; border-left:2px solid #334155;">
                &bull; {directive}
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown(f"""
        <div class="downlink-terminal">
            <div class="downlink-title">NavIC S-Band Telemetry Downlink Payload (240-Bit Frame)</div>
            <div class="downlink-payload">{tactical.navic_hex_payload}</div>
        </div>
        """, unsafe_allow_html=True)

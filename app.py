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

st.set_page_config(page_title="ORCA Tactical Oceanic Sentry", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url("https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;600;700&display=swap");
    * { font-family: "Inter", sans-serif; }
    code, .mono { font-family: "JetBrains Mono", monospace !important; }
    .stApp { background-color: #040813; color: #D1D5DB; }
    .orca-nav {
        background: #0A1324; border: 1px solid #16263D; border-top: 3px solid #00E5FF;
        border-radius: 4px; padding: 14px 20px; margin-bottom: 20px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .status-badge {
        font-family: "JetBrains Mono", monospace; font-size: 0.72rem; padding: 4px 10px;
        background: rgba(0, 229, 255, 0.08); border: 1px solid rgba(0, 229, 255, 0.3);
        border-radius: 2px; color: #00E5FF; letter-spacing: 1px;
    }
    .telemetry-card {
        background: #070F1E; border: 1px solid #132238; border-radius: 3px;
        padding: 10px 12px; margin-bottom: 8px;
    }
    .telemetry-label { font-size: 0.68rem; letter-spacing: 1.2px; text-transform: uppercase; color: #64748B; font-family: "JetBrains Mono"; }
    .telemetry-val { font-size: 1.2rem; font-weight: 700; font-family: "JetBrains Mono"; margin-top: 2px; }
    .agent-box {
        background: #08101F; border: 1px solid #14233A; border-radius: 3px;
        padding: 14px; margin-bottom: 12px;
    }
    .agent-header {
        display: flex; justify-content: space-between; align-items: center;
        border-bottom: 1px solid #122035; padding-bottom: 8px; margin-bottom: 10px;
    }
    .downlink-terminal {
        background: #02050B; border: 1px solid #13243C; border-left: 3px solid #00E5FF;
        border-radius: 2px; padding: 12px 14px; margin-top: 10px;
    }
    .downlink-payload { font-family: "JetBrains Mono"; font-size: 0.9rem; color: #00E5FF; letter-spacing: 2px; word-break: break-all; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="orca-nav">
    <div>
        <div style="font-size:1.1rem; font-weight:700; letter-spacing:2px; color:#F8FAFC;">PROJECT ORCA &bull; NAVAL OCEANIC SENTRY</div>
        <div style="font-size:0.75rem; color:#64748B; letter-spacing:1px; margin-top:2px;">AUTONOMOUS MULTI-AGENT BIOGEOCHEMICAL & PHYSICAL DISASTER NETWORK</div>
    </div>
    <div class="status-badge">SENTINEL TELEMETRY ONLINE</div>
</div>
""", unsafe_allow_html=True)

presets = {
    "Malabar Upwelling Zone (Arabian Sea)": {"lat": 11.25, "lon": 74.80, "sst": 25.8, "chl": 9.85, "wind": 8.2, "z": 3.42},
    "Gulf of Mannar Biological Sanctuary (Bay of Bengal)": {"lat": 8.95, "lon": 79.15, "sst": 29.4, "chl": 4.12, "wind": 5.1, "z": 2.18},
    "Konkan Basin Shelf (Central Arabian Sea)": {"lat": 15.50, "lon": 73.65, "sst": 28.1, "chl": 1.45, "wind": 3.4, "z": 0.85},
    "Manual Spatial Coordinate Ingestion": {"lat": 12.00, "lon": 75.00, "sst": 26.0, "chl": 6.50, "wind": 7.0, "z": 2.80}
}

selected_preset = st.sidebar.selectbox("Observation Domain", list(presets.keys()))
p = presets[selected_preset]

if selected_preset == "Manual Spatial Coordinate Ingestion":
    c_lat = st.sidebar.number_input("Latitude (N)", 5.0, 25.0, p["lat"], 0.05)
    c_lon = st.sidebar.number_input("Longitude (E)", 65.0, 90.0, p["lon"], 0.05)
    c_sst = st.sidebar.slider("SST (C)", 20.0, 34.0, p["sst"], 0.1)
    c_chl = st.sidebar.slider("Chlorophyll-a (mg/m3)", 0.1, 25.0, p["chl"], 0.1)
    c_wind = st.sidebar.slider("Wind Velocity (m/s)", 0.0, 25.0, p["wind"], 0.1)
    c_z = st.sidebar.slider("Anomaly Significance (Sigma)", 0.0, 5.0, p["z"], 0.05)
else:
    c_lat, c_lon, c_sst, c_chl, c_wind, c_z = p["lat"], p["lon"], p["sst"], p["chl"], p["wind"], p["z"]

telemetry = AnomalyDetectionEvent(
    event_id=f"ORCA-2026-T-{int(c_lat*100)}", center_lat=c_lat, center_lon=c_lon,
    peak_chlorophyll=c_chl, mean_sst=c_sst, wind_speed=c_wind, z_score=c_z
)

col_map, col_analysis = st.columns([5, 6], gap="large")

with col_map:
    st.markdown("<div style="font-size:0.75rem; font-weight:700; letter-spacing:1px; color:#94A3B8; margin-bottom:8px; font-family:monospace;">GEOSPATIAL TACTICAL PROJECTION</div>", unsafe_allow_html=True)
    tactical_map = folium.Map(
        location=[c_lat, c_lon], zoom_start=7,
        tiles="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
        attr="CARTO", control_scale=False
    )
    tier_color = "#FF3366" if c_z >= 3.0 else ("#FFB020" if c_z >= 1.5 else "#00E5FF")
    folium.Circle(location=[c_lat, c_lon], radius=40000, color=tier_color, weight=1.5, fill=True, fill_color=tier_color, fill_opacity=0.25).add_to(tactical_map)
    folium.CircleMarker(location=[c_lat, c_lon], radius=5, color="#FFFFFF", weight=2, fill=True, fill_color=tier_color, fill_opacity=1.0).add_to(tactical_map)
    st_folium(tactical_map, height=430, use_container_width=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f"<div class="telemetry-card"><div class="telemetry-label">SST</div><div class="telemetry-val" style="color:#38BDF8;">{c_sst:.1f}&deg;C</div></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class="telemetry-card"><div class="telemetry-label">Chl-a</div><div class="telemetry-val" style="color:#34D399;">{c_chl:.2f}</div></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class="telemetry-card"><div class="telemetry-label">Wind</div><div class="telemetry-val" style="color:#FACC15;">{c_wind:.1f}</div></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class="telemetry-card"><div class="telemetry-label">Z-Sigma</div><div class="telemetry-val" style="color:{tier_color};">+{c_z:.2f}</div></div>", unsafe_allow_html=True)

with col_analysis:
    st.markdown("<div style="font-size:0.75rem; font-weight:700; letter-spacing:1px; color:#94A3B8; margin-bottom:8px; font-family:monospace;">MULTI-AGENT REASONING CORE</div>", unsafe_allow_html=True)
    run_btn = st.button("RUN DISTRIBUTED DELIBERATION PIPELINE", use_container_width=True, type="primary")

    if run_btn or "event_id" not in st.session_state or st.session_state.event_id != telemetry.event_id:
        st.session_state.event_id = telemetry.event_id
        with st.status("Executing Multi-Agent Telemetry Ingestion...", expanded=True) as status_box:
            st.write("Node 1: Physical Oceanographer verifying wind stress and isotherm shoaling...")
            hydro = run_hydrodynamic_agent(telemetry)
            st.write("Node 2: Marine Biogeochemist modeling bloom taxa senescence and BOD consumption...")
            bio = run_biogeochemical_agent(telemetry, hydro)
            st.write("Node 3: Tactical Synthesizer computing operational directives and NavIC S-band frame...")
            tactical = run_synthesizer_agent(telemetry, hydro, bio)
            status_box.update(label="Deliberation Sequence Finalized", state="complete", expanded=False)
            st.session_state.hydro = hydro
            st.session_state.bio = bio
            st.session_state.tactical = tactical

    if "tactical" in st.session_state:
        hydro, bio, tactical = st.session_state.hydro, st.session_state.bio, st.session_state.tactical
        st.markdown(f"""
        <div class="agent-box" style="border-left: 3px solid #0284C7;">
            <div class="agent-header">
                <span style="font-size:0.8rem; font-weight:700; color:#38BDF8; font-family:monospace;">NODE 1 &bull; PHYSICAL OCEANOGRAPHER</span>
                <span style="font-size:0.7rem; color:#38BDF8; font-family:monospace;">CONFIDENCE: {hydro.physical_confidence_score * 100:.0f}%</span>
            </div>
            <div style="font-size:0.85rem; color:#CBD5E1; margin-bottom:4px;"><b>Upwelling:</b> {"Active Dynamic Divergence" if hydro.upwelling_detected else "Quiescent"}</div>
            <div style="font-size:0.85rem; color:#94A3B8; margin-bottom:4px;"><b>Ekman:</b> {hydro.ekman_transport_assessment}</div>
            <div style="font-size:0.85rem; color:#94A3B8;"><b>Thermocline:</b> {hydro.thermocline_dynamics}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="agent-box" style="border-left: 3px solid #059669;">
            <div class="agent-header">
                <span style="font-size:0.8rem; font-weight:700; color:#34D399; font-family:monospace;">NODE 2 &bull; MARINE BIOGEOCHEMIST</span>
                <span style="font-size:0.7rem; color:#F43F5E; font-family:monospace;">HYPOXIA: {bio.hypoxia_risk_level}</span>
            </div>
            <div style="font-size:0.85rem; color:#CBD5E1; margin-bottom:4px;"><b>Suspected Taxa:</b> <em>{bio.primary_taxa_identified}</em></div>
            <div style="font-size:0.85rem; color:#94A3B8; margin-bottom:4px;"><b>BOD Trajectory:</b> {bio.bod_trajectory}</div>
            <div style="font-size:0.85rem; color:#94A3B8;"><b>Threat Narrative:</b> {bio.ecological_threat_narrative}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="agent-box" style="border-left: 3px solid #E11D48;">
            <div class="agent-header">
                <span style="font-size:0.8rem; font-weight:700; color:#FB7185; font-family:monospace;">NODE 3 &bull; CRISIS OPERATIONS SYNTHESIZER</span>
                <span style="font-size:0.7rem; color:#FB7185; font-family:monospace;">{tactical.alert_tier}</span>
            </div>
            <div style="font-size:0.85rem; color:#CBD5E1; margin-bottom:6px;"><b>Target Sector:</b> {tactical.target_geography}</div>
        </div>
        """, unsafe_allow_html=True)

        for d in tactical.operational_directives:
            st.markdown(f"<div style="font-size:0.82rem; color:#CBD5E1; margin-left:12px; margin-bottom:4px;">&bull; {d}</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="downlink-terminal">
            <div style="font-size:0.68rem; color:#64748B; font-family:monospace; margin-bottom:4px;">NAVIC S-BAND TELEMETRY DOWNLINK (240-BIT FRAME)</div>
            <div class="downlink-payload">{tactical.navic_hex_payload}</div>
        </div>
        """, unsafe_allow_html=True)
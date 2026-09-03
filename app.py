import streamlit as st
import folium
from streamlit_folium import st_folium
import json

from engine import generate_mock_satellite_raster, run_anomaly_detector
from agents import hydrodynamic_agent, biogeochemist_agent, disaster_synthesizer_agent

st.set_page_config(page_title="ORCA - Marine Ecosystem Sentry", layout="wide")

# CSS to remove top header clipping and optimize margins
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("ORCA: Marine EcoSystem Reasoning Platform")
st.caption("Distributed Multi-Agent Architecture for Space-to-Sea Ecological Disaster Early Warning")

# Sidebar Controls
st.sidebar.header("Mission Control")
region = st.sidebar.selectbox("Observation Zone", ["South-Eastern Arabian Sea (Malabar Shelf)"])
threshold = st.sidebar.slider("Anomaly Z-Score Sensitivity Threshold", min_value=1.5, max_value=4.0, value=2.5, step=0.1)

col_map, col_stream = st.columns([1.2, 1])

# Run Ingestion & Anomaly Detection Pipeline
raster = generate_mock_satellite_raster()
packet = run_anomaly_detector(raster, threshold_z=threshold)

with col_map:
    st.subheader("Spatial Telemetry & Sensor Layer")
    
    # High-resolution Esri Satellite base map without API key restrictions
    m = folium.Map(
        location=[12.0, 74.5],
        zoom_start=7,
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery"
    )
    
    if packet and packet.detected:
        # Hotspot polygon indicator
        folium.Circle(
            location=[packet.center_lat, packet.center_lon],
            radius=35000,
            color="#ff3333",
            fill=True,
            fill_color="#ff3333",
            fill_opacity=0.35,
            tooltip=(
                f"Anomaly Cluster\n"
                f"Lat: {packet.center_lat}N, Lon: {packet.center_lon}E\n"
                f"Chl-a: {packet.peak_chlorophyll} mg/m3\n"
                f"SST: {packet.mean_sst} C"
            )
        ).add_to(m)

        folium.Marker(
            location=[packet.center_lat, packet.center_lon],
            popup=f"Epicenter: {packet.peak_chlorophyll} mg/m3 Chl-a"
        ).add_to(m)
        
    st_folium(m, width=700, height=450)

    # Metrics strip below map
    if packet:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Peak Chl-a", f"{packet.peak_chlorophyll} mg/m3", delta=f"Z={packet.z_score}")
        m2.metric("Mean SST", f"{packet.mean_sst} C", delta="-2.8 C", delta_color="inverse")
        m3.metric("Wind Stress", f"{packet.wind_divergence} m/s", delta="Offshore")
        m4.metric("Status", "Triggered", delta_color="normal")

with col_stream:
    st.subheader("Autonomous Multi-Agent Consensus Stream")
    
    if packet and packet.detected:
        state = {
            "telemetry": packet,
            "oceanographer_report": "",
            "biogeochemist_report": "",
            "advisory_consensus": {}
        }
        
        with st.status("Agents deliberating over spatial telemetry...", expanded=True) as status:
            st.write("**Orbital Perception Agent:** Anomaly vector bounded and broadcasted.")
            
            # Hydrodynamic Agent
            state.update(hydrodynamic_agent(state))
            st.write(f"**Hydrodynamic Oceanographer:** {state['oceanographer_report']}")
            
            # Biogeochemist Agent
            state.update(biogeochemist_agent(state))
            st.write(f"**Marine Biogeochemist:** {state['biogeochemist_report']}")
            
            # Synthesizer Agent
            state.update(disaster_synthesizer_agent(state))
            status.update(label="Consensus achieved. Actionable bulletin generated.", state="complete")
            
        bulletin = state["advisory_consensus"]
        
        st.error(bulletin['alert_level'])
        st.markdown(f"**Target Coordinates:** `{bulletin['coordinates']}`")
        st.markdown(f"**Primary Hazard:** *{bulletin['primary_hazard']}*")
        
        with st.expander("Tactical Directives for Maritime Stakeholders", expanded=True):
            for directive in bulletin["actionable_directives"]:
                st.markdown(f"- {directive}")

        # Direct NavIC broadcast simulation
        with st.expander("Simulated NavIC 240-bit S-Band Emergency Frame"):
            hex_payload = f"0xORCA_{int(packet.center_lat*100):04X}{int(packet.center_lon*100):04X}_CRIT_HYPOXIA"
            st.code(hex_payload, language="text")
    else:
        st.info("No significant marine anomaly detected at the current threshold.")

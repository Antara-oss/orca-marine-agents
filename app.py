import streamlit as st
import folium
from streamlit_folium import st_folium
from schemas import AnomalyDetectionEvent
from agent_core import (
    run_hydrodynamic_agent,
    run_biogeochemical_agent,
    run_synthesizer_agent,
    LAST_RUN_STATUS,
)

st.set_page_config(page_title="ORCA Oceanic Sentry", layout="wide")

st.title("PROJECT ORCA • NAVAL OCEANIC SENTRY")
st.caption("AUTONOMOUS MULTI-AGENT BIOGEOCHEMICAL & PHYSICAL DISASTER NETWORK")

presets = {
    "Malabar Upwelling Zone": {
        "lat": 11.25,
        "lon": 74.80,
        "sst": 25.8,
        "chl": 9.85,
        "wind": 8.2,
        "z": 3.42,
    },
    "Gulf of Mannar": {
        "lat": 8.95,
        "lon": 79.15,
        "sst": 29.4,
        "chl": 4.12,
        "wind": 5.1,
        "z": 2.18,
    },
    "Konkan Basin": {
        "lat": 15.50,
        "lon": 73.65,
        "sst": 28.1,
        "chl": 1.45,
        "wind": 3.4,
        "z": 0.85,
    },
    "Manual Injection": {
        "lat": 12.00,
        "lon": 75.00,
        "sst": 26.0,
        "chl": 6.50,
        "wind": 7.0,
        "z": 2.80,
    },
}

selected = st.sidebar.selectbox("Observation Sector", list(presets.keys()))
p = presets[selected]

if selected == "Manual Injection":
    c_lat = st.sidebar.number_input("Lat (N)", 5.0, 25.0, p["lat"], 0.05)
    c_lon = st.sidebar.number_input("Lon (E)", 65.0, 90.0, p["lon"], 0.05)
    c_sst = st.sidebar.slider("SST (C)", 20.0, 34.0, p["sst"], 0.1)
    c_chl = st.sidebar.slider("Chl-a (mg/m3)", 0.1, 25.0, p["chl"], 0.1)
    c_wind = st.sidebar.slider("Wind (m/s)", 0.0, 25.0, p["wind"], 0.1)
    c_z = st.sidebar.slider("Z-Score", 0.0, 5.0, p["z"], 0.05)
else:
    c_lat, c_lon, c_sst, c_chl, c_wind, c_z = (
        p["lat"],
        p["lon"],
        p["sst"],
        p["chl"],
        p["wind"],
        p["z"],
    )

telemetry = AnomalyDetectionEvent(
    event_id=f"ORCA-2026-T-{int(c_lat * 100)}",
    center_lat=c_lat,
    center_lon=c_lon,
    peak_chlorophyll=c_chl,
    mean_sst=c_sst,
    wind_speed=c_wind,
    z_score=c_z,
)

col1, col2 = st.columns([5, 6], gap="large")

with col1:
    st.subheader("Geospatial Tactical Projection")
    tactical_map = folium.Map(
        location=[c_lat, c_lon], zoom_start=7, tiles="OpenStreetMap"
    )
    t_color = "red" if c_z >= 3.0 else ("orange" if c_z >= 1.5 else "blue")
    folium.Circle(
        location=[c_lat, c_lon],
        radius=40000,
        color=t_color,
        fill=True,
        fill_opacity=0.3,
    ).add_to(tactical_map)
    folium.Marker(location=[c_lat, c_lon], tooltip=telemetry.event_id).add_to(tactical_map)
    st_folium(tactical_map, height=380, use_container_width=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("SST", f"{c_sst:.1f} °C")
    m2.metric("Chl-a", f"{c_chl:.2f} mg/m³")
    m3.metric("Wind", f"{c_wind:.1f} m/s")
    m4.metric("Z-Score", f"{c_z:.2f}")

with col2:
    st.subheader("Multi-Agent Deliberation Pipeline")
    run_btn = st.button(
        "RUN MULTI-AGENT PIPELINE", use_container_width=True, type="primary"
    )

    if run_btn:
        try:
            with st.status("Executing Multi-Agent Orchestration...", expanded=True) as s:
                st.write("Node 1: Physical Oceanographer evaluating Ekman transport & upwelling...")
                hydro = run_hydrodynamic_agent(telemetry)

                st.write("Node 2: Biogeochemist modeling bloom taxonomy & hypoxia trajectory...")
                bio = run_biogeochemical_agent(telemetry, hydro)

                st.write("Node 3: Operations Synthesizer compiling tactical directives & NavIC hex payload...")
                tactical = run_synthesizer_agent(telemetry, hydro, bio)

                s.update(label="Consensus Finalized", state="complete", expanded=False)

            st.session_state.hydro = hydro
            st.session_state.bio = bio
            st.session_state.tactical = tactical
            st.session_state.run_status = dict(LAST_RUN_STATUS)

        except Exception as e:
            st.error(f"Pipeline orchestration error: {e}")
            st.caption("Inspect 'Manage app → Logs' for stack trace.")

    if "tactical" in st.session_state:
        hydro = st.session_state.hydro
        bio = st.session_state.bio
        tactical = st.session_state.tactical
        run_status = st.session_state.get("run_status", {})

        if any(v.get("source") == "fallback" for v in run_status.values()):
            with st.expander("⚠️ Heuristic Fallback Invocation Notice", expanded=True):
                st.caption(
                    "One or more agents operated via deterministic heuristic logic due to upstream API constraints:"
                )
                for node, info in run_status.items():
                    src = info.get("source", "unknown").upper()
                    err = info.get("error")
                    st.write(f"- **{node.title()} Agent**: `{src}`" + (f" (Reason: `{err}`)" if err else ""))

        with st.expander("Node 1: Physical Oceanographer", expanded=True):
            st.write(f"**Upwelling:** {'Active' if hydro.upwelling_detected else 'Quiescent'}")
            st.write(f"**Ekman Transport:** {hydro.ekman_transport_assessment}")
            st.write(f"**Thermocline:** {hydro.thermocline_dynamics}")
            st.caption(f"Physical Confidence: {hydro.physical_confidence_score * 100:.0f}%")

        with st.expander("Node 2: Marine Biogeochemist", expanded=True):
            st.write(f"**Taxa:** *{bio.primary_taxa_identified}*")
            st.write(f"**Hypoxia Risk:** {bio.hypoxia_risk_level}")
            st.write(f"**BOD Trajectory:** {bio.bod_trajectory}")
            st.caption(f"Ecological Assessment: {bio.ecological_threat_narrative}")

        with st.expander("Node 3: Tactical Advisory Bulletin", expanded=True):
            st.error(f"Alert Tier: {tactical.alert_tier}")
            st.write(f"**Target Sector:** {tactical.target_geography}")
            st.write("**Operational Directives:**")
            for directive in tactical.operational_directives:
                st.write(f"- {directive}")
            st.write("**NavIC S-Band Payload (240-Bit Frame):**")
            st.code(tactical.navic_hex_payload, language="text")

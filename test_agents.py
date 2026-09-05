import warnings
warnings.filterwarnings("ignore")

from schemas import AnomalyDetectionEvent
from agent_core import (
    run_hydrodynamic_agent,
    run_biogeochemical_agent,
    run_synthesizer_agent,
)

test_telemetry = AnomalyDetectionEvent(
    event_id="ORCA-2026-AS-001",
    center_lat=11.25,
    center_lon=74.80,
    peak_chlorophyll=9.85,
    mean_sst=25.8,
    wind_speed=8.2,
    z_score=3.42,
)

print("\n" + "="*50)
print(">>> NODE 1: HYDRODYNAMIC AGENT")
print("="*50)
hydro_report = run_hydrodynamic_agent(test_telemetry)
print(f"Upwelling Confirmed: {hydro_report.upwelling_detected}")
print(f"Confidence Score:    {hydro_report.physical_confidence_score}")
print(f"Ekman Dynamics:      {hydro_report.ekman_transport_assessment}")
print(f"Thermocline:         {hydro_report.thermocline_dynamics}")

print("\n" + "="*50)
print(">>> NODE 2: BIOGEOCHEMICAL AGENT")
print("="*50)
bio_report = run_biogeochemical_agent(test_telemetry, hydro_report)
print(f"Suspected Taxa:      {bio_report.primary_taxa_identified}")
print(f"Hypoxia Risk:        {bio_report.hypoxia_risk_level}")
print(f"BOD Trajectory:        {bio_report.bod_trajectory}")
print(f"Threat Narrative:    {bio_report.ecological_threat_narrative}")

print("\n" + "="*50)
print(">>> NODE 3: TACTICAL SYNTHESIZER AGENT")
print("="*50)
tactical = run_synthesizer_agent(test_telemetry, hydro_report, bio_report)
print(f"Alert Level:         {tactical.alert_tier}")
print(f"Target Sector:       {tactical.target_geography}")
print("Directives:")
for act in tactical.operational_directives:
    print(f"  • {act}")
print(f"NavIC S-Band Frame:  {tactical.navic_hex_payload}\n")

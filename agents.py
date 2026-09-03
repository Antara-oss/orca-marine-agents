# agents.py
from typing import TypedDict, List
from pydantic import BaseModel
from engine import AnomalyPacket, generate_mock_satellite_raster, run_anomaly_detector

# Define shared blackboard state
class MultiAgentState(TypedDict):
    telemetry: AnomalyPacket
    oceanographer_report: str
    biogeochemist_report: str
    advisory_consensus: dict

# Agent 1: Hydrodynamic Oceanographer Agent
def hydrodynamic_agent(state: MultiAgentState) -> dict:
    telemetry = state["telemetry"]
    sst_val = telemetry.mean_sst
    wind_val = telemetry.wind_divergence
    
    # Physics deduction rule
    if sst_val < 27.0 and wind_val > 8.0:
        diagnosis = (
            f"Active wind-driven coastal upwelling confirmed at {telemetry.center_lat}N, {telemetry.center_lon}E. "
            f"Thermal depression to {sst_val}°C indicates sub-surface thermocline shoaling bringing deep nutrients."
        )
    else:
        diagnosis = "Thermal anomalies remain within standard convective limits. Influx likely anthropogenic/riverine."
    
    return {"oceanographer_report": diagnosis}

# Agent 2: Marine Biogeochemist Agent
def biogeochemist_agent(state: MultiAgentState) -> dict:
    telemetry = state["telemetry"]
    chl = telemetry.peak_chlorophyll
    hydro = state["oceanographer_report"]
    
    # Biogeochemical deduction rule
    if "upwelling" in hydro.lower() and chl > 5.0:
        risk = (
            f"CRITICAL: Chlorophyll-a concentration ({chl} mg/m³) indicates bloom acceleration (likely Noctiluca scintillans "
            f"or diatom outburst). Severe risk of dissolved oxygen crash (hypoxia < 1.5 ml/L) within 48-72h."
        )
    else:
        risk = f"Moderate biomass elevation ({chl} mg/m³). Low immediate asphyxiation risk."
        
    return {"biogeochemist_report": risk}

# Agent 3: Disaster Advisory Synthesizer
def disaster_synthesizer_agent(state: MultiAgentState) -> dict:
    telemetry = state["telemetry"]
    bulletin = {
        "alert_level": "RED - TIER 2 RAPID RESPONSE",
        "coordinates": f"{telemetry.center_lat}°N, {telemetry.center_lon}°E",
        "primary_hazard": "Severe Coastal Hypoxia & Toxic Bloom Expansion",
        "scientific_rationale": f"{state['oceanographer_report']} | {state['biogeochemist_report']}",
        "actionable_directives": [
            "Issue immediate advisory to local fisheries: halt bottom trawling in sector.",
            "Alert INCOIS and State Pollution Control Board for water sampling at 5m depth.",
            "Broadcast compressed 240-bit hazard packet via NavIC marine messaging."
        ]
    }
    return {"advisory_consensus": bulletin}

if __name__ == "__main__":
    # Test full pipeline end-to-end
    raster = generate_mock_satellite_raster()
    packet = run_anomaly_detector(raster)
    
    if packet:
        print("--- RUNNING AGENTIC WORKFLOW ---")
        state: MultiAgentState = {
            "telemetry": packet,
            "oceanographer_report": "",
            "biogeochemist_report": "",
            "advisory_consensus": {}
        }
        
        # Sequentially simulate the consensus graph
        state.update(hydrodynamic_agent(state))
        state.update(biogeochemist_agent(state))
        state.update(disaster_synthesizer_agent(state))
        
        print("\n[1] Physical Oceanography Evaluation:")
        print(state["oceanographer_report"])
        
        print("\n[2] Biogeochemical Diagnostics:")
        print(state["biogeochemist_report"])
        
        print("\n[3] Synthesized Early-Warning Bulletin:")
        import json
        print(json.dumps(state["advisory_consensus"], indent=2))


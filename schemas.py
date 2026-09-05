from pydantic import BaseModel, Field
from typing import List

class AnomalyDetectionEvent(BaseModel):
    event_id: str
    center_lat: float
    center_lon: float
    peak_chlorophyll: float = Field(description="Max Chlorophyll-a in mg/m³")
    mean_sst: float = Field(description="Mean Sea Surface Temperature in Celsius")
    wind_speed: float = Field(description="Local wind magnitude in m/s")
    z_score: float = Field(description="Calculated spatial statistical anomaly score")

class HydrodynamicReport(BaseModel):
    upwelling_detected: bool = Field(description="Whether physical upwelling is driving the anomaly")
    ekman_transport_assessment: str = Field(description="Assessment of wind stress and offshore water displacement")
    thermocline_dynamics: str = Field(description="State of the pycnocline/thermocline shoaling")
    physical_confidence_score: float = Field(description="Confidence value between 0.0 and 1.0")

class BiogeochemicalReport(BaseModel):
    primary_taxa_identified: str = Field(description="Dominant phytoplankton/algal species suspected")
    hypoxia_risk_level: str = Field(description="CRITICAL, ELEVATED, or NOMINAL")
    bod_trajectory: str = Field(description="Biochemical Oxygen Demand and dissolved oxygen depletion forecast")
    ecological_threat_narrative: str = Field(description="Mechanistic summary of the biological risk")

class TacticalAdvisoryBulletin(BaseModel):
    alert_tier: str = Field(description="Formal alert tier (e.g. TIER-1 RED, TIER-2 AMBER)")
    target_geography: str = Field(description="Maritime sector description and coordinates")
    operational_directives: List[str] = Field(description="Concrete actions for fisheries, ports, and research vessels")
    navic_hex_payload: str = Field(description="Simulated 240-bit hex frame for direct satellite downlink")

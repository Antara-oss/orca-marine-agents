import os
import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
from google import genai
from google.genai import types
from schemas import (
    AnomalyDetectionEvent,
    HydrodynamicReport,
    BiogeochemicalReport,
    TacticalAdvisoryBulletin,
)

load_dotenv()

# 1. Resolve API Key with explicit priority: Streamlit Cloud Secrets -> os.environ
api_key = None
try:
    import streamlit as st
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not api_key:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "CRITICAL: GEMINI_API_KEY not found. Set it in Streamlit Cloud Secrets "
        "or in your local .env file."
    )

# 2. Correct Model Identifier
MODEL_NAME = "gemini-3.6-flash"

client = genai.Client(api_key=api_key)


def run_hydrodynamic_agent(telemetry: AnomalyDetectionEvent) -> HydrodynamicReport:
    sys_instr = (
        "You are a Senior Physical Oceanographer specializing in the Arabian Sea. "
        "Analyze SST depression, wind vectors, and Ekman divergence."
    )
    prompt_str = (
        f"Analyze anomaly at {telemetry.center_lat}N, {telemetry.center_lon}E with "
        f"SST {telemetry.mean_sst}C, Wind {telemetry.wind_speed} m/s, Z-score {telemetry.z_score}."
    )
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt_str,
        config=types.GenerateContentConfig(
            system_instruction=sys_instr,
            response_mime_type="application/json",
            response_schema=HydrodynamicReport,
            temperature=0.1,
        ),
    )
    return HydrodynamicReport.model_validate_json(response.text)


def run_biogeochemical_agent(
    telemetry: AnomalyDetectionEvent, hydro: HydrodynamicReport
) -> BiogeochemicalReport:
    sys_instr = (
        "You are a Marine Biogeochemist. Evaluate taxa, biomass surge, and hypoxia/BOD collapse risk."
    )
    prompt_str = (
        f"Evaluate biological risk for Chl-a {telemetry.peak_chlorophyll} mg/m3, "
        f"Z-score {telemetry.z_score}, Upwelling={hydro.upwelling_detected}, "
        f"Ekman={hydro.ekman_transport_assessment}."
    )
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt_str,
        config=types.GenerateContentConfig(
            system_instruction=sys_instr,
            response_mime_type="application/json",
            response_schema=BiogeochemicalReport,
            temperature=0.1,
        ),
    )
    return BiogeochemicalReport.model_validate_json(response.text)


def run_synthesizer_agent(
    telemetry: AnomalyDetectionEvent,
    hydro: HydrodynamicReport,
    bio: BiogeochemicalReport,
) -> TacticalAdvisoryBulletin:
    sys_instr = (
        "You are the Crisis Operations Synthesizer for ORCA. Issue maritime directives "
        "and a 240-bit NavIC hex payload."
    )
    prompt_str = (
        f"Synthesize tactical bulletin for sector {telemetry.center_lat}N, {telemetry.center_lon}E "
        f"with Taxa={bio.primary_taxa_identified}, Hypoxia={bio.hypoxia_risk_level}."
    )
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt_str,
        config=types.GenerateContentConfig(
            system_instruction=sys_instr,
            response_mime_type="application/json",
            response_schema=TacticalAdvisoryBulletin,
            temperature=0.2,
        ),
    )
    return TacticalAdvisoryBulletin.model_validate_json(response.text)

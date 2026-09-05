import os
import warnings
warnings.filterwarnings('ignore')

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

api_key = os.getenv('GEMINI_API_KEY')
try:
    import streamlit as st
    if 'GEMINI_API_KEY' in st.secrets:
        api_key = st.secrets['GEMINI_API_KEY']
except Exception:
    pass

client = genai.Client(api_key=api_key)

# Production model fallback cascade
MODELS_TO_TRY = ['gemini-2.5-flash', 'gemini-1.5-flash']

def _call_gemini_with_fallback(sys_instr: str, prompt: str, schema):
    last_err = None
    for model_name in MODELS_TO_TRY:
        try:
            return client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=sys_instr,
                    response_mime_type='application/json',
                    response_schema=schema,
                    temperature=0.1,
                ),
            )
        except Exception as e:
            last_err = e
            continue
    raise last_err

def run_hydrodynamic_agent(telemetry: AnomalyDetectionEvent) -> HydrodynamicReport:
    sys_instr = 'You are a Senior Physical Oceanographer specializing in the Arabian Sea. Analyze SST depression, wind vectors, and Ekman divergence.'
    prompt_str = f'Analyze anomaly at {telemetry.center_lat}N, {telemetry.center_lon}E with SST {telemetry.mean_sst}C, Wind {telemetry.wind_speed} m/s, Z-score {telemetry.z_score}.'
    response = _call_gemini_with_fallback(sys_instr, prompt_str, HydrodynamicReport)
    return HydrodynamicReport.model_validate_json(response.text)

def run_biogeochemical_agent(telemetry: AnomalyDetectionEvent, hydro: HydrodynamicReport) -> BiogeochemicalReport:
    sys_instr = 'You are a Marine Biogeochemist. Evaluate taxa, biomass surge, and hypoxia/BOD collapse risk.'
    prompt_str = f'Evaluate biological risk for Chl-a {telemetry.peak_chlorophyll} mg/m3, Z-score {telemetry.z_score}, Upwelling={hydro.upwelling_detected}, Ekman={hydro.ekman_transport_assessment}.'
    response = _call_gemini_with_fallback(sys_instr, prompt_str, BiogeochemicalReport)
    return BiogeochemicalReport.model_validate_json(response.text)

def run_synthesizer_agent(telemetry: AnomalyDetectionEvent, hydro: HydrodynamicReport, bio: BiogeochemicalReport) -> TacticalAdvisoryBulletin:
    sys_instr = 'You are the Crisis Operations Synthesizer for ORCA. Issue maritime directives and a 240-bit NavIC hex payload.'
    prompt_str = f'Synthesize tactical bulletin for sector {telemetry.center_lat}N, {telemetry.center_lon}E with Taxa={bio.primary_taxa_identified}, Hypoxia={bio.hypoxia_risk_level}.'
    response = _call_gemini_with_fallback(sys_instr, prompt_str, TacticalAdvisoryBulletin)
    return TacticalAdvisoryBulletin.model_validate_json(response.text)
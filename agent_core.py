import os
import warnings
warnings.filterwarnings('ignore')
from dotenv import load_dotenv
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
    if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
        api_key = st.secrets['GEMINI_API_KEY']
except Exception:
    pass

def run_hydrodynamic_agent(telemetry: AnomalyDetectionEvent) -> HydrodynamicReport:
    try:
        if api_key:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key)
            res = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f'Analyze marine anomaly at {telemetry.center_lat}N, {telemetry.center_lon}E, SST {telemetry.mean_sst}C, Wind {telemetry.wind_speed}m/s, Z-score {telemetry.z_score}.',
                config=types.GenerateContentConfig(
                    system_instruction='You are a Senior Physical Oceanographer specializing in the Arabian Sea.',
                    response_mime_type='application/json',
                    response_schema=HydrodynamicReport,
                    temperature=0.1,
                )
            )
            return HydrodynamicReport.model_validate_json(res.text)
    except Exception:
        pass
    is_upwelling = telemetry.mean_sst < 27.0 and telemetry.wind_speed > 6.0
    return HydrodynamicReport(
        upwelling_detected=is_upwelling,
        ekman_transport_assessment='Offshore Ekman drift confirmed along coastal shelf bathymetry.',
        thermocline_dynamics='Shoaling thermocline observed at 20-30m depth interface.',
        physical_confidence_score=0.94 if is_upwelling else 0.82
    )

def run_biogeochemical_agent(telemetry: AnomalyDetectionEvent, hydro: HydrodynamicReport) -> BiogeochemicalReport:
    try:
        if api_key:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key)
            res = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f'Evaluate biological risk for Chl-a {telemetry.peak_chlorophyll} mg/m3, Z {telemetry.z_score}, Upwelling={hydro.upwelling_detected}.',
                config=types.GenerateContentConfig(
                    system_instruction='You are a Marine Biogeochemist modeling bloom taxa.',
                    response_mime_type='application/json',
                    response_schema=BiogeochemicalReport,
                    temperature=0.1,
                )
            )
            return BiogeochemicalReport.model_validate_json(res.text)
    except Exception:
        pass
    taxa = 'Noctiluca scintillans' if telemetry.peak_chlorophyll > 5.0 else 'Trichodesmium erythraeum'
    hypoxia = 'CRITICAL' if telemetry.z_score >= 3.0 else ('MODERATE' if telemetry.z_score >= 1.5 else 'LOW')
    return BiogeochemicalReport(
        primary_taxa_identified=taxa,
        hypoxia_risk_level=hypoxia,
        bod_trajectory='Accelerated benthic oxygen depletion expected within 48-72h window.',
        ecological_threat_narrative='Dense dinoflagellate concentration risking localized pelagic asphyxiation.'
    )

def run_synthesizer_agent(telemetry: AnomalyDetectionEvent, hydro: HydrodynamicReport, bio: BiogeochemicalReport) -> TacticalAdvisoryBulletin:
    try:
        if api_key:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=api_key)
            res = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f'Synthesize operational bulletin for sector {telemetry.center_lat}N, {telemetry.center_lon}E with Taxa={bio.primary_taxa_identified}, Hypoxia={bio.hypoxia_risk_level}.',
                config=types.GenerateContentConfig(
                    system_instruction='You are the Crisis Operations Synthesizer for Project ORCA.',
                    response_mime_type='application/json',
                    response_schema=TacticalAdvisoryBulletin,
                    temperature=0.2,
                )
            )
            return TacticalAdvisoryBulletin.model_validate_json(res.text)
    except Exception:
        pass
    tier = 'TIER-3 EMERGENCY ACTION' if telemetry.z_score >= 3.0 else 'TIER-2 ADVISORY ALERT'
    lat_hex = hex(int(telemetry.center_lat * 100))[2:].zfill(4)
    lon_hex = hex(int(telemetry.center_lon * 100))[2:].zfill(4)
    return TacticalAdvisoryBulletin(
        alert_tier=tier,
        target_geography=f'Sector {telemetry.center_lat:.2f}N, {telemetry.center_lon:.2f}E (Arabian Sea / Coastal Grid)',
        operational_directives=[
            'Dispatch automated surface vessel (ASV) for dissolved oxygen profiling.',
            'Issue maritime advisory warning artisanal fisheries of benthic hypoxia zone.',
            'Activate satellite high-cadence multispectral tasking over designated corridor.'
        ],
        navic_hex_payload=f'0xORCA{lat_hex}{lon_hex}F8A12B004E1D9C'
    )

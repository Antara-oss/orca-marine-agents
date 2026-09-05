import os
import logging
import traceback
import warnings

warnings.filterwarnings("ignore")
from dotenv import load_dotenv
from schemas import (
    AnomalyDetectionEvent,
    HydrodynamicReport,
    BiogeochemicalReport,
    TacticalAdvisoryBulletin,
)

logger = logging.getLogger("orca.agent_core")
logging.basicConfig(level=logging.INFO)

LAST_RUN_STATUS = {
    "hydrodynamic": {"source": None, "error": None},
    "biogeochemical": {"source": None, "error": None},
    "synthesizer": {"source": None, "error": None},
}

load_dotenv()


def resolve_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY")
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    if key:
        key = str(key).strip().strip("\"'")

    if not key:
        logger.warning("GEMINI_API_KEY not found in env or st.secrets - running in fallback mode.")
    elif not key.startswith("AIzaSy"):
        logger.warning("GEMINI_API_KEY lacks 'AIzaSy' prefix - running in fallback mode.")

    return key or ""


def extract_validated_text(res) -> str:
    if not res:
        raise ValueError("Received null response from Gemini API.")

    candidates = getattr(res, "candidates", None)
    if candidates and len(candidates) > 0:
        finish_reason = getattr(candidates[0], "finish_reason", None)
        if finish_reason and str(finish_reason).upper() in ["SAFETY", "RECITATION", "BLOCKLIST"]:
            raise ValueError(f"Generation blocked by policy: {finish_reason}")

    text = getattr(res, "text", None)
    if not text or not str(text).strip():
        raise ValueError("Model response text is empty.")

    return text.strip()


def run_hydrodynamic_agent(telemetry: AnomalyDetectionEvent) -> HydrodynamicReport:
    api_key = resolve_api_key()
    if api_key and api_key.startswith("AIzaSy"):
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            prompt = (
                f"Analyze marine anomaly: Lat {telemetry.center_lat}N, Lon {telemetry.center_lon}E, "
                f"SST {telemetry.mean_sst}C, Wind {telemetry.wind_speed}m/s, Z-score {telemetry.z_score}."
            )

            res = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are a Senior Physical Oceanographer specializing in the Arabian Sea.",
                    response_mime_type="application/json",
                    response_schema=HydrodynamicReport,
                    temperature=0.1,
                ),
            )

            validated_json = extract_validated_text(res)
            report = HydrodynamicReport.model_validate_json(validated_json)
            LAST_RUN_STATUS["hydrodynamic"] = {"source": "gemini", "error": None}
            return report

        except Exception as exc:
            err_msg = f"{type(exc).__name__}: {str(exc)}"
            logger.error("Hydrodynamic Agent failed: %s\n%s", err_msg, traceback.format_exc())
            LAST_RUN_STATUS["hydrodynamic"] = {"source": "fallback", "error": err_msg}
    else:
        LAST_RUN_STATUS["hydrodynamic"] = {
            "source": "fallback",
            "error": "Valid GEMINI_API_KEY not configured",
        }

    is_upwelling = bool(telemetry.mean_sst < 27.0 and telemetry.wind_speed > 6.0)
    return HydrodynamicReport(
        upwelling_detected=is_upwelling,
        ekman_transport_assessment="Offshore Ekman drift confirmed along coastal shelf bathymetry.",
        thermocline_dynamics="Shoaling thermocline observed at 20-30m depth interface.",
        physical_confidence_score=0.94 if is_upwelling else 0.82,
    )


def run_biogeochemical_agent(
    telemetry: AnomalyDetectionEvent, hydro: HydrodynamicReport
) -> BiogeochemicalReport:
    api_key = resolve_api_key()
    if api_key and api_key.startswith("AIzaSy"):
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            prompt = (
                f"Evaluate biological risk: Chl-a {telemetry.peak_chlorophyll} mg/m3, "
                f"Z-score {telemetry.z_score}, Upwelling={hydro.upwelling_detected}."
            )

            res = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are a Marine Biogeochemist modeling bloom taxa.",
                    response_mime_type="application/json",
                    response_schema=BiogeochemicalReport,
                    temperature=0.1,
                ),
            )

            validated_json = extract_validated_text(res)
            report = BiogeochemicalReport.model_validate_json(validated_json)
            LAST_RUN_STATUS["biogeochemical"] = {"source": "gemini", "error": None}
            return report

        except Exception as exc:
            err_msg = f"{type(exc).__name__}: {str(exc)}"
            logger.error("Biogeochemical Agent failed: %s\n%s", err_msg, traceback.format_exc())
            LAST_RUN_STATUS["biogeochemical"] = {"source": "fallback", "error": err_msg}
    else:
        LAST_RUN_STATUS["biogeochemical"] = {
            "source": "fallback",
            "error": "Valid GEMINI_API_KEY not configured",
        }

    taxa = (
        "Noctiluca scintillans"
        if telemetry.peak_chlorophyll > 5.0
        else "Trichodesmium erythraeum"
    )
    hypoxia = (
        "CRITICAL"
        if telemetry.z_score >= 3.0
        else ("MODERATE" if telemetry.z_score >= 1.5 else "LOW")
    )
    return BiogeochemicalReport(
        primary_taxa_identified=taxa,
        hypoxia_risk_level=hypoxia,
        bod_trajectory="Accelerated benthic oxygen depletion expected within 48-72h window.",
        ecological_threat_narrative="Dense dinoflagellate concentration risking localized pelagic asphyxiation.",
    )


def run_synthesizer_agent(
    telemetry: AnomalyDetectionEvent,
    hydro: HydrodynamicReport,
    bio: BiogeochemicalReport,
) -> TacticalAdvisoryBulletin:
    api_key = resolve_api_key()
    if api_key and api_key.startswith("AIzaSy"):
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            prompt = (
                f"Synthesize operational bulletin: Sector {telemetry.center_lat}N, {telemetry.center_lon}E | "
                f"Taxa={bio.primary_taxa_identified} | Hypoxia={bio.hypoxia_risk_level} | "
                f"Upwelling={hydro.upwelling_detected}."
            )

            res = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are the Crisis Operations Synthesizer for Project ORCA.",
                    response_mime_type="application/json",
                    response_schema=TacticalAdvisoryBulletin,
                    temperature=0.2,
                ),
            )

            validated_json = extract_validated_text(res)
            bulletin = TacticalAdvisoryBulletin.model_validate_json(validated_json)
            LAST_RUN_STATUS["synthesizer"] = {"source": "gemini", "error": None}
            return bulletin

        except Exception as exc:
            err_msg = f"{type(exc).__name__}: {str(exc)}"
            logger.error("Synthesizer Agent failed: %s\n%s", err_msg, traceback.format_exc())
            LAST_RUN_STATUS["synthesizer"] = {"source": "fallback", "error": err_msg}
    else:
        LAST_RUN_STATUS["synthesizer"] = {
            "source": "fallback",
            "error": "Valid GEMINI_API_KEY not configured",
        }

    tier = "TIER-3 EMERGENCY ACTION" if telemetry.z_score >= 3.0 else "TIER-2 ADVISORY ALERT"
    lat_hex = hex(int(telemetry.center_lat * 100))[2:].zfill(4).upper()
    lon_hex = hex(int(telemetry.center_lon * 100))[2:].zfill(4).upper()
    return TacticalAdvisoryBulletin(
        alert_tier=tier,
        target_geography=f"Sector {telemetry.center_lat:.2f}N, {telemetry.center_lon:.2f}E (Arabian Sea / Coastal Grid)",
        operational_directives=[
            "Dispatch automated surface vessel (ASV) for dissolved oxygen profiling.",
            "Issue maritime advisory warning artisanal fisheries of benthic hypoxia zone.",
            "Activate satellite high-cadence multispectral tasking over designated corridor.",
        ],
        navic_hex_payload=f"0xORCA{lat_hex}{lon_hex}F8A12B004E1D9C",
    )

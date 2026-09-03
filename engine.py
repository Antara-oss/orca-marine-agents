# engine.py
import numpy as np
import xarray as xr
from pydantic import BaseModel
from typing import Optional

class AnomalyPacket(BaseModel):
    detected: bool
    center_lat: float
    center_lon: float
    peak_chlorophyll: float
    mean_sst: float
    wind_divergence: float
    z_score: float

def generate_mock_satellite_raster() -> xr.Dataset:
    """Generates a synthetic 2D ocean raster simulating Oceansat-3/MODIS telemetry."""
    lats = np.linspace(10.0, 14.0, 40)
    lons = np.linspace(73.0, 76.0, 30)
    
    # Baseline normal marine background
    np.random.seed(42)
    chl_a = np.random.normal(loc=0.8, scale=0.2, size=(len(lats), len(lons)))
    sst = np.random.normal(loc=29.0, scale=0.5, size=(len(lats), len(lons)))
    wind = np.random.normal(loc=4.5, scale=1.0, size=(len(lats), len(lons)))
    
    # Inject a localized algal bloom / upwelling anomaly at index (20, 15) -> ~ 12.0 N, 74.5 E
    chl_a[18:23, 13:18] += 7.5   # Massive Chlorophyll spike
    sst[18:23, 13:18] -= 2.8     # Localized cold upwelling plume
    wind[18:23, 13:18] += 5.2    # Strong offshore wind stress

    ds = xr.Dataset(
        data_vars={
            "chlorophyll": (("lat", "lon"), chl_a),
            "sst": (("lat", "lon"), sst),
            "wind_speed": (("lat", "lon"), wind),
        },
        coords={"lat": lats, "lon": lons}
    )
    return ds

def run_anomaly_detector(ds: xr.Dataset, threshold_z: float = 2.5) -> Optional[AnomalyPacket]:
    """Applies a spatial Z-score filter to identify anomalous ocean bounding cells."""
    chl = ds["chlorophyll"].values
    mean_val = np.mean(chl)
    std_val = np.std(chl)
    z_scores = (chl - mean_val) / std_val
    
    max_idx = np.unravel_index(np.argmax(z_scores), z_scores.shape)
    peak_z = float(z_scores[max_idx])
    
    if peak_z >= threshold_z:
        target_lat = float(ds["lat"].values[max_idx[0]])
        target_lon = float(ds["lon"].values[max_idx[1]])
        
        return AnomalyPacket(
            detected=True,
            center_lat=round(target_lat, 2),
            center_lon=round(target_lon, 2),
            peak_chlorophyll=round(float(chl[max_idx]), 2),
            mean_sst=round(float(ds["sst"].values[max_idx]), 2),
            wind_divergence=round(float(ds["wind_speed"].values[max_idx]), 2),
            z_score=round(peak_z, 2)
        )
    return None

if __name__ == "__main__":
    ds = generate_mock_satellite_raster()
    anomaly = run_anomaly_detector(ds)
    print("Edge Ingestion Test Result:", anomaly)

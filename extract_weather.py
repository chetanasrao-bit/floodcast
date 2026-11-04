from pathlib import Path
import pandas as pd
import xarray as xr
import numpy as np
import h5py

RAW = Path("data/raw")
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)

discharge = pd.read_csv(
    OUT / "discharge_clean.csv",
    parse_dates=["date"]
)

stations = discharge[
    ["station_id", "latitude", "longitude"]
].drop_duplicates("station_id")

print("Stations:", len(stations))


def extract_grid(file, variable):
    with h5py.File(file, "r") as h:
        group = list(h.keys())[0]

    ds = xr.open_dataset(file, group=group)

    results = []

    for _, station in stations.iterrows():
        lat = station["latitude"]
        lon = station["longitude"]

        # Nearest grid cell
        point = ds[variable].sel(
            lat=lat,
            lon=lon,
            method="nearest"
        )

        values = point.to_series().reset_index()
        values.columns = ["date", variable]

        values["station_id"] = station["station_id"]
        values["date"] = pd.to_datetime(values["date"]).dt.normalize()

        results.append(values)

    ds.close()

    return pd.concat(results, ignore_index=True)


# ---------------- RAINFALL ----------------

rain_files = sorted(RAW.glob("*.nc"))

rain_frames = []

for file in rain_files:
    with h5py.File(file, "r") as h:
        group = list(h.keys())[0]

    if group != "rain":
        continue

    print("Extracting rainfall:", file.name)

    rain = extract_grid(file, "rain")
    rain_frames.append(rain)

rainfall = pd.concat(rain_frames, ignore_index=True)

rainfall = rainfall.drop_duplicates(
    ["station_id", "date"],
    keep="last"
)

rainfall.to_csv(
    OUT / "rainfall_station_daily.csv",
    index=False
)

print("Rainfall saved:", len(rainfall))


# ---------------- TEMPERATURE ----------------

temp_frames = []

for file in rain_files:
    with h5py.File(file, "r") as h:
        group = list(h.keys())[0]

    if group not in ["tmin", "tmax"]:
        continue

    print("Extracting temperature:", file.name)

    temp = extract_grid(file, group)
    temp_frames.append(temp)

temperature = pd.concat(temp_frames, ignore_index=True)

temperature = temperature.drop_duplicates(
    ["station_id", "date"],
    keep="last"
)

temperature.to_csv(
    OUT / "temperature_station_daily.csv",
    index=False
)

print("Temperature saved:", len(temperature))
print("WEATHER EXTRACTION COMPLETE")
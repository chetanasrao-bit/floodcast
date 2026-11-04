from pathlib import Path
import pandas as pd
import numpy as np

RAW = Path("data/raw")
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)

frames = []

for file in RAW.glob("river_discharge*.csv"):
    print("Reading:", file.name)

    df = pd.read_csv(file, low_memory=False)
    df.columns = df.columns.str.strip()

    # Identify columns dynamically
    discharge_col = next(
        (c for c in df.columns if "discharge" in c.lower()),
        None
    )

    date_col = next(
        (c for c in df.columns
         if "acquisition time" in c.lower()
         or c.lower() == "date"
         or "timestamp" in c.lower()),
        None
    )

    lat_col = next(
        (c for c in df.columns if "latitude" in c.lower()),
        None
    )

    lon_col = next(
        (c for c in df.columns if "longitude" in c.lower()),
        None
    )

    if not all([discharge_col, date_col, lat_col, lon_col]):
        print("Skipping: required columns missing")
        print(df.columns.tolist())
        continue

    station_col = next(
        (c for c in df.columns
         if "station" in c.lower()
         or "site" in c.lower()),
        None
    )

    state_col = next(
        (c for c in df.columns if c.lower() == "state"),
        None
    )

    district_col = next(
        (c for c in df.columns if "district" in c.lower()),
        None
    )

    part = pd.DataFrame()

    part["station"] = (
        df[station_col].astype(str)
        if station_col else file.stem
    )

    part["state"] = (
        df[state_col].astype(str)
        if state_col else "Unknown"
    )

    part["district"] = (
        df[district_col].astype(str)
        if district_col else "Unknown"
    )

    part["latitude"] = pd.to_numeric(
        df[lat_col], errors="coerce"
    )

    part["longitude"] = pd.to_numeric(
        df[lon_col], errors="coerce"
    )

    part["date"] = pd.to_datetime(
        df[date_col],
        dayfirst=True,
        errors="coerce"
    ).dt.normalize()

    part["discharge"] = pd.to_numeric(
        df[discharge_col], errors="coerce"
    )

    part = part.dropna(
        subset=["date", "latitude", "longitude", "discharge"]
    )

    part = part[
        (part["discharge"] >= 0)
        & part["latitude"].between(6, 38)
        & part["longitude"].between(65, 100)
    ]

    frames.append(part)

if not frames:
    raise ValueError("No discharge files were successfully processed.")

data = pd.concat(frames, ignore_index=True)

data["station_id"] = (
    data["station"].astype(str).str.strip()
    + "_"
    + data["latitude"].round(3).astype(str)
    + "_"
    + data["longitude"].round(3).astype(str)
)

data = data.drop_duplicates(
    subset=["station_id", "date"],
    keep="last"
)

data.to_csv(
    OUT / "discharge_clean.csv",
    index=False
)

print("\nDischarge cleaned!")
print("Rows:", len(data))
print("Stations:", data["station_id"].nunique())
print("Date range:", data["date"].min(), data["date"].max())
print("Saved:", OUT / "discharge_clean.csv")
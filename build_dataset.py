from pathlib import Path
import pandas as pd

DATA = Path("data/processed")

flow = pd.read_csv(
    DATA / "discharge_clean.csv",
    parse_dates=["date"]
)

rain = pd.read_csv(
    DATA / "rainfall_station_daily.csv",
    parse_dates=["date"]
)

temp = pd.read_csv(
    DATA / "temperature_station_daily.csv",
    parse_dates=["date"]
)

# Merge weather with discharge
df = flow.merge(
    rain[["station_id", "date", "rain"]],
    on=["station_id", "date"],
    how="left"
)

df = df.merge(
    temp[["station_id", "date", "tmin", "tmax"]],
    on=["station_id", "date"],
    how="left"
)

df = df.sort_values(["station_id", "date"])

# Missing rainfall -> zero only if truly no rainfall data?
# Keep missing as missing for now
df["rain"] = df["rain"].fillna(0)

# Lagged flow
df["flow_lag1"] = df.groupby("station_id")["discharge"].shift(1)
df["flow_lag2"] = df.groupby("station_id")["discharge"].shift(2)
df["flow_lag3"] = df.groupby("station_id")["discharge"].shift(3)

# Rainfall accumulation
df["rain_3day"] = (
    df.groupby("station_id")["rain"]
    .transform(lambda x: x.rolling(3).sum())
)

df["rain_7day"] = (
    df.groupby("station_id")["rain"]
    .transform(lambda x: x.rolling(7).sum())
)

# Predict next day's discharge
df["target_next_day"] = (
    df.groupby("station_id")["discharge"].shift(-1)
)

# Remove rows without necessary features
df = df.dropna(
    subset=[
        "flow_lag1",
        "flow_lag2",
        "flow_lag3",
        "rain_3day",
        "rain_7day",
        "target_next_day"
    ]
)

df.to_csv(DATA / "training_dataset.csv", index=False)

print("Training dataset created!")
print("Rows:", len(df))
print("Stations:", df["station_id"].nunique())
print("Date range:", df["date"].min(), df["date"].max())
print(df.head())
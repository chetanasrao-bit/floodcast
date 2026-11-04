from pathlib import Path
import pandas as pd
import xarray as xr

RAW = Path("data/raw")
REPORT = Path("reports/data_inspection.txt")

REPORT.parent.mkdir(exist_ok=True)

with open(REPORT, "w", encoding="utf-8") as f:

    def log(*args):
        text = " ".join(map(str, args))
        print(text)
        f.write(text + "\n")

    for file in sorted(RAW.iterdir()):
        if not file.is_file():
            continue

        log("\n" + "=" * 70)
        log("FILE:", file.name)

        try:
            if file.suffix.lower() == ".nc":
                ds = xr.open_dataset(file)

                log("DIMENSIONS:", ds.sizes)
                log("VARIABLES:")

                for var in ds.data_vars:
                    log(
                        var,
                        ds[var].dims,
                        ds[var].shape,
                        ds[var].attrs.get("units"),
                        ds[var].attrs.get("long_name")
                    )

                log("COORDINATES:")
                for coord in ds.coords:
                    log(coord, ds[coord].values.flatten()[:5])

                ds.close()

            elif file.suffix.lower() == ".csv":
                df = pd.read_csv(file)

                log("SHAPE:", df.shape)
                log("COLUMNS:", df.columns.tolist())
                log("DTYPES:")
                log(df.dtypes)
                log("SAMPLE:")
                log(df.head().to_string())
                log("MISSING:")
                log(df.isna().sum().to_string())

        except Exception as e:
            log("ERROR:", e)

print("\nInspection complete!")
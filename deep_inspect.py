from pathlib import Path
import xarray as xr
import pandas as pd
import h5py
import os

RAW = Path("data/raw")
REPORT = Path("reports/deep_inspection.txt")

REPORT.parent.mkdir(exist_ok=True)

with open(REPORT, "w", encoding="utf-8") as report:

    def log(*args):
        text = " ".join(map(str, args))
        print(text)
        report.write(text + "\n")

    # ----------------------------------------
    # NETCDF INSPECTION
    # ----------------------------------------

    for file in RAW.glob("*.nc"):

        log("\n" + "=" * 90)
        log("NETCDF:", file.name)
        log("SIZE MB:", round(file.stat().st_size / 1024**2, 3))

        # HDF5 structure
        try:
            with h5py.File(file, "r") as h:
                log("\nHDF5 ROOT KEYS:", list(h.keys()))

                def show_hdf(name, obj):
                    if isinstance(obj, h5py.Dataset):
                        log(
                            "HDF5 DATASET:", name,
                            "SHAPE:", obj.shape,
                            "DTYPE:", obj.dtype
                        )

                h.visititems(show_hdf)

        except Exception as e:
            log("HDF5 ERROR:", e)

        # Try different NetCDF engines
        for engine in ["netcdf4", "h5netcdf", "scipy"]:

            try:
                ds = xr.open_dataset(file, engine=engine)

                log("\nENGINE:", engine)
                log("DIMENSIONS:", ds.sizes)
                log("VARIABLES:", list(ds.data_vars))
                log("COORDINATES:", list(ds.coords))
                log("GLOBAL ATTRIBUTES:", ds.attrs)

                for var in ds.variables:

                    da = ds[var]

                    log("\nVARIABLE:", var)
                    log("DIMS:", da.dims)
                    log("SHAPE:", da.shape)
                    log("DTYPE:", da.dtype)
                    log("ATTRS:", da.attrs)

                    if da.size > 0 and da.size < 10000000:
                        try:
                            log("SAMPLE:", da.values.flatten()[:10])
                        except Exception as e:
                            log("VALUE ERROR:", e)

                ds.close()
                break

            except Exception as e:
                log("ENGINE ERROR", engine, e)

    # ----------------------------------------
    # SOIL MOISTURE INSPECTION
    # ----------------------------------------

    soil_files = list(RAW.glob("*Soilmoisture*.csv"))

    for file in soil_files:

        log("\n" + "=" * 90)
        log("SOIL FILE:", file.name)

        log("\nFIRST 15 RAW LINES:")

        with open(file, encoding="utf-8", errors="replace") as f:
            for i in range(15):
                line = f.readline()
                log(i, repr(line))

        for skip in [0, 4, 5, 6]:

            try:
                df = pd.read_csv(file, skiprows=skip)

                log("\nSKIPROWS:", skip)
                log("SHAPE:", df.shape)
                log("COLUMNS:", df.columns.tolist())
                log("SAMPLE:")
                log(df.head(10).to_string())

            except Exception as e:
                log("CSV ERROR:", e)

print("\nDeep inspection complete!")
print("Report:", REPORT)
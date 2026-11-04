from pathlib import Path
import h5py
import xarray as xr

RAW = Path("data/raw")

for file in RAW.glob("*.nc"):
    print("\n" + "=" * 80)
    print("FILE:", file.name)

    # Automatically detect the internal NetCDF group
    with h5py.File(file, "r") as h:
        group = list(h.keys())[0]

    print("GROUP:", group)

    ds = xr.open_dataset(file, group=group)

    print(ds)
    print("Variables:", list(ds.data_vars))
    print("Dimensions:", dict(ds.sizes))

    print("Latitude:", ds["lat"].values.min(),
          ds["lat"].values.max())

    print("Longitude:", ds["lon"].values.min(),
          ds["lon"].values.max())

    print("Time range:",
          ds["time"].values[0],
          "to",
          ds["time"].values[-1])

    variable = group

    print("Units:", ds[variable].attrs.get("units"))
    print("First values:",
          ds[variable].isel(time=0).values.flatten()[:10])

    ds.close()

print("\nINSPECTION COMPLETE")
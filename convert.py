import xarray as xr
import pandas as pd
import glob
import os

files = glob.glob("**/*.nc", recursive=True)

print(f"Found {len(files)} NC files")

for file in files:
    print(f"\nConverting: {file}")

    try:
        ds = xr.open_dataset(file)

        # Handle datasets with dimensions
        if len(ds.dims) > 0:
            df = ds.to_dataframe().reset_index()

        # Handle datasets containing only scalar values
        else:
            data = {}

            for name, var in ds.variables.items():
                data[name] = var.values.item()

            df = pd.DataFrame([data])

        # Save CSV beside original NC file
        output = os.path.splitext(file)[0] + ".csv"

        df.to_csv(output, index=False)

        print(f"SUCCESS: {output}")
        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")

        ds.close()

    except Exception as e:
        print(f"ERROR in {file}: {e}")

print("\nConversion process finished!")
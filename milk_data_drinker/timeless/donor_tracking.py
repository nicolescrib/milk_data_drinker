import logging
import os
import pandas as pd

from ._normalizer import normalize, normalize_columns, split_id_name

# The raw report has two columns both named "Donor/Milk Bank":
# the first is the donor ID+name, the second is the deposit count.
# After normalize_columns(), pandas' auto-renamed duplicate becomes "donor_milk_bank_1".
_COLUMN_RENAMES = {
    "donor_milk_bank_1": "deposit_count",
}


def read_file(file_path: str) -> pd.DataFrame:
    filename = os.path.basename(file_path)
    logging.info(f"Processing donor tracking report: {filename}")

    df = normalize(file_path)
    df = normalize_columns(df)
    df = df.rename(columns=_COLUMN_RENAMES)

    # "Donor/Milk Bank" contains "DON012345 : Lastname, Firstname" in real exports
    if "donor_milk_bank" in df.columns:
        df["donor_id"], df["donor_name"] = split_id_name(df["donor_milk_bank"])
        df = df.drop(columns=["donor_milk_bank"])

    if "total_received_volume_ml" in df.columns:
        df["total_received_volume_ml"] = pd.to_numeric(
            df["total_received_volume_ml"].astype(str).str.replace(",", "", regex=False),
            errors="coerce",
        )

    front = [c for c in ["donor_id", "donor_name"] if c in df.columns]
    df = df[front + [c for c in df.columns if c not in front]]

    logging.info(f"Extracted {len(df)} rows from {filename}")
    return df

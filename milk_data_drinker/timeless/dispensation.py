import logging
import os
import pandas as pd

from ._normalizer import normalize, normalize_columns, split_id_name

# Timeless appends 4 summary/total rows at the end of every dispensation export
_SUMMARY_ROWS = 4
_DATE_COLS = ["dispense_date", "date_cancelled"]


def read_file(file_path: str) -> pd.DataFrame:
    filename = os.path.basename(file_path)
    logging.info(f"Processing dispensation report: {filename}")

    df = normalize(file_path)
    df = df.iloc[:-_SUMMARY_ROWS].reset_index(drop=True)
    df = normalize_columns(df)

    # "Recipient" contains "PAT012345:Lastname, Firstname" for patients;
    # hospital recipients are bare IDs ("HOS000078") with no name part
    if "recipient" in df.columns:
        df["recipient_id"], df["recipient_name"] = split_id_name(df["recipient"])
        df = df.drop(columns=["recipient"])

    for col in _DATE_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    front = [c for c in ["recipient_id", "recipient_name"] if c in df.columns]
    df = df[front + [c for c in df.columns if c not in front]]

    logging.info(f"Extracted {len(df)} rows from {filename}")
    return df

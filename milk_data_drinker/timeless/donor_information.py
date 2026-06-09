import logging
import os
import pandas as pd

from ._normalizer import normalize, normalize_columns


def read_file(file_path: str) -> pd.DataFrame:
    filename = os.path.basename(file_path)
    logging.info(f"Processing donor information report: {filename}")

    df = normalize(file_path)
    df = normalize_columns(df)

    for col in df.columns:
        if "date" in col:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    logging.info(f"Extracted {len(df)} rows from {filename}")
    return df

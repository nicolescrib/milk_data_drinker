import logging
import os
import pandas as pd

from .._utils import clean_column_names


def read_file(file_path: str) -> pd.DataFrame:
    """
    Read a timeless report file (HTML-as-XLS, XLSX, or CSV).
    Tries HTML parse first to handle disguised web exports, then Excel, then CSV.
    Returns a normalized DataFrame with clean column names.
    """
    filename = os.path.basename(file_path)
    logging.info(f"Processing timeless report: {filename}")

    for strategy in (_try_html, _try_excel, _try_csv):
        df = strategy(file_path)
        if df is not None:
            result = clean_column_names(df)
            logging.info(f"Extracted {len(result)} rows from {filename}")
            return result

    raise ValueError(f"Could not read timeless report with any available parser: {file_path}")


def _try_html(file_path: str) -> pd.DataFrame | None:
    try:
        tables = pd.read_html(file_path)
        if not tables:
            return None
        df = max(tables, key=lambda t: len(t))
        # HTML exports from Timeless sometimes use integer column indices instead of headers
        if all(isinstance(c, int) for c in df.columns):
            df.columns = df.iloc[0]
            df = df.iloc[1:].reset_index(drop=True)
        return df
    except Exception:
        return None


def _try_excel(file_path: str) -> pd.DataFrame | None:
    try:
        return pd.read_excel(file_path)
    except Exception:
        return None


def _try_csv(file_path: str) -> pd.DataFrame | None:
    try:
        return pd.read_csv(file_path, encoding="latin1")
    except Exception:
        return None

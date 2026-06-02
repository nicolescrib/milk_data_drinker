import csv
import logging
import os
import re
import pandas as pd
from io import StringIO

from .milk_reader import SampleReader


def read_file(file_path: str) -> pd.DataFrame:
    """Read a lactoscope .xls, .xlsx, or .csv file. Returns a DataFrame."""
    filename = os.path.basename(file_path)
    logging.info(f"Processing: {filename}")

    if file_path.endswith('.xls') or file_path.endswith('.xlsx'):
        csv_content = _xls_to_csv_string(file_path)
    else:
        with open(file_path, 'r') as f:
            csv_content = f.read()

    return _parse_csv_content(csv_content, filename)


def _xls_to_csv_string(path: str) -> str:
    df_raw = pd.read_excel(path, header=None)
    first_data_row = 0
    for i in range(min(10, len(df_raw))):
        if df_raw.iloc[i].notna().any():
            first_data_row = i
            break
    if first_data_row > 0:
        df_raw = df_raw.iloc[first_data_row:].reset_index(drop=True)
    buf = StringIO()
    df_raw.to_csv(buf, index=False, header=False)
    return buf.getvalue()


def _parse_csv_content(csv_content: str, filename: str) -> pd.DataFrame:
    lines = csv_content.split('\n')
    first_data_line = next((i for i, line in enumerate(lines) if line.strip()), 0)
    if first_data_line > 0:
        logging.debug(f"Skipped {first_data_line} blank row(s) at start of {filename}")
        csv_content = '\n'.join(lines[first_data_line:])

    reader = SampleReader(csv.reader(StringIO(csv_content)))
    frames = []

    while not reader.end_of_file:
        df = reader.read_sample()
        if not df.empty:
            df['source_file'] = filename
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
            frames.append(df)

    if not frames:
        logging.warning(f"No data extracted from {filename}")
        return pd.DataFrame()

    result = pd.concat(frames, ignore_index=True)
    result = _clean_column_names(result)
    result = _standardize_name_column(result)
    logging.info(f"Extracted {len(result)} records from {filename}")
    return result


def _clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    clean = {}
    for col in df.columns:
        c = col.replace(' ', '_').replace(',', '_').replace(';', '_')
        c = c.replace('(', '_').replace(')', '_').replace('\n', '_')
        c = c.replace('\t', '_').replace('=', '_').replace('{', '_').replace('}', '_')
        while '__' in c:
            c = c.replace('__', '_')
        clean[col] = c.strip('_')
    return df.rename(columns=clean)


def _standardize_name_column(df: pd.DataFrame) -> pd.DataFrame:
    def extract_dep_id(name):
        if pd.isna(name):
            return None
        match = re.search(r'(DEP\s*\d+)', str(name), re.IGNORECASE)
        return match.group(1) if match else None

    def extract_donor_name(name):
        if pd.isna(name):
            return None
        match = re.search(r'DEP\s*\d+\s*-\s*(.+)', str(name), re.IGNORECASE)
        if match:
            donor = match.group(1).strip()
            return donor if donor else None
        return None

    def classify_sample_type(name):
        if pd.isna(name):
            return 'unknown'
        name_lower = str(name).lower().strip()
        if re.search(r'dep\s*\d+', name_lower):
            return 'deposit'
        test_keywords = ['test', 'pilot', 'blank', 'control', 'qc', 'standard',
                         'decon', 'calibration', 'validation', 'check', 'dunn', 'sonicate', 'skimmed']
        if any(kw in name_lower for kw in test_keywords):
            return 'test_control'
        return 'other'

    df['name_original'] = df['Name']
    df['dep_id'] = df['Name'].apply(extract_dep_id)
    df['donor_name'] = df['Name'].apply(extract_donor_name)
    df['sample_type'] = df['Name'].apply(classify_sample_type)
    return df

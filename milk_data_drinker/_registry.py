import logging
import os
from pathlib import Path

import pandas as pd

# Directory name → report type. Checked against every component of the file's path.
_PATH_HINTS = [
    ("Analyzer Reports", "analyzer"),
    ("Dispensation Reports", "dispensation"),
    ("Deposit Record Reports", "deposit_record"),
    ("Donor Tracking Reports", "donor_tracking"),
    ("Donor Approval Reports", "donor_approval"),
    ("Donor Information Reports", "donor_information"),
]

# Substrings to match in the file stem (lowercased, underscores/hyphens → spaces).
_FILENAME_HINTS = [
    ("dispensation", "dispensation"),
    ("deposit record", "deposit_record"),
    ("donor tracking", "donor_tracking"),
    ("donor approval", "donor_approval"),
    ("donor information", "donor_information"),
]

# Column sets that uniquely fingerprint each Timeless report type.
# Used only when path and filename give no match.
_CONTENT_FINGERPRINTS = {
    "dispensation": {"Order Number", "Bottle Size (mL)", "Dispense Date"},
    "deposit_record": {"Deposit", "Expiry Date", "Volume Remaining (mL)"},
    "donor_tracking": {"Total Received Volume (mL)", "Follow Up Dates"},
    "donor_approval": {"Approved Date", "Donor ID"},
    "donor_information": {"Donor Barcode", "Passed Screening"},
}

_SUPPORTED_EXTENSIONS = {".xls", ".xlsx", ".csv"}


def read_file(file_path: str) -> pd.DataFrame:
    """Detect the report type and return a normalized DataFrame."""
    report_type = detect_type(file_path)
    logging.info(f"Detected report type '{report_type}' for {file_path}")
    return _dispatch(report_type, file_path)


def read_directory(root: str) -> dict[str, pd.DataFrame]:
    """
    Walk a directory tree, read every supported report file, and return a dict
    of {report_type: DataFrame} with results from each type concatenated.
    Files whose type cannot be determined are skipped with a warning.
    """
    frames: dict[str, list[pd.DataFrame]] = {}
    for dirpath, _, filenames in os.walk(root):
        for name in sorted(filenames):
            if Path(name).suffix.lower() not in _SUPPORTED_EXTENSIONS:
                continue
            file_path = os.path.join(dirpath, name)
            try:
                report_type = detect_type(file_path)
                df = _dispatch(report_type, file_path)
                frames.setdefault(report_type, []).append(df)
            except Exception as e:
                logging.warning(f"Skipped {file_path}: {e}")
    return {rtype: pd.concat(dfs, ignore_index=True) for rtype, dfs in frames.items()}


def detect_type(file_path: str) -> str:
    """
    Determine report type using three strategies in priority order:
    1. Directory name — folder names are self-explanatory and most reliable.
    2. Filename — Timeless default download names include the report type.
    3. File content — column fingerprinting as a last resort.
    """
    path_parts = Path(os.path.abspath(file_path)).parts
    for hint, report_type in _PATH_HINTS:
        if any(hint in part for part in path_parts):
            return report_type

    stem = Path(file_path).stem.lower().replace("_", " ").replace("-", " ")
    for hint, report_type in _FILENAME_HINTS:
        if hint in stem:
            return report_type

    return _detect_by_content(file_path)


def _detect_by_content(file_path: str) -> str:
    from .timeless._normalizer import normalize
    try:
        df = normalize(file_path)
        cols = set(df.columns)
        for report_type, fingerprint in _CONTENT_FINGERPRINTS.items():
            if fingerprint.issubset(cols):
                return report_type
    except Exception:
        pass
    return "analyzer"


def _dispatch(report_type: str, file_path: str) -> pd.DataFrame:
    if report_type == "analyzer":
        from .analyzer.reader import read_file as _read
        return _read(file_path)
    if report_type == "dispensation":
        from .timeless.dispensation import read_file as _read
        return _read(file_path)
    if report_type == "deposit_record":
        from .timeless.deposit_record import read_file as _read
        return _read(file_path)
    if report_type == "donor_tracking":
        from .timeless.donor_tracking import read_file as _read
        return _read(file_path)
    if report_type == "donor_approval":
        from .timeless.donor_approval import read_file as _read
        return _read(file_path)
    if report_type == "donor_information":
        from .timeless.donor_information import read_file as _read
        return _read(file_path)
    raise ValueError(f"Unknown report type '{report_type}' for {file_path}")

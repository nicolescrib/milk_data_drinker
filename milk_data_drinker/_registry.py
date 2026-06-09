import logging
import pandas as pd


def read_file(file_path: str) -> pd.DataFrame:
    """
    Detect the report type from file content and dispatch to the appropriate reader.
    Returns a normalized DataFrame.
    """
    report_type = detect_type(file_path)
    logging.info(f"Detected report type '{report_type}' for {file_path}")

    if report_type == "timeless":
        from .timeless.normalizer import read_file as _read
        return _read(file_path)

    if report_type == "analyzer":
        from .analyzer.reader import read_file as _read
        return _read(file_path)

    raise ValueError(f"Unknown report type '{report_type}' for {file_path}")


def detect_type(file_path: str) -> str:
    """
    Detect report type from file content.
    HTML parse succeeding indicates a timeless report (Timeless exports HTML tables).
    Falls back to analyzer for CSV/XLS files with the lactoscope chunk structure.
    """
    try:
        tables = pd.read_html(file_path)
        if tables:
            return "timeless"
    except Exception:
        pass

    return "analyzer"

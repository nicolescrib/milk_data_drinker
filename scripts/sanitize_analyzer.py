#!/usr/bin/env python3
"""
Sanitize analyzer report files for use as test fixtures.

Strips donor names from sample name fields, leaving only the DEP ID
(e.g. "DEP041036-Lastname Firstname,,Milk Donors-Raw" → "DEP041036,,Milk Donors-Raw").

XLS/XLSX inputs are converted to CSV on output — CSV is easier to inspect and
sufficient for the parser.

Usage:
    # Single file
    python scripts/sanitize_analyzer.py path/to/report.xls tests/fixtures/

    # Whole directory
    python scripts/sanitize_analyzer.py path/to/reports/ tests/fixtures/
"""

import os
import re
import sys
from io import StringIO

import pandas as pd


# Matches donor name fields in CSV-formatted analyzer output.
# Unquoted:  DEP041036-Lastname Firstname,,Milk Donors-Raw
# CSV-quoted: "DEP035593-Tran, J",,Milk Donors-Raw  (name contains comma → quoted by CSV writer)
# Group 1: optional opening quote + DEP ID (e.g. 'DEP041036' or '"DEP041036') — DEP ID kept, quote stripped
# Group 2: separator + name fragment — stripped
# Group 3: optional closing quote — stripped
# Group 4: CSV column separator commas — kept
# Group 5: "Milk Donors" literal — kept
_NAME_RE = re.compile(
    r'("?DEP\d+)([-\s][^,"\n]+(?:,[^,"\n]+)*)(\"?)(,+)(Milk\s+Donors)',
    re.IGNORECASE,
)


def _read_as_text(input_path: str) -> str:
    ext = os.path.splitext(input_path)[1].lower()
    if ext in ('.xls', '.xlsx'):
        df = pd.read_excel(input_path, header=None)
        buf = StringIO()
        df.to_csv(buf, index=False, header=False)
        return buf.getvalue()
    with open(input_path, encoding='latin1') as f:
        return f.read()


def _strip_names(content: str) -> str:
    # group(1): DEP ID (possibly with leading quote — strip the quote)
    # group(4): CSV column separator commas
    # group(5): "Milk Donors"
    return _NAME_RE.sub(lambda m: f"{m.group(1).lstrip('\"')}{m.group(4)}{m.group(5)}", content)


def sanitize_file(input_path: str, output_dir: str) -> None:
    stem = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, stem + ".csv")

    content = _read_as_text(input_path)
    matches = _NAME_RE.findall(content)

    if not matches:
        print(f"  WARNING: no donor name pattern found in {os.path.basename(input_path)}")
        print("  Expected format: DEP{id}-{name}{,+}Milk Donors-{type}")
        print("  File will be written as-is (check for PII before committing)")

    sanitized = _strip_names(content)

    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(sanitized)

    print(f"  {os.path.basename(input_path)} → {os.path.basename(output_path)} ({len(matches)} donor name(s) stripped)")


def main() -> None:
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    input_path, output_dir = sys.argv[1], sys.argv[2]

    if os.path.isdir(input_path):
        files = [
            os.path.join(input_path, f)
            for f in sorted(os.listdir(input_path))
            if not f.startswith('.') and os.path.isfile(os.path.join(input_path, f))
        ]
        print(f"Sanitizing {len(files)} file(s) from {input_path}")
        for f in files:
            sanitize_file(f, output_dir)
    else:
        print(f"Sanitizing {os.path.basename(input_path)}")
        sanitize_file(input_path, output_dir)

    print(f"\nDone. Review files in {output_dir} before committing.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Sanitize analyzer report files for use as test fixtures.

Replaces donor name fragments in sample name fields with consistent pseudonyms
(Donor_A, Donor_B, ...) while preserving DEP IDs, nutrient values, and dates.

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


# Matches: DEP{id}{separator}{name fragment} Milk Donors
# e.g. "DEP041036-lastnar Milk Donors-Raw"
#      "DEP040955 Jane Smith Milk Donors-Raw"
# Group 1: DEP prefix + separator
# Group 2: name fragment (PII — one or more words, stops before "Milk Donors")
# Group 3: " Milk Donors" suffix
_NAME_RE = re.compile(
    r'(DEP\d+[-\s]+)((?:(?!Milk\s+Donors)\S+\s*)+)(Milk\s+Donors)',
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


def _build_name_map(content: str) -> dict[str, str]:
    """Map each unique name fragment to a stable pseudonym."""
    fragments = sorted({m.group(2).strip() for m in _NAME_RE.finditer(content)})
    return {name: f"Donor_{chr(65 + i)}" for i, name in enumerate(fragments)}


def _apply_name_map(content: str, name_map: dict[str, str]) -> str:
    def replace(m: re.Match) -> str:
        fragment = m.group(2).strip()
        pseudonym = name_map.get(fragment, "Donor_X")
        # Preserve whitespace style from the original (space or dash before name)
        sep = m.group(1)[-1]  # last char of prefix: '-' or ' '
        prefix = m.group(1)[:-1] + sep
        return f"{prefix}{pseudonym} {m.group(3)}"
    return _NAME_RE.sub(replace, content)


def sanitize_file(input_path: str, output_dir: str) -> None:
    stem = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, stem + ".csv")

    content = _read_as_text(input_path)
    name_map = _build_name_map(content)

    if not name_map:
        print(f"  WARNING: no donor name pattern found in {os.path.basename(input_path)}")
        print("  Expected format: DEP{id}-{name} Milk Donors-{type}")
        print("  File will be written as-is (check for PII before committing)")

    sanitized = _apply_name_map(content, name_map)

    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(sanitized)

    print(f"  {os.path.basename(input_path)} → {os.path.basename(output_path)}")
    for original, pseudonym in name_map.items():
        print(f"    '{original}' → '{pseudonym}'")


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

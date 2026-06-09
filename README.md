# milk_data_drinker

Reads Delta Lactoscope and Timeless milk analyzer reports and returns normalized pandas DataFrames. Written for the Northwest Mothers Milk Bank.

## Installation

```bash
pip install -e .
```

## Usage

```python
import milk_data_drinker

df = milk_data_drinker.read_file("path/to/report.xls")
```

`read_file` detects the report type automatically and dispatches to the appropriate reader. It accepts `.xls`, `.xlsx`, and `.csv` files.

### Analyzer (Lactoscope) output columns

| Column | Description |
|---|---|
| `dep_id` | Deposit ID (e.g. `DEP041036`) |
| `date` | Timestamp of the measurement |
| `fat`, `protein`, `lactose`, `nutritive_protein`, `solids`, `calories` | Mean macronutrient values |
| `fat_stddev`, `protein_stddev`, … | Instrument stddev across the three measurement replicates |
| `source_file` | Filename the record came from |

Each row represents one sample. Individual replicates are not included.

## Sanitizing files for test fixtures

Raw analyzer reports contain donor names. Use the sanitizer to strip them before committing files as fixtures:

```bash
# Single file
python scripts/sanitize_analyzer.py path/to/report.xls tests/fixtures/

# Whole directory
python scripts/sanitize_analyzer.py path/to/reports/ tests/fixtures/
```

The sanitizer strips the name fragment from each donor field (e.g. `DEP041036-Lastname Firstname` → `DEP041036`) and converts XLS/XLSX to CSV. Review the output before committing.

## Data

Raw reports with PHI are stored under `data/sensitive/` and are never committed to the repository.

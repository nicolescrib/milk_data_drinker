# milk_data_drinker

Reads Delta Lactoscope analyzer reports and Timeless Medical Milk Bank Management System reports, returning normalized pandas DataFrames. Written for the Northwest Mothers Milk Bank.

## Installation

```bash
pip install -e .
```

## Usage

```python
import milk_data_drinker

# Single file — returns a DataFrame
df = milk_data_drinker.read_file("path/to/report.xls")

# Directory — returns a dict keyed by report type
results = milk_data_drinker.read_directory("path/to/reports/")
# {"dispensation": df, "deposit_record": df, "analyzer": df, ...}
```

Report type is detected automatically: first by directory name, then by filename, then by file content. Supported formats: `.xls`, `.xlsx`, `.csv`.

## Report types and output columns

### Analyzer (Delta Lactoscope)

Each row represents one sample. Individual replicates are not included.

| Column | Description |
|---|---|
| `dep_id` | Deposit ID (e.g. `DEP041036`) |
| `date` | Timestamp of the measurement |
| `fat`, `protein`, `lactose`, `nutritive_protein`, `solids`, `calories` | Mean macronutrient values across replicates |
| `fat_stddev`, `protein_stddev`, … | Instrument stddev across the three measurement replicates |
| `source_file` | Filename the record came from |

### Dispensation Report (Timeless)

Each row represents one bottle-size line item within an order.

| Column | Description |
|---|---|
| `order_number` | Order identifier |
| `recipient` | Patient or hospital ID |
| `recipient_city`, `recipient_region` | Recipient location |
| `batch` | Batch identifier |
| `bottle_size_ml`, `bottle_count`, `bottle_volume_ml` | Bottle size and quantity |
| `state` | Milk bank state |
| `deposit`, `deposit_count`, `deposit_volume_ml` | Associated deposit info |
| `milk_type` | Milk caloric classification (e.g. `20 cal/oz`) |
| `fat`, `protein`, `lactose`, `g_dl` | Nutritional values |
| `dispense_date`, `date_cancelled` | Dispensation dates |
| `order_status` | Current order state |
| `purchase_order` | Associated purchase order |

### Deposit Record Report (Timeless)

Each row represents one milk deposit.

| Column | Description |
|---|---|
| `deposit` | Deposit ID (e.g. `DEP049229`) |
| `donor_id` | Donor ID (e.g. `DON014232`) |
| `donor_warnings` | Any active donor warnings |
| `split_off_from` | Parent deposit if split |
| `location` | Storage location |
| `milk_type` | Term / preterm classification |
| `date_received` | Date deposit was received |
| `expiry_date` | Expiration date |
| `volume_remaining_ml`, `used_volume_ml`, `total_volume_ml` | Volume tracking |
| `donor_approved` | Donor approval status |
| `deposit_state` | Current state of deposit |

### Donor Tracking Report (Timeless)

Each row represents one donor's aggregate donation activity.

| Column | Description |
|---|---|
| `donor_id` | Donor ID (e.g. `DON013650`) |
| `type` | Record type (typically `DONOR`) |
| `total_received_volume_ml` | Total volume donated |
| `deposit_count` | Number of deposits |
| `follow_up_dates` | Follow-up date(s) |

### Donor Approval Report (Timeless)

Each row represents one approved donor.

| Column | Description |
|---|---|
| `donor_id` | Donor ID |
| `approved_date` | Date of approval |
| `city`, `state`, `zip_code` | Donor location |

### Donor Information Report (Timeless)

Comprehensive donor record. Each row represents one donor. Contains many fields — see source report for full column list.

## Directory structure

The module expects reports organized into named subdirectories. Directory names are used as the primary type hint:

```
reports-root/
├── Analyzer Reports/
└── Timeless Reports/
    ├── Dispensation Reports/
    ├── Deposit Record Reports/
    ├── Donor Tracking Reports/
    └── (extensible to other Timeless report types)
```

Files not matched by directory name are identified by filename, then by column fingerprint.

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

Raw reports with PHI are stored under `data/sensitive/` and are never committed to the repository or accesed by agents, LLMs, or AI. Example sanitized reports are in `data/example reports/`.

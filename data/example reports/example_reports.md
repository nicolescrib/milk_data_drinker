# example reports
Notes on example reports. Some reports contain PHI and have been anonymized/sanitized. Those changes are noted here. When developing software that uses these reports, consider the changes that were made to anonymize the data and design for the unsanitized, unanonymized version. Actual reports will not be sanitized before processing.

If HIPAA-protected PHI is present in any of these example reports, stop tasks and alert the user.

## Directory structure
Reports are organized into subdirectories by type. The system should use directory names as hints for report type detection, falling back to filename and then file content.

```
example reports/
├── Analyzer Reports/       # Delta Lactoscope analyzer output
└── Timeless Reports/       # Timeless Medical Milk Bank Management System exports
    ├── Dispensation Reports/
    ├── Deposit Record Reports/
    ├── Donor Tracking Reports/
    └── (other report types as added)
```

Timeless report default download filename: `{report_name}_{date_of_report_run}.xls`
Timeless report renamed convention: `{report_name}_{start_date}_{end_date}.xls`
* Two dates → date range of data
* Single full date → date report was run (not data range)
* Single year or year/month → data for that year or month

---

## Analyzer Report
* Data from Delta Lactoscope Analyzer describing nutritional tests on samples of milk deposits.
* Filename indicates time interval of report (hand typed, subject to error).
    * Interval of time reported on can be inferred from range of dates in data.

Example files: `Analyzer Reports/*`

Sanitization changes:
* Donor names removed using `scripts/sanitize_analyzer.py`

---

## Deposit Record Report
* Record of all milk deposits (individual donations) with volume, location, and state information.
* `"Donor/Milk Bank"` column contains the donor ID.

Example file: `Timeless Reports/deposit_record_report_example_sanitized.csv`

Sanitization changes:
* Converted to .csv
* Donor name was removed from column `"Donor/Milk Bank"`.
    * Original format: `"DON012345 Lastname, Firstname"`
    * Sanitized format: `"DON012345"`

---

## Dispensation Report
* Report of all dispensation to outpatients, hospitals, and other facilities from this milk bank over an interval of time.
    * Interval of time reported on can be inferred from range of dates in `"Dispense Date"` column.
* `"Bottle Volume (mL)"` column is the product of `"Bottle Size (mL)"` and `"Bottle Count"` columns.
    * Dispensation is described per bottle size. Each line describes the quantity of a certain bottle size in an order or purchase order. There may be multiple `"Order Numbers"` in a single `"Purchase Order"`.
* `"Recipient"` column contains a patient or hospital ID. Hospital IDs (e.g. `HOS000078`) are non-patient recipients.
* The file contains a secondary sheet `"hospital_names"` mapping hospital IDs to names. This sheet is reference-only and should be ignored by readers.

Example file: `Timeless Reports/dispensation_report_example_sanitized.xlsx`

Sanitization changes:
* Converted to .xlsx
* Recipient name was removed from column `"Recipient"`.
    * Original format: `"PAT012345:Lastname, Firstname"`
    * Sanitized format: `"PAT012345"`
* Non-patient recipient names were moved to a separate sheet called `"hospital_names"` instead of appearing inline.
* Some purchase orders were selectively cleared from the `"Purchase Order"` column if they contained an obvious name.

---

## Donor Approval Report
* Report of approval dates for donors approved for milk donation within an interval of time.
    * Interval of time reported on can be loosely inferred by the range of dates in the `"Approved Date"` column.
* Useful lightweight report for pairing donor IDs to zip codes, states, or cities.
* **File format note:** The CSV has 5 metadata/header rows before the column header row. Readers must skip rows 0–4 and treat row 5 as the header.

Example file: `Timeless Reports/donor_approval_report_example_sanitized.csv`

Sanitization changes:
* Converted to .csv
* All data was cleared from the `"First Name"`, `"Last Name"`, `"Donor Address"`, `"Baby First Name"`, and `"Baby Last Name"` columns.

---

## Donor Information Report
* Extensive report on all information on donors. Some fields are ephemeral/subject to change, some are permanent.

Example file: `Timeless Reports/donor_information_report_example_sanitized.csv`

Sanitization changes:
* Cleared information from these columns:
    * Donor First Name
    * Donor Last Name
    * Milk Depot Affiliation
    * Home Phone
    * Work Phone
    * Cell Phone
    * Email
    * Address 1
    * Address 2
    * Baby First Name
    * Baby Last Name
    * ZIP Code
    * IMTU Form 1–8
    * Miscellaneous Form 1–2
    * Ethnicity
    * Ethnicity(Others)
    * Education
    * Occupation
    * Employer
    * Partners Occupation
    * Partners Employer
    * Household Income
* Obfuscated information from these columns:
    * Date of Birth
* Included list of milk depots/milk drops as separate sheet named `"milk_drops"`.
* `"IMTU Form 1"` and other `"Form"` fields were strings of filenames that occasionally held donor names.

---

## Donor Tracking Report
* Reports on volumes donated by donors over an interval of time.
    * Report does not indicate interval; rely on filename to understand interval of time reported on.
* **Column note:** The raw file contains two columns both named `"Donor/Milk Bank"`. The first is the donor ID (e.g. `DON013650`); the second is the deposit count (integer). Readers must rename these on import to avoid collision.

Example file: `Timeless Reports/donor_tracking_example_sanitized.csv`

Sanitization changes:
* Donor name was removed from column `"Donor/Milk Bank"`.
    * Original format: `"DON012345 : Lastname, Firstname"`
    * Sanitized format: `"DON012345 "` (note trailing space)

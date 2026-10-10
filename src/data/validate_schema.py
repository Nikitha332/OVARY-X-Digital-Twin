from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "synthetic"

EHR_FILE = DATA_DIR / "ehr_demo.csv"
WEARABLE_FILE = DATA_DIR / "wearable_demo.csv"

EHR_REQUIRED = {
    "patient_id",
    "age",
    "bmi",
    "pcos_status",
    "data_type",
}

WEARABLE_REQUIRED = {
    "patient_id",
    "timestamp",
    "heart_rate",
    "hrv",
    "steps",
    "data_type",
}


def validate_columns(data, required, filename):
    missing = required - set(data.columns)

    if missing:
        raise ValueError(
            f"{filename}: missing columns: {sorted(missing)}"
        )

    if data.empty:
        raise ValueError(f"{filename}: file contains no records.")

    print(f"{filename}: {len(data)} rows; required columns present.")


def main():
    print("OVARY-X data validation")
    print("-----------------------")

    for path in (EHR_FILE, WEARABLE_FILE):
        if not path.exists():
            raise FileNotFoundError(
                f"Required file not found: {path}"
            )

    ehr = pd.read_csv(EHR_FILE, dtype={"patient_id": "string"})
    wearable = pd.read_csv(
        WEARABLE_FILE, dtype={"patient_id": "string"}
    )

    validate_columns(ehr, EHR_REQUIRED, "EHR")
    validate_columns(wearable, WEARABLE_REQUIRED, "Wearable")

    # Check patient IDs.
    for name, data in (("EHR", ehr), ("Wearable", wearable)):
        if data["patient_id"].isna().any() or (
            data["patient_id"].str.strip() == ""
        ).any():
            raise ValueError(f"{name}: missing patient IDs.")

    ehr_ids = set(ehr["patient_id"])
    wearable_ids = set(wearable["patient_id"])
    unmatched_ids = wearable_ids - ehr_ids

    if unmatched_ids:
        raise ValueError(
            f"Wearable IDs missing from EHR: {sorted(unmatched_ids)}"
        )

    print("Patient ID matching: passed.")

    # Check timestamp format.
    timestamps = pd.to_datetime(
        wearable["timestamp"], errors="coerce"
    )

    if timestamps.isna().any():
        raise ValueError("Wearable: invalid or missing timestamps.")

    print("Timestamp validation: passed.")

    # Ensure every row is labelled as synthetic.
    if not (
        ehr["data_type"].eq("SYNTHETIC").all()
        and wearable["data_type"].eq("SYNTHETIC").all()
    ):
        raise ValueError(
            "All demo records must be labelled SYNTHETIC."
        )

    print("Synthetic data labels: passed.")
    print("OVARY-X data validation completed.")


if __name__ == "__main__":
    main()
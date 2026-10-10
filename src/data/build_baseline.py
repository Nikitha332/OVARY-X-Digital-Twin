from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = PROJECT_ROOT / "data" / "synthetic" / "wearable_demo.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "baseline_demo.csv"

MEASUREMENTS = ["heart_rate", "hrv", "steps"]


def main():
    print("OVARY-X personal baseline engine")
    print("--------------------------------")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Wearable input not found: {INPUT_FILE}"
        )

    data = pd.read_csv(
        INPUT_FILE, dtype={"patient_id": "string"}
    )

    required = {
        "patient_id",
        "timestamp",
        *MEASUREMENTS,
        "data_type",
    }

    missing = required - set(data.columns)
    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    if data.empty:
        raise ValueError("No wearable records found.")

    if data["patient_id"].isna().any():
        raise ValueError("Missing patient IDs.")

    if not data["data_type"].eq("SYNTHETIC").all():
        raise ValueError("Expected explicitly synthetic records.")

    data["timestamp"] = pd.to_datetime(
        data["timestamp"], errors="raise"
    )

    for column in MEASUREMENTS:
        data[column] = pd.to_numeric(
            data[column], errors="raise"
        )

    if data[MEASUREMENTS].isna().any().any():
        raise ValueError("Missing measurement values found.")

    # Sort readings before computing each patient's baseline.
    data = data.sort_values(["patient_id", "timestamp"])

    # Calculate per-person reference values from available readings.
    baseline = data.groupby("patient_id").agg(
        baseline_readings=("timestamp", "count"),
        baseline_start=("timestamp", "min"),
        baseline_end=("timestamp", "max"),
        baseline_heart_rate=("heart_rate", "mean"),
        baseline_hrv=("hrv", "mean"),
        baseline_steps=("steps", "mean"),
    ).reset_index()

    # Attach each patient's reference values to their readings.
    tracked = data.merge(
        baseline,
        on="patient_id",
        how="left",
        validate="many_to_one",
    )

    # These are descriptive differences, not clinical risk scores.
    tracked["heart_rate_difference"] = (
        tracked["heart_rate"] - tracked["baseline_heart_rate"]
    )
    tracked["hrv_difference"] = (
        tracked["hrv"] - tracked["baseline_hrv"]
    )
    tracked["steps_difference"] = (
        tracked["steps"] - tracked["baseline_steps"]
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    tracked.to_csv(OUTPUT_FILE, index=False)

    print(f"Patients processed: {baseline['patient_id'].nunique()}")
    print(f"Wearable readings: {len(tracked)}")
    print("Per-person baseline values calculated.")
    print("Reading-to-baseline differences calculated.")
    print(f"Output saved to: {OUTPUT_FILE.relative_to(PROJECT_ROOT)}")
    print("All records remain labelled synthetic.")
    print("Baseline engine completed successfully.")


if __name__ == "__main__":
    main()
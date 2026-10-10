from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "baseline_demo.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "scenario_demo.csv"


def main():
    print("OVARY-X digital-twin scenario engine")
    print("------------------------------------")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Baseline file not found: {INPUT_FILE}"
        )

    data = pd.read_csv(
        INPUT_FILE, dtype={"patient_id": "string"}
    )

    required = {
        "patient_id",
        "baseline_heart_rate",
        "baseline_hrv",
        "baseline_steps",
        "data_type",
    }

    missing = required - set(data.columns)
    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    if data.empty:
        raise ValueError("No baseline records found.")

    if not data["data_type"].eq("SYNTHETIC").all():
        raise ValueError(
            "This demonstration expects synthetic records only."
        )

    # Keep one baseline profile per patient.
    profiles = data.drop_duplicates(
        subset=["patient_id"]
    ).copy()

    for column in (
        "baseline_heart_rate",
        "baseline_hrv",
        "baseline_steps",
    ):
        profiles[column] = pd.to_numeric(
            profiles[column], errors="raise"
        )

    # These are arbitrary engineering test scenarios,
    # not clinical thresholds or medically validated predictions.
    scenarios = [
        {
            "scenario": "Reference baseline",
            "heart_rate_change_bpm": 0.0,
            "hrv_change_percent": 0.0,
            "steps_change_percent": 0.0,
        },
        {
            "scenario": "Illustrative higher heart rate",
            "heart_rate_change_bpm": 10.0,
            "hrv_change_percent": 0.0,
            "steps_change_percent": 0.0,
        },
        {
            "scenario": "Illustrative lower HRV",
            "heart_rate_change_bpm": 0.0,
            "hrv_change_percent": -10.0,
            "steps_change_percent": 0.0,
        },
        {
            "scenario": "Illustrative reduced steps",
            "heart_rate_change_bpm": 0.0,
            "hrv_change_percent": 0.0,
            "steps_change_percent": -20.0,
        },
    ]

    results = []

    for _, profile in profiles.iterrows():
        for scenario in scenarios:
            baseline_hr = profile["baseline_heart_rate"]
            baseline_hrv = profile["baseline_hrv"]
            baseline_steps = profile["baseline_steps"]

            results.append({
                "patient_id": profile["patient_id"],
                "scenario": scenario["scenario"],
                "baseline_heart_rate": baseline_hr,
                "simulated_heart_rate": (
                    baseline_hr
                    + scenario["heart_rate_change_bpm"]
                ),
                "baseline_hrv": baseline_hrv,
                "simulated_hrv": (
                    baseline_hrv
                    * (1 + scenario["hrv_change_percent"] / 100)
                ),
                "baseline_steps": baseline_steps,
                "simulated_steps": (
                    baseline_steps
                    * (1 + scenario["steps_change_percent"] / 100)
                ),
                "data_type": "SYNTHETIC_SIMULATION",
                "clinical_interpretation": (
                    "Not clinically validated; not a risk prediction"
                ),
            })

    output = pd.DataFrame(results)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUTPUT_FILE, index=False)

    print(f"Patient profiles: {len(profiles)}")
    print(f"Scenarios per profile: {len(scenarios)}")
    print(f"Scenario rows generated: {len(output)}")
    print(f"Output saved to: {OUTPUT_FILE.relative_to(PROJECT_ROOT)}")
    print("Scenario engine completed successfully.")
    print("All scenario values are illustrative simulations.")


if __name__ == "__main__":
    main()
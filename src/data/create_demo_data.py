
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "synthetic"


def write_csv(filename, columns, rows):
    path = OUTPUT_DIR / filename

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(rows)

    print(f"Created: {path.relative_to(PROJECT_ROOT)}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Fictional records for software testing only.
    ehr_columns = [
        "patient_id",
        "age",
        "bmi",
        "pcos_status",
        "data_type",
    ]

    ehr_rows = [
        ["SYN001", 24, 27.1, "synthetic_example", "SYNTHETIC"],
        ["SYN002", 29, 31.4, "synthetic_example", "SYNTHETIC"],
    ]

    wearable_columns = [
        "patient_id",
        "timestamp",
        "heart_rate",
        "hrv",
        "steps",
        "data_type",
    ]

    wearable_rows = [
        ["SYN001", "2026-10-10T09:00:00", 76, 48, 1200, "SYNTHETIC"],
        ["SYN001", "2026-10-10T09:05:00", 79, 45, 1350, "SYNTHETIC"],
        ["SYN002", "2026-10-10T09:00:00", 82, 39, 900, "SYNTHETIC"],
        ["SYN002", "2026-10-10T09:05:00", 80, 41, 1050, "SYNTHETIC"],
    ]

    write_csv("ehr_demo.csv", ehr_columns, ehr_rows)
    write_csv("wearable_demo.csv", wearable_columns, wearable_rows)

    print("Synthetic test data generated successfully.")
    print("These records are fictional, not clinical evidence.")


if __name__ == "__main__":
    main()

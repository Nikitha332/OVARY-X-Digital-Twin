import subprocess
import sys
import unittest
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
SYNTHETIC_DIR = DATA_DIR / "synthetic"
PROCESSED_DIR = DATA_DIR / "processed"


def run_script(relative_path):
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / relative_path)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Script failed: {relative_path}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

    return result.stdout


class TestOvaryXPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Rebuild outputs in dependency order.
        run_script("src/data/create_demo_data.py")
        run_script("src/data/validate_schema.py")
        run_script("src/data/fuse_data.py")
        run_script("src/data/build_baseline.py")
        run_script("src/data/scenario_engine.py")

    def test_synthetic_input_files_exist(self):
        self.assertTrue(
            (SYNTHETIC_DIR / "ehr_demo.csv").exists()
        )
        self.assertTrue(
            (SYNTHETIC_DIR / "wearable_demo.csv").exists()
        )

    def test_patient_ids_match(self):
        ehr = pd.read_csv(
            SYNTHETIC_DIR / "ehr_demo.csv",
            dtype={"patient_id": "string"},
        )
        wearable = pd.read_csv(
            SYNTHETIC_DIR / "wearable_demo.csv",
            dtype={"patient_id": "string"},
        )

        self.assertTrue(
            set(wearable["patient_id"]).issubset(
                set(ehr["patient_id"])
            )
        )

    def test_all_demo_records_are_synthetic(self):
        ehr = pd.read_csv(SYNTHETIC_DIR / "ehr_demo.csv")
        wearable = pd.read_csv(
            SYNTHETIC_DIR / "wearable_demo.csv"
        )

        self.assertTrue(ehr["data_type"].eq("SYNTHETIC").all())
        self.assertTrue(
            wearable["data_type"].eq("SYNTHETIC").all()
        )

    def test_fusion_output(self):
        fused = pd.read_csv(
            PROCESSED_DIR / "fused_demo.csv"
        )

        self.assertEqual(len(fused), 2)
        self.assertEqual(fused["patient_id"].nunique(), 2)
        self.assertIn("mean_heart_rate", fused.columns)
        self.assertIn("mean_hrv", fused.columns)

    def test_baseline_output(self):
        baseline = pd.read_csv(
            PROCESSED_DIR / "baseline_demo.csv"
        )

        self.assertEqual(len(baseline), 4)
        self.assertIn("heart_rate_difference", baseline.columns)
        self.assertIn("hrv_difference", baseline.columns)

    def test_scenario_output(self):
        scenarios = pd.read_csv(
            PROCESSED_DIR / "scenario_demo.csv"
        )

        self.assertEqual(len(scenarios), 8)
        self.assertEqual(
            scenarios["patient_id"].nunique(), 2
        )
        self.assertTrue(
            scenarios["data_type"]
            .eq("SYNTHETIC_SIMULATION")
            .all()
        )

    def test_reference_scenario_matches_baseline(self):
        scenarios = pd.read_csv(
            PROCESSED_DIR / "scenario_demo.csv"
        )

        reference = scenarios.loc[
            scenarios["scenario"] == "Reference baseline"
        ]

        self.assertEqual(len(reference), 2)

        for _, row in reference.iterrows():
            self.assertAlmostEqual(
                row["simulated_heart_rate"],
                row["baseline_heart_rate"],
            )
            self.assertAlmostEqual(
                row["simulated_hrv"],
                row["baseline_hrv"],
            )
            self.assertAlmostEqual(
                row["simulated_steps"],
                row["baseline_steps"],
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
SYNTHETIC_DIR = DATA_DIR / "synthetic"
PROCESSED_DIR = DATA_DIR / "processed"

st.set_page_config(
    page_title="OVARY-X | Digital Twin",
    page_icon="🧬",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    ehr = pd.read_csv(
        SYNTHETIC_DIR / "ehr_demo.csv",
        dtype={"patient_id": "string"},
    )
    wearable = pd.read_csv(
        SYNTHETIC_DIR / "wearable_demo.csv",
        dtype={"patient_id": "string"},
    )
    baseline = pd.read_csv(
        PROCESSED_DIR / "baseline_demo.csv",
        dtype={"patient_id": "string"},
    )
    scenarios = pd.read_csv(
        PROCESSED_DIR / "scenario_demo.csv",
        dtype={"patient_id": "string"},
    )

    wearable["timestamp"] = pd.to_datetime(
        wearable["timestamp"], errors="raise"
    )

    return ehr, wearable, baseline, scenarios


st.title("OVARY-X")
st.subheader("Personalized Digital Twin | PCOS Research Prototype")

st.warning(
    "RESEARCH DEMONSTRATION — All current patient records and "
    "scenario outputs are synthetic. This application is not "
    "a medical device, diagnostic tool, or clinically validated "
    "risk-prediction system."
)

try:
    ehr, wearable, baseline, scenarios = load_data()
except FileNotFoundError as error:
    st.error(
        f"Required data file not found: {error.filename or error}"
    )
    st.info(
        "Run the data generator, fusion, baseline, and scenario "
        "scripts before starting the dashboard."
    )
    st.stop()
except Exception as error:
    st.error(f"Unable to load project data: {error}")
    st.stop()


# Sidebar controls
st.sidebar.header("Digital Twin Controls")

patient_ids = sorted(
    ehr["patient_id"].dropna().astype(str).unique()
)

if not patient_ids:
    st.error("No patient profiles are available.")
    st.stop()

selected_patient = st.sidebar.selectbox(
    "Select synthetic patient",
    patient_ids,
)

patient = ehr.loc[
    ehr["patient_id"].astype(str) == selected_patient
].iloc[0]

patient_wearable = wearable.loc[
    wearable["patient_id"].astype(str) == selected_patient
].sort_values("timestamp")

patient_baseline = baseline.loc[
    baseline["patient_id"].astype(str) == selected_patient
]

patient_scenarios = scenarios.loc[
    scenarios["patient_id"].astype(str) == selected_patient
]

if patient_wearable.empty or patient_baseline.empty:
    st.error("Wearable readings or baseline data are unavailable.")
    st.stop()

reference = patient_baseline.iloc[0]

# Patient overview
st.markdown("### 1. Personal Profile")

profile_col1, profile_col2, profile_col3, profile_col4 = (
    st.columns(4)
)

profile_col1.metric("Patient ID", selected_patient)
profile_col2.metric("Age", f"{patient['age']} years")
profile_col3.metric("BMI", f"{patient['bmi']}")
profile_col4.metric(
    "Profile type",
    str(patient["data_type"]),
)

st.caption(
    "Profile values are fictional test data and do not represent "
    "an actual person."
)

# Baseline overview
st.markdown("### 2. Personal Wearable Baseline")

kpi1, kpi2, kpi3 = st.columns(3)

kpi1.metric(
    "Mean heart rate",
    f"{reference['baseline_heart_rate']:.1f} bpm",
)
kpi2.metric(
    "Mean HRV",
    f"{reference['baseline_hrv']:.1f}",
)
kpi3.metric(
    "Mean steps value",
    f"{reference['baseline_steps']:.1f}",
)

st.caption(
    "These are averages of the available synthetic readings. "
    "HRV units and the meaning of the supplied step values have "
    "not been independently established. These averages are not "
    "healthy ranges or clinical thresholds."
)

# Wearable trends
st.markdown("### 3. Wearable Time-Series Explorer")

if patient_wearable.empty:
    st.info("No wearable readings are available for this profile.")
else:
    hr_chart = px.line(
        patient_wearable,
        x="timestamp",
        y="heart_rate",
        markers=True,
        title="Heart Rate Across Recorded Readings",
        labels={
            "timestamp": "Timestamp",
            "heart_rate": "Heart rate (bpm)",
        },
    )
    hr_chart.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(hr_chart, use_container_width=True)

    hrv_chart = px.line(
        patient_wearable,
        x="timestamp",
        y="hrv",
        markers=True,
        title="HRV Across Recorded Readings",
        labels={
            "timestamp": "Timestamp",
            "hrv": "HRV (source units unverified)",
        },
    )
    hrv_chart.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    st.plotly_chart(hrv_chart, use_container_width=True)

    st.dataframe(
        patient_wearable[
            ["timestamp", "heart_rate", "hrv", "steps"]
        ],
        hide_index=True,
        use_container_width=True,
    )

# Baseline deviations
st.markdown("### 4. Reading-to-Baseline Comparison")

comparison = patient_wearable.copy()

comparison["heart_rate_difference"] = (
    comparison["heart_rate"]
    - reference["baseline_heart_rate"]
)
comparison["hrv_difference"] = (
    comparison["hrv"] - reference["baseline_hrv"]
)
comparison["steps_difference"] = (
    comparison["steps"] - reference["baseline_steps"]
)

st.dataframe(
    comparison[
        [
            "timestamp",
            "heart_rate_difference",
            "hrv_difference",
            "steps_difference",
        ]
    ].rename(
        columns={
            "timestamp": "Timestamp",
            "heart_rate_difference": "Heart rate difference (bpm)",
            "hrv_difference": "HRV difference (source units)",
            "steps_difference": "Steps-value difference",
        }
    ),
    hide_index=True,
    use_container_width=True,
)

st.caption(
    "Differences are descriptive comparisons against a baseline "
    "computed from the same small set of readings. They are not "
    "independent predictions or adverse-event alerts."
)

# What-if scenarios
st.markdown("### 5. What-If Scenario Simulator")

st.write(
    "Choose a hypothetical scenario to inspect its illustrative "
    "effect on the selected profile's baseline values."
)

if patient_scenarios.empty:
    st.info("No scenario outputs found for this profile.")
else:
    scenario_names = patient_scenarios["scenario"].tolist()

    selected_scenario_name = st.selectbox(
        "Choose a simulated scenario",
        scenario_names,
    )

    selected_scenario = patient_scenarios.loc[
        patient_scenarios["scenario"] == selected_scenario_name
    ].iloc[0]

    scenario_col1, scenario_col2, scenario_col3 = st.columns(3)

    scenario_col1.metric(
        "Simulated heart rate",
        f"{selected_scenario['simulated_heart_rate']:.1f} bpm",
        delta=(
            f"{selected_scenario['simulated_heart_rate'] - selected_scenario['baseline_heart_rate']:+.1f} bpm"
        ),
    )
    scenario_col2.metric(
        "Simulated HRV",
        f"{selected_scenario['simulated_hrv']:.1f}",
        delta=(
            f"{selected_scenario['simulated_hrv'] - selected_scenario['baseline_hrv']:+.1f}"
        ),
    )
    scenario_col3.metric(
        "Simulated steps value",
        f"{selected_scenario['simulated_steps']:.1f}",
        delta=(
            f"{selected_scenario['simulated_steps'] - selected_scenario['baseline_steps']:+.1f}"
        ),
    )

    st.info(
        "This is a manually specified numerical scenario. "
        "It does not predict an actual physiological response, "
        "PCOS progression, or an adverse event."
    )

    st.dataframe(
        patient_scenarios[
            [
                "scenario",
                "baseline_heart_rate",
                "simulated_heart_rate",
                "baseline_hrv",
                "simulated_hrv",
                "baseline_steps",
                "simulated_steps",
            ]
        ],
        hide_index=True,
        use_container_width=True,
    )

# Data quality and transparency
st.markdown("### 6. Data Quality and Limitations")

quality1, quality2, quality3 = st.columns(3)

quality1.metric(
    "EHR profiles",
    len(ehr),
)
quality2.metric(
    "Wearable readings",
    len(wearable),
)
quality3.metric(
    "Synthetic scenarios",
    len(scenarios),
)

st.write(
    "- All current demonstration records are synthetic."
)
st.write(
    "- Each patient's wearable records are matched using patient ID."
)
st.write(
    "- Two readings per patient are insufficient to establish "
    "a meaningful personal health baseline."
)
st.write(
    "- No clinically validated adverse-event prediction model "
    "is implemented in this version."
)

st.divider()
st.caption(
    "OVARY-X | Engineering proof-of-concept | "
    "For demonstration and educational use only"
)
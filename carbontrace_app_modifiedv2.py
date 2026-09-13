import math
import random
import urllib.parse
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd
import plotly.graph_objects as go


# ============================================================
# CARBONTRACE × ATLAS
# Transport Emissions Intelligence & Environmental Impact
#
# CURRENT VERSION:
#   DEMONSTRATION / SIMULATED SENSOR DATA
#
# IMPORTANT:
#   - No carbon-credit purchasing
#   - No payment processing
#   - No real tree-equivalent calculations
#   - No automatic carbon-neutrality claims
#   - No claim that environmental contributions offset emissions
#
# FUTURE:
#   Replace simulator with:
#   - ATLAS sensors
#   - CO2 NDIR
#   - CO / O2 / NOx / HC
#   - PM
#   - Exhaust temperature / pressure / flow
#   - GPS / GNSS
#   - CAN / OBD-II / J1939
#   - Fuel / ECU data
#   - Calibrated emissions instrumentation
# ============================================================


st.set_page_config(
    page_title="CarbonTrace × ATLAS",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# GLOBAL STYLING
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f7f9fc;
    }

    .hero {
        padding: 30px 34px;
        border-radius: 22px;
        background: linear-gradient(
            135deg,
            #071426 0%,
            #102b46 55%,
            #173b55 100%
        );
        color: white;
        margin-bottom: 22px;
    }

    .hero h1 {
        font-size: 2.6rem;
        margin-bottom: 6px;
    }

    .hero p {
        font-size: 1.05rem;
        opacity: 0.88;
        margin-bottom: 0;
    }

    .section-title {
        font-size: 1.45rem;
        font-weight: 700;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    .metric-card {
        border: 1px solid #dfe5ec;
        border-radius: 16px;
        padding: 16px;
        background: white;
        min-height: 125px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.035);
    }

    .metric-label {
        color: #667085;
        font-size: 0.82rem;
        margin-bottom: 6px;
    }

    .metric-value {
        font-size: 1.75rem;
        font-weight: 750;
        color: #101828;
    }

    .metric-note {
        color: #667085;
        font-size: 0.76rem;
        margin-top: 5px;
    }

    .recommendation {
        border: 1px solid #d9e4ef;
        border-radius: 18px;
        padding: 20px;
        background: white;
        margin-bottom: 14px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.04);
    }

    .recommendation h3 {
        margin-top: 5px;
    }

    .impact-card {
        border: 2px solid #d9e8dd;
        border-radius: 18px;
        padding: 22px;
        background: #fbfefc;
        margin-top: 10px;
    }

    .guardrail-card {
        border: 1px solid #f0d48a;
        border-radius: 16px;
        padding: 18px;
        background: #fffaf0;
        margin: 12px 0;
    }

    .architecture-card {
        border: 1px solid #d9e4ef;
        border-radius: 16px;
        padding: 18px;
        background: white;
        margin-bottom: 12px;
    }

    .status-demo {
        padding: 11px 15px;
        border-radius: 12px;
        background: #fff4d6;
        border: 1px solid #f1d98b;
        color: #684f00;
        font-weight: 600;
        margin-bottom: 18px;
    }

    .status-live {
        padding: 11px 15px;
        border-radius: 12px;
        background: #e6f7ec;
        border: 1px solid #b8dfc4;
        color: #14532d;
        font-weight: 600;
        margin-bottom: 18px;
    }

    .small-muted {
        color: #667085;
        font-size: 0.82rem;
    }

    .big-number {
        font-size: 2.2rem;
        font-weight: 750;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA ARCHITECTURE
# ============================================================

SENSOR_ARCHITECTURE = {
    "ambient_temperature_c": {
        "label": "Ambient Temperature",
        "unit": "°C",
        "source": "ATLAS",
        "type": "measured",
    },
    "ambient_humidity_percent": {
        "label": "Ambient Humidity",
        "unit": "%",
        "source": "ATLAS",
        "type": "measured",
    },
    "ambient_pressure_kpa": {
        "label": "Ambient Pressure",
        "unit": "kPa",
        "source": "Future sensor",
        "type": "measured",
    },
    "ambient_co2_ppm": {
        "label": "Ambient CO₂",
        "unit": "ppm",
        "source": "Future gas sensor",
        "type": "measured",
    },
    "exhaust_co2_percent": {
        "label": "Exhaust CO₂",
        "unit": "%",
        "source": "High-range NDIR",
        "type": "measured",
    },
    "co_ppm": {
        "label": "CO",
        "unit": "ppm",
        "source": "Future gas sensor",
        "type": "measured",
    },
    "o2_percent": {
        "label": "O₂",
        "unit": "%",
        "source": "Future gas sensor",
        "type": "measured",
    },
    "nox_ppm": {
        "label": "NOx",
        "unit": "ppm",
        "source": "Future NOx sensor",
        "type": "measured",
    },
    "hc_ppm": {
        "label": "Hydrocarbons",
        "unit": "ppm",
        "source": "Future gas sensor",
        "type": "measured",
    },
    "pm2_5_ug_m3": {
        "label": "PM2.5",
        "unit": "µg/m³",
        "source": "Future PM module",
        "type": "measured",
    },
    "exhaust_temperature_c": {
        "label": "Exhaust Temperature",
        "unit": "°C",
        "source": "K-type thermocouple",
        "type": "measured",
    },
    "exhaust_pressure_kpa": {
        "label": "Exhaust Pressure",
        "unit": "kPa",
        "source": "Pressure transducer",
        "type": "measured",
    },
    "exhaust_flow_kg_s": {
        "label": "Exhaust Mass Flow",
        "unit": "kg/s",
        "source": "Professional flow meter",
        "type": "measured",
    },
    "vehicle_speed_kmh": {
        "label": "Vehicle Speed",
        "unit": "km/h",
        "source": "GPS / CAN",
        "type": "measured",
    },
    "engine_rpm": {
        "label": "Engine RPM",
        "unit": "RPM",
        "source": "CAN / J1939",
        "type": "measured",
    },
    "engine_load_pct": {
        "label": "Engine Load",
        "unit": "%",
        "source": "CAN / J1939",
        "type": "measured",
    },
    "fuel_rate_l_h": {
        "label": "Fuel Rate",
        "unit": "L/h",
        "source": "CAN / fuel measurement",
        "type": "measured",
    },
    "latitude": {
        "label": "Latitude",
        "unit": "",
        "source": "GNSS",
        "type": "measured",
    },
    "longitude": {
        "label": "Longitude",
        "unit": "",
        "source": "GNSS",
        "type": "measured",
    },
}


# ============================================================
# SIMULATED SENSOR DATA
# ============================================================

def generate_demo_data(rows=240):

    start = datetime.now().replace(second=0, microsecond=0)

    records = []

    for i in range(rows):

        timestamp = start - timedelta(seconds=(rows - i) * 5)

        phase = i / rows * math.pi * 7

        speed = max(
            0,
            min(
                100,
                58
                + 22 * math.sin(phase)
                + random.uniform(-8, 8),
            ),
        )

        rpm = max(
            800,
            min(
                3500,
                1300
                + speed * 18
                + random.uniform(-160, 160),
            ),
        )

        engine_load = max(
            10,
            min(
                100,
                30
                + speed * 0.60
                + 18 * math.sin(phase * 1.5)
                + random.uniform(-5, 5),
            ),
        )

        fuel_rate = max(
            4,
            min(
                18,
                5
                + engine_load * 0.085
                + random.uniform(-0.35, 0.35),
            ),
        )

        exhaust_temperature = max(
            200,
            min(
                750,
                230
                + engine_load * 4.5
                + random.uniform(-15, 15),
            ),
        )

        exhaust_pressure = max(
            100,
            min(
                110,
                101.3
                + engine_load * 0.055
                + random.uniform(-1.0, 1.0),
            ),
        )

        exhaust_co2 = max(
            3,
            min(
                15,
                4
                + engine_load * 0.065
                + fuel_rate * 0.10
                + random.uniform(-0.20, 0.20),
            ),
        )

        oxygen = max(
            2,
            min(
                14,
                13
                - engine_load * 0.075
                + random.uniform(-0.3, 0.3),
            ),
        )

        co = max(
            20,
            min(
                1000,
                70
                + engine_load * 5.5
                + random.uniform(-25, 25),
            ),
        )

        nox = max(
            80,
            min(
                1600,
                150
                + engine_load * 9
                + exhaust_temperature * 0.75
                + random.uniform(-70, 70),
            ),
        )

        hc = max(
            5,
            min(
                100,
                15
                + (100 - engine_load) * 0.38
                + random.uniform(-5, 5),
            ),
        )

        pm = max(
            4,
            min(
                160,
                12
                + engine_load * 0.65
                + random.uniform(-5, 5),
            ),
        )

        exhaust_flow = max(
            0.008,
            min(
                0.07,
                0.012
                + engine_load * 0.00048
                + random.uniform(-0.0015, 0.0015),
            ),
        )

        # ----------------------------------------------------
        # DEMONSTRATION-ONLY CO2 RATE
        #
        # This is NOT a regulatory emissions calculation.
        # Production calculation requires validated gas
        # concentration + exhaust mass flow + gas properties
        # + appropriate correction/measurement methodology.
        # ----------------------------------------------------

        co2_rate = max(
            0.2,
            min(
                20,
                exhaust_co2
                * exhaust_flow
                * 19.5,
            ),
        )

        latitude = 51.5074 + 0.015 * math.sin(phase / 2)
        longitude = -0.1278 + 0.025 * math.cos(phase / 2)

        records.append(
            {
                "timestamp": timestamp,

                "ambient_temperature_c":
                    18.5 + 2.2 * math.sin(phase / 3),

                "ambient_humidity_percent":
                    61 + 8 * math.sin(phase / 2),

                "ambient_pressure_kpa":
                    101.2 + random.uniform(-1, 1),

                "ambient_co2_ppm":
                    430 + random.uniform(-25, 25),

                "exhaust_co2_percent": exhaust_co2,
                "co_ppm": co,
                "o2_percent": oxygen,
                "nox_ppm": nox,
                "hc_ppm": hc,
                "pm2_5_ug_m3": pm,

                "exhaust_temperature_c":
                    exhaust_temperature,

                "exhaust_pressure_kpa":
                    exhaust_pressure,

                "exhaust_flow_kg_s":
                    exhaust_flow,

                "vehicle_speed_kmh":
                    speed,

                "engine_rpm":
                    rpm,

                "engine_load_pct":
                    engine_load,

                "fuel_rate_l_h":
                    fuel_rate,

                "latitude":
                    latitude,

                "longitude":
                    longitude,

                "co2_rate_g_s":
                    co2_rate,
            }
        )

    df = pd.DataFrame(records)

    # Five-second samples
    df["distance_km"] = (
        df["vehicle_speed_kmh"] * 5 / 3600
    )

    # Demonstration integration
    df["co2_g"] = (
        df["co2_rate_g_s"] * 5
    )

    df["fuel_l"] = (
        df["fuel_rate_l_h"] * 5 / 3600
    )

    return df


# ============================================================
# EMISSIONS ENGINE
# ============================================================

def calculate_emissions(df):

    distance_km = df["distance_km"].sum()

    co2_kg = df["co2_g"].sum() / 1000

    fuel_l = df["fuel_l"].sum()

    co2_g_per_km = (
        co2_kg * 1000 / distance_km
        if distance_km > 0
        else 0
    )

    average_speed = (
        df["vehicle_speed_kmh"].mean()
    )

    average_load = (
        df["engine_load_pct"].mean()
    )

    peak_co2_rate = (
        df["co2_rate_g_s"].max()
    )

    idle_seconds = (
        (df["vehicle_speed_kmh"] < 5).sum() * 5
    )

    idle_minutes = idle_seconds / 60

    return {
        "distance_km": distance_km,
        "co2_kg": co2_kg,
        "fuel_l": fuel_l,
        "co2_g_per_km": co2_g_per_km,
        "average_speed": average_speed,
        "average_load": average_load,
        "peak_co2_rate": peak_co2_rate,
        "idle_minutes": idle_minutes,
    }


# ============================================================
# AI / EVENT ENGINE
# ============================================================

def detect_events(df):

    avg_co2 = (
        df["co2_rate_g_s"].mean()
    )

    events = []

    for _, row in df.iterrows():

        score = 0
        causes = []

        if row["engine_load_pct"] > 82:
            score += 25
            causes.append("High engine load")

        if row["vehicle_speed_kmh"] > 80:
            score += 20
            causes.append("High-speed operation")

        if row["exhaust_temperature_c"] > 570:
            score += 20
            causes.append("Elevated exhaust temperature")

        if row["co2_rate_g_s"] > avg_co2 * 1.25:
            score += 25
            causes.append("CO₂ rate above trip baseline")

        if (
            row["vehicle_speed_kmh"] < 5
            and row["engine_rpm"] > 900
        ):
            score += 15
            causes.append("Possible engine idling")

        if score >= 45:

            events.append(
                {
                    "timestamp": row["timestamp"],
                    "score": min(score, 100),
                    "co2_rate": row["co2_rate_g_s"],
                    "speed": row["vehicle_speed_kmh"],
                    "load": row["engine_load_pct"],
                    "temperature": row["exhaust_temperature_c"],
                    "causes": causes,
                }
            )

    return events


# ============================================================
# REDUCTION ENGINE
# ============================================================

def generate_recommendations(metrics, events):

    recommendations = []

    if metrics["idle_minutes"] > 2:

        recommendations.append(
            {
                "category": "Idle reduction",
                "priority": "HIGH",
                "title": "Reduce unnecessary engine idling",
                "reason": (
                    f"The demonstration journey contains approximately "
                    f"{metrics['idle_minutes']:.1f} minutes of low-speed "
                    "operation with the engine running."
                ),
                "action": (
                    "Identify avoidable idle periods and introduce "
                    "driver/fleet idle-reduction policies."
                ),
                "potential": "3–8% illustrative range",
            }
        )

    if metrics["average_load"] > 60:

        recommendations.append(
            {
                "category": "Driving efficiency",
                "priority": "HIGH",
                "title": "Reduce high-load acceleration events",
                "reason": (
                    f"Average engine load is approximately "
                    f"{metrics['average_load']:.0f}%."
                ),
                "action": (
                    "Use smoother acceleration and avoid unnecessary "
                    "high-load operation where traffic conditions allow."
                ),
                "potential": "4–10% illustrative range",
            }
        )

    if metrics["average_speed"] > 65:

        recommendations.append(
            {
                "category": "Speed optimisation",
                "priority": "MEDIUM",
                "title": "Optimise cruising speed",
                "reason": (
                    f"Average speed is approximately "
                    f"{metrics['average_speed']:.0f} km/h."
                ),
                "action": (
                    "Evaluate route and speed optimisation against "
                    "delivery-time requirements."
                ),
                "potential": "2–6% illustrative range",
            }
        )

    if len(events) > 5:

        recommendations.append(
            {
                "category": "Fleet intelligence",
                "priority": "MEDIUM",
                "title": "Investigate repeated high-emission events",
                "reason": (
                    f"{len(events)} high-emission events were identified "
                    "in the demonstration data."
                ),
                "action": (
                    "Compare vehicle, driver, route and load conditions "
                    "to identify repeatable causes."
                ),
                "potential": "5–12% illustrative range",
            }
        )

    recommendations.append(
        {
            "category": "Maintenance intelligence",
            "priority": "MEDIUM",
            "title": "Use emissions patterns for predictive maintenance",
            "reason": (
                "Persistent abnormal relationships between exhaust "
                "temperature, CO₂, O₂, NOx and engine load may indicate "
                "maintenance conditions requiring investigation."
            ),
            "action": (
                "Compare live sensor patterns against historical vehicle "
                "baselines before triggering maintenance alerts."
            ),
            "potential": "Diagnostic",
        }
    )

    return recommendations


# ============================================================
# ENVIRONMENTAL PROJECT ARCHITECTURE
# ============================================================

PROJECTS = {

    "🌳 Woodland project": {
        "type": "Land-based environmental project",
        "tag": "Nature + restoration",
        "priority": "carbon",
        "description": (
            "Support a woodland project with documented land, "
            "management and environmental outcomes."
        ),
        "benefits": [
            "Woodland restoration",
            "Biodiversity",
            "Long-term land stewardship",
        ],
        "verification": [
            "Project identity",
            "Land information",
            "Additionality / permanence evidence",
            "Applicable carbon methodology where relevant",
        ],
        "customer_value": (
            "Suitable for customers prioritising nature restoration "
            "and long-term environmental stewardship."
        ),
    },

    "🌾 Farmer agroforestry": {
        "type": "Agriculture + environmental impact",
        "tag": "Carbon + farmer livelihood",
        "priority": "farmer",
        "description": (
            "Support farmers integrating trees with productive "
            "agricultural land."
        ),
        "benefits": [
            "Farmer livelihood",
            "Soil health",
            "Biodiversity",
            "Agroforestry",
        ],
        "verification": [
            "Farmer/project identity",
            "Land records",
            "Intervention records",
            "Carbon methodology where applicable",
        ],
        "customer_value": (
            "Suitable for customers wanting environmental action "
            "combined with farmer livelihood and land benefits."
        ),
    },

    "🔥 Biochar": {
        "type": "Durable carbon removal",
        "tag": "Durable carbon storage",
        "priority": "durable",
        "description": (
            "Support a biochar pathway where biomass is converted "
            "into a durable carbon-rich material."
        ),
        "benefits": [
            "Durable carbon storage",
            "Biomass utilisation",
            "Potential soil benefits",
        ],
        "verification": [
            "Feedstock source",
            "Production records",
            "Carbon accounting methodology",
            "Verification / traceability",
        ],
        "customer_value": (
            "Suitable for customers specifically interested in "
            "durable carbon-removal pathways."
        ),
    },

    "🌱 Community environmental project": {
        "type": "Community environmental impact",
        "tag": "Local environmental benefit",
        "priority": "community",
        "description": (
            "Support local environmental projects such as urban "
            "greening, biodiversity or environmental education."
        ),
        "benefits": [
            "Community participation",
            "Urban greening",
            "Biodiversity",
            "Environmental education",
        ],
        "verification": [
            "Project delivery evidence",
            "Community outcome evidence",
            "Financial traceability",
            "Carbon claims separated from wider impact claims",
        ],
        "customer_value": (
            "Suitable for customers wanting visible local "
            "environmental and community outcomes."
        ),
    },
}


# ============================================================
# DETERMINISTIC PROJECT MATCHING
# ============================================================

def match_projects(customer_goal):

    mapping = {
        "Maximum carbon-removal focus":
            "🌳 Woodland project",

        "Support farmers":
            "🌾 Farmer agroforestry",

        "Durable carbon removal":
            "🔥 Biochar",

        "Local community impact":
            "🌱 Community environmental project",
    }

    primary = mapping[customer_goal]

    scores = {
        "🌳 Woodland project": 78,
        "🌾 Farmer agroforestry": 76,
        "🔥 Biochar": 80,
        "🌱 Community environmental project": 72,
    }

    scores[primary] = 96

    results = []

    for name, project in PROJECTS.items():

        results.append(
            {
                "project": name,
                "score": scores[name],
                "data": project,
            }
        )

    results.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    return results


# ============================================================
# PROJECT PACKAGES, PRICING & RECORD HELPERS
# ============================================================

PROJECT_PACKAGES = {
    "🌳 Woodland project": {
        "program": "Woodland restoration contribution",
        "unit": "restoration unit",
        "price_per_unit": 7.50,
        "minimum_quantity": 100,
        "quantity_label": "Number of restoration units",
    },
    "🌾 Farmer agroforestry": {
        "program": "Farmer agroforestry support",
        "unit": "farmer intervention unit",
        "price_per_unit": 6.50,
        "minimum_quantity": 100,
        "quantity_label": "Number of farmer intervention units",
    },
    "🔥 Biochar": {
        "program": "Biochar production / deployment",
        "unit": "kg biochar",
        "price_per_unit": 3.00,
        "minimum_quantity": 100,
        "quantity_label": "Biochar quantity (kg)",
    },
    "🌱 Community environmental project": {
        "program": "Community tree-pot / urban greening programme",
        "unit": "tree pot / greening unit",
        "price_per_unit": 5.00,
        "minimum_quantity": 100,
        "quantity_label": "Number of tree pots / greening units",
    },
}


def money(value):
    return f"£{value:,.2f}"


def build_impact_record(
    selected_project,
    selected_data,
    package,
    quantity,
    estimated_price,
    metrics,
    customer_goal,
    co2_evidence_kg,
    evidence_status,
):

    # Demonstration-only reduction assumption.
    # Production CarbonTrace must replace this with
    # validated vehicle-specific evidence.
    illustrative_reduction = 0.11

    potential_reduction_kg = (
        metrics["co2_kg"] * illustrative_reduction
    )

    residual_kg = (
        metrics["co2_kg"] - potential_reduction_kg
    )

    return {
        "Impact Record ID": st.session_state.impact_record_id,
        "Record timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Vehicle": vehicle,
        "Protocol": protocol,
        "Trip distance (km)": round(metrics["distance_km"], 2),
        "Trip estimated CO2 (kg)": round(metrics["co2_kg"], 2),

        "Illustrative reduction opportunity (kg)": round(
            potential_reduction_kg, 2
        ),

        "Illustrative residual basis (kg)": round(
            residual_kg, 2
        ),

        "Customer objective": customer_goal,
        "Selected pathway": selected_project,
        "Programme": package["program"],
        "Quantity": quantity,
        "Unit": package["unit"],
        "Illustrative programme price (GBP)": round(
            estimated_price, 2
        ),
        "Project completion status":
            "Completed — demonstration"
            if st.session_state.project_completed
            else "Selected — not completed",

        "Project evidence status": evidence_status,

        "Project CO2 evidence / credited amount (kg)": round(
            co2_evidence_kg, 2
        ),

        "Carbon credit purchase": "Not enabled",
        "Payment processing": "Not enabled",
        "Carbon neutrality claim": "Not made",
        "Tree-equivalent offset calculation": "Not provided",
        "Claim status": "DEMO — NOT A CARBON CREDIT",
    }


def build_claim_audit_record(impact_record, selected_data):
    return {
        "Impact Record ID": impact_record["Impact Record ID"],
        "Claim/Audit Record ID": "AUD-" + impact_record["Impact Record ID"].replace("CT-", ""),
        "Generated at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Measurement source": data_mode,
        "Emissions data status": "Simulated / demonstration",
        "Emissions calculation status": "Illustrative demonstration calculation",
        "Project pathway": impact_record["Selected pathway"],
        "Project type": selected_data["type"],
        "Programme": impact_record["Programme"],
        "Quantity delivered": impact_record["Quantity"],
        "Unit": impact_record["Unit"],
        "Programme price estimate (GBP)": impact_record["Illustrative programme price (GBP)"],
        "Project completion": impact_record["Project completion status"],
        "Project evidence status": impact_record["Project evidence status"],
        "CO2 evidence / credited amount (kg)": impact_record["Project CO2 evidence / credited amount (kg)"],
        "Carbon credit issued": "No",
        "Carbon credit purchase": "No",
        "Payment processed": "No",
        "Carbon neutral claim": "No",
        "Offset claim": "No",
        "Tree equivalent claim": "No",
        "Methodology evidence": "Required before any carbon claim",
        "Verification evidence": "Required before any verified carbon claim",
        "Traceability": "Impact record generated; project evidence pending/attached separately",
        "Double-counting control": "Required for production carbon claims",
        "Audit status": "Demonstration / not independently audited",
        "Claim status": "DEMO — NOT A CARBON CREDIT",
    }


def social_caption(impact_record):
    return (
        f"CarbonTrace × ATLAS: emissions measured and analysed for {impact_record['Vehicle']}. "
        f"We selected {impact_record['Selected pathway']} through the {impact_record['Programme']} "
        f"({impact_record['Quantity']} {impact_record['Unit']}). "
        "This demonstration separates emissions measurement, reduction and environmental impact evidence. "
        "No carbon-credit purchase or carbon-neutral claim is made in this demo. #CarbonTrace #ATLAS #ClimateTech #Emissions"
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🌍 CarbonTrace")

    data_mode = st.radio(
        "Data source",
        [
            "🟡 SIMULATED DATA",
            "🟢 LIVE SENSOR MODE",
        ],
    )

    st.divider()

    vehicle = st.selectbox(
        "Vehicle",
        [
            "Demo Truck 001",
            "Demo Van 014",
            "Demo Bus 007",
            "Fleet Vehicle 021",
        ],
    )

    protocol = st.selectbox(
        "Vehicle data protocol",
        [
            "SAE J1939",
            "OBD-II / CAN",
        ],
    )

    st.divider()

    st.subheader("Customer objective")

    customer_goal = st.selectbox(
        "What matters most to this customer?",
        [
            "Maximum carbon-removal focus",
            "Support farmers",
            "Durable carbon removal",
            "Local community impact",
        ],
    )

    st.divider()

    st.caption(
        "CarbonTrace separates measured data, derived calculations, "
        "AI predictions and environmental project claims."
    )


# ============================================================
# MAIN HERO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <h1>🌍 CarbonTrace × ATLAS</h1>
        <p>
        Transport emissions intelligence for measuring,
        understanding, reducing and responsibly managing residual impact.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MODE STATUS
# ============================================================

if data_mode == "🟡 SIMULATED DATA":

    st.markdown(
        """
        <div class="status-demo">
        🟡 DEMONSTRATION MODE — Sensor values are simulated.
        The architecture is prepared for ATLAS hardware, GPS,
        CAN/J1939 and future emissions instrumentation.
        </div>
        """,
        unsafe_allow_html=True,
    )

else:

    st.markdown(
        """
        <div class="status-live">
        🟢 LIVE SENSOR MODE — Hardware interface selected.
        Connect configured sensor drivers to replace the simulator.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CREATE DATA
# ============================================================

df = generate_demo_data()

metrics = calculate_emissions(df)

events = detect_events(df)

recommendations = generate_recommendations(
    metrics,
    events,
)

project_matches = match_projects(
    customer_goal
)


# ============================================================
# IMPACT / CLAIM STATE
# ============================================================

if "impact_record_id" not in st.session_state:
    st.session_state.impact_record_id = (
        "CT-" + datetime.now().strftime("%Y%m%d") + "-" +
        str(random.randint(10000, 99999))
    )

if "project_completed" not in st.session_state:
    st.session_state.project_completed = False

if "selected_project" not in st.session_state:
    st.session_state.selected_project = project_matches[0]["project"]

if "project_quantity" not in st.session_state:
    st.session_state.project_quantity = 100

if "project_co2_evidence_kg" not in st.session_state:
    st.session_state.project_co2_evidence_kg = 0.0

if "project_evidence_status" not in st.session_state:
    st.session_state.project_evidence_status = "Pending project evidence"

if "project_reference" not in st.session_state:
    st.session_state.project_reference = "Pending"


# ============================================================
# VEHICLE SNAPSHOT
# ============================================================

st.markdown(
    '<div class="section-title">🚛 Vehicle emissions cockpit</div>',
    unsafe_allow_html=True,
)

latest = df.iloc[-1]

cols = st.columns(6)

live_metrics = [
    (
        "CO₂ concentration",
        f"{latest.exhaust_co2_percent:.2f} %",
        "High-range NDIR",
    ),
    (
        "CO₂ emission rate",
        f"{latest.co2_rate_g_s:.2f} g/s",
        "Derived demo value",
    ),
    (
        "NOx",
        f"{latest.nox_ppm:.0f} ppm",
        "Future sensor",
    ),
    (
        "Exhaust temperature",
        f"{latest.exhaust_temperature_c:.0f} °C",
        "K-type",
    ),
    (
        "Engine load",
        f"{latest.engine_load_pct:.0f} %",
        "CAN/J1939",
    ),
    (
        "Vehicle speed",
        f"{latest.vehicle_speed_kmh:.0f} km/h",
        "GPS/CAN",
    ),
]

for col, item in zip(cols, live_metrics):

    label, value, note = item

    with col:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# JOURNEY SUMMARY
# ============================================================

st.markdown(
    '<div class="section-title">📊 Journey intelligence</div>',
    unsafe_allow_html=True,
)

cols = st.columns(6)

journey_metrics = [
    ("Distance", f"{metrics['distance_km']:.1f} km"),
    ("Estimated CO₂", f"{metrics['co2_kg']:.1f} kg"),
    ("CO₂ intensity", f"{metrics['co2_g_per_km']:.0f} g/km"),
    ("Fuel consumed", f"{metrics['fuel_l']:.1f} L"),
    ("Average speed", f"{metrics['average_speed']:.0f} km/h"),
    ("Idle time", f"{metrics['idle_minutes']:.1f} min"),
]

for col, (label, value) in zip(
    cols,
    journey_metrics,
):

    col.metric(
        label,
        value,
    )


# ============================================================
# TABS
# ============================================================

(
    tab_dashboard,
    tab_emissions,
    tab_ai,
    tab_reduce,
    tab_impact,
    tab_data,
) = st.tabs(
    [
        "🏠 Executive Dashboard",
        "🧪 Emissions",
        "🤖 AI Analysis",
        "⬇️ Reduce",
        "🌱 Impact",
        "🗃 Data & Sensors",
    ]
)


# ============================================================
# EXECUTIVE DASHBOARD
# ============================================================

with tab_dashboard:

    st.subheader("CarbonTrace executive view")

    c1, c2 = st.columns([1.5, 1])

    with c1:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["co2_rate_g_s"],
                mode="lines",
                name="CO₂ emission rate",
            )
        )

        fig.update_layout(
            title="Real-time CO₂ emission profile",
            height=350,
            margin=dict(
                l=10,
                r=10,
                t=50,
                b=10,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with c2:

        st.markdown("### 🧠 CarbonTrace status")

        st.success(
            "Monitoring engine active"
        )

        st.write(f"**Vehicle:** {vehicle}")

        st.write(f"**Protocol:** {protocol}")

        st.write(
            f"**Distance analysed:** "
            f"{metrics['distance_km']:.1f} km"
        )

        st.write(
            f"**CO₂ intensity:** "
            f"{metrics['co2_g_per_km']:.0f} g/km"
        )

        st.write(
            f"**High-emission events:** "
            f"{len(events)}"
        )

        st.write(
            "**Data status:** "
            "Simulated / hardware-ready"
        )

    st.divider()

    st.subheader("🚨 What needs attention?")

    if recommendations:

        for rec in recommendations[:3]:

            st.markdown(
                f"""
                <div class="recommendation">
                    <b>{rec['priority']} — {rec['category']}</b>
                    <h3>{rec['title']}</h3>
                    <p>{rec['reason']}</p>
                    <b>Recommended action:</b>
                    <p>{rec['action']}</p>
                    <span class="small-muted">
                    Potential improvement: {rec['potential']}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )


    st.divider()
    st.subheader("🌱 Project Evidence & Impact Dashboard")

    if st.session_state.project_completed:
        dash_project = st.session_state.selected_project
        dash_package = PROJECT_PACKAGES[dash_project]
        dash_data = PROJECTS[dash_project]
        dash_co2 = st.session_state.project_co2_evidence_kg
        dash_evidence_status = st.session_state.project_evidence_status
        dash_quantity = st.session_state.project_quantity
        dash_price = dash_quantity * dash_package["price_per_unit"]

        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Project", dash_project)
        d2.metric("Delivery", f"{dash_quantity:,} {dash_package['unit']}")
        d3.metric("Programme value", money(dash_price))
        d4.metric("CO₂ project evidence", "Pending" if dash_co2 <= 0 else f"{dash_co2:,.1f} kg")

        if dash_co2 > 0 and dash_evidence_status == "Independent verification evidence supplied":
            st.success(
                f"PROJECT EVIDENCE: {dash_co2:,.2f} kg CO₂e is recorded as project evidence. "
                "It remains separate from the vehicle emissions record and does not automatically establish carbon neutrality."
            )
        elif dash_co2 > 0:
            st.info(
                f"PROJECT EVIDENCE: {dash_co2:,.2f} kg CO₂e has been entered from project documentation, "
                "but it is not presented as independently verified."
            )
        else:
            st.info(
                "PROJECT EVIDENCE: Project completed, but no project-level CO₂ evidence has been supplied yet."
            )

        dashboard_impact = build_impact_record(
            dash_project,
            dash_data,
            dash_package,
            dash_quantity,
            dash_price,
            metrics,
            customer_goal,
            dash_co2,
            dash_evidence_status,
        )
        dashboard_impact_df = pd.DataFrame([dashboard_impact])
        dashboard_audit = build_claim_audit_record(dashboard_impact, dash_data)
        dashboard_audit_df = pd.DataFrame([dashboard_audit])

        with st.expander("📄 IMPACT RECORD dashboard", expanded=True):
            st.dataframe(dashboard_impact_df.T.rename(columns={0: "Value"}), use_container_width=True)
            st.download_button(
                "Download IMPACT RECORD CSV",
                data=dashboard_impact_df.to_csv(index=False).encode("utf-8"),
                file_name=f"carbontrace_impact_record_{st.session_state.impact_record_id}.csv",
                mime="text/csv",
                key="dashboard_impact_csv",
            )

        with st.expander("🔐 CLAIM / AUDIT LAYER dashboard", expanded=True):
            st.dataframe(dashboard_audit_df.T.rename(columns={0: "Value"}), use_container_width=True)
            st.download_button(
                "Download CLAIM / AUDIT CSV",
                data=dashboard_audit_df.to_csv(index=False).encode("utf-8"),
                file_name=f"carbontrace_claim_audit_{st.session_state.impact_record_id}.csv",
                mime="text/csv",
                key="dashboard_audit_csv",
            )
    else:
        st.info(
            "No project has been completed yet. Go to the 🌱 Impact tab, select a programme and "
            "complete the demonstration delivery to populate Project Evidence, Impact Record and Claim / Audit dashboards."
        )


# ============================================================
# EMISSIONS TAB
# ============================================================

with tab_emissions:

    st.subheader("🧪 Multi-pollutant emissions profile")

    cols = st.columns(5)

    pollutant_metrics = [
        (
            "CO₂",
            f"{latest.exhaust_co2_percent:.2f} %",
            "Measured concentration",
        ),
        (
            "CO",
            f"{latest.co_ppm:.0f} ppm",
            "Future gas sensor",
        ),
        (
            "O₂",
            f"{latest.o2_percent:.1f} %",
            "Future gas sensor",
        ),
        (
            "NOx",
            f"{latest.nox_ppm:.0f} ppm",
            "Future NOx sensor",
        ),
        (
            "HC",
            f"{latest.hc_ppm:.0f} ppm",
            "Future gas sensor",
        ),
    ]

    for col, (label, value, note) in zip(
        cols,
        pollutant_metrics,
    ):

        with col:

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-note">{note}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    c1, c2 = st.columns(2)

    with c1:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["nox_ppm"],
                name="NOx",
                mode="lines",
            )
        )

        fig.update_layout(
            title="NOx trend",
            height=300,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with c2:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["co_ppm"],
                name="CO",
                mode="lines",
            )
        )

        fig.update_layout(
            title="CO trend",
            height=300,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    st.subheader("Exhaust conditions")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Exhaust temperature",
        f"{latest.exhaust_temperature_c:.0f} °C",
    )

    c2.metric(
        "Exhaust pressure",
        f"{latest.exhaust_pressure_kpa:.2f} kPa",
    )

    c3.metric(
        "Exhaust flow",
        f"{latest.exhaust_flow_kg_s:.4f} kg/s",
    )

    st.info(
        "Important: gas concentration alone is not equivalent to "
        "mass emissions. CarbonTrace is architected to combine "
        "gas concentration with exhaust flow, vehicle data and "
        "time to estimate emissions."
    )

    st.warning(
        "DEMONSTRATION NOTICE: The displayed emissions values are "
        "simulated. Production measurements require appropriate "
        "calibrated instrumentation, sampling, flow measurement, "
        "validation and applicable regulatory methodology."
    )


# ============================================================
# AI ANALYSIS
# ============================================================

with tab_ai:

    st.subheader("🤖 CarbonTrace AI analysis")

    if events:

        strongest = max(
            events,
            key=lambda x: x["score"],
        )

        st.warning(
            f"High-emission event detected at "
            f"{strongest['timestamp'].strftime('%H:%M:%S')}"
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Event score",
            f"{strongest['score']}/100",
        )

        c2.metric(
            "CO₂ rate",
            f"{strongest['co2_rate']:.2f} g/s",
        )

        c3.metric(
            "Engine load",
            f"{strongest['load']:.0f}%",
        )

        c4.metric(
            "Speed",
            f"{strongest['speed']:.0f} km/h",
        )

        st.markdown("### Possible contributing factors")

        for cause in strongest["causes"]:

            st.write(
                "• " + cause
            )

    else:

        st.success(
            "No significant emissions event detected."
        )

    st.divider()

    st.markdown(
        "### 🔍 AI-generated operational recommendations"
    )

    for rec in recommendations:

        st.markdown(
            f"""
            <div class="recommendation">
                <b>{rec['priority']} PRIORITY</b>
                <h3>{rec['title']}</h3>

                <p>
                <b>Why CarbonTrace flagged this:</b><br>
                {rec['reason']}
                </p>

                <p>
                <b>Recommended action:</b><br>
                {rec['action']}
                </p>

                <p>
                <b>Illustrative potential:</b>
                {rec['potential']}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(
        "AI recommendations shown here are demonstration rules. "
        "Future models can learn from longitudinal vehicle, route, "
        "driver, load, weather and emissions data."
    )


# ============================================================
# REDUCE TAB
# ============================================================

with tab_reduce:

    st.subheader("⬇️ Reduce before environmental contribution")

    st.write(
        "CarbonTrace follows a reduction-first pathway: "
        "measure emissions, identify operational improvements, "
        "reduce where possible, then assess the residual impact "
        "basis for potential environmental action."
    )

    illustrative_reduction = 0.11

    potential_reduction_kg = (
        metrics["co2_kg"]
        * illustrative_reduction
    )

    residual_kg = (
        metrics["co2_kg"]
        - potential_reduction_kg
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Current estimated emissions",
        f"{metrics['co2_kg']:.1f} kg",
    )

    c2.metric(
        "Illustrative reduction opportunity",
        f"{potential_reduction_kg:.1f} kg",
    )

    c3.metric(
        "Illustrative residual basis",
        f"{residual_kg:.1f} kg",
    )

    st.divider()

    st.markdown("### Recommended reduction programme")

    reduction_programme = [
        (
            "1",
            "Driver efficiency",
            "Identify aggressive acceleration and high-load events.",
        ),
        (
            "2",
            "Idle reduction",
            "Identify avoidable engine-running periods.",
        ),
        (
            "3",
            "Route optimisation",
            "Compare routes by CO₂ per kilometre and journey conditions.",
        ),
        (
            "4",
            "Vehicle comparison",
            "Benchmark vehicles under comparable operating conditions.",
        ),
        (
            "5",
            "Predictive maintenance",
            "Investigate persistent abnormal emissions patterns.",
        ),
    ]

    for number, title, description in reduction_programme:

        st.markdown(
            f"""
            <div class="recommendation">
                <b>{number}. {title}</b>
                <p>{description}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.warning(
        "The 11% reduction figure is illustrative demonstration "
        "logic only. Production CarbonTrace must calculate reduction "
        "potential from validated vehicle-specific evidence."
    )

    st.divider()

    st.markdown("### 🔬 CarbonTrace measurement philosophy")

    st.write(
        "The production system should compare multiple evidence "
        "streams rather than relying on a single sensor."
    )

    evidence_df = pd.DataFrame(
        [
            [
                "Exhaust measurement",
                "CO₂ concentration + exhaust flow",
                "Direct emissions evidence",
            ],
            [
                "Fuel / ECU",
                "Fuel rate + engine parameters",
                "Independent emissions estimate",
            ],
            [
                "Vehicle dynamics",
                "Speed + RPM + load",
                "Operating-condition context",
            ],
            [
                "GNSS",
                "Position + route + distance",
                "Journey context",
            ],
            [
                "Environmental",
                "Temperature + humidity + pressure",
                "Measurement/context correction",
            ],
        ],
        columns=[
            "Evidence stream",
            "Inputs",
            "Purpose",
        ],
    )

    st.dataframe(
        evidence_df,
        use_container_width=True,
        hide_index=True,
    )

    st.success(
        "Long-term objective: independent measurement pathways "
        "can be compared to identify anomalies, sensor faults and "
        "calculation discrepancies."
    )


# ============================================================
# IMPACT TAB
# ============================================================

with tab_impact:

    st.subheader("🌱 Environmental impact pathway")

    st.write(
        "Select an environmental programme, choose a delivery quantity and review "
        "an illustrative programme price. Project evidence is recorded separately "
        "from the vehicle emissions calculation."
    )

    st.markdown(
        """
        <div class="guardrail-card">
            <h3>⚠️ Carbon accounting & claims safeguard</h3>
            <p>
            Programme pricing is an <b>illustrative estimate</b> and is not a carbon-credit price.
            CarbonTrace does not automatically convert programme quantities into CO₂ removal,
            tree-equivalent offsets or carbon neutrality. Any CO₂ amount shown as project evidence
            must come from appropriate project documentation and verification.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_project = st.radio(
        "1. Customer project choice",
        list(PROJECTS.keys()),
        index=list(PROJECTS.keys()).index(st.session_state.selected_project),
        horizontal=True,
        key="impact_project_choice",
    )
    st.session_state.selected_project = selected_project
    selected_data = PROJECTS[selected_project]
    package = PROJECT_PACKAGES[selected_project]

    selected_score = next(
        x["score"] for x in project_matches if x["project"] == selected_project
    )

    st.markdown(
        f"""
        <div class="impact-card">
            <h2>{selected_project}</h2>
            <b>{selected_data['tag']}</b>
            <p>{selected_data['description']}</p>
            <h4>CarbonTrace demonstration match score</h4>
            <div class="big-number">{selected_score}/100</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(selected_data["customer_value"])

    st.divider()
    st.markdown("### 2. Programme quantity & pricing estimate")

    q1, q2, q3 = st.columns(3)
    with q1:
        quantity = st.number_input(
            package["quantity_label"],
            min_value=int(package["minimum_quantity"]),
            value=max(int(st.session_state.project_quantity), int(package["minimum_quantity"])),
            step=100,
            key="impact_quantity",
        )
    with q2:
        st.metric(
            "Illustrative price / unit",
            money(package["price_per_unit"]),
            package["unit"],
        )
    estimated_price = quantity * package["price_per_unit"]
    with q3:
        st.metric("Illustrative programme price", money(estimated_price))

    st.caption(
        "Pricing is a configurable demonstration estimate only. A production version should use "
        "a live partner quotation, geography, delivery cost, taxes and project-specific terms."
    )

    st.divider()
    st.markdown("### 3. Project evidence")

    st.write(
        "Enter a CO₂ amount only when it is supported by the environmental project's own "
        "appropriate accounting/evidence. CarbonTrace does not calculate this amount from the "
        "number of tree pots, trees or kilograms of biochar."
    )

    e1, e2 = st.columns(2)
    with e1:
        evidence_status = st.selectbox(
            "Project evidence status",
            [
                "Pending project evidence",
                "Project documentation supplied — not independently audited",
                "Independent verification evidence supplied",
            ],
            index=[
                "Pending project evidence",
                "Project documentation supplied — not independently audited",
                "Independent verification evidence supplied",
            ].index(st.session_state.project_evidence_status),
            key="impact_evidence_status",
        )
    with e2:
        co2_evidence_kg = st.number_input(
            "CO₂ project evidence / credited amount (kg CO₂e)",
            min_value=0.0,
            value=float(st.session_state.project_co2_evidence_kg),
            step=1.0,
            help="Enter only an amount supported by project documentation. This field does not calculate CO₂ from programme quantity.",
            key="impact_co2_evidence",
        )

    st.session_state.project_quantity = quantity
    st.session_state.project_co2_evidence_kg = co2_evidence_kg
    st.session_state.project_evidence_status = evidence_status

    if co2_evidence_kg > 0 and evidence_status == "Pending project evidence":
        st.warning(
            "A CO₂ evidence amount has been entered but the evidence status is still pending. "
            "For production use, link the amount to project documentation before presenting it as verified."
        )

    st.divider()
    st.markdown("### 4. Emissions context")

    c1, c2, c3 = st.columns(3)
    c1.metric("Trip estimated CO₂", f"{metrics['co2_kg']:.1f} kg")
    c2.metric("Illustrative reduction opportunity", f"{potential_reduction_kg:.1f} kg")
    c3.metric("Illustrative residual basis", f"{residual_kg:.1f} kg")

    st.caption(
        "Vehicle emissions figures are demonstration calculations from simulated data and are not a verified carbon liability."
    )

    st.divider()
    st.markdown("### 5. Project completion")

    st.write(
        f"**Programme:** {package['program']}  \n"
        f"**Quantity:** {quantity:,} {package['unit']}  \n"
        f"**Illustrative programme value:** {money(estimated_price)}"
    )

    if st.session_state.project_completed:
        st.success(
            "Project selection recorded as completed in this demonstration. "
            "The dashboard now exposes the Project Evidence, Impact Record and Claim / Audit layers."
        )
    else:
        if st.button("✅ Complete project delivery (demonstration)", type="primary", use_container_width=True):
            st.session_state.project_completed = True
            st.rerun()

    st.divider()
    st.markdown("### 6. Project evidence dashboard")

    if st.session_state.project_completed:
        evidence_display = "Pending" if co2_evidence_kg <= 0 else f"{co2_evidence_kg:,.2f} kg CO₂e"
        evidence_label = (
            "CO₂ evidenced / credited"
            if evidence_status == "Independent verification evidence supplied" and co2_evidence_kg > 0
            else "CO₂ project evidence"
        )
        pc1, pc2, pc3, pc4 = st.columns(4)
        pc1.metric("Project status", "COMPLETED")
        pc2.metric("Programme delivered", f"{quantity:,} {package['unit']}")
        pc3.metric(evidence_label, evidence_display)
        pc4.metric("Programme value", money(estimated_price))

        if co2_evidence_kg > 0:
            if evidence_status == "Independent verification evidence supplied":
                st.success(
                    f"Project evidence records {co2_evidence_kg:,.2f} kg CO₂e. "
                    "This figure is displayed as project evidence and does not by itself make the vehicle journey carbon neutral."
                )
            else:
                st.info(
                    f"Project documentation currently records {co2_evidence_kg:,.2f} kg CO₂e. "
                    "It is not presented as independently verified until the required verification evidence is available."
                )
        else:
            st.info(
                "Project completed, but no project-level CO₂ evidence has been entered. "
                "CarbonTrace will not invent or calculate a compensated amount from programme quantity."
            )

    st.divider()
    st.markdown("### 7. IMPACT RECORD")

    impact_record = build_impact_record(
        selected_project,
        selected_data,
        package,
        quantity,
        estimated_price,
        metrics,
        customer_goal,
        co2_evidence_kg,
        evidence_status,
    )
    impact_df = pd.DataFrame([impact_record])
    st.dataframe(impact_df.T.rename(columns={0: "Value"}), use_container_width=True)

    impact_csv = impact_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download IMPACT RECORD — CSV",
        data=impact_csv,
        file_name=f"carbontrace_impact_record_{st.session_state.impact_record_id}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.divider()
    st.markdown("### 8. CLAIM / AUDIT LAYER")

    audit_record = build_claim_audit_record(impact_record, selected_data)
    audit_df = pd.DataFrame([audit_record])
    st.dataframe(audit_df.T.rename(columns={0: "Value"}), use_container_width=True)

    audit_csv = audit_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download CLAIM / AUDIT LAYER — CSV",
        data=audit_csv,
        file_name=f"carbontrace_claim_audit_{st.session_state.impact_record_id}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.warning(
        "AUDIT STATUS: Demonstration / not independently audited. The audit layer is an evidence "
        "structure, not a certification or carbon-credit issuance record."
    )

    st.divider()
    st.markdown("### 9. Share the impact story")

    caption = social_caption(impact_record)
    st.text_area(
        "Social media caption",
        value=caption,
        height=140,
        key="social_caption",
    )

    st.info(
        "For LinkedIn, X and other networks, use the links below with the prepared caption. "
        "Instagram does not provide a reliable desktop URL for pre-filling a post caption, so "
        "the caption can be copied and the downloaded record/audit file can be used as supporting material."
    )

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        linkedin_url = "https://www.linkedin.com/feed/?shareActive=true"
        st.link_button("🔗 LinkedIn", linkedin_url, use_container_width=True)
    with s2:
        x_url = "https://x.com/intent/post?text=" + urllib.parse.quote(caption)
        st.link_button("𝕏 X", x_url, use_container_width=True)
    with s3:
        st.link_button("📸 Instagram", "https://www.instagram.com/", use_container_width=True)
    with s4:
        st.link_button("🌐 Facebook", "https://www.facebook.com/", use_container_width=True)

    st.caption(
        "Social sharing is informational. CarbonTrace does not publish, certify, purchase, retire or "
        "transfer carbon credits through these links."
    )

    st.divider()
    st.markdown("### 🔎 Evidence required for a future verified claim")

    due_diligence = [
        "Project identity and responsible organisation",
        "Project location and ownership / management information",
        "Intervention and delivery evidence",
        "Applicable recognised carbon methodology, where relevant",
        "Additionality and permanence assessment, where relevant",
        "Monitoring and independent verification evidence",
        "Financial and project traceability",
        "Registry / issuance / retirement evidence where applicable",
        "Double-counting controls",
    ]

    for i, item in enumerate(due_diligence, start=1):
        st.write(f"**{i}.** {item}")

    st.success(
        "Customer journey: MEASURE → UNDERSTAND → REDUCE → SELECT PROGRAMME → COMPLETE → "
        "PROJECT EVIDENCE → IMPACT RECORD → CLAIM / AUDIT LAYER"
    )


# ============================================================
# PROJECT COMPARISON
# ============================================================

with tab_impact:

    st.divider()

    st.subheader("🏆 CarbonTrace project matching")

    st.write(
        "The recommendation engine can eventually match customer "
        "preferences, geography, budget, carbon-removal requirements, "
        "community objectives and project verification status."
    )

    comparison_rows = []

    for result in project_matches:

        project_name = result["project"]

        comparison_rows.append(
            [
                project_name,
                result["score"],
                result["data"]["type"],
                result["data"]["tag"],
            ]
        )

    comparison_df = pd.DataFrame(
        comparison_rows,
        columns=[
            "Project pathway",
            "Demonstration match",
            "Project type",
            "Focus",
        ],
    )

    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Match scores are demonstration logic only. Production "
        "matching should use customer requirements and verified "
        "project metadata rather than arbitrary scores."
    )


# ============================================================
# DATA & SENSOR TAB
# ============================================================

with tab_data:

    st.subheader("🗃 CarbonTrace data architecture")

    st.write(
        "The production platform should preserve raw measurements, "
        "processed calculations, intelligence outputs and project "
        "evidence as separate layers."
    )

    # --------------------------------------------------------
    # DATA LAYERS
    # --------------------------------------------------------

    data_layers = pd.DataFrame(
        [
            [
                "Layer 1",
                "RAW",
                "Direct sensor / CAN / GPS readings",
                "Never overwrite",
            ],
            [
                "Layer 2",
                "PROCESSED",
                "Cleaned data and calculated emissions",
                "Version calculations",
            ],
            [
                "Layer 3",
                "INTELLIGENCE",
                "Events, anomalies, predictions and recommendations",
                "Explainable AI",
            ],
            [
                "Layer 4",
                "IMPACT",
                "Environmental project records",
                "Evidence + traceability",
            ],
            [
                "Layer 5",
                "AUDIT",
                "Calibration, methodology and verification evidence",
                "Immutable / traceable",
            ],
        ],
        columns=[
            "Layer",
            "Type",
            "Purpose",
            "Rule",
        ],
    )

    st.dataframe(
        data_layers,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # SENSOR READINESS
    # --------------------------------------------------------

    st.subheader("🔌 Sensor readiness")

    readiness = []

    for key, info in SENSOR_ARCHITECTURE.items():

        if key in [
            "ambient_temperature_c",
            "ambient_humidity_percent",
        ]:

            status = "🟢 Existing ATLAS"

        else:

            status = "🟡 Interface ready"

        readiness.append(
            [
                info["label"],
                info["unit"],
                info["source"],
                info["type"],
                status,
            ]
        )

    readiness_df = pd.DataFrame(
        readiness,
        columns=[
            "Signal",
            "Unit",
            "Source",
            "Data type",
            "Status",
        ],
    )

    st.dataframe(
        readiness_df,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # ADDITIONAL ARCHITECTURE
    # --------------------------------------------------------

    st.subheader("🧠 Production intelligence architecture")

    st.markdown(
        """
        <div class="architecture-card">
        <b>1. Sensor ingestion</b><br>
        ATLAS + gas sensors + temperature + pressure + exhaust flow
        + GPS/GNSS + CAN/J1939 + fuel/ECU data
        </div>

        <div class="architecture-card">
        <b>2. Data quality layer</b><br>
        Timestamping + sensor health + missing values +
        range checks + calibration status + signal plausibility
        </div>

        <div class="architecture-card">
        <b>3. Emissions calculation layer</b><br>
        Concentration + exhaust flow + time + vehicle context →
        estimated mass emissions
        </div>

        <div class="architecture-card">
        <b>4. Independent cross-check</b><br>
        Exhaust-derived CO₂ estimate compared against
        fuel/ECU-derived CO₂ estimate
        </div>

        <div class="architecture-card">
        <b>5. Intelligence layer</b><br>
        Event detection + anomaly detection + vehicle baseline +
        route intelligence + driver behaviour + predictive maintenance
        </div>

        <div class="architecture-card">
        <b>6. Reduction layer</b><br>
        Identify operational changes before environmental contribution
        </div>

        <div class="architecture-card">
        <b>7. Environmental project layer</b><br>
        Match customer objectives with project type, geography,
        verification and environmental/community outcomes
        </div>

        <div class="architecture-card">
        <b>8. Claims & audit layer</b><br>
        Keep measured emissions, calculated emissions,
        environmental contributions and verified carbon units
        as separate records
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # HARDWARE ARCHITECTURE
    # --------------------------------------------------------

    st.subheader("🔗 Future hardware architecture")

    st.code(
        """
                         CARBONTRACE × ATLAS
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
           ATLAS             EXHAUST SYSTEM       VEHICLE
              │                   │                   │
       Temp / Humidity        CO₂ NDIR             OBD-II
       Ambient pressure       CO                     │
       Ambient CO₂            O₂                  CAN
                              NOx                    │
                              HC                  J1939
                              PM                     │
                              Temp                   │
                              Pressure               │
                              Flow                   │
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                              GPS / GNSS
                                  │
                                  ▼
                         SENSOR INGESTION
                                  │
                                  ▼
                           DATA QUALITY
                                  │
                   ┌──────────────┴──────────────┐
                   │                             │
                   ▼                             ▼
                RAW DATA                   SENSOR HEALTH
                   │
                   ▼
                       EMISSIONS ENGINE
                   │
          ┌────────┼────────┬────────┐
          │        │        │        │
         CO₂      CO       NOx      HC / PM
          │
          ▼
                  MASS EMISSIONS
          │
          ├───────────────┐
          │               │
          ▼               ▼
   EXHAUST-BASED     FUEL / ECU-BASED
   CO₂ ESTIMATE      CO₂ ESTIMATE
          │               │
          └───────┬───────┘
                  ▼
             CROSS-CHECK
                  │
                  ▼
             AI ANALYSIS
                  │
          ┌───────┴────────┐
          │                │
          ▼                ▼
     EVENT DETECTION   PREDICTION
          │                │
          └───────┬────────┘
                  ▼
            REDUCTION ENGINE
                  │
                  ▼
          RESIDUAL BASIS
                  │
                  ▼
        PROJECT MATCHING
                  │
       ┌──────────┼──────────┐
       │          │          │
    Woodland   Agroforestry Biochar
       │          │          │
       └──────────┼──────────┘
                  │
                  ▼
        Community projects
                  │
                  ▼
          PROJECT EVIDENCE
                  │
                  ▼
            IMPACT RECORD
                  │
                  ▼
         CLAIM / AUDIT LAYER

IMPORTANT:
Environmental contribution ≠ automatically a carbon credit.
Carbon removal claim ≠ automatically carbon neutrality.
Tree planting ≠ automatically verified carbon removal.
        """,
        language="text",
    )

    # --------------------------------------------------------
    # DATA PROVENANCE
    # --------------------------------------------------------

    st.subheader("🔐 Data provenance & evidence")

    provenance_df = pd.DataFrame(
        [
            [
                "Sensor ID",
                "Which physical sensor produced the reading",
            ],
            [
                "Timestamp",
                "When the measurement occurred",
            ],
            [
                "Calibration status",
                "Whether the sensor is within calibration requirements",
            ],
            [
                "Raw value",
                "Original measurement before processing",
            ],
            [
                "Processed value",
                "Value after validated processing",
            ],
            [
                "Calculation version",
                "Version of emissions algorithm used",
            ],
            [
                "Vehicle ID",
                "Vehicle associated with the measurement",
            ],
            [
                "Route / GPS",
                "Journey and location context",
            ],
            [
                "Project ID",
                "Environmental project associated with impact record",
            ],
            [
                "Verification evidence",
                "Evidence supporting future environmental claims",
            ],
        ],
        columns=[
            "Field",
            "Purpose",
        ],
    )

    st.dataframe(
        provenance_df,
        use_container_width=True,
        hide_index=True,
    )

    # --------------------------------------------------------
    # EXPORT
    # --------------------------------------------------------

    st.subheader("📥 Export demonstration data")

    csv = df.to_csv(
        index=False
    )

    st.download_button(
        label="Download simulated sensor dataset",
        data=csv,
        file_name="carbontrace_demo_sensor_data.csv",
        mime="text/csv",
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    ### CarbonTrace × ATLAS

    **MEASURE → UNDERSTAND → REDUCE → RESPONSIBLY MANAGE IMPACT**

    CarbonTrace is currently a research and demonstration platform.
    Emissions values shown in this prototype are simulated.

    The platform does not currently:
    - sell carbon credits
    - process environmental payments
    - calculate a guaranteed number of trees required to offset emissions
    - issue carbon-removal certificates
    - automatically declare customers carbon neutral

    Any future carbon-credit or carbon-removal claim should be based
    on appropriate project-level accounting, recognised methodology,
    verification, traceability and applicable standards.
    """,
)

st.caption(
    "CarbonTrace × ATLAS — XNetwork research and demonstration platform."
)

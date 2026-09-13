# CarbonTrace × ATLAS Demo

A pitch-ready Streamlit prototype using simulated emissions data.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Design

The simulator is deliberately separated conceptually from the dashboard. Replace `make_demo_data()` with ATLAS sensor/CAN/GPS drivers when hardware is connected.

Current UI demonstrates:

- Live emissions cockpit
- CO2, NOx, temperature, load and speed
- Journey emissions
- CO2 intensity
- AI-style anomaly/reduction insights
- Four customer environmental pathways
- Impact ID
- Sensor-readiness map
- Clear SIMULATED DATA labeling

Important: current values are illustrative only and are not regulatory-grade emissions measurements.

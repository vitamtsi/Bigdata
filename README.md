Interactive Data Exploration of Air Pollution Across European Capital Cities (2018–2025)

This repository contains the full implementation of an interactive dashboard for exploring nitrogen dioxide (NO₂) concentrations across European capital cities from 2018–2025. The dashboard is built using Streamlit and provides a user-friendly environment for filtering, visualizing, and comparing air-quality data.

The project is part of Project 7: User/Data Interaction (HCI, M2M, UI, UX) in the Big Data Systems coursework.

Live Application

The dashboard is publicly available here: https://bigdata-vitamtsi.streamlit.app/

No installation required — the app loads directly in your browser.

Repository Structure

.devcontainer/
clean_no2_long.csv          # cleaned dataset (Eurostat env_air_no2)
no2_rf_pipeline.pkl         # ML model from Project 5 
project7_app.py             # Streamlit dashboard source code
requirements.txt            # package dependencies for Streamlit Cloud
README.md                   # documentation

 Dashboard Overview

The application presents interactive visual analytics through four main tabs:

1. NO₂ Over Time
	•	Multiselect menu to choose cities
	•	Adjustable year range slider
	•	High-resolution time-series visualization

2. NO₂ Levels by City
	•	Month-by-month comparison
	•	Color-coded bars indicating deviation from the EU27 aggregate:
	•	🔴 red = higher than EU average
	•	🟢 green = lower than EU average
	•	🟡 yellow = EU27 aggregate

3. Correlation (Time vs NO₂)
	•	Correlation coefficient for each city
	•	Reversed RdYlGn color scale (greener = stronger decrease over time)

4. Seasonal Variation
	•	Boxplot distribution across Winter, Spring, Summer, Autumn
	•	Intuitive color palette (purple/gold/green/orange)
	•	Hover tooltips with per-city NO₂ values

Key Features
	•	Interactive UI (sliders, dropdowns, multiselects)
	•	Dynamic Plotly charts
	•	Automatic data processing on load
	•	Efficient caching with @st.cache_data
	•	Consistent color semantics and layout
	•	Designed according to HCI heuristics (Nielsen, 1994)
	•	Supports both human users and programmatic access use cases


Installation (Local Use)

1. Clone the repository

2. Install dependencies

(Use exactly the versions in requirements.txt)

pip install -r requirements.txt

3. Run Streamlit app

streamlit run project7_app.py

Dependencies

Main packages:
	•	streamlit
	•	pandas
	•	plotly
	•	numpy

All dependencies are listed in requirements.txt for reproducibility.

Data Source

The dashboard uses NO₂ concentration data from Eurostat:
Dataset: env_air_no2
https://ec.europa.eu/eurostat/databrowser/view/env_air_no2/default/table?lang=en&category=env.env_air.env_air_ 

Values represent monthly mean nitrogen dioxide levels (µg/m³) for European capital cities.

Data processing steps (cleaning, reshaping) were completed in previous projects and saved as clean_no2_long.csv.


Usability & UX Evaluation

A short heuristic evaluation and test with sample users showed:

✔ intuitive navigation via tab structure
✔ clear color coding and minimal cognitive load
✔ responsive graph updates
✔ meaningful tooltips and labels

Users found the design accessible and informative.

<img width="1315" height="385" alt="Screenshot 2025-11-17 at 21 03 53" src="https://github.com/user-attachments/assets/e79335b6-29a5-4c46-9f7b-80457f863674" />



Relevant Course Projects

This dashboard builds upon earlier project outputs:
	•	Project 1–3: Data acquisition, cleaning, pipelines
	•	Project 4: Feature engineering
	•	Project 5: ML pipeline (saved as no2_rf_pipeline.pkl)
	•	Project 6: REST API deployment with Flask

Project 7 completes the workflow by adding an interactive analytics interface.

License

This project is for educational purposes under the Big Data Systems module.

Acknowledgements
	•	Eurostat for open environmental data
	•	Streamlit for free cloud deployment
	•	University staff for guidance



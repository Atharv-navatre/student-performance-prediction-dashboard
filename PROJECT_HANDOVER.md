# Student Performance Predictor - Project Handover

## Overview
This project is an end-to-end Machine Learning web application designed to predict student performance, analyze educational factors, and identify at-risk students. The system uses an XGBoost machine learning model, a Flask REST API backend, a Streamlit interactive frontend, and a Supabase (PostgreSQL) remote database.

## Architecture & Tech Stack
- **Frontend**: Streamlit (`dashboard/`) - Features custom CSS glass-morphism UI, interactive charts (Plotly), and multi-page navigation (Home, Predict, Analytics Dashboard, At-Risk, What-If).
- **Backend**: Flask (`api/`) - Serves the REST API to handle prediction requests and fetch aggregated data/stats.
- **Machine Learning**: Scikit-Learn & XGBoost (`ml/`) - Data preprocessing, feature importance mapping, and predictive modeling for student scores.
- **Database**: Supabase (`database/`) - Stores student records, prediction logs, and aggregate insights.
- **Containerization**: Docker & Docker Compose (`docker-compose.yml`, `Dockerfile`) - Containerizes the API and Streamlit apps for easy deployment.

## What Has Been Built (Completed)
1. **ML Pipeline & Data Generator**: Scripts to generate synthetic data, train the XGBoost model, and save `.joblib` artifacts.
2. **REST API**: Endpoints to request live predictions and pull dashboard statistics.
3. **Streamlit Dashboard**:
   - `01_predict.py`: Single student prediction interface.
   - `02_dashboard.py`: Broad analytics dashboard displaying score distribution, feature importance, and recently added **Power BI CSV Export** functionality.
   - `03_at_risk.py`: Highlights students categorized as "At Risk" based on prediction thresholds.
   - `04_what_if.py`: Interactive sliders for teachers to simulate changes in a student's habits (e.g., increasing study hours) to see score impacts.
4. **Database Integration & Pipeline**:
   - `database/supabase_client.py`: Handles Supabase operations. **Crucial Note:** We recently implemented a mapping layer where local key `student_code` is mapped to remote Supabase column `student_name` to fix schema mismatch (42703 column does not exist) errors during insertions.
   - `database/seed.py`: ETL script that clears old data, predicts outcomes for raw data (`StudentPerformanceFactors.csv`), and bulk-inserts records (students, predictions, insights) into Supabase.

## Current State & Remaining Tasks
- **Database Seeding Quirks**: Recently, `database/seed.py` completed but logged `Students inserted: 0` and `Predictions inserted: 0`, throwing warnings like `Skipping prediction; no student id for STUXXXXX`. We just re-applied the `student_name = clean_row.pop("student_code")` mapping logic in `supabase_client.py`'s `bulk_insert_students` to resolve this. 
- **Pending Verification**: We need to successfully run `python database/seed.py` one final time to confirm ~6600 rows insert perfectly into Supabase without skipping records.
- **Final Polish**: Ensure that the Flask API and Streamlit containers (`docker-compose up`) safely pull from this fully seeded remote database and that there are no remaining "No prediction data" states in the UI.

## How to Run locally:
1. To test data ingestion: `python database/seed.py`
2. To run the app suite: `docker-compose down; docker-compose up --build -d`
3. Access UI at `http://localhost:8501`
# 📊 Student Performance Prediction Dashboard

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white" alt="Python 3.11" />
  <img src="https://img.shields.io/badge/XGBoost-Regressor-EC6B23" alt="XGBoost" />
  <img src="https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Flask-API-000000?logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase&logoColor=white" alt="Supabase" />
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/AWS%20EC2-Deployment%20Ready-FF9900?logo=amazonaws&logoColor=white" alt="AWS EC2" />
</p>

<p align="center">
  AI-powered student analytics system that predicts academic performance, detects at-risk students, and provides actionable insights through an interactive dashboard.
</p>

## 🌐 Live Demo

- Dashboard: http://YOUR_EC2_IP:8501
- Note: Click **Enter Dashboard** for instant access

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 Predict | Predicts a student’s exam outcome from academic, behavioral, and background inputs using a trained XGBoost regressor. |
| ⚠️ At-Risk Monitor | Flags vulnerable students, ranks low-performing records, and surfaces intervention-focused cohort views. |
| 🔬 What-If Simulator | Lets educators adjust student factors and instantly observe how predicted performance changes. |
| 📈 Analytics Dashboard | Shows cohort KPIs, score distributions, feature importance, category breakdowns, and insight summaries. |
| 📊 Power BI Export | Exports prediction, at-risk, and summary CSV datasets for downstream reporting and BI workflows. |
| 🔐 Auth System | Includes a lightweight gated landing experience with demo-mode entry for presentations and quick evaluation. |
| 🐳 Docker | Runs the Flask API and Streamlit dashboard in containers with persistent mounted data and model directories. |
| ☁️ AWS EC2 | Structured for deployment on an EC2 instance through Docker Compose and a container-first runtime. |

## 🏗 Architecture

```text
┌───────────────┐
│    Browser    │
└───────┬───────┘
        │
        ▼
┌──────────────────────┐
│ Streamlit UI : 8501  │
└─────────┬────────────┘
          │ HTTP / JSON
          ▼
┌──────────────────────┐        ┌──────────────────────┐
│   Flask API : 5001   │ <----> │   ML Engine          │
│  Gunicorn Runtime    │        │   XGBoost + SKLearn  │
└─────────┬────────────┘        └──────────────────────┘
          │
          ▼
┌──────────────────────┐
│ Supabase PostgreSQL  │
└──────────────────────┘
```

## 🧠 Tech Stack

| Layer | Technology | Purpose |
|------|------------|---------|
| ML | XGBoost, Scikit-learn, Pandas, NumPy | Model training, preprocessing, feature engineering, and prediction |
| API | Flask, Gunicorn | REST interface between dashboard, local fallbacks, and database-backed services |
| UI | Streamlit, Plotly | Interactive dashboard, simulation workflows, and visual analytics |
| DB | Supabase (PostgreSQL) | Cloud persistence for students, predictions, performance history, and insights |
| Infra | Docker, Docker Compose, AWS EC2 | Containerized local deployment and cloud-ready hosting workflow |

## 📊 Model Performance

| Metric | Value |
|--------|-------|
| Algorithm | XGBoost Regressor |
| Dataset | 6,607 students |
| Features | 15 (12 original + 3 engineered) |
| MAE | 1.68 exam points |
| R² Score | 0.504 |
| Training set | 5,285 students |
| Test set | 1,322 students |

## 🚀 Quick Start

### Local Development

```bash
pip install -r requirements.txt
cp .env.example .env
python run_pipeline.py
python database/seed.py
python api/app.py
streamlit run dashboard/app.py
```

### Docker

```bash
docker-compose up --build
```

### AWS EC2

1. Launch an Ubuntu-based EC2 instance and open inbound ports `8501` and `5001` in the security group.
2. Install Docker and Docker Compose on the instance.
3. Copy the project to the instance and configure `.env` with your Supabase credentials.
4. Run `docker-compose up --build -d`.
5. Access the dashboard using `http://YOUR_EC2_IP:8501`.

## 📁 Project Structure

```text
student_performance/
├── api/                          # Flask API package
│   ├── __init__.py               # API package marker
│   └── app.py                    # Flask routes, health checks, and local CSV fallbacks
├── dashboard/                    # Streamlit application
│   ├── .streamlit/
│   │   └── config.toml           # Streamlit theme and sidebar navigation settings
│   ├── components/
│   │   ├── __init__.py           # Components package marker
│   │   ├── cards.py              # Reusable Streamlit card components
│   │   ├── charts.py             # Plotly chart builders
│   │   ├── footer.py             # Shared footer renderer
│   │   └── styles.py             # Shared page styles and page config helpers
│   ├── pages/
│   │   ├── 01_predict.py         # Single-student prediction workflow
│   │   ├── 02_dashboard.py       # Analytics dashboard and exports
│   │   ├── 03_at_risk.py         # At-risk monitoring page
│   │   └── 04_what_if.py         # What-if simulation page
│   ├── __init__.py               # Dashboard package marker
│   ├── app.py                    # Landing page and home dashboard
│   └── auth.py                   # Demo-mode access gate
├── data/                         # Dataset storage
│   ├── processed/
│   │   └── students_clean.csv    # Cleaned dataset used by the app
│   └── raw/
│       ├── StudentPerformanceFactors.csv  # Original Kaggle dataset
│       └── synthetic_students.csv         # Offline testing dataset
├── database/                     # Database schema and seed utilities
│   ├── __init__.py               # Database package marker
│   ├── migrations.sql            # Supabase schema definitions
│   ├── seed.py                   # Database seeding pipeline
│   └── supabase_client.py        # Centralized Supabase access layer
├── exports/                      # Runtime JSON exports
│   ├── insights.json             # Cohort insight export
│   └── prediction.json           # Single prediction export
├── ml/                           # Machine learning pipeline
│   ├── saved_models/
│   │   ├── scaler.joblib         # Saved preprocessing scaler
│   │   └── xgboost_*.joblib      # Versioned trained model artifacts
│   ├── __init__.py               # ML package marker
│   ├── data_generator.py         # Synthetic test-data generator
│   ├── data_loader.py            # Raw Kaggle CSV loader and cleaner
│   ├── insights.py               # Rule-based cohort insight generator
│   ├── model.py                  # Training, evaluation, prediction, and export logic
│   └── preprocessor.py           # Cleaning, feature engineering, and scaling pipeline
├── tests/                        # Test package scaffold
│   └── __init__.py               # Tests package marker
├── .dockerignore                 # Docker build exclusions
├── .env.example                  # Safe environment template
├── .gitignore                    # Git ignore rules
├── config.py                     # Global configuration, paths, schemas, and constants
├── docker-compose.yml            # Multi-container local deployment
├── Dockerfile                    # Unified image definition
├── requirements.txt              # Pinned Python dependencies
├── run_pipeline.py               # End-to-end model orchestration
├── setup_project.py              # Project scaffold script
├── verify_env.py                 # Environment verification helper
└── verify_install.py             # Dependency verification helper
```

## ⚙️ Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Supabase project URL used by the API and dashboard-backed services |
| `SUPABASE_KEY` | Yes | Supabase anon/public key for authenticated database access |
| `FLASK_DEBUG` | Optional | Enables Flask debug mode for local development when set to `true` |
| `API_BASE_URL` | Yes | Base URL used by Streamlit to reach the Flask API |

Example:

```text
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_KEY=your_supabase_anon_key_here
FLASK_DEBUG=false
API_BASE_URL=http://localhost:5001
```

## 📚 Dataset

- Source: Kaggle — **Student Performance Factors**
- Rows used in the project: **6,607 students**
- Raw columns: **20**
- Engineered model features: **15**
- Target variable: **Exam Score**
- Score range used in this project: **55–101**
- Dataset link: https://www.kaggle.com/datasets/lainguyn123/student-performance-factors

## 👨‍💻 Author

**Atharv Navatre**  
Built as a **6th Semester college project**  
Year: **2026**

# LLM_Day

Repository for LLM Day testing.

## About
This repo was created as part of learning Git and GitHub basics.

## Contents
- Notes and experiments from LLM Day
- **Madison, WI Monthly Expense Estimator** — Streamlit web app for estimating monthly living costs

## Running the Expense Estimator

### Install dependencies (first time only)
```bash
pip install streamlit plotly
```

### Launch the app
```bash
cd LLM_Day
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## Files
| File | Purpose |
|---|---|
| `app.py` | Streamlit UI, calculation engine, charts |
| `data.py` | Hardcoded Madison, WI market data (rent, transit, utilities, etc.) |

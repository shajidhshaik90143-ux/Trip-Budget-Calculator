# ✈️ Trip Budget Calculator

A strong, portfolio-ready travel budgeting dashboard built with Python and Streamlit.

## Features

- Trip name, destination, travelers, dates and currency
- Seven major travel expense categories
- Configurable emergency/contingency percentage
- Automatic per-traveler calculations
- Daily budget planning
- Interactive Plotly charts
- Expense distribution and category analytics
- Budget insights
- CSV export
- JSON export
- Responsive Streamlit layout
- Clean modular Python architecture

## Project Structure

```text
Trip Budget Calculator/
├── app.py
├── requirements.txt
├── README.md
└── src/
    ├── __init__.py
    ├── calculator.py
    └── exporter.py
```

## Windows Setup

```powershell
cd "Trip Budget Calculator"
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Then open:

http://localhost:8501

## Notes

The calculator treats category amounts as total trip costs for the entire group. The dashboard then derives per-traveler and daily estimates.

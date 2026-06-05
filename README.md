# Riddell Operations & Financial Dashboard

A Streamlit prototype covering Operational and Financial analytics for Riddell's Gameday store program.

Built with synthetic data — ready to connect to live data sources.

---

## Pages

| Page | Audience | Description |
|------|----------|-------------|
| 🏠 Home | All | Summary KPIs and navigation |
| 📦 Order Pipeline | Supply Chain (Brian) | Open orders by stage, $ and units, backorder flags |
| ⏱️ Aging & SLA | Supply Chain (Brian) | Aging buckets, SLA promise tracking, late orders |
| 🏪 Store Details | Sales / Ops | Stores opened, rep attribution, performance by store |
| 📊 Financial Dashboard | Executive | Monthly shipped recap, CY vs LY, KPI trends |
| 🏆 Scoreboard & Reps | Sales Leadership | Top reps, top regions, top stores, stores created |

---

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Deploy to Streamlit Cloud

1. Push this repo to GitHub (public or private)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app**
4. Select your repo, branch `main`, and set **Main file path** to `app.py`
5. Click **Deploy**

That's it — no config needed for the synthetic data version.

---

## Connect Live Data

Replace `pages_src/data.py` with real data sources:

- **SQL / Azure SQL**: use `sqlalchemy` + `pandas.read_sql()`
- **Azure Data Lake / Fabric**: use `azure-storage-file-datalake` or Fabric REST API
- **CSV uploads**: use `st.file_uploader()` in each page
- **Dynamics 365**: use the Dataverse Web API

Example SQL swap:
```python
# In data.py, replace get_orders() with:
from sqlalchemy import create_engine
engine = create_engine(st.secrets["SQL_CONN"])

def get_orders():
    return pd.read_sql("SELECT * FROM vw_open_orders", engine)
```

Store secrets in `.streamlit/secrets.toml` locally, or in Streamlit Cloud's Secrets manager.

---

## Structure

```
riddell-dashboard/
├── app.py                  # Main entry point + sidebar nav
├── requirements.txt
├── README.md
└── pages_src/
    ├── data.py             # Synthetic data generator (swap for live)
    ├── home.py             # Landing page
    ├── order_pipeline.py   # Order Pipeline view
    ├── aging_sla.py        # Aging report + SLA tracking
    ├── store_details.py    # Store details
    ├── financial.py        # Financial dashboard
    └── scoreboard.py       # Scoreboard & reps
```

---

*Prototype built for Riddell · June 2026*

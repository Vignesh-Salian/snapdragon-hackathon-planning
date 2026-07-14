# Real Data Sources — Blood Demand Forecasting

**TL;DR:** No public dataset matches our 15-feature hospital-demand schema
(hospital_type, dengue_cases_weekly, road_accidents, blood_donation_camp, …).
The public "blood" datasets solve a *different* problem — donor retention, not
hospital demand. So the right approach is **realistic synthetic data calibrated
to real public distributions**, not force-fitting a mismatched dataset.

---

## Why not just use a public dataset?

| Dataset | What it actually is | Fits our schema? |
|---|---|---|
| [UCI / Kaggle Blood Transfusion Service Center](https://www.kaggle.com/datasets/sumedh1507/blood-donor-dataset) (748 rows, RFM) | Predicts whether a **donor** will donate again | ❌ Donor-side, not demand |
| [Kaggle Blood Bank Details](https://www.kaggle.com/datasets/amalsp220/bloodbankdetails) | Blood bank directory / metadata | ❌ No time series / demand target |
| Academic ([Tema Hospital, Ghana](https://www.sciencedirect.com/science/article/pii/S0169207021001710); [COVID LSTM](https://pmc.ncbi.nlm.nih.gov/articles/PMC9359598/)) | Real hospital demand time series | ⚠️ Data private to the studies, not downloadable |

## Recommended: calibrate the synthetic generator with real distributions

Keep `blood_demand.csv` schema-correct, but ground the feature distributions in
real Indian public data so it's defensible to judges ("calibrated to real
epidemiological + climate data"), not arbitrary:

- **Weather (temperature_c, rainfall_mm, season):** IMD / [Kaggle India climate](https://www.kaggle.com/datasets/sumanthvrao/daily-climate-time-series-data)
- **Dengue seasonality (dengue_cases_weekly):** India NVBDCP monthly/weekly reports; WHO Dengue surveillance
- **Road accidents (road_accidents):** India MoRTH "Road Accidents in India" annual tables
- **Blood group distribution (blood_type):** published Indian ABO/Rh frequency tables (O+ ~37%, B+ ~32%, A+ ~22%, AB+ ~7%, negatives rare)

## Optional second model (real data, different task)

If we want a genuinely-real-data model for the demo, the UCI Blood Transfusion
set supports a **donor-return classifier** (will this donor come back?) — a
clean complement to the demand regressor, using real data. Separate endpoint,
does not touch the 15-feature demand model.

> **Decision for the team:** stick with calibrated-synthetic for the demand
> forecaster (no real substitute exists); optionally add the UCI donor-return
> classifier if we want a "trained on real data" talking point.

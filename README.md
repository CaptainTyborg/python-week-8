# CORD-19 Metadata Explorer (Frameworks_Assignment)

This repository contains a starter solution for the CORD-19 metadata assignment.

Files added:
- `cord19_analysis.py`: Data loading, cleaning, and plotting helpers.
- `app.py`: A simple Streamlit application to explore `metadata.csv`.
- `requirements.txt`: Minimal dependencies.

How to run

1. Install dependencies (recommended in a virtualenv):

```powershell
pip install -r requirements.txt
```

2. Put `metadata.csv` in this folder (download from Kaggle or use a smaller sample).

A small sample `metadata.csv` is included in this repository so you can run the app and notebook immediately. Replace it with the full `metadata.csv` downloaded from Kaggle when you're ready to run the full analysis.

3. Run the Streamlit app:

```powershell
streamlit run app.py
```

Notes & next steps
- The starter code performs basic cleaning (datetime parsing, year extraction, word counts).
- Extend the app by adding a word cloud, title search, filtering by journal, or exporting selected rows.

If you want, I can:
- run a quick syntax check on the new files,
- or try loading a small sample of `metadata.csv` if you upload it here.

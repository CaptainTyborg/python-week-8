"""Streamlit app for exploring the CORD-19 `metadata.csv` dataset.

Run with:
    streamlit run app.py

The app loads `metadata.csv` from the same folder. If the file is large,
use a smaller sample (set `nrows` in `load_data`).
"""
import streamlit as st
import pandas as pd
from typing import Optional

import cord19_analysis as ca

st.set_page_config(page_title="CORD-19 Data Explorer", layout="wide")

@st.cache_data
def load_cached(path: str = "metadata.csv", nrows: Optional[int] = None) -> pd.DataFrame:
    return ca.clean_prepare(ca.load_data(path, nrows=nrows))


def main():
    st.title("CORD-19 Data Explorer")
    st.write("A simple starter app to explore the CORD-19 `metadata.csv` file.")

    st.sidebar.header("Configuration")
    sample = st.sidebar.checkbox("Load sample (nrows=20000)", value=True)
    nrows = 20000 if sample else None

    try:
        df = load_cached("metadata.csv", nrows=nrows)
    except FileNotFoundError:
        st.error("Place `metadata.csv` in this folder (the app folder) and reload.")
        return

    st.sidebar.markdown(f"Rows loaded: **{len(df):,}**")

    # year filter
    years = df["year"].dropna().astype(int)
    if not years.empty:
        min_year, max_year = int(years.min()), int(years.max())
        year_range = st.sidebar.slider("Select year range", min_year, max_year, (min_year, max_year))
        df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]

    # top journals
    top_n = st.sidebar.slider("Top journals to show", 5, 30, 10)
    show_wordcloud = st.sidebar.checkbox("Show title word cloud", value=False)

    st.header("Publications Over Time")
    fig_time = ca.plot_publications_over_time(df)
    st.pyplot(fig_time)

    st.header("Top Journals")
    fig_j = ca.plot_top_journals(df, top_n=top_n)
    st.pyplot(fig_j)

    st.header("Source Distribution")
    fig_s = ca.plot_source_distribution(df)
    st.pyplot(fig_s)

    if show_wordcloud:
        st.header("Title Word Cloud")
        try:
            fig_wc = ca.plot_title_wordcloud(df)
            st.pyplot(fig_wc)
        except RuntimeError:
            st.warning("`wordcloud` package is not installed. Add it to `requirements.txt` and install to enable this feature.")

    st.header("Sample of Data")
    st.dataframe(df.head(50))

    st.markdown("---")
    st.write("Notes: This is a starter app. You can extend it with word clouds, text search, and more." )


if __name__ == "__main__":
    main()

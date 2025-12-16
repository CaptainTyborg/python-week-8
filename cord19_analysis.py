"""cord19_analysis.py

Starter analysis utilities for the CORD-19 `metadata.csv` assignment.

Functions here load the CSV, perform light cleaning, compute simple
analytics, and return matplotlib `Figure` objects suitable for a Streamlit app.

Usage:
    python cord19_analysis.py  # will run a small local demo (if metadata.csv exists)
"""
from typing import Optional, Tuple
import os
import re
from collections import Counter

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure

sns.set(style="whitegrid")


def load_data(path: str = "metadata.csv", nrows: Optional[int] = None) -> pd.DataFrame:
    """Load metadata CSV into a DataFrame.

    Parameters
    - path: path to `metadata.csv`
    - nrows: if set, read only that many rows (useful for sampling)
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found: {path}")
    df = pd.read_csv(path, nrows=nrows)
    return df


def basic_explore(df: pd.DataFrame) -> None:
    print("Shape:", df.shape)
    print(df.info())
    print("Missing values (top columns):")
    print(df.isnull().sum().sort_values(ascending=False).head(20))


def clean_prepare(df: pd.DataFrame) -> pd.DataFrame:
    """Perform minimal cleaning and add helpful columns.

    - Convert `publish_time` (or `publish_date`) to datetime if present
    - Extract `year` for time-based analysis
    - Compute `title_word_count` and `abstract_word_count` when available
    """
    df = df.copy()

    # Common column names in different samples
    date_cols = [c for c in df.columns if "publish" in c.lower() or "date" in c.lower()]
    date_col = None
    for c in date_cols:
        if "time" in c.lower() or "date" in c.lower():
            date_col = c
            break

    if date_col is not None:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df["year"] = df[date_col].dt.year
    else:
        df["year"] = pd.NA

    # word counts
    if "title" in df.columns:
        df["title_word_count"] = df["title"].fillna("").astype(str).str.split().map(len)
    if "abstract" in df.columns:
        df["abstract_word_count"] = df["abstract"].fillna("").astype(str).str.split().map(len)

    return df


def top_journals(df: pd.DataFrame, top_n: int = 10) -> pd.Series:
    if "journal" in df.columns:
        return df["journal"].fillna("(unknown)").value_counts().nlargest(top_n)
    # some datasets use `journal_ref` or `journal_name`
    for alt in ["journal_ref", "journal_name"]:
        if alt in df.columns:
            return df[alt].fillna("(unknown)").value_counts().nlargest(top_n)
    return pd.Series(dtype=int)


_SIMPLE_STOPWORDS = {
    "the", "and", "of", "in", "a", "to", "for", "on", "with", "by", "is", "at", "from",
    "an", "as", "using", "study", "studies", "covid", "covid-19", "sars-cov-2",
}


def title_word_frequencies(df: pd.DataFrame, top_n: int = 25) -> Counter:
    text = " ".join(df.get("title", pd.Series()).dropna().astype(str).tolist())
    # simple tokenization
    tokens = re.findall(r"\b[0-9A-Za-z'-]+\b", text.lower())
    tokens = [t for t in tokens if t not in _SIMPLE_STOPWORDS and len(t) > 2]
    return Counter(tokens).most_common(top_n)


def plot_title_wordcloud(df: pd.DataFrame, max_words: int = 100) -> Figure:
    """Generate a wordcloud figure from the `title` column.

    Returns a matplotlib Figure.
    """
    try:
        from wordcloud import WordCloud
    except Exception as e:
        raise RuntimeError("wordcloud package is required for this function") from e

    text = " ".join(df.get("title", pd.Series()).dropna().astype(str).tolist())
    if not text:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No title text available", ha="center")
        return fig

    wc = WordCloud(width=800, height=400, background_color="white", max_words=max_words)
    wc.generate(text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    plt.tight_layout()
    return fig


def plot_publications_over_time(df: pd.DataFrame, year_col: str = "year") -> plt.Figure:
    years = df[year_col].dropna().astype(int)
    counts = years.value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(counts.index.astype(int), counts.values, color="#4C72B0")
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Papers")
    ax.set_title("Publications by Year")
    plt.tight_layout()
    return fig


def plot_top_journals(df: pd.DataFrame, top_n: int = 10) -> plt.Figure:
    series = top_journals(df, top_n=top_n)
    fig, ax = plt.subplots(figsize=(8, 4))
    series.sort_values().plot(kind="barh", ax=ax, color="#55A868")
    ax.set_xlabel("Number of Papers")
    ax.set_title(f"Top {len(series)} Journals by Paper Count")
    plt.tight_layout()
    return fig


def plot_source_distribution(df: pd.DataFrame, source_col: str = "source_x") -> plt.Figure:
    if source_col not in df.columns:
        source_col = [c for c in df.columns if "source" in c.lower()]
        source_col = source_col[0] if source_col else None
    if source_col is None:
        # fallback: empty plot
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No source column found", ha="center")
        return fig
    series = df[source_col].fillna("(unknown)").value_counts()
    fig, ax = plt.subplots(figsize=(6, 4))
    series.nlargest(10).plot(kind="bar", ax=ax, color="#E15759")
    ax.set_ylabel("Number of Papers")
    ax.set_title("Top Sources")
    plt.tight_layout()
    return fig


if __name__ == "__main__":
    # Simple demo runner if the file is executed directly.
    try:
        df = load_data("metadata.csv", nrows=50000)
    except FileNotFoundError:
        print("Place `metadata.csv` in this folder to run the demo.")
    else:
        print("Loaded", df.shape)
        df = clean_prepare(df)
        print("Years available:", df["year"].dropna().unique()[:10])
        print("Top journals:\n", top_journals(df, 10))
        print("Top title words:\n", title_word_frequencies(df, 20))
        fig1 = plot_publications_over_time(df)
        fig1.savefig("publications_by_year.png", dpi=150)
        fig2 = plot_top_journals(df)
        fig2.savefig("top_journals.png", dpi=150)

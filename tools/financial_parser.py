"""Financial Data Parser Tool using Pandas for corporate metrics analysis."""

import config.settings  # noqa: F401 - Initialize environment and cache isolation before crewai imports
from pathlib import Path
import pandas as pd
from crewai.tools import tool
from config.settings import SAMPLE_CSV_PATH


def parse_financial_metrics_df(csv_path: str | Path) -> pd.DataFrame:
    """Load financial metrics from a CSV file and return statistical summary DataFrame.

    Calculates count, mean, std (standard deviation), min, and max for numeric columns.
    """
    path = Path(csv_path)
    if not path.is_absolute():
        # Check relative to workspace or data dir
        if not path.exists() and (Path.cwd() / path).exists():
            path = Path.cwd() / path
        elif not path.exists() and SAMPLE_CSV_PATH.name == path.name:
            path = SAMPLE_CSV_PATH

    if not path.exists():
        raise FileNotFoundError(f"Financial data CSV file not found at: {csv_path}")

    try:
        df = pd.read_csv(path)
    except Exception as exc:
        raise ValueError(f"Failed to parse CSV file '{path.name}': {exc}") from exc

    if df.empty:
        raise ValueError(f"The CSV file at '{path.name}' is empty.")

    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty:
        raise ValueError(f"No numeric columns found in '{path.name}' to analyze.")

    # Calculate required summary statistics: count, mean, std, min, max
    summary = numeric_df.describe().round(2)
    return summary


@tool("calculate_financial_metrics")
def calculate_financial_metrics(csv_path: str) -> str:
    """Loads corporate metrics from CSV and returns summary statistics as Markdown."""
    try:
        summary_df = parse_financial_metrics_df(csv_path)
        markdown_table = summary_df.to_markdown()
        return (
            "### Corporate Financial Metrics Summary Statistics (Illustrative Sample)\n\n"
            f"{markdown_table}\n"
        )
    except Exception as exc:
        return f"Error analyzing financial metrics: {str(exc)}"

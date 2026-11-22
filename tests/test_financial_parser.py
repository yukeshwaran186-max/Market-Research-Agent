"""Unit tests for tools.financial_parser using pytest and mock data."""

import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pytest
import pandas as pd
from tools.financial_parser import calculate_financial_metrics, parse_financial_metrics_df
from config.settings import SAMPLE_CSV_PATH


@pytest.fixture
def mock_csv_file(tmp_path):
    """Fixture providing a mock CSV with known statistical values."""
    csv_file = tmp_path / "mock_metrics.csv"
    # Using simple values:
    # Revenue: [100.0, 200.0, 300.0] -> mean=200.0, min=100.0, max=300.0, std=100.0
    # Operating Margin: [0.10, 0.20, 0.30] -> mean=0.20, min=0.10, max=0.30, std=0.10
    content = (
        "Company,Revenue,Operating Margin\n"
        "Alpha Mock,100.0,0.10\n"
        "Beta Mock,200.0,0.20\n"
        "Gamma Mock,300.0,0.30\n"
    )
    csv_file.write_text(content, encoding="utf-8")
    return str(csv_file)


def test_parse_financial_metrics_df_math(mock_csv_file):
    """Test that parse_financial_metrics_df calculates exact summary statistics."""
    summary = parse_financial_metrics_df(mock_csv_file)
    assert isinstance(summary, pd.DataFrame)

    # Check index operations
    required_stats = ["mean", "std", "min", "max", "count"]
    for stat in required_stats:
        assert stat in summary.index

    # Assert exact statistical values for Revenue
    assert summary.loc["mean", "Revenue"] == 200.0
    assert summary.loc["min", "Revenue"] == 100.0
    assert summary.loc["max", "Revenue"] == 300.0
    assert summary.loc["std", "Revenue"] == 100.0
    assert summary.loc["count", "Revenue"] == 3.0

    # Assert exact statistical values for Operating Margin
    assert summary.loc["mean", "Operating Margin"] == 0.20
    assert summary.loc["min", "Operating Margin"] == 0.10
    assert summary.loc["max", "Operating Margin"] == 0.30
    assert summary.loc["std", "Operating Margin"] == 0.10


def test_calculate_financial_metrics_tool_markdown(mock_csv_file):
    """Test that the calculate_financial_metrics tool returns a valid Markdown table."""
    result = calculate_financial_metrics.run(csv_path=mock_csv_file)
    assert isinstance(result, str)
    assert "### Corporate Financial Metrics Summary Statistics" in result
    assert "| Revenue" in result or "|   Revenue" in result
    assert "| mean" in result or "|:---|:---" in result or "|:------|" in result
    assert "200" in result
    assert "300" in result


def test_sample_csv_dataset_execution():
    """Verify tool runs cleanly on the repository sample CSV."""
    result = calculate_financial_metrics.run(csv_path=str(SAMPLE_CSV_PATH))
    assert "Error analyzing financial metrics" not in result
    assert "Revenue" in result
    assert "Net Income" in result
    assert "mean" in result


def test_missing_file_handling():
    """Verify tool safely handles a missing file without raising an unhandled exception."""
    result = calculate_financial_metrics.run(csv_path="non_existent_path_xyz.csv")
    assert "Error analyzing financial metrics" in result
    assert "not found" in result.lower()


def test_empty_csv_handling(tmp_path):
    """Verify tool safely handles an empty CSV file."""
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("", encoding="utf-8")

    result = calculate_financial_metrics.run(csv_path=str(empty_file))
    assert "Error analyzing financial metrics" in result


def test_non_numeric_csv_handling(tmp_path):
    """Verify tool safely handles a CSV file containing only non-numeric data."""
    text_csv = tmp_path / "text_only.csv"
    text_csv.write_text("Company,Industry,City\nAlpha,Tech,Austin\nBeta,Health,Boston\n", encoding="utf-8")

    result = calculate_financial_metrics.run(csv_path=str(text_csv))
    assert "Error analyzing financial metrics" in result
    assert "no numeric columns" in result.lower()

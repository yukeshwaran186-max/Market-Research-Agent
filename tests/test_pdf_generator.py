"""Automated pytest suite for report.pdf_generator verifying layout and text integrity."""

import sys
from pathlib import Path

# Ensure project root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pytest
import pypdfium2
from report.pdf_generator import generate_pdf_report


@pytest.fixture
def sample_report_markdown():
    """Fixture providing structured Markdown with sections and a tabular grid."""
    return """# Market Research Report: Semiconductor Industry Q3

## 1. Executive Summary
The semiconductor sector demonstrated strong expansion driven by AI acceleration and enterprise infrastructure.

## 2. Market Dynamics & Key Trends
- High-bandwidth memory (HBM) demand increased dramatically.
- Advanced packaging capacity expanded across foundry partners.
- Automotive silicon faced inventory normalization headwinds.

## 3. Quantitative Financial Analysis
Summary statistics for corporate financial metrics across the sector:

| Metric | Revenue ($B) | Net Income ($B) | Operating Margin | R&D ($B) | YoY Growth |
|---|---|---|---|---|---|
| mean | 65.20 | 16.70 | 0.25 | 11.76 | 0.16 |
| min | 34.80 | 7.60 | 0.22 | 7.20 | 0.12 |
| max | 95.00 | 28.40 | 0.30 | 16.10 | 0.22 |
| std | 26.14 | 8.32 | 0.03 | 3.52 | 0.04 |

## 4. Strategic Risk Assessment & Opportunities
1. **Supply Bottlenecks:** Foundry wafer starts require sustained investment.
2. **Geopolitical Factors:** Export regulations necessitate resilient regional supply chains.

## 5. Forward Outlook & Recommendations
Maintain exposure to foundational compute providers with superior margin defensibility.
"""


def test_pdf_generation_file_creation(tmp_path, sample_report_markdown):
    """Verify that generate_pdf_report creates a valid, non-empty PDF file."""
    output_pdf = tmp_path / "test_report.pdf"
    result_path = generate_pdf_report(
        content=sample_report_markdown,
        query="Semiconductor Industry Q3",
        output_path=output_pdf,
    )

    assert result_path.exists()
    assert result_path == output_pdf
    assert result_path.stat().st_size > 1000


def test_pdf_a4_dimensions(tmp_path, sample_report_markdown):
    """Verify that every generated PDF page matches exact A4 dimensions (595.28 x 841.89 pt)."""
    output_pdf = tmp_path / "test_dimensions.pdf"
    generate_pdf_report(
        content=sample_report_markdown,
        query="Semiconductor Industry Q3",
        output_path=output_pdf,
    )

    doc = pypdfium2.PdfDocument(output_pdf)
    assert len(doc) >= 1
    for i in range(len(doc)):
        page = doc[i]
        width, height = page.get_size()
        assert round(width, 1) == 595.3, f"Page {i+1} width {width} != A4 width"
        assert round(height, 1) == 841.9, f"Page {i+1} height {height} != A4 height"


def test_pdf_content_and_page_numbering(tmp_path, sample_report_markdown):
    """Verify that title, query, section headings, tables, and page numbers are present in extracted text."""
    output_pdf = tmp_path / "test_content.pdf"
    generate_pdf_report(
        content=sample_report_markdown,
        query="Semiconductor Industry Q3",
        output_path=output_pdf,
    )

    doc = pypdfium2.PdfDocument(output_pdf)
    all_text = "\n".join([page.get_textpage().get_text_range() for page in doc])

    # Verify banner and metadata
    assert "MARKET RESEARCH REPORT" in all_text
    assert "Semiconductor Industry Q3" in all_text

    # Verify sections
    assert "1. Executive Summary" in all_text
    assert "2. Market Dynamics & Key Trends" in all_text
    assert "3. Quantitative Financial Analysis" in all_text
    assert "4. Strategic Risk Assessment & Opportunities" in all_text
    assert "5. Forward Outlook & Recommendations" in all_text

    # Verify table data
    assert "Revenue" in all_text
    assert "Net Income" in all_text
    assert "65.20" in all_text

    # Verify footer and dynamic page numbering
    assert "Page 1 of" in all_text
    assert "MarketResearchAgent" in all_text


def test_pdf_multipage_handling(tmp_path):
    """Verify that long content spans multiple pages and each page has correct dynamic numbering."""
    output_pdf = tmp_path / "test_multipage.pdf"

    # Generate long content to force a multi-page document
    long_paragraphs = [
        f"## Section {i}\n" + ("This is detailed market intelligence paragraph discussing industry metrics. " * 15)
        for i in range(1, 12)
    ]
    long_content = "\n\n".join(long_paragraphs)

    generate_pdf_report(
        content=long_content,
        query="Multi-Page Market Analysis",
        output_path=output_pdf,
    )

    doc = pypdfium2.PdfDocument(output_pdf)
    total_pages = len(doc)
    assert total_pages > 1, f"Expected multi-page PDF, but got {total_pages} page(s)"

    # Verify dynamic page numbers on each page
    for idx in range(total_pages):
        page_text = doc[idx].get_textpage().get_text_range()
        expected_page_str = f"Page {idx + 1} of {total_pages}"
        assert expected_page_str in page_text, f"Missing '{expected_page_str}' on page {idx + 1}"


def test_pdf_empty_content_handling(tmp_path):
    """Verify that empty or whitespace content compiles cleanly without raising exceptions."""
    output_pdf = tmp_path / "test_empty.pdf"
    result = generate_pdf_report(
        content="",
        query="Empty Report Test",
        output_path=output_pdf,
    )

    assert result.exists()
    assert result.stat().st_size > 500

    doc = pypdfium2.PdfDocument(output_pdf)
    assert len(doc) == 1
    page_text = doc[0].get_textpage().get_text_range()
    assert "Empty Report Test" in page_text
    assert "Page 1 of 1" in page_text

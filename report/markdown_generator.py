"""Markdown Report Generator for compiling structured market research reports."""

from datetime import datetime
from pathlib import Path
from config.settings import MARKDOWN_OUTPUT_PATH


def generate_markdown_report(
    content: str,
    query: str = "Tech Sector Q3 Analysis",
    output_path: str | Path | None = None,
) -> Path:
    """Generate, format, and save a professional Markdown market research report.

    Args:
        content: The text/markdown body produced by the Content Writer or workflow.
        query: Target industry, sector, or company name.
        output_path: Optional custom file path; defaults to MARKDOWN_OUTPUT_PATH.

    Returns:
        Path to the saved Markdown file.
    """
    target_path = Path(output_path or MARKDOWN_OUTPUT_PATH)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    generated_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Safe handling of empty or missing content
    sanitized_content = (content or "").strip()
    if not sanitized_content:
        body = (
            "## 1. Executive Summary\n"
            "No content provided for executive summary.\n\n"
            "## 2. Market Dynamics & Key Trends\n"
            "No market trends data available.\n\n"
            "## 3. Quantitative Financial Analysis\n"
            "No financial analysis available.\n\n"
            "## 4. Strategic Risk Assessment & Opportunities\n"
            "No risk assessment data available.\n\n"
            "## 5. Forward Outlook & Recommendations\n"
            "No forward outlook available.\n"
        )
    else:
        body = sanitized_content

    # Assemble structured document with metadata header banner
    markdown_doc = (
        f"# Market Research Report: {query}\n\n"
        "**Document Metadata:**\n"
        f"- **Subject / Query:** {query}\n"
        f"- **Generated Date:** {generated_date}\n"
        "- **Status:** Final Executive Report\n"
        "- **Notice:** All financial data and corporate metrics represent illustrative sample benchmarks.\n\n"
        "---\n\n"
        f"{body}\n\n"
        "---\n"
        "*Report compiled automatically by MarketResearchAgent.*"
    )

    target_path.write_text(markdown_doc, encoding="utf-8")
    return target_path

"""CrewAI Task definitions for the Market Research workflow."""

from typing import Any
from pathlib import Path
import config.settings  # noqa: F401 - Initialize environment before crewai imports
from crewai import Task, Agent
from config.settings import SAMPLE_CSV_PATH


def create_research_task(
    agent: Agent,
    query: str = "Tech Sector Q3 Analysis",
) -> Task:
    """Create the market intelligence gathering task for the Lead Researcher."""
    return Task(
        description=(
            f"Conduct comprehensive market research on '{query}'. "
            "Use the web search and scraping tool to identify major industry trends, "
            "competitive dynamics, macroeconomic factors, and key technological shifts. "
            "Collect verified source citations and URLs."
        ),
        expected_output=(
            "A structured market research brief including executive highlights, "
            "major industry trends, competitive developments, and verified source citations/URLs."
        ),
        agent=agent,
    )


def create_analysis_task(
    agent: Agent,
    csv_path: str | Path | None = None,
) -> Task:
    """Create the financial data analysis task for the Data Analyst."""
    target_csv = str(csv_path or SAMPLE_CSV_PATH)
    return Task(
        description=(
            f"Analyze corporate financial metrics from the CSV at '{target_csv}'. "
            "Use the calculate_financial_metrics tool to compute summary statistics: "
            "mean, minimum, maximum, and standard deviation for numeric columns. "
            "Present a clean Markdown table of metrics and provide statistical insights on "
            "revenue spreads, operating margin variance, and growth distribution. "
            "Clearly note that figures represent illustrative sample benchmarks."
        ),
        expected_output=(
            "A comprehensive financial analysis report featuring a complete summary statistics "
            "Markdown table (mean, min, max, std), observations on margins and growth, and "
            "an explicit note labeling data as illustrative sample metrics."
        ),
        agent=agent,
    )


def create_writing_task(
    agent: Agent,
    query: str = "Tech Sector Q3 Analysis",
    context_tasks: list[Task] | None = None,
) -> Task:
    """Create the report synthesis task for the Content Writer."""
    return Task(
        description=(
            f"Synthesize the research findings and financial data analysis into an executive-ready "
            f"market research report on '{query}'. "
            "Structure the report with the following sections:\n"
            "1. Executive Summary\n"
            "2. Market Dynamics & Key Trends\n"
            "3. Quantitative Financial Analysis (incorporating the statistical summary table)\n"
            "4. Strategic Risk Assessment & Opportunities\n"
            "5. Forward Outlook & Recommendations\n\n"
            "Ensure copy is professional, balanced, and incorporates both empirical metrics and "
            "qualitative research context. Reference all data sources and maintain clear section headers."
        ),
        expected_output=(
            "A complete, publication-grade market research report in clean Markdown format, "
            "fully incorporating the financial statistics table, detailed market synthesis, "
            "and professional section headers."
        ),
        agent=agent,
        context=context_tasks or [],
    )


def create_market_research_tasks(
    agents: dict[str, Agent],
    query: str = "Tech Sector Q3 Analysis",
    csv_path: str | Path | None = None,
) -> list[Task]:
    """Convenience factory creating and linking all three workflow tasks with dependencies."""
    research_task = create_research_task(
        agent=agents["lead_researcher"],
        query=query,
    )
    analysis_task = create_analysis_task(
        agent=agents["data_analyst"],
        csv_path=csv_path,
    )
    writing_task = create_writing_task(
        agent=agents["content_writer"],
        query=query,
        context_tasks=[research_task, analysis_task],
    )

    return [research_task, analysis_task, writing_task]

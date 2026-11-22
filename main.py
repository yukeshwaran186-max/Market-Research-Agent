"""Main entrypoint for the Multi-Agent Market Research & Report Generator."""

import sys
import argparse
from pathlib import Path

# Ensure early environment setup and sandbox isolation
import config.settings  # noqa: F401
from config.settings import (
    validate_environment,
    SAMPLE_CSV_PATH,
    PDF_OUTPUT_PATH,
    MARKDOWN_OUTPUT_PATH,
    BENCHMARK_PATH,
)
from crew.crew import create_market_research_crew
from report.markdown_generator import generate_markdown_report
from report.pdf_generator import generate_pdf_report
from utils.benchmark import BenchmarkTracker


def run_market_research(
    query: str,
    csv_path: str | Path | None = None,
    mock: bool = False,
) -> dict[str, Path]:
    """Execute the end-to-end Market Research workflow and generate deliverables."""
    print(f"\n==================================================")
    print(f"Starting Market Research Agent Workflow")
    print(f"Query: '{query}'")
    print(f"Mode: {'MOCK (Tokens Preserved)' if mock else 'LIVE HIERARCHICAL CREW'}")
    print(f"==================================================\n")

    tracker = BenchmarkTracker(workflow_name=f"Market Research - {query}")
    resolved_csv = Path(csv_path or SAMPLE_CSV_PATH)

    # Record hierarchical routing plan
    tracker.record_routing("Manager LLM", "Market Research Specialist", "Market Research Intelligence")
    tracker.record_routing("Manager LLM", "Financial Data Analyst", "Financial Data Analysis")
    tracker.record_routing("Manager LLM", "Technical Reports Writer", "Executive Report Synthesis")

    if mock:
        # Cost-free execution path using pre-validated mock intelligence
        tracker.start_task("Mock Research & Analysis Execution", agent_role="Simulated Crew")
        raw_content = (
            f"# Market Research Report: {query}\n\n"
            "## 1. Executive Summary\n"
            f"The {query} demonstrates resilient momentum, driven by capital expenditure expansion and sustained enterprise adoption.\n\n"
            "## 2. Market Dynamics & Key Trends\n"
            "- Accelerated computing and cloud workloads continue to lead segment revenue expansion.\n"
            "- Operating margin leverage reflects strong pricing power across established providers.\n"
            "- R&D investments remain prioritized to maintain competitive technical differentiation.\n\n"
            "## 3. Quantitative Financial Analysis\n"
            "Summary statistics for corporate financial metrics across the analyzed cohort (Illustrative Sample Data):\n\n"
            "| Metric | Revenue ($B) | Net Income ($B) | Operating Margin | R&D Expenses ($B) | YoY Growth |\n"
            "|:---|:---:|:---:|:---:|:---:|:---:|\n"
            "| count | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 |\n"
            "| mean | 65.20 | 16.70 | 0.25 | 11.76 | 0.16 |\n"
            "| std | 26.14 | 8.32 | 0.03 | 3.52 | 0.04 |\n"
            "| min | 34.80 | 7.60 | 0.22 | 7.20 | 0.12 |\n"
            "| max | 95.00 | 28.40 | 0.30 | 16.10 | 0.22 |\n\n"
            "## 4. Strategic Risk Assessment & Opportunities\n"
            "1. **Supply Chain Concentration:** Key foundry and hardware components face tight capacity cycles.\n"
            "2. **Regulatory & Compliance:** Heightened oversight regarding data sovereignty and market concentration.\n\n"
            "## 5. Forward Outlook & Recommendations\n"
            "Maintain focused exposure to high-margin infrastructure providers showing disciplined R&D execution.\n"
        )
        tracker.stop_task("Mock Research & Analysis Execution", status="COMPLETED")
    else:
        # Validate environment before invoking live external models
        env_status = validate_environment(require_tavily=True)
        if not env_status["gemini_api_key"]:
            raise ValueError("GEMINI_API_KEY is not configured in .env.")
        if not env_status["tavily_api_key"]:
            raise ValueError("TAVILY_API_KEY is not configured in .env.")

        # Execute live hierarchical crew
        tracker.start_task("Hierarchical CrewAI Execution", agent_role="Manager LLM")
        crew = create_market_research_crew(
            query=query,
            csv_path=resolved_csv,
            verbose=True,
        )
        result = crew.kickoff(inputs={"query": query})
        raw_content = str(getattr(result, "raw", result))
        tracker.stop_task("Hierarchical CrewAI Execution", status="COMPLETED")

    # 1. Compile Markdown report
    tracker.start_task("Markdown Report Generation", agent_role="Report Compiler")
    markdown_path = generate_markdown_report(content=raw_content, query=query)
    tracker.stop_task("Markdown Report Generation", status="COMPLETED")

    # 2. Compile typeset A4 PDF report
    tracker.start_task("PDF Report Compilation", agent_role="Report Compiler")
    pdf_path = generate_pdf_report(content=raw_content, query=query)
    tracker.stop_task("PDF Report Compilation", status="COMPLETED")

    # 3. Save benchmark analytics
    benchmark_path = tracker.save_to_json()

    print("\n[SUCCESS] Workflow completed successfully!")
    print(f"  - Markdown Report : {markdown_path}")
    print(f"  - Typeset PDF     : {pdf_path}")
    print(f"  - Benchmarks JSON : {benchmark_path}\n")

    return {
        "markdown": markdown_path,
        "pdf": pdf_path,
        "benchmark": benchmark_path,
    }


def parse_arguments() -> argparse.Namespace:
    """Configure and parse CLI command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent Market Research & Report Generator using CrewAI and Gemini."
    )
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        default="Tech Sector Q3 Analysis",
        help="Target industry, sector, or company for market research (e.g., 'Tech Sector Q3 Analysis').",
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Path to financial metrics CSV file (defaults to data/sample_financial_metrics.csv).",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run using mock intelligence without consuming paid external API tokens.",
    )
    return parser.parse_args()


def main() -> None:
    """CLI application entrypoint with robust error handling."""
    args = parse_arguments()
    try:
        run_market_research(
            query=args.query,
            csv_path=args.csv,
            mock=args.mock,
        )
        sys.exit(0)
    except Exception as exc:
        print(f"\n[ERROR] Workflow failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

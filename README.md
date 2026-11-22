# Multi-Agent Market Research & Report Generator with CrewAI

An enterprise-grade multi-agent market research and financial reporting application built using **CrewAI**, **Google Gemini**, **Tavily**, **Pandas**, and **ReportLab**. The application coordinates three specialized autonomous agents managed hierarchically to research market trends, analyze corporate metrics, and compile styled, executive-ready A4 PDF reports alongside execution benchmarks.

---

## 1. Project Overview & Architecture

### Autonomous Agent Roles
1. **Lead Researcher** (`Market Research Specialist`):
   - Queries search engines using the custom Tavily tool (`web_search_and_scrape`).
   - Gathers qualitative market intelligence, competitive positioning, and verified source citations.
2. **Data Analyst** (`Financial Data Analyst`):
   - Uses the Pandas statistical tool (`calculate_financial_metrics`).
   - Computes summary statistics: `mean`, `min`, `max`, and standard deviation (`std`) across corporate financial metrics.
   - Formats statistics into clean Markdown tables.
3. **Content Writer** (`Technical Reports Writer`):
   - Synthesizes findings from both the Researcher and Data Analyst.
   - Authors a structured 5-section executive report (Executive Summary, Market Trends, Financial Analysis, Risk Assessment, and Outlook).

### Hierarchical Orchestration
- Managed hierarchically via `Process.hierarchical` under a supervisor `manager_llm` powered by Google Gemini.
- The manager assigns and coordinates tasks dynamically, enforcing strict context dependencies:
  $$\text{Manager LLM} \longrightarrow \text{Researcher} + \text{Data Analyst} \longrightarrow \text{Content Writer} \longrightarrow \text{Report Compiler}$$

---

## 2. Project Directory Structure

```
MarketResearchAgent/
├── config/
│   └── settings.py               # Paths, environment config, and Gemini LLM factory
├── crew/
│   ├── agents.py                 # 3 specialized CrewAI worker agents
│   ├── tasks.py                  # Sequential & context-dependent tasks
│   └── crew.py                   # Hierarchical Crew setup with manager LLM
├── data/
│   └── sample_financial_metrics.csv # Illustrative corporate financial data
├── output/                       # Generated deliverables
│   ├── market_report.md          # Markdown market report
│   ├── market_report.pdf         # Typeset A4 PDF report
│   └── benchmarks.json           # Task timing and routing metrics
├── report/
│   ├── markdown_generator.py     # Markdown compiler with metadata headers
│   └── pdf_generator.py          # ReportLab A4 compiler with NumberedCanvas
├── tests/
│   ├── test_financial_parser.py  # Pytest suite for Pandas math & error handling
│   └── test_pdf_generator.py     # Pytest suite for PDF layout, A4 size & text
├── tools/
│   ├── financial_parser.py       # @tool calculate_financial_metrics
│   └── web_search.py             # @tool web_search_and_scrape (Tavily)
├── utils/
│   └── benchmark.py              # BenchmarkTracker for execution analytics
├── .env                          # Local API keys (excluded from git)
├── .env.example                  # Template for API keys
├── .gitignore                    # Git exclusions
├── main.py                       # CLI application entrypoint
├── requirements.txt              # Project Python dependencies
└── README.md                     # Project documentation
```

---

## 3. Installation & Setup (Windows PowerShell)

### Prerequisites
- Python 3.11 installed.
- Valid Google Gemini API Key and Tavily API Key.

### Setup Instructions
1. **Clone the repository and enter directory**:
   ```powershell
   git clone <repository-url>
   cd MarketResearchAgent
   ```

2. **Activate the Virtual Environment**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   *(If creating a new virtual environment: `python -m venv venv` followed by activation).*

3. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and insert your API keys:
   ```powershell
   Copy-Item .env.example .env
   ```
   Edit `.env`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```
   > **Note**: API keys are loaded exclusively from `.env` and are never hardcoded or tracked in version control.

---

## 4. CLI Usage & Execution

### Standard Workflow (Live API Orchestration)
Execute the complete multi-agent market research pipeline for a target sector or topic:
```powershell
python main.py --query "Tech Sector Q3 Analysis"
```

### Optional Custom Dataset
Specify a custom corporate financial metrics CSV:
```powershell
python main.py --query "Semiconductor Sector Review" --csv "data/sample_financial_metrics.csv"
```

### Mock Mode (Token & Cost Preservation)
Run the entire end-to-end report generation and benchmarking pipeline using illustrative mock intelligence without consuming paid API credits:
```powershell
python main.py --query "Tech Sector Q3 Analysis" --mock
```

---

## 5. Deliverables & Output Files

Every completed run produces three synchronized deliverables inside `output/`:
1. **`output/market_report.md`**:
   - Structured Markdown report with metadata banner, Executive Summary, Trends, Financial Table, Risks, and Outlook.
2. **`output/market_report.pdf`**:
   - Typeset A4 PDF generated via ReportLab.
   - Includes full-width navy banner, styled typography, grid table, and dynamic `"Page X of Y"` footers.
3. **`output/benchmarks.json`**:
   - Traced execution analytics capturing total runtime, per-task duration, completion status, and supervisor routing sequence.

---

## 6. Notice Regarding Financial Data

> **IMPORTANT**: The corporate metrics contained in `data/sample_financial_metrics.csv` (Revenue, Net Income, Operating Margin, R&D Expenses, YoY Growth) are **illustrative sample benchmarks** designed specifically for validating statistical aggregations and table compilation. They do not represent audited or actual corporate financial filings.

---

## 7. Automated Testing Suite

Automated unit tests use `pytest` with mock fixtures to verify mathematical calculations, layout rendering, and edge-case handling without calling external APIs.

### Run All Tests
```powershell
pytest -v
```

### Run Financial Parser Tests
```powershell
pytest tests/test_financial_parser.py -v
```
- Validates `mean`, `std`, `min`, `max`, and `count` calculations.
- Tests empty files, missing files, and non-numeric CSVs.

### Run PDF Generator Tests
```powershell
pytest tests/test_pdf_generator.py -v
```
- Validates file creation and exact A4 page dimensions (`595.28 x 841.89 pt`).
- Extracts and verifies banner metadata, headings, financial tables, and dynamic `"Page X of Y"` page numbers.
- Tests multi-page layout and empty content handling.

---

## 8. Troubleshooting & Guidance

- **Windows Permission / AppData Issues**:
  The system automatically redirects CrewAI local credential storage to `.crewai_cache/` in the workspace, bypassing Windows `AppData/Local` sandbox permission locks.
- **Tavily Search Key**:
  If Tavily returns authentication errors, verify `TAVILY_API_KEY` in `.env`. You can always run with `--mock` to test downstream reporting without network or API dependencies.
- **Gemini Model Version**:
  The system defaults to `gemini-2.5-flash` with automatic OpenAI-compatible endpoint routing for native compatibility with the installed environment.

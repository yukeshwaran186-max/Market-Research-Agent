"""Configuration settings and environment management for MarketResearchAgent."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Define base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
CACHE_DIR = BASE_DIR / ".crewai_cache"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Standard file paths
SAMPLE_CSV_PATH = DATA_DIR / "sample_financial_metrics.csv"
BENCHMARK_PATH = OUTPUT_DIR / "benchmarks.json"
PDF_OUTPUT_PATH = OUTPUT_DIR / "market_report.pdf"
MARKDOWN_OUTPUT_PATH = OUTPUT_DIR / "market_report.md"

# Load environment variables
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Configure environment for CrewAI telemetry and local sandbox isolation
# Must directly override LOCALAPPDATA so TokenManager writes to the workspace cache dir
os.environ["LOCALAPPDATA"] = str(CACHE_DIR)
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"

# API Keys and Model Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
# Default to the active Gemini Flash model with .env override support
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
GEMINI_API_BASE = os.getenv(
    "GEMINI_API_BASE",
    "https://generativelanguage.googleapis.com/v1beta/openai/",
)


def get_llm(model: str | None = None, temperature: float = 0.5, timeout: int = 120):
    """Instantiate and return a CrewAI-compatible LLM instance for Gemini.

    Uses the verified Gemini model and routes via Google's OpenAI-compatible
    endpoint or native provider depending on installed package capabilities.
    """
    from crewai.llm import LLM

    selected_model = model or DEFAULT_GEMINI_MODEL
    api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")

    # Check if google-genai native provider is installed
    try:
        import google.genai  # noqa: F401
        has_native_genai = True
    except ImportError:
        has_native_genai = False

    if has_native_genai:
        model_name = selected_model if selected_model.startswith("gemini/") else f"gemini/{selected_model}"
        return LLM(
            model=model_name,
            api_key=api_key,
            temperature=temperature,
            timeout=timeout,
        )

    # Route via Gemini's OpenAI-compatible endpoint using installed openai dependency
    clean_model = selected_model.replace("gemini/", "")
    return LLM(
        model=clean_model,
        api_key=api_key,
        base_url=GEMINI_API_BASE,
        custom_openai=True,
        temperature=temperature,
        timeout=timeout,
    )


def get_manager_llm(model: str | None = None, temperature: float = 0.2, timeout: int = 120):
    """Return a manager LLM instance with lower temperature for hierarchical orchestration."""
    return get_llm(model=model, temperature=temperature, timeout=timeout)


def validate_environment(require_tavily: bool = True) -> dict[str, bool]:
    """Validate that required environment variables and API keys are set."""
    status = {
        "gemini_api_key": bool(GEMINI_API_KEY.strip()),
        "tavily_api_key": bool(TAVILY_API_KEY.strip()) if require_tavily else True,
    }
    return status
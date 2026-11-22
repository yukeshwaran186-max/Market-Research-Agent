"""CrewAI Agent definitions for the Market Research team."""

from typing import Any
import config.settings  # noqa: F401 - Initialize environment before crewai imports
from crewai import Agent
from config.settings import get_llm
from tools.web_search import web_search_and_scrape
from tools.financial_parser import calculate_financial_metrics


def create_lead_researcher(llm: Any = None) -> Agent:
    """Create the Lead Researcher agent responsible for gathering market intelligence."""
    return Agent(
        role="Market Research Specialist",
        goal="Query search networks, locate financial data, and scrape company metrics.",
        backstory=(
            "A seasoned market research specialist adept at identifying industry developments, "
            "tracking competitive landscapes, and gathering verified corporate information."
        ),
        tools=[web_search_and_scrape],
        llm=llm or get_llm(),
        verbose=True,
        allow_delegation=False,
    )


def create_data_analyst(llm: Any = None) -> Agent:
    """Create the Data Analyst agent responsible for parsing financial metrics."""
    return Agent(
        role="Financial Data Analyst",
        goal="Parse data matrices using Pandas, compute averages, and verify numeric consistency.",
        backstory=(
            "A quantitative financial analyst with deep expertise in statistical evaluation, "
            "metrics aggregation, variance analysis, and tabular data synthesis using Pandas."
        ),
        tools=[calculate_financial_metrics],
        llm=llm or get_llm(),
        verbose=True,
        allow_delegation=False,
    )


def create_content_writer(llm: Any = None) -> Agent:
    """Create the Content Writer agent responsible for producing executive market reports."""
    return Agent(
        role="Technical Reports Writer",
        goal="Synthesize information, write sections, and structure copy into an executive-ready market research report.",
        backstory=(
            "A corporate communications and technical writer specializing in compiling comprehensive, "
            "lucid market research reports combining empirical statistics and qualitative commentary."
        ),
        tools=[],
        llm=llm or get_llm(),
        verbose=True,
        allow_delegation=False,
    )


def create_research_agents(llm: Any = None) -> dict[str, Agent]:
    """Convenience factory returning all three specialized agents in a dictionary."""
    agent_llm = llm or get_llm()
    return {
        "lead_researcher": create_lead_researcher(llm=agent_llm),
        "data_analyst": create_data_analyst(llm=agent_llm),
        "content_writer": create_content_writer(llm=agent_llm),
    }

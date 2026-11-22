"""Hierarchical CrewAI Crew orchestration for Market Research."""

from typing import Any
from pathlib import Path
import config.settings  # noqa: F401 - Initialize environment before crewai imports
from crewai import Crew, Process
from config.settings import get_manager_llm
from crew.agents import create_research_agents
from crew.tasks import create_market_research_tasks

__all__ = ["create_market_research_crew", "Process", "Crew"]


def create_market_research_crew(
    query: str = "Tech Sector Q3 Analysis",
    csv_path: str | Path | None = None,
    manager_llm: Any = None,
    verbose: bool = True,
) -> Crew:
    """Create and assemble the hierarchical Market Research Crew.

    Orchestrates the Lead Researcher, Financial Data Analyst, and Content Writer
    under a hierarchical process coordinated by a manager LLM.
    """
    # 1. Instantiate the 3 specialized worker agents
    agents_dict = create_research_agents()
    agents_list = [
        agents_dict["lead_researcher"],
        agents_dict["data_analyst"],
        agents_dict["content_writer"],
    ]

    # 2. Instantiate tasks with context dependencies
    tasks_list = create_market_research_tasks(
        agents=agents_dict,
        query=query,
        csv_path=csv_path,
    )

    # 3. Resolve manager LLM
    resolved_manager_llm = manager_llm or get_manager_llm()

    # 4. Construct hierarchical Crew
    crew = Crew(
        agents=agents_list,
        tasks=tasks_list,
        process=Process.hierarchical,
        manager_llm=resolved_manager_llm,
        verbose=verbose,
    )

    return crew

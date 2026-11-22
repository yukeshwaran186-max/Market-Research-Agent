"""Execution Benchmarking and Analytics for the Market Research workflow."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from config.settings import BENCHMARK_PATH


class BenchmarkTracker:
    """Tracks task durations, routing sequences, and execution statistics."""

    def __init__(self, workflow_name: str = "Market Research Workflow"):
        self.workflow_name = workflow_name
        self.start_timestamp: str = datetime.now().isoformat()
        self._start_perf: float = time.perf_counter()
        self._end_perf: float | None = None
        self.total_duration_seconds: float = 0.0

        self.tasks: list[dict[str, Any]] = []
        self.routing_history: list[dict[str, Any]] = []
        self._active_tasks: dict[str, dict[str, Any]] = {}

    def start_task(self, task_name: str, agent_role: str = "") -> None:
        """Begin timing an agent task."""
        now_perf = time.perf_counter()
        now_iso = datetime.now().isoformat()
        self._active_tasks[task_name] = {
            "task_name": task_name,
            "agent_role": agent_role,
            "start_time": now_iso,
            "_start_perf": now_perf,
        }

    def record_routing(self, source_agent: str, target_agent: str, task_name: str) -> None:
        """Trace the routing history between supervisor/manager and worker agents."""
        self.routing_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "source_agent": source_agent,
                "target_agent": target_agent,
                "task_name": task_name,
            }
        )

    def stop_task(
        self,
        task_name: str,
        status: str = "COMPLETED",
        notes: str | None = None,
    ) -> dict[str, Any]:
        """Stop timing an agent task and record metrics."""
        end_perf = time.perf_counter()
        end_iso = datetime.now().isoformat()

        active = self._active_tasks.pop(task_name, None)
        if active:
            start_perf = active.pop("_start_perf", end_perf)
            duration = round(end_perf - start_perf, 4)
            record = {
                **active,
                "end_time": end_iso,
                "duration_seconds": duration,
                "status": status,
            }
        else:
            record = {
                "task_name": task_name,
                "agent_role": "",
                "start_time": end_iso,
                "end_time": end_iso,
                "duration_seconds": 0.0,
                "status": status,
            }

        if notes:
            record["notes"] = notes

        self.tasks.append(record)
        return record

    def finalize(self) -> dict[str, Any]:
        """Finalize total execution timing and return the summary data dict."""
        self._end_perf = time.perf_counter()
        self.total_duration_seconds = round(self._end_perf - self._start_perf, 4)

        return {
            "workflow_name": self.workflow_name,
            "start_time": self.start_timestamp,
            "end_time": datetime.now().isoformat(),
            "total_duration_seconds": self.total_duration_seconds,
            "task_count": len(self.tasks),
            "tasks": self.tasks,
            "routing_history": self.routing_history,
        }

    def save_to_json(self, file_path: str | Path | None = None) -> Path:
        """Save benchmark data as formatted JSON to disk."""
        target_path = Path(file_path or BENCHMARK_PATH)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        data = self.finalize() if not self.tasks or self.total_duration_seconds == 0.0 else {
            "workflow_name": self.workflow_name,
            "start_time": self.start_timestamp,
            "end_time": datetime.now().isoformat(),
            "total_duration_seconds": round(time.perf_counter() - self._start_perf, 4),
            "task_count": len(self.tasks),
            "tasks": self.tasks,
            "routing_history": self.routing_history,
        }

        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return target_path


def load_benchmark(file_path: str | Path | None = None) -> dict[str, Any]:
    """Safely load and return benchmark JSON data from disk."""
    target_path = Path(file_path or BENCHMARK_PATH)
    if not target_path.exists():
        return {}

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

"""
LangSmith Free Tier and Deep Evaluator Adapter.

Provides zero-cost observability and automated verification integration:
- Connects to LangSmith Free Tier (5,000 free traces/month, zero-cost developer tier).
- Gracefully falls back to local standalone Deep Evaluator mode when offline or without credentials.
- Supports both standard REST API (zero-dependency) and official langsmith SDK if installed.
"""

import json
import logging
import os
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

logger = logging.getLogger("agent_factory.evals.langsmith")


class LangSmithAdapter:
    """Zero-cost adapter for LangSmith Developer/Free Tier & Deep Evaluator telemetry."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        project: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
        self.endpoint = (
            endpoint
            or os.getenv("LANGSMITH_ENDPOINT")
            or os.getenv("LANGCHAIN_ENDPOINT")
            or "https://api.smith.langchain.com"
        ).rstrip("/")
        self.project = (
            project
            or os.getenv("LANGSMITH_PROJECT")
            or os.getenv("LANGCHAIN_PROJECT")
            or "agent-development-factory"
        )
        
        # Tracing flag: default to true if API key is present
        tracing_env = os.getenv("LANGSMITH_TRACING") or os.getenv("LANGCHAIN_TRACING_V2") or ""
        self.enabled = bool(self.api_key) and (tracing_env.lower() in ("true", "1", "") if self.api_key else False)

    def is_enabled(self) -> bool:
        """Returns True if LangSmith free tier tracing is active."""
        return self.enabled

    def get_status(self) -> Dict[str, Any]:
        """Returns connection and operating mode status."""
        return {
            "mode": "langsmith_cloud" if self.enabled else "deep_evaluator_local",
            "tracing_enabled": self.enabled,
            "project": self.project,
            "endpoint": self.endpoint,
            "has_api_key": bool(self.api_key),
            "cost": 0.0,
            "tier": "LangSmith Free / Developer (5,000 monthly traces)",
        }

    def record_evaluation(
        self,
        agent_name: str,
        evaluation_data: Dict[str, Any],
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Record agent evaluation run metrics.
        In local Deep Evaluator mode, formats structured telemetry.
        In LangSmith mode, dispatches trace to LangSmith Free Tier endpoint.
        """
        run_id = f"eval-{int(time.time() * 1000)}"
        payload = {
            "id": run_id,
            "name": f"eval_{agent_name}",
            "run_type": "chain",
            "session_name": self.project,
            "inputs": {
                "agent_name": agent_name,
                "session_id": session_id or run_id,
            },
            "outputs": {
                "verdict": evaluation_data.get("verdict"),
                "passed": evaluation_data.get("passed"),
                "efficacy": evaluation_data.get("efficacy"),
                "safety": evaluation_data.get("safety"),
                "grader_details": evaluation_data.get("grader_details", {}),
            },
            "extra": {
                "metadata": {
                    "efficiency": evaluation_data.get("efficiency", {}),
                    "zero_cost_pipeline": True,
                    "evaluator": "Deep Evaluator / LangSmith Free Tier",
                }
            },
            "start_time": time.time(),
            "end_time": time.time(),
        }

        if not self.enabled:
            # Standalone Deep Evaluator Local Path
            return {
                "status": "recorded_locally",
                "run_id": run_id,
                "mode": "deep_evaluator_local",
                "telemetry": payload,
            }

        # Remote LangSmith Free Tier dispatch via standard HTTP (no heavy deps required)
        try:
            req_url = f"{self.endpoint}/runs"
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
            }
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(req_url, data=req_data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=5) as response:
                resp_body = response.read().decode("utf-8")
                return {
                    "status": "dispatched_to_langsmith",
                    "run_id": run_id,
                    "mode": "langsmith_cloud",
                    "response": resp_body,
                }
        except Exception as e:
            logger.warning("LangSmith dispatch failed (%s); falling back to local evaluation ledger", e)
            return {
                "status": "fallback_local",
                "run_id": run_id,
                "mode": "deep_evaluator_local",
                "error": str(e),
                "telemetry": payload,
            }

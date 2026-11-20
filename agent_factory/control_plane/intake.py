"""
Request Intake, Requirements Decomposition, Solution Triage, and Cost Estimator Engine.
Synthesised against S1 (Anthropic Effective Agents), S2 (OpenAI Practical Guide), and S5 (Anthropic Multi-Agent).
"""

from enum import Enum
import re
import uuid
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from agent_factory.specs.schema import (
    UniversalAgentSpec,
    InputParameter,
    OutputParameter,
    PolicySpec,
    LimitsSpec,
    StateSpec,
    AcceptanceSpec,
    EffectLevel,
    RiskClassification,
)


class SolutionType(str, Enum):
    NO_AGENT = "no_agent"
    DETERMINISTIC_WORKFLOW = "deterministic_workflow"
    AUTONOMOUS_AGENT = "autonomous_agent"
    MULTI_AGENT_SYSTEM = "multi_agent_system"


class SolutionTriageResult(BaseModel):
    solution_type: SolutionType
    reasoning: str
    token_multiplier: float
    recommended_pattern: str
    simplicity_rationale: str


class CostFeasibilityEstimate(BaseModel):
    token_budget: int
    projected_tokens_per_run: int
    projected_cost_usd: float
    is_feasible: bool
    feasibility_status: str
    recommendation: str


class ClarificationQuestion(BaseModel):
    field: str
    question: str
    options: Optional[List[str]] = None
    impact_on_build: str


class ClarificationResult(BaseModel):
    is_complete: bool
    questions: List[ClarificationQuestion]
    extracted_intent: Dict[str, Any]


class IntakeResult(BaseModel):
    project_id: str
    agent_id: str
    risk_level: RiskClassification
    spec: UniversalAgentSpec
    triage: Optional[SolutionTriageResult] = None
    cost_estimate: Optional[CostFeasibilityEstimate] = None


class RequestIntake:
    """Decomposes raw user requests into validated Universal Agent Specifications with triage & feasibility."""

    @classmethod
    def triage_solution_complexity(cls, prompt: str) -> SolutionTriageResult:
        """
        S1/S2 Principle: 'Use the simplest solution that works.'
        Evaluates whether a problem needs No Agent, a Deterministic Workflow, a Single Agent, or Multi-Agent.
        """
        lower = prompt.lower()

        # Check for NO_AGENT (Static calculations, regex, SQL queries, pure scripts)
        if any(k in lower for k in ["regex", "calculate sum", "sql query", "csv to json", "parse timestamp", "math formula"]):
            return SolutionTriageResult(
                solution_type=SolutionType.NO_AGENT,
                reasoning="Task has zero semantic ambiguity and can be resolved deterministically without an LLM.",
                token_multiplier=0.0,
                recommended_pattern="deterministic_script",
                simplicity_rationale="S1/S2: Zero token expenditure and zero latency variance. Avoid unnecessary agent abstraction."
            )

        # Check for MULTI_AGENT_SYSTEM (Disparate specialist roles, adversarial review, parallel fleet)
        if any(k in lower for k in ["multi-agent", "team of agents", "critic and generator", "swarm", "parallel fleet", "specialist roles"]):
            return SolutionTriageResult(
                solution_type=SolutionType.MULTI_AGENT_SYSTEM,
                reasoning="Task specifies independent peer agents, adversarial verification, or fanned-out specialist roles.",
                token_multiplier=15.0,  # S5: Anthropic Multi-Agent research indicates ~15x token consumption
                recommended_pattern="orchestrator_worker",
                simplicity_rationale="S5: High token cost (~15x chat baseline). Verify high-value justification before deployment."
            )

        # Check for DETERMINISTIC_WORKFLOW (Sequential DAG, step-by-step pipeline without branch ambiguity)
        if any(k in lower for k in ["step 1", "pipeline", "etl", "sequential", "daily report pipeline", "download and extract"]):
            return SolutionTriageResult(
                solution_type=SolutionType.DETERMINISTIC_WORKFLOW,
                reasoning="Task follows a fixed sequence of known operational steps with predictable control flow.",
                token_multiplier=1.0,
                recommended_pattern="prompt_chain",
                simplicity_rationale="S1/S2: Fixed DAG reduces tool execution failures and context window drift."
            )

        # Default: AUTONOMOUS_AGENT (Dynamic observation-action loop needed)
        return SolutionTriageResult(
            solution_type=SolutionType.AUTONOMOUS_AGENT,
            reasoning="Task requires dynamic tool invocation, exploratory data retrieval, or variable decision paths.",
            token_multiplier=2.5,
            recommended_pattern="single_agent",
            simplicity_rationale="S1/S2: Bounded single agent with discrete tool effect permissions."
        )

    @classmethod
    def estimate_feasibility_and_cost(
        cls,
        prompt: str,
        solution_type: Optional[SolutionType] = None,
        base_tokens: int = 1500,
        model_cost_per_million: float = 0.0,  # Default 0.0 for zero-cost local / free-tier
    ) -> CostFeasibilityEstimate:
        """
        S5 Principle: Estimates token overhead and cost before code synthesis.
        """
        if solution_type is None:
            triage = cls.triage_solution_complexity(prompt)
            solution_type = triage.solution_type

        multiplier = {
            SolutionType.NO_AGENT: 0.0,
            SolutionType.DETERMINISTIC_WORKFLOW: 1.0,
            SolutionType.AUTONOMOUS_AGENT: 2.5,
            SolutionType.MULTI_AGENT_SYSTEM: 15.0,
        }.get(solution_type, 2.5)

        projected_tokens = int(base_tokens * multiplier)
        projected_cost = (projected_tokens / 1_000_000.0) * model_cost_per_million

        # Feasibility bounds: Reject excessive token runs beyond max budget
        token_budget = 8000
        is_feasible = projected_tokens <= 50_000

        if solution_type == SolutionType.NO_AGENT:
            status = "OPTIMAL_ZERO_COST"
            rec = "Execute via pure standard library script; bypass LLM entirely."
        elif projected_tokens > token_budget * 2:
            status = "HIGH_TOKEN_WARNING"
            rec = f"Multi-agent architecture projected at ~{projected_tokens} tokens (~15x baseline). Consider simplifying to single agent."
        else:
            status = "FEASIBLE"
            rec = f"Solution type '{solution_type.value}' is within acceptable token boundaries (~{projected_tokens} tokens)."

        return CostFeasibilityEstimate(
            token_budget=token_budget,
            projected_tokens_per_run=projected_tokens,
            projected_cost_usd=round(projected_cost, 4),
            is_feasible=is_feasible,
            feasibility_status=status,
            recommendation=rec,
        )

    @classmethod
    def clarify_intent(cls, prompt: str) -> ClarificationResult:
        """
        Layer 1: Intent capture and clarification.
        Asks only the questions that change the build: goal, users, systems touched, risk level, success criteria.
        """
        lower = prompt.lower()
        questions = []
        extracted = {}

        # 1. Goal / users
        if len(prompt.strip()) < 20:
            questions.append(ClarificationQuestion(
                field="goal_clarification",
                question="What specific outcome or deliverable should the agent generate?",
                options=["Analytical Report", "Processed Data Artifact", "Notification Alert", "Automated Action"],
                impact_on_build="Determines primary output parameter format and acceptance criteria."
            ))
        else:
            extracted["goal"] = prompt.strip()

        # 2. Systems touched
        if not any(k in lower for k in ["csv", "json", "api", "database", "file", "web", "repo"]):
            questions.append(ClarificationQuestion(
                field="systems_touched",
                question="Which systems or data formats will this agent need to read or write?",
                options=["Local Files (CSV/JSON)", "HTTP REST APIs", "Database / SQLite", "Git Repository"],
                impact_on_build="Determines required tool capabilities and effect level permissions."
            ))
        else:
            extracted["systems_touched"] = [k for k in ["csv", "json", "api", "database", "file", "web", "repo"] if k in lower]

        # 3. Autonomy / Risk level
        if not any(k in lower for k in ["draft", "read-only", "approve", "autonomous", "delete", "write"]):
            questions.append(ClarificationQuestion(
                field="autonomy_level",
                question="What authority boundary should govern this agent's actions?",
                options=["Draft Only (Local files, no external change)", "Read-Only (Public / private inspection)", "Write with Human Approval"],
                impact_on_build="Sets PolicySpec mode, RiskClassification, and approval gate tokens."
            ))

        return ClarificationResult(
            is_complete=len(questions) == 0,
            questions=questions,
            extracted_intent=extracted,
        )

    @classmethod
    def process_request(
        cls,
        prompt: str,
        owner: str = "Admin",
        forced_risk: Optional[RiskClassification] = None,
    ) -> IntakeResult:
        # Determine slug and identifiers
        slug_match = re.sub(r"[^a-zA-Z0-9_]+", "_", prompt.lower()[:30]).strip("_")
        agent_id = slug_match if slug_match else f"agent_{uuid.uuid4().hex[:8]}"
        project_id = f"proj_{uuid.uuid4().hex[:10]}"

        # Risk Classification Heuristics
        lower_prompt = prompt.lower()
        if forced_risk:
            risk = forced_risk
        elif any(k in lower_prompt for k in ["delete", "spend", "money", "payment", "publish", "send email", "telegram"]):
            risk = RiskClassification.HIGH
        elif any(k in lower_prompt for k in ["private", "modify", "database", "write remote"]):
            risk = RiskClassification.MEDIUM
        else:
            risk = RiskClassification.LOW

        # Define policy permissions based on risk
        permitted_effects = [EffectLevel.READ_PUBLIC, EffectLevel.WRITE_LOCAL_DRAFT]
        if risk == RiskClassification.MEDIUM:
            permitted_effects.append(EffectLevel.READ_PRIVATE)

        # Run triage and cost feasibility
        triage = cls.triage_solution_complexity(prompt)
        cost_est = cls.estimate_feasibility_and_cost(prompt, triage.solution_type)

        spec = UniversalAgentSpec(
            schema_version=1,
            agent_id=agent_id,
            version="1.0.0",
            owner=owner,
            purpose=prompt.strip(),
            inputs={
                "input_data": InputParameter(
                    type="string",
                    description="Path to target input dataset or parameters",
                    required=True,
                )
            },
            outputs={
                "report": OutputParameter(
                    type="file",
                    format="markdown",
                    path="artifacts/report.md",
                    description="Primary operational report",
                ),
                "summary": OutputParameter(
                    type="file",
                    format="json",
                    path="artifacts/summary.json",
                    description="Structured outcome ledger",
                ),
            },
            policy=PolicySpec(
                mode="draft_only",
                data_classification="public_or_synthetic",
                permitted_tools=["read_local_csv", "compute_statistics", "write_workspace_artifact"],
                permitted_effects=permitted_effects,
                secrets="none",
            ),
            limits=LimitsSpec(
                max_steps=20,
                max_wall_time_seconds=60,
                paid_spend_ceiling=0.0,
                max_parallel_workers=1,
            ),
            state=StateSpec(durable_fields=["project_id", "stage", "evidence_refs"]),
            acceptance=AcceptanceSpec(
                suite="evals/standard_pack",
                required_checks=["functional_correctness", "schema_compliance", "zero_unauthorized_effects"],
                minimum_efficacy=0.95,
                minimum_safety=1.00,
            ),
            targets={"local_process": "candidate", "hermes": "candidate"},
        )

        return IntakeResult(
            project_id=project_id,
            agent_id=agent_id,
            risk_level=risk,
            spec=spec,
            triage=triage,
            cost_estimate=cost_est,
        )

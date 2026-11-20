"""
Pattern Library and Multi-Agent Topology Generator.
Synthesised from S1 (Anthropic: Building Effective Agents), S2 (OpenAI: Practical Guide to Building Agents),
S5 (Anthropic: Multi-Agent Research System), and S10 (A2A Protocol).
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class AgentPattern(str, Enum):
    DATA_PROCESSOR = "data_processor"
    PROMPT_CHAIN = "prompt_chain"
    ROUTER = "router"
    ORCHESTRATOR_WORKER = "orchestrator_worker"
    EVALUATOR_OPTIMIZER = "evaluator_optimizer"


class PatternMetadata(BaseModel):
    pattern: AgentPattern
    name: str
    description: str
    suitable_for: List[str]
    token_overhead: str
    sample_topology: Dict[str, Any]


class PatternLibrary:
    """Library of reusable agentic and workflow architectural patterns."""

    PATTERNS: Dict[AgentPattern, PatternMetadata] = {
        AgentPattern.DATA_PROCESSOR: PatternMetadata(
            pattern=AgentPattern.DATA_PROCESSOR,
            name="Tabular Data Processor & Anomaly Analyzer",
            description="Analyzes structured datasets for missing values, statistical Z-score outliers, and schema drift.",
            suitable_for=["CSV inspection", "ETL validation", "Data quality auditing"],
            token_overhead="Low (~1x-2x). Computations run in native Python; LLM used only for executive summaries.",
            sample_topology={
                "type": "single_agent",
                "nodes": ["ingest", "compute_stats", "detect_outliers", "render_report"],
            },
        ),
        AgentPattern.PROMPT_CHAIN: PatternMetadata(
            pattern=AgentPattern.PROMPT_CHAIN,
            name="Sequential Prompt Chain",
            description="Decomposes a task into a sequence of deterministic steps where the output of step N feeds step N+1.",
            suitable_for=["Document drafting", "Multi-stage text translation", "Step-by-step verification"],
            token_overhead="Linear (1x baseline per step). High reliability, low hallucination rate.",
            sample_topology={
                "type": "pipeline",
                "nodes": ["extract", "transform", "synthesize", "verify"],
            },
        ),
        AgentPattern.ROUTER: PatternMetadata(
            pattern=AgentPattern.ROUTER,
            name="Intent Router & Dispatcher",
            description="Classifies incoming requests and routes them to dedicated specialized tool handlers or models.",
            suitable_for=["Customer support triage", "Multi-domain query answering", "Specialized tool routing"],
            token_overhead="Low to Moderate (~1.2x). Classification turn followed by single specialist execution.",
            sample_topology={
                "type": "router_dispatcher",
                "nodes": ["classifier", "handler_a", "handler_b", "handler_c", "fallback"],
            },
        ),
        AgentPattern.ORCHESTRATOR_WORKER: PatternMetadata(
            pattern=AgentPattern.ORCHESTRATOR_WORKER,
            name="Orchestrator-Worker Decomposition",
            description="A central lead orchestrator decomposes a complex task, dispatches sub-workers, and synthesizes results.",
            suitable_for=["Complex multi-source research", "Parallel code refactoring", "Large codebase audits"],
            token_overhead="High (~15x chat baseline per S5). Uses fanned-out sub-agents communicating via A2A protocol.",
            sample_topology={
                "type": "orchestrator_worker",
                "orchestrator": "lead_agent",
                "workers": ["worker_researcher", "worker_analyst", "worker_critic"],
                "protocol": "A2A_v1",
            },
        ),
        AgentPattern.EVALUATOR_OPTIMIZER: PatternMetadata(
            pattern=AgentPattern.EVALUATOR_OPTIMIZER,
            name="Evaluator-Optimizer Loop",
            description="One agent generates candidates while another independently evaluates and provides actionable feedback.",
            suitable_for=["Code generation with test execution", "High-accuracy translation", "Contract review"],
            token_overhead="Iterative (2x-5x depending on retry budget). Guarantees high quality threshold.",
            sample_topology={
                "type": "feedback_loop",
                "nodes": ["generator", "evaluator_critic", "refiner"],
                "exit_condition": "all_checks_passed_or_max_retries",
            },
        ),
    }

    @classmethod
    def list_patterns(cls) -> List[PatternMetadata]:
        return list(cls.PATTERNS.values())

    @classmethod
    def get_pattern(cls, pattern_name: str) -> Optional[PatternMetadata]:
        for k, v in cls.PATTERNS.items():
            if k.value == pattern_name.lower():
                return v
        return None

    @classmethod
    def select_pattern_for_prompt(cls, prompt: str) -> AgentPattern:
        lower = prompt.lower()
        if any(k in lower for k in ["csv", "anomaly", "dataset", "column", "z-score", "tabular", "clean data"]):
            return AgentPattern.DATA_PROCESSOR
        if any(k in lower for k in ["route", "router", "triage", "dispatch", "classify query"]):
            return AgentPattern.ROUTER
        if any(k in lower for k in ["multi-agent", "team", "orchestrator", "worker", "swarm", "parallel fleet"]):
            return AgentPattern.ORCHESTRATOR_WORKER
        if any(k in lower for k in ["evaluate", "critic", "refine", "optimizer", "self-healing", "feedback loop"]):
            return AgentPattern.EVALUATOR_OPTIMIZER
        if any(k in lower for k in ["chain", "pipeline", "step by step", "sequential", "stage"]):
            return AgentPattern.PROMPT_CHAIN
        return AgentPattern.DATA_PROCESSOR  # Standard default

    @classmethod
    def generate_topology(cls, pattern: AgentPattern, agent_id: str) -> Dict[str, Any]:
        """
        S10 (A2A Protocol): Generates machine-readable agent topology wiring
        lead agents, sub-agents, message channels, and boundaries.
        """
        if pattern == AgentPattern.ORCHESTRATOR_WORKER:
            return {
                "protocol": "A2A_v1",
                "topology_type": "orchestrator_worker",
                "lead_agent": {
                    "id": f"{agent_id}_coordinator",
                    "role": "Coordinator & Task Decomposer",
                    "channels": ["inbound_user", "internal_bus"],
                },
                "sub_agents": [
                    {
                        "id": f"{agent_id}_worker_1",
                        "role": "Specialist Domain Worker",
                        "inbound": "internal_bus",
                        "outbound": "internal_bus",
                    },
                    {
                        "id": f"{agent_id}_verifier",
                        "role": "Independent Verifier & Grader",
                        "inbound": "internal_bus",
                        "outbound": "internal_bus",
                    },
                ],
                "message_contracts": [
                    "TaskDelegationMessage",
                    "TaskCompletionReport",
                    "VerificationProof",
                ],
            }
        elif pattern == AgentPattern.EVALUATOR_OPTIMIZER:
            return {
                "protocol": "A2A_v1",
                "topology_type": "evaluator_optimizer",
                "lead_agent": {
                    "id": f"{agent_id}_generator",
                    "role": "Candidate Generator",
                },
                "critic_agent": {
                    "id": f"{agent_id}_critic",
                    "role": "Independent Critic & Rubric Grader",
                },
                "max_iterations": 3,
            }
        elif pattern == AgentPattern.ROUTER:
            return {
                "protocol": "A2A_v1",
                "topology_type": "router_dispatcher",
                "router": {
                    "id": f"{agent_id}_router",
                    "role": "Intent Classifier",
                },
                "routes": {
                    "inquiry": f"{agent_id}_inquiry_handler",
                    "operational": f"{agent_id}_ops_handler",
                    "fallback": f"{agent_id}_fallback_handler",
                },
            }
        else:
            return {
                "protocol": "A2A_v1",
                "topology_type": "single_agent",
                "agent_id": agent_id,
                "role": "Autonomous Single Execution Agent",
            }

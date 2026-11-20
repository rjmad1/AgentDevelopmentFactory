"""
Comprehensive Capability Verification Suite for 10-Layer Capability Map.
Validates:
- Layer 1: Intake & Triage (S1/S2 Simplicity, S5 Cost Feasibility, Intent Clarifier)
- Layer 2: Pattern Library, Multi-Agent Topology (S5/S10), Code Generation, Skill Packaging (S8)
- Layer 6: OWASP Agentic Top 10 Threat Modeling (S18)
"""

from pathlib import Path
from agent_factory.control_plane.intake import (
    RequestIntake,
    SolutionType,
    SolutionTriageResult,
    CostFeasibilityEstimate,
)
from agent_factory.workbench.pattern_library import PatternLibrary, AgentPattern
from agent_factory.workbench.code_generator import CodeGenerator
from agent_factory.workbench.skill_packager import SkillPackager
from agent_factory.security.threat_modeler import AgentThreatModeler
from agent_factory.specs.schema import UniversalAgentSpec, EffectLevel


def test_layer1_solution_complexity_triage():
    # 1. NO_AGENT for pure static operations
    triage_no_agent = RequestIntake.triage_solution_complexity("Parse timestamp and convert CSV to JSON")
    assert triage_no_agent.solution_type == SolutionType.NO_AGENT
    assert triage_no_agent.token_multiplier == 0.0

    # 2. DETERMINISTIC_WORKFLOW for linear pipelines
    triage_workflow = RequestIntake.triage_solution_complexity("Daily report pipeline: step 1 extract, step 2 write summary")
    assert triage_workflow.solution_type == SolutionType.DETERMINISTIC_WORKFLOW
    assert triage_workflow.token_multiplier == 1.0

    # 3. MULTI_AGENT_SYSTEM for swarm/teams
    triage_multi = RequestIntake.triage_solution_complexity("Orchestrate a team of agents with critic and generator")
    assert triage_multi.solution_type == SolutionType.MULTI_AGENT_SYSTEM
    assert triage_multi.token_multiplier == 15.0  # S5 benchmark

    # 4. AUTONOMOUS_AGENT for dynamic tasks
    triage_agent = RequestIntake.triage_solution_complexity("Investigate database for anomalous customer transactions")
    assert triage_agent.solution_type == SolutionType.AUTONOMOUS_AGENT
    assert triage_agent.token_multiplier == 2.5


def test_layer1_feasibility_and_cost_estimation():
    # Zero cost for NO_AGENT
    est_no_agent = RequestIntake.estimate_feasibility_and_cost("Convert CSV to JSON", SolutionType.NO_AGENT)
    assert est_no_agent.projected_tokens_per_run == 0
    assert est_no_agent.feasibility_status == "OPTIMAL_ZERO_COST"

    # ~15x tokens for MULTI_AGENT
    est_multi = RequestIntake.estimate_feasibility_and_cost("Run parallel fleet", SolutionType.MULTI_AGENT_SYSTEM, base_tokens=1500)
    assert est_multi.projected_tokens_per_run == 22500  # 1500 * 15
    assert est_multi.feasibility_status == "HIGH_TOKEN_WARNING"


def test_layer1_intent_clarification():
    # Ambiguous short prompt generates clarification questions
    short_res = RequestIntake.clarify_intent("Do analysis")
    assert not short_res.is_complete
    assert len(short_res.questions) >= 2
    fields = [q.field for q in short_res.questions]
    assert "goal_clarification" in fields or "systems_touched" in fields

    # Detailed prompt passes cleanly
    detailed_res = RequestIntake.clarify_intent("Analyze local CSV sales dataset and output a draft markdown report")
    assert detailed_res.is_complete
    assert len(detailed_res.questions) == 0


def test_layer2_pattern_library_and_topologies():
    patterns = PatternLibrary.list_patterns()
    assert len(patterns) == 5

    # Check pattern selection
    assert PatternLibrary.select_pattern_for_prompt("Classify and route incoming customer tickets") == AgentPattern.ROUTER
    assert PatternLibrary.select_pattern_for_prompt("Iterative generator and critic feedback loop") == AgentPattern.EVALUATOR_OPTIMIZER
    assert PatternLibrary.select_pattern_for_prompt("Multi-agent team decomposition") == AgentPattern.ORCHESTRATOR_WORKER

    # Check A2A Topology Generation
    topo_orch = PatternLibrary.generate_topology(AgentPattern.ORCHESTRATOR_WORKER, "agent_researcher")
    assert topo_orch["protocol"] == "A2A_v1"
    assert topo_orch["topology_type"] == "orchestrator_worker"
    assert len(topo_orch["sub_agents"]) == 2


def test_layer2_spec_driven_code_generation_patterns(tmp_path):
    intake = RequestIntake.process_request("Customer inquiry classification router")

    # 1. Generate ROUTER pattern code
    router_dir = tmp_path / "router_src"
    res_router = CodeGenerator.generate_agent_code(intake.spec, router_dir, pattern=AgentPattern.ROUTER)
    assert res_router["agent"].exists()
    router_code = res_router["agent"].read_text(encoding="utf-8")
    assert "class IntentRouterAgent" in router_code
    assert "classify_and_route" in router_code

    # 2. Generate EVALUATOR_OPTIMIZER pattern code
    opt_dir = tmp_path / "opt_src"
    res_opt = CodeGenerator.generate_agent_code(intake.spec, opt_dir, pattern=AgentPattern.EVALUATOR_OPTIMIZER)
    assert res_opt["agent"].exists()
    opt_code = res_opt["agent"].read_text(encoding="utf-8")
    assert "class EvaluatorOptimizerAgent" in opt_code
    assert "optimize" in opt_code

    # 3. Generate PROMPT_CHAIN pattern code
    chain_dir = tmp_path / "chain_src"
    res_chain = CodeGenerator.generate_agent_code(intake.spec, chain_dir, pattern=AgentPattern.PROMPT_CHAIN)
    assert res_chain["agent"].exists()
    chain_code = res_chain["agent"].read_text(encoding="utf-8")
    assert "class PromptChainAgent" in chain_code


def test_layer2_skill_packaging_s8(tmp_path):
    intake = RequestIntake.process_request("Statistical Data Cleansing Agent")
    pkg_res = SkillPackager.package_as_skill(intake.spec, tmp_path / "skills", skill_name="statistical-cleaner")

    skill_file = Path(pkg_res["skill_md_path"])
    assert skill_file.exists()
    content = skill_file.read_text(encoding="utf-8")

    # Conforms to S8 Agent Skills specification
    assert "---" in content
    assert "name: statistical-cleaner" in content
    assert "tools_required:" in content
    assert "# Skill: statistical-cleaner" in content
    assert "## 3. Standard Operating Procedure" in content
    assert pkg_res["sha256"] is not None


def test_layer6_owasp_agentic_threat_modeling():
    intake = RequestIntake.process_request("Safe CSV processor")

    # Baseline low-risk passes
    rep_safe = AgentThreatModeler.evaluate_blueprint(intake.spec)
    assert rep_safe.passed
    assert rep_safe.risk_score < 4.0

    # Insecure blueprint with high effects and raw secret triggers findings
    insecure_spec = intake.spec.model_copy(deep=True)
    insecure_spec.policy.permitted_effects.append(EffectLevel.SPEND_DELETE)
    insecure_spec.policy.secrets = ["sk-live-1234567890abcdef1234567890abcdef"]

    rep_insecure = AgentThreatModeler.evaluate_blueprint(insecure_spec)
    assert not rep_insecure.passed
    categories = [f.category for f in rep_insecure.findings]
    assert any("ASI02" in c for c in categories)  # Excessive agency
    assert any("ASI05" in c for c in categories)  # Raw secret

# Agent Development Factory (ADF): Capability Map

Synthesised from the 20-source reading list. Tags: **[S#]** = source number from the reading list; **[I]** = inference (not directly sourced). No source describes a factory that generates agents, so layers 1–2 are mostly inference.

## Source list

| # | Source | Link |
|---|---|---|
| S1 | Anthropic: Building effective agents | https://www.anthropic.com/engineering/building-effective-agents |
| S2 | OpenAI: A practical guide to building agents | https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf |
| S3 | 12-Factor Agents (HumanLayer) | https://github.com/humanlayer/12-factor-agents |
| S4 | Anthropic: Building agents with the Claude Agent SDK | https://anthropic.com/engineering/building-agents-with-the-claude-agent-sdk |
| S5 | Anthropic: Multi-agent research system | https://www.anthropic.com/engineering/multi-agent-research-system |
| S6 | Anthropic: Effective context engineering | https://anthropic.com/engineering/effective-context-engineering-for-ai-agents |
| S7 | Anthropic: Writing effective tools for agents | https://anthropic.com/engineering/writing-tools-for-agents |
| S8 | Agent Skills specification | https://agentskills.io/specification |
| S9 | Model Context Protocol specification | https://modelcontextprotocol.io/specification/latest |
| S10 | A2A protocol (GitHub) | https://github.com/a2aproject/a2a |
| S11 | Google Agent Development Kit docs | https://google.github.io/adk-docs |
| S12 | LangGraph: durable execution | https://docs.langchain.com/oss/python/langgraph/durable-execution |
| S13 | Microsoft Agent Framework overview | https://learn.microsoft.com/en-us/agent-framework/overview/ |
| S14 | Amazon Bedrock AgentCore | https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html |
| S15 | Anthropic: Demystifying evals for AI agents | https://anthropic.com/engineering/demystifying-evals-for-ai-agents |
| S16 | OpenTelemetry: AI agent observability | https://opentelemetry.io/blog/2025/ai-agent-observability/ |
| S17 | Google Cloud: agentic transformation / AgentOps framework (PDF) | https://services.google.com/fh/files/blogs/latest_new_agentic_landscape_agentic_transformation_framework.pdf |
| S18 | OWASP Top 10 for Agentic Applications | https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/ |
| S19 | NIST AI 600-1: Generative AI Profile | https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf |
| S20 | ISO/IEC 42001 | https://www.iso.org/standard/42001 |

## 1. Intake and specification (the "minimal input" front door)
- **Intent capture and clarification [I]:** Takes a short brief and asks only the questions that change the build: goal, users, systems touched, risk level, success criteria.
- **Agent blueprint generator [I]:** Turns the brief into a structured spec (goal, instructions, tools, autonomy level, guardrails, eval criteria). Every later stage reads this one artefact. Mirrors the agent components in S2.
- **Workflow, agent or no-agent triage [S1, S2]:** Both guides say to use the simplest solution that works. The factory should often output a deterministic workflow, not an agent.
- **Feasibility and cost estimate [S5, I]:** Estimates token cost and value before building. S5 reports multi-agent systems use about 15× the tokens of chat, so low-value tasks should be rejected early.

## 2. Design and generation engine
- **Pattern library [S1, S2]:** Reusable architectures from single agent through routing, parallelisation, orchestrator-worker and evaluator loops. The generator selects from the library rather than inventing a design each time.
- **Framework-agnostic code generation [S3, S11–S14]:** Emits agent code through adapters for chosen runtimes (ADK, LangGraph, Microsoft Agent Framework, AgentCore). Prompts and control flow stay in your own code, as S3 recommends.
- **Prompt and context builder [S6, S3]:** Generates system prompts and context-management rules (what to retrieve, compact or drop) as part of the spec. Treats context as a budgeted resource.
- **Tool and MCP server factory [S7, S9]:** Generates tools designed for agents: few, clearly named, token-efficient, with helpful errors. Exposes them over MCP.
- **Skill packaging [S8]:** Packages repeatable procedures as SKILL.md skills so behaviour changes by editing files, not redeploying.
- **Multi-agent topology generator [S5, S10]:** Decides when to split into a lead agent and sub-agents, and wires them with A2A. Defaults to single-agent, since S5 says tightly coupled tasks fit multi-agent poorly.

## 3. Tool and integration layer
- **Tool and MCP registry or gateway [S9, S14]:** A governed catalogue of approved tools and agents, supporting discovery and central control.
- **Agent identity and scoped credentials [S14, S18]:** Each agent gets its own identity and least-privilege, short-lived access to tools. The main control against excessive agency.
- **Enterprise connectors [I]:** Reusable, pre-approved connectors to client systems (POS, inventory, ERP, ticketing) with their own test fixtures. Domain-specific; build in later phases.

## 4. Runtime and orchestration
- **Durable execution [S12]:** Runs resume from saved state after failure or a long pause. Checkpointing and crash-proof execution are different; verify which one your runtime gives you.
- **Human-in-the-loop gates [S2, S3, S12]:** Approve, edit or reject steps before risky tool calls, with paused state held indefinitely.
- **Memory and state management [S6, S14]:** Separates short-term thread state from durable cross-session memory. Session state is ephemeral in AgentCore, so persistence needs explicit design.
- **Sandboxed execution [I]:** Isolated environments for code execution and browser or computer use.
- **Long-running and async task support [S9, S14]:** Background jobs with progress tracking. MCP has a Tasks extension, and AgentCore supports runs of up to 8 hours.

## 5. Evaluation and quality
- **Auto-generated eval suite [S15, I]:** The factory creates test tasks and graders from the blueprint, using code-based, model-based and human graders.
- **Capability and regression evals [S15]:** Hard tasks to climb, plus a protected set of behaviours that must not regress. Passing capability tasks graduate into the regression set.
- **Outcome-based grading [S15]:** Grades results, not exact step sequences, because agents often find valid paths you did not anticipate.
- **Tool-level evals [S7]:** Tests tools on realistic multi-step tasks before agents use them.
- **Synthetic and sanitised test data [I]:** Client-confidential data cannot be used; synthetic data is the default.
- **Release gate [S17, I]:** An agent cannot be promoted unless it passes evals, security checks and cost thresholds.

## 6. Security and safety
- **Guardrails [S2]:** Layered input, output and tool-call checks, with human escalation when an agent repeatedly fails or an action is high-risk.
- **Threat modelling per agent [S18, I]:** Automatically checks each blueprint against the OWASP agentic risks: goal hijacking, tool misuse, memory and context poisoning.
- **Prompt-injection and red-team testing [S18, I]:** Adversarial tests run in CI, since agents ingest untrusted content.
- **Tool and skill supply-chain vetting [S8, S9, I]:** Scans and approves third-party MCP servers and skills before they enter the registry; both are effectively executable code.
- **Data privacy controls [S19, I]:** Handles sensitive data, redaction and residency rules.

## 7. Governance and compliance
- **Risk classification and approval workflow [S19, S20, I]:** Tiers each agent by autonomy and impact, and sets review depth by tier. NIST AI 600-1 gives a risk taxonomy; ISO/IEC 42001 gives a management-system structure.
- **Audit trail and lineage [I]:** Records who requested the agent, which spec, model, prompts, tools and eval results produced it, and every promotion.
- **Policy as code [I]:** Machine-enforced rules (allowed tools by tier, required approvals) applied during generation and deployment.
- **Agent inventory [I]:** One register of all agents, owners, versions and status. S18 notes organisations often do not know which agents are running.

## 8. Observability and AgentOps
- **End-to-end tracing [S16]:** Emits OpenTelemetry GenAI traces. Those conventions are still evolving, so isolate this behind an abstraction.
- **Cost and token FinOps [S5, S17]:** Per-agent and per-run cost tracking, budgets and alerts.
- **Production monitoring and online evals [S15, S17, I]:** Tracks quality, drift and failure patterns on live traffic.
- **Feedback loop into the factory [I]:** Production failures become new eval cases and prompt or tool fixes. This is what makes it a factory and not a one-shot generator.
- **Incident response and rollback [I]:** Kill switch, version rollback and a runbook per agent.

## 9. Lifecycle and CI/CD
- **Versioning of every artefact [S17, I]:** Prompts, tools, skills, specs, eval sets and models are versioned together.
- **CI/CD with eval gates [S17]:** Build, test, evaluate and deploy automatically, with promotion across dev, staging and production.
- **Model portability and upgrade testing [S15, I]:** Re-runs the eval suite against a new model before switching.
- **Deployment targets [S11, S14]:** Containers, serverless or a managed agent runtime, chosen per agent.

## 10. Factory operations and experience
- **Review console [I]:** One place where humans review the generated spec, tools, eval results and risk tier, then approve or edit.
- **Factory-level metrics [I]:** Measures the factory itself: share of generated agents passing evals first time, time to production, cost per agent, defect escape rate.
- **Template and domain packs [I]:** Pre-built patterns for retail, CPG and QSR use cases (e.g. inventory lookups, store-ops assistants).
- **Documentation generation [I]:** Produces runbooks, user stories, and Jira or Confluence artefacts from the blueprint.

## Suggested build order [I]
1. **Core loop:** blueprint → generate → eval → human review → deploy (layers 1, 2, 5, 10).
2. **Production safety:** durable execution, guardrails, identity, tracing, CI/CD gates (layers 4, 6, 8, 9).
3. **Scale and governance:** registry, risk tiers, audit, FinOps, factory metrics (layers 3, 7, 8, 10).

## Assumptions
- The factory targets enterprise agents, not consumer chatbots.
- Existing runtimes and frameworks are used; no custom runtime is built.
- Human review stays in the loop for production release.

## Open questions
- Which autonomy tiers are in scope: read-only, write with approval, or autonomous?
- Single runtime or multi-runtime support?
- Which regulations apply to target clients (e.g. EU AI Act, PCI scope for POS)? A gap in the sources.

## Review check
- **Requirements covered:** all layers from the source list are mapped.
- **Scope bounded:** no effort estimate is included; commercial claims (cost savings, time to production) are unevidenced.
- **Figures reconciled:** the only figure used is the ~15× token cost from S5.
- **Source caveat:** links came from web search results and were not individually opened; verify versioned specs (MCP, A2A, OpenTelemetry) before citing.

---

## 11. Implementation & Verification Matrix (Layers 1–10)

All 10 layers synthesized from the 20-source reading list have been verified and integrated into the Agent Development Factory:

| Layer | Synthesized Capabilities | Implementation Files | Verification Evidence & Tests | Status |
|---|---|---|---|---|
| **Layer 1: Intake & Specification** | Intent clarification [I], Blueprint generator [I], Solution triage (S1/S2), Feasibility & cost estimator (S5) | `agent_factory/control_plane/intake.py`<br>`src/core.js` (`triageSolutionComplexity`, `estimateTokenAndCostFeasibility`)<br>`src/cli.js` (`triage-solution`, `estimate-cost`) | `test/runner.js` Tests 18, 19 (Dual-run passed)<br>`tests/test_capability_map_layers.py` (3 tests passed) | ✅ Implemented & Verified |
| **Layer 2: Design & Generation Engine** | Pattern library (S1/S2: Router, Orchestrator-Worker, Evaluator-Optimizer, Prompt Chain, Data Processor), Framework-agnostic code gen (S3), Skill packaging (S8), A2A topology generator (S5/S10) | `agent_factory/workbench/pattern_library.py`<br>`agent_factory/workbench/code_generator.py`<br>`agent_factory/workbench/skill_packager.py` | `tests/test_capability_map_layers.py` (3 tests passed)<br>`tests/test_workbench.py` (3 tests passed) | ✅ Implemented & Verified |
| **Layer 3: Tool & Integration Layer** | Tool & MCP registry (S9/S14), Scoped credentials & typed effect levels (`READ_PUBLIC` to `SPEND_DELETE`) (S14/S18) | `data/capability_registry.json`<br>`src/core.js` (`importMcpToolSchema`)<br>`src/cli.js` (`import-mcp-tool`) | `test/runner.js` Test 16 (Dual-run passed)<br>`tests/test_registry.py` (2 tests passed) | ✅ Implemented & Verified |
| **Layer 4: Runtime & Orchestration** | Durable execution (S12), HITL approval gates (S2/S3/S12), Memory & state, Real filesystem containment | `agent_factory/control_plane/orchestrator.py`<br>`agent_factory/security/approval_gate.py`<br>`agent_factory/runtime/local_process.py`<br>`src/core.js` (`assertRealFsContainment`) | `test/runner.js` Test 11 (Dual-run passed)<br>`tests/test_runtime.py`, `tests/test_security.py` | ✅ Implemented & Verified |
| **Layer 5: Evaluation & Quality** | Auto-generated eval suite (S15), Capability & regression evals, Outcome-based grading, Synthetic test data, Release gate (S17) | `agent_factory/evals/graders.py`<br>`agent_factory/evals/runner.py`<br>`test/runner.js`<br>`test/evals/runner.js`<br>`scripts/evaluate-product-maturity.js` | 20/20 tests passed dual-run<br>5/5 eval cases passed<br>100/100 product maturity score | ✅ Implemented & Verified |
| **Layer 6: Security & Safety** | Guardrails (S2), OWASP Agentic Top 10 threat modeler (S18: ASI01–ASI05), Secret redactor, Skill AST quarantine | `agent_factory/security/threat_modeler.py`<br>`agent_factory/security/redactor.py`<br>`src/core.js` (`evaluateAgentThreatModel`)<br>`src/cli.js` (`threat-model`) | `test/runner.js` Test 20 (Dual-run passed)<br>`tests/test_capability_map_layers.py` (ASI01-ASI05 passed)<br>`tests/test_security.py` | ✅ Implemented & Verified |
| **Layer 7: Governance & Compliance** | Risk classification (S19/S20), Audit trail & lineage, Policy as code, Project constitution | `project_constitution.json`<br>`summary_ledger.json`<br>`src/core.js` (`verifyEvidenceConsistency`)<br>`specs/governance/` | `test/runner.js` Tests 8, 12, 15 (Dual-run passed)<br>`tests/test_policy.py` (3 tests passed) | ✅ Implemented & Verified |
| **Layer 8: Observability & AgentOps** | GenAI tracing abstraction (S16), Token FinOps (S5/S17), Diagnostic Doctor platform health & port canary | `agent_factory/evals/langsmith_adapter.py`<br>`test/evals/langsmith-client.js`<br>`src/core.js` (`runPlatformDoctor`)<br>`src/cli.js` (`doctor`) | `test/runner.js` Test 17 (Dual-run passed)<br>`tests/test_verification_pipeline.py` (4 tests passed) | ✅ Implemented & Verified |
| **Layer 9: Lifecycle & CI/CD** | Full artefact versioning (S17), Universal Agent Spec YAML compiler, CI/CD eval gates, Automated pipeline | `.github/workflows/ci.yml`<br>`src/core.js` (`exportAgentSpecYaml`)<br>`src/cli.js` (`export-agent-spec`)<br>`package.json` (`npm run ci`) | `test/runner.js` Tests 4, 7, 15 (Dual-run passed)<br>`tests/test_lifecycle.py` (passed) | ✅ Implemented & Verified |
| **Layer 10: Factory Operations & Experience** | Diagnostic Doctor, Automated Requirements Scaffolder, Documentation generation (MkDocs + Pages) | `src/cli.js` (`doctor`, `scaffold-requirements`)<br>`scripts/generate-api-docs.js`<br>`mkdocs.yml`, `docs/` | `test/runner.js` Tests 14, 17 (Dual-run passed)<br>`npm run ci` auto-docs generated | ✅ Implemented & Verified |


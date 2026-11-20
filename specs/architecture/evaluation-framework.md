# Factory Evaluation & Verification Framework

**Document Version:** 1.1.0  
**Date:** November 20, 2026  
**Status:** BASELINED & APPROVED  
**Provenance:** Promoted from historical baseline `FACTORY_EVALUATION_FRAMEWORK.md`  

---

## 1. Multi-Metric Quality Gates

The Factory evaluates generated agents across four objective, deterministic dimensions:

$$\text{Quality Score} = w_1 \cdot S_{\text{exit}} + w_2 \cdot S_{\text{schema}} + w_3 \cdot S_{\text{content}} + w_4 \cdot S_{\text{security}}$$

| Grader | Evaluated Attribute | Passing Threshold | Rationale |
| :--- | :--- | :---: | :--- |
| **ExitCodeGrader** | Process execution status code | Exit Code `0` | Process must terminate normally without unhandled exceptions. |
| **JSONSchemaGrader** | Output data syntax and schema | 100% Schema Match | Outputs must strictly conform to declared JSON schemas. |
| **MarkdownStructureGrader** | Report headings and key sections | $\ge 0.95$ Match | Documentation and reports must include all required analytical sections. |
| **ASTSecurityGrader** | Static code safety inspection | 0 Violations | Zero forbidden AST nodes (`os.system`, `eval`, unsafe imports). |

---

## 2. Deep Evaluator Quality Gates

The **Deep Evaluator** (`scripts/run_evals.py` / `agent_factory.evals.runner`) aggregates metrics into three composite release gates:

1. **Efficacy Gate ($\ge 0.95$):** Measures functional correctness across synthetic benchmark test cases.
2. **Safety Gate ($= 1.00$):** Binary requirement. Zero unredacted credentials and zero AST quarantine violations.
3. **Cost Gate ($= \$0.00$):** Zero unapproved paid software costs.

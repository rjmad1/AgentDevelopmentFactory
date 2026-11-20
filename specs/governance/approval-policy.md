# Factory Approval Policy

**Policy ID:** POL-SPEC-06  
**Version:** 1.0.0  
**Effective Date:** November 20, 2026  
**Status:** MANDATORY & ENFORCEABLE  
**Provenance:** Promoted from historical baseline `FACTORY_APPROVAL_POLICY.md`  

---

## 1. Approval Governance Principle

An agent or automated workflow cannot approve its own authority expansion, deployment, or policy overrides. Furthermore:

> **A model summary, worker completion report, or plain-text chat message cannot authenticate owner approval.**

All approvals for medium/high-risk actions, policy modifications, and production releases must be backed by a structured, verifiable **Approval Record** signed by an authorized human stakeholder.

---

## 2. Approval Record Schema

Every human approval record must be recorded in `evidence/approval_ledger.jsonl` and embedded in the candidate release manifest:

```json
{
  "approval_id": "appr_01H...",
  "project_id": "proj_20261103_001",
  "agent_id": "csv_data_anomaly_analyzer",
  "target_version": "1.0.0",
  "action_scope": "RELEASE_PROMOTION",
  "risk_classification": "LOW",
  "approved_effects": ["READ_PUBLIC", "WRITE_LOCAL_DRAFT"],
  "approver_identity": "Raja",
  "approver_role": "Platform Owner",
  "decision": "APPROVED",
  "approval_token": "AUTO_APPROVED_LOW_RISK_SHA256_b4c8a...",
  "timestamp": "2026-11-03T11:23:00Z",
  "rationale": "All automated evaluations passed; synthetic test fixtures verified."
}
```

---

## 3. Human Approval Gates

1. **Intake Gate:** High-risk capabilities requested during brief intake require explicit human confirmation before the workbench provisions tools.
2. **Quarantine Release Gate:** Code triggering AST quarantine violations (e.g. attempting subprocess execution) cannot be un-quarantined autonomously; it requires human override.
3. **Release Promotion Gate:** Promotion to the capability registry and production deployment requires human approval unless the candidate is explicitly classified as Tier 1 Low Risk.

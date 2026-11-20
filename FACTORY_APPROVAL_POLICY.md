# Factory Approval Policy

**Document Version:** 1.0.0  
**Date:** 2026-11-03  
**Author:** Antigravity 2.0 (Supervising Principal Platform Architect)  
**Status:** BASELINED & APPROVED  

---

## 1. Approval Governance Principle

An agent or automated workflow cannot approve its own authority expansion, deployment, or policy overrides. Furthermore, as established in Section 15 of the *Full-Lifecycle Engineering Handbook*, **a model summary, worker completion report, or plain-text chat message cannot authenticate owner approval**.

All approvals for medium/high-risk actions, policy modifications, and production releases must be backed by a structured, verifiable **Approval Record** signed by an authorized human stakeholder.

---

## 2. Approval Record Structure

An Approval Record must be recorded in `evidence/approval_ledger.jsonl` and embedded in the release manifest:

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
  "expiry": "2026-12-03T11:23:00Z",
  "revoked": false
}
```

---

## 3. Approval Gates in the Factory Lifecycle

```
[SPEC_DRAFT] ───(Gate A: Spec Approval)───► [BUILD]
                                               │
                                               ▼
[EVALUATE]   ───(Gate B: Release Gate) ───► [PACKAGE & DEPLOY]
                                               │
                                               ▼
[INCIDENT]   ───(Gate C: Recovery Gate)───► [RESTORE & RE-RUN]
```

### Gate A: Before Build (Spec Approval)
* Verifies that the Universal Agent Specification has passed semantic validation, dependencies exist in the Capability Registry, and execution resource limits are explicitly bounded.
* **Low Risk:** Autonomous clearance.
* **Medium/High Risk:** Requires human confirmation of scope and data classifications.

### Gate B: Before Release (Deployment Approval)
* Verifies that 100% of unit tests passed, all deterministic evaluation benchmarks met target thresholds, zero unauthorized side-effects occurred, and SHA-256 manifest is complete.
* **Low Risk:** Autonomous release promotion.
* **Medium/High Risk:** Requires cryptographically verified human token.

### Gate C: Before Recovery / Remediation Promotion (Change Approval)
* When autonomous remediation fixes a defect, promotion to production requires re-evaluating regressions and explicit owner sign-off.

---

## 4. Anti-Forgery & Verification Mechanism

To prevent rogue agents or hallucinating models from generating pseudo-approvals:
1. **Approval Verification Function:**
   ```python
   def verify_approval_token(token: str, project_id: str, risk_level: str) -> bool:
       if risk_level == "LOW" and token.startswith("AUTO_APPROVED_LOW_RISK"):
           return True
       # High-risk tokens must validate against HMAC-SHA256 signature using host-local secret
       return validate_hmac_signature(token, project_id)
   ```
2. **State Machine Lock:** The orchestrator physically checks `verify_approval_token()` before calling the packager or deployer. If verification fails, it raises `UnauthorizedActionException` and dumps the execution trace.

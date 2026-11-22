# Multi-Industry Sample Agent Blueprints & Reference Recipes

This guide provides production-ready specifications, workflow briefs, architectural patterns, tool definitions, and guardrail policies to create robust software agents across 6 major enterprise industries using the **Agent Development Factory (ADF)**.

Every blueprint adheres strictly to the **Universal Agent Specification Standard (`agent.yaml`)** and the **$0.00 spend ceiling invariant**.

---

## Blueprint Index

1. [Financial Services: Autonomous AML Transaction & Fraud Reconciliation Agent](#1-financial-services-autonomous-aml-transaction--fraud-reconciliation-agent)
2. [Healthcare & Life Sciences: HIPAA-Compliant Clinical Trial Patient Intake Agent](#2-healthcare--life-sciences-hipaa-compliant-clinical-trial-patient-intake-agent)
3. [Retail & E-Commerce: Dynamic Multichannel Inventory & Supplier SLA Agent](#3-retail--e-commerce-dynamic-multichannel-inventory--supplier-sla-agent)
4. [Cybersecurity & Cloud Ops: Zero-Trust Cloud Security Posture & Incident Triage Agent](#4-cybersecurity--cloud-ops-zero-trust-cloud-security-posture--incident-triage-agent)
5. [Manufacturing & Industrial IoT: SCADA Telemetry Anomaly & Predictive Maintenance Agent](#5-manufacturing--industrial-iot-scada-telemetry-anomaly--predictive-maintenance-agent)
6. [Legal & Corporate Governance: Multi-Jurisdiction Contract Risk & Clause Compliance Agent](#6-legal--corporate-governance-multi-jurisdiction-contract-risk--clause-compliance-agent)

---

## 1. Financial Services: Autonomous AML Transaction & Fraud Reconciliation Agent

### Executive Context
Financial institutions process millions of daily transaction records across automated clearing houses (ACH), SWIFT networks, and retail payment gateways. Regulatory frameworks (such as FinCEN SAR reporting and EU AMLD6) mandate real-time detection of structuring, sudden velocity spikes, and discrepancies between settlement ledgers.

### Blueprint Specifications
* **Industry**: Financial Services & FinTech
* **Solution Complexity**: `S2_AGENTIC_COMPLEX`
* **Architectural Pattern**: **Orchestrator-Worker** (Lead investigator coordinating anomaly analyzers)
* **Risk Tier**: `T1` (Contained local write to audit artifacts; Gate 8 Human-in-the-Loop review mandatory)
* **Target Platform**: Google Antigravity 2.0 or LangGraph

### Tool Allowlist & Capabilities
* `read_transaction_ledger`: Read localized daily transaction CSV/JSON exports (`READ_PUBLIC`).
* `compute_statistical_velocity`: Calculate transaction velocity, z-scores, and Benford's law compliance (`READ_PUBLIC`).
* `write_compliance_sar_docket`: Generate Markdown Suspicious Activity Report (SAR) in `./artifacts/sar_dockets/` (`WORKSPACE_WRITE`).
* ⛔ **Prohibited Tools**: `initiate_wire_transfer`, `freeze_customer_account` (strictly denied without dual-key T3 signoff).

### Workflow Brief Text (Copy into Factory Intake)
```text
Autonomous Financial Crime & AML Transaction Anomaly Detection Agent.
The agent ingests daily transaction records from localized CSV exports, parses transaction timestamps, amounts, origin accounts, and destination country codes.
It computes velocity metrics, identifies structuring patterns (multiple transactions just under $10,000 threshold), and detects international wire hops to unverified foreign banking entities.
Upon detecting anomalous transaction clusters, the agent must generate a standardized, timestamped Markdown SAR docket into ./artifacts/sar_dockets/ detailing suspicious account IDs, confidence scores, and rule violation justifications.
The agent must never execute fund freezes, balance adjustments, or external network calls. Spend ceiling is strictly $0.00.
```

### Confirmed Requirements & Behavioral Contracts
* `REQ-FIN-01`: Parse daily transaction ledger files without modifying raw source records.
* `REQ-FIN-02`: Calculate transaction frequency and flag accounts exceeding 5 transactions within a 15-minute rolling window.
* `REQ-FIN-03`: Flag structuring transactions within 5% of the $10,000 regulatory reporting threshold.
* `REQ-FIN-04`: Generate Markdown SAR compliance report into `./artifacts/` containing cryptographic SHA-256 evidence hashes.
* `REQ-FIN-05`: Strictly prohibit external financial API calls or automated account modifications.

---

## 2. Healthcare & Life Sciences: HIPAA-Compliant Clinical Trial Patient Intake Agent

### Executive Context
Clinical trial operations require screening thousands of electronic health record (EHR) summaries against complex inclusion and exclusion criteria (biomarkers, prior therapies, renal function limits) while maintaining zero-tolerance compliance with HIPAA privacy standards and cryptographic data isolation.

### Blueprint Specifications
* **Industry**: Healthcare & Life Sciences
* **Solution Complexity**: `S2_AGENTIC_COMPLEX`
* **Architectural Pattern**: **Hierarchical Supervisor** (Triager agent routing to Inclusion Specialist and Privacy Guard)
* **Risk Tier**: `T1` (Strict PII redaction; write confined to de-identified screening dossiers)
* **Target Platform**: Google Antigravity 2.0 or CrewAI

### Tool Allowlist & Capabilities
* `read_trial_protocol`: Ingest clinical trial protocol specification and inclusion/exclusion matrices (`READ_PUBLIC`).
* `read_patient_summary`: Ingest de-identified clinical notes and laboratory panels (`READ_PUBLIC`).
* `redact_protected_health_info`: High-entropy regex scrubber for Safe Harbor 18 PII identifiers (`READ_PUBLIC`).
* `write_trial_eligibility_report`: Write de-identified screening docket to `./artifacts/screenings/` (`WORKSPACE_WRITE`).
* ⛔ **Prohibited Tools**: `export_unmasked_ehr`, `send_patient_notification` (prohibited by Execution Rails).

### Workflow Brief Text (Copy into Factory Intake)
```text
HIPAA-Compliant Clinical Trial Patient Eligibility & Protocol Screening Agent.
The agent ingests de-identified clinical lab summaries (platelet counts, EGFR, ECOG performance status) and cross-references them against trial inclusion/exclusion criteria.
Before processing any narrative clinical notes, the agent executes mandatory Safe Harbor PII sanitization, masking patient names, medical record numbers, dates, and geographic identifiers.
For patients satisfying protocol parameters, the agent compiles an eligibility score and writes a de-identified Markdown screening dossier into ./artifacts/screenings/ outlining met criteria, unmet criteria, and required confirmatory tests.
The agent must never store or expose unmasked patient identifiers. Spend ceiling is strictly $0.00.
```

### Confirmed Requirements & Behavioral Contracts
* `REQ-HEALTH-01`: Enforce NeMo Output Rails to detect and mask all 18 HIPAA Safe Harbor identifiers.
* `REQ-HEALTH-02`: Parse laboratory panels and evaluate numerical thresholds against protocol inclusion criteria.
* `REQ-HEALTH-03`: Grade patient performance status (ECOG 0-2) based on verified physician encounter notes.
* `REQ-HEALTH-04`: Write structured screening recommendation dossier into `./artifacts/` with deterministic timestamps.
* `REQ-HEALTH-05`: Refuse processing of raw data feeds containing unencrypted social security numbers or cleartext names.

---

## 3. Retail & E-Commerce: Dynamic Multichannel Inventory & Supplier SLA Agent

### Executive Context
Modern omnichannel retailers balance distribution center inventory against regional sales velocities, holiday demand spikes, and supplier delivery lead times. Stockouts cause severe revenue leakage, while over-allocation inflates carrying costs.

### Blueprint Specifications
* **Industry**: Retail, E-Commerce & Supply Chain
* **Solution Complexity**: `S2_AGENTIC_COMPLEX`
* **Architectural Pattern**: **Orchestrator-Worker** (Inventory Triager delegating to Lead-Time & Sales Velocity workers)
* **Risk Tier**: `T1` (Local analysis and reorder recommendation reports; no automated fund transfers)
* **Target Platform**: Google Antigravity 2.0 or AutoGen

### Tool Allowlist & Capabilities
* `read_inventory_snapshot`: Read warehouse SKU stock levels and backorder logs (`READ_PUBLIC`).
* `read_historical_velocity`: Parse 30-day regional sell-through velocity rates (`READ_PUBLIC`).
* `calculate_reorder_point`: Calculate safety stock, economic order quantity (EOQ), and stockout risk date (`READ_PUBLIC`).
* `write_procurement_manifest`: Write proposed purchase orders to `./artifacts/purchase_orders/` (`WORKSPACE_WRITE`).
* ⛔ **Prohibited Tools**: `submit_live_purchase_order`, `charge_company_credit_line` (denied without T2/T3 elevation).

### Workflow Brief Text (Copy into Factory Intake)
```text
Multichannel Retail Inventory Optimization & Supplier SLA Performance Monitor.
The agent ingests daily inventory CSV snapshots across regional fulfillment centers alongside 30-day sales velocity data.
It calculates days of supply (DoS), compares available stock against vendor delivery lead times, and flags SKUs at risk of stockout within the next 14 days.
Additionally, it audits supplier fulfillment history to compute vendor SLA adherence percentages (on-time delivery vs late arrivals).
The agent outputs a prioritized Procurement Action Plan into ./artifacts/procurement/ with recommended reorder quantities and emergency redistribution transfers.
The agent operates with read-only supply chain data and bounded file output. Spend ceiling is strictly $0.00.
```

### Confirmed Requirements & Behavioral Contracts
* `REQ-RETAIL-01`: Ingest regional warehouse stock tables and identify SKUs with days of supply < 10 days.
* `REQ-RETAIL-02`: Evaluate vendor lead-time variance and calculate dynamic safety stock margins.
* `REQ-RETAIL-03`: Generate proposed purchase order recommendations in Markdown format inside `./artifacts/`.
* `REQ-RETAIL-04`: Track supplier delivery SLA metrics and flag vendors falling below 92% on-time performance.
* `REQ-RETAIL-05`: Enforce zero-spend ceiling ($0.00 USD) by utilizing local deterministic forecasting calculations.

---

## 4. Cybersecurity & Cloud Ops: Zero-Trust Cloud Security Posture & Incident Triage Agent

### Executive Context
Cloud engineering teams face alert fatigue from hundreds of daily security alarms across AWS, GCP, and Azure environments. Triage requires analyzing IAM permissions, public bucket exposures, network security group rules, and suspicious login vectors.

### Blueprint Specifications
* **Industry**: Cybersecurity & Cloud Infrastructure
* **Solution Complexity**: `S2_AGENTIC_COMPLEX`
* **Architectural Pattern**: **Hierarchical Supervisor** (Incident Commander delegating to IAM, Network, and Compliance Auditors)
* **Risk Tier**: `T1` (Audit & triage reporting; no automated destruction of cloud assets)
* **Target Platform**: Google Antigravity 2.0 or LangGraph

### Tool Allowlist & Capabilities
* `read_cloud_trail_events`: Ingest localized JSON CloudTrail / Audit logs (`READ_PUBLIC`).
* `audit_iam_permissions`: Evaluate IAM policies for wildcard (`"Action": "*"`) permissions (`READ_PUBLIC`).
* `verify_network_ingress`: Inspect security group rules for unauthenticated `0.0.0.0/0` exposure on sensitive ports (`READ_PUBLIC`).
* `write_incident_triage_docket`: Generate Markdown incident report into `./artifacts/security_incidents/` (`WORKSPACE_WRITE`).
* ⛔ **Prohibited Tools**: `terminate_cloud_instance`, `revoke_iam_role` (destructive effects gated behind approval tokens).

### Workflow Brief Text (Copy into Factory Intake)
```text
Automated Cloud Infrastructure Security Posture (CSPM) & Security Incident Triage Agent.
The agent audits local cloud configuration snapshots and event logs for critical security misconfigurations based on CIS Benchmarks and OWASP Cloud Top 10.
It inspects IAM roles for excessive privilege escalation vectors, flags S3 buckets or storage blobs exposed to public read/write without authentication, and identifies open security group ports (22 SSH, 3389 RDP, 5432 Postgres) bound to 0.0.0.0/0.
The agent compiles a Severity-Ranked Security Incident Dossier into ./artifacts/security_incidents/ outlining CVSS scores, affected resource ARNs, and exact remediation CLI commands.
The agent operates in read-only audit mode and will not mutate infrastructure resources. Spend ceiling is strictly $0.00.
```

### Confirmed Requirements & Behavioral Contracts
* `REQ-SEC-01`: Detect and flag IAM policies containing wildcard permissions (`*`) on critical services.
* `REQ-SEC-02`: Detect storage buckets configured with public ACLs or missing server-side encryption.
* `REQ-SEC-03`: Map detected exposures to MITRE ATT&CK techniques and CIS Cloud Benchmark controls.
* `REQ-SEC-04`: Write remediation plan to `./artifacts/` with copyable CLI remediation commands.
* `REQ-SEC-05`: Strictly prohibit automated resource termination or credential mutation.

---

## 5. Manufacturing & Industrial IoT: SCADA Telemetry Anomaly & Predictive Maintenance Agent

### Executive Context
Manufacturing plants, chemical refineries, and energy grids rely on SCADA systems monitoring thousands of IoT sensors (vibration, temperature, oil pressure, motor RPM). Detecting early stage mechanical wear prevents catastrophic equipment failure and multimillion-dollar downtime.

### Blueprint Specifications
* **Industry**: Manufacturing, Energy & Industrial IoT
* **Solution Complexity**: `S2_AGENTIC_COMPLEX`
* **Architectural Pattern**: **Single Focused Agent** with high-throughput batch processing loop
* **Risk Tier**: `T1` (Telemetry analysis and maintenance advisory dockets)
* **Target Platform**: Google Antigravity 2.0 or AutoGen

### Tool Allowlist & Capabilities
* `read_sensor_stream`: Parse time-series CSV sensor feeds (vibration mm/s, bearing temperature Celsius, RPM) (`READ_PUBLIC`).
* `compute_moving_average_drift`: Statistical standard deviation and exponential moving average (EMA) calculation (`READ_PUBLIC`).
* `write_maintenance_work_order`: Generate Markdown work order ticket into `./artifacts/maintenance_orders/` (`WORKSPACE_WRITE`).
* ⛔ **Prohibited Tools**: `shutdown_generator`, `override_scada_plc` (critical safety boundary).

### Workflow Brief Text (Copy into Factory Intake)
```text
Industrial SCADA Sensor Telemetry Anomaly Detector & Predictive Maintenance Advisory Agent.
The agent consumes high-frequency industrial IoT telemetry logs tracking motor vibration (mm/s), bearing operating temperatures (°C), and rotational frequency (RPM).
It computes rolling standard deviations, identifies thermal creep exceeding manufacturer baseline thresholds by > 2.5 sigma, and detects harmonic vibration signatures indicative of bearing fatigue or rotor misalignment.
Upon anomaly confirmation, the agent outputs a Predictive Maintenance Work Order into ./artifacts/maintenance_orders/ detailing machine asset IDs, hours until projected failure, and required spare parts.
The agent is an advisory observer and cannot send command packets to PLC or SCADA controllers. Spend ceiling is strictly $0.00.
```

### Confirmed Requirements & Behavioral Contracts
* `REQ-MFG-01`: Process time-series sensor logs with robust handling of missing readings or sensor dropouts.
* `REQ-MFG-02`: Calculate thermal and vibration drift relative to 30-day operating baselines.
* `REQ-MFG-03`: Classify equipment risk into Normal, Watchlist, or Critical Emergency Escalation.
* `REQ-MFG-04`: Generate Markdown maintenance advisory ticket into `./artifacts/` with component part numbers.
* `REQ-MFG-05`: Enforce safety isolation: the agent has zero write access to industrial control networks or PLCs.

---

## 6. Legal & Corporate Governance: Multi-Jurisdiction Contract Risk & Clause Compliance Agent

### Executive Context
Corporate legal teams manage hundreds of inbound vendor agreements, non-disclosure agreements (NDAs), and Master Services Agreements (MSAs). Reviewing governing law clauses, indemnification caps, intellectual property assignments, and data protection addenda across multiple jurisdictions is time-intensive and error-prone.

### Blueprint Specifications
* **Industry**: Legal, Risk & Corporate Governance
* **Solution Complexity**: `S2_AGENTIC_COMPLEX`
* **Architectural Pattern**: **Orchestrator-Worker** (Chief Legal Reviewer delegating to Liability, IP, and Privacy specialists)
* **Risk Tier**: `T1` (Legal review memos written to `./artifacts/legal_reviews/`)
* **Target Platform**: Google Antigravity 2.0 or CrewAI

### Tool Allowlist & Capabilities
* `read_contract_text`: Parse structured Markdown or plain-text contract agreements (`READ_PUBLIC`).
* `audit_liability_clauses`: Search and evaluate limitation of liability, consequential damages waivers, and indemnity caps (`READ_PUBLIC`).
* `audit_privacy_clauses`: Evaluate GDPR Article 28 and CCPA processor obligations (`READ_PUBLIC`).
* `write_redline_summary`: Write redline advisory memorandum to `./artifacts/legal_reviews/` (`WORKSPACE_WRITE`).
* ⛔ **Prohibited Tools**: `electronically_sign_agreement`, `accept_vendor_terms` (strictly prohibited).

### Workflow Brief Text (Copy into Factory Intake)
```text
Corporate Legal Risk Audit & Vendor Contract Compliance Analysis Agent.
The agent reviews commercial vendor contracts (Master Service Agreements, Software Licensing Agreements) in plain text or Markdown format.
It evaluates critical legal risk categories: unlimited liability clauses, missing reciprocal indemnification, unilateral termination rights, non-standard governing law jurisdictions, and GDPR/CCPA data transfer terms.
For every identified legal risk, the agent scores the risk severity (Low, Medium, High, Dealbreaker) and outputs a Redline Advisory Memorandum into ./artifacts/legal_reviews/ citing the problematic clause text, the corporate policy violation, and alternative compromise language.
The agent operates purely as an analytical assistant and cannot execute or approve contracts. Spend ceiling is strictly $0.00.
```

### Confirmed Requirements & Behavioral Contracts
* `REQ-LEGAL-01`: Ingest contract agreements and extract structured sections (Liability, Term, IP, Data Privacy).
* `REQ-LEGAL-02`: Identify uncapped liability clauses or asymmetric indemnification requirements.
* `REQ-LEGAL-03`: Verify data processing agreements against statutory GDPR Article 28 checklist items.
* `REQ-LEGAL-04`: Generate structured Redline Advisory Memorandum into `./artifacts/` with proposed compromise clause wording.
* `REQ-LEGAL-05`: Strictly prohibit automated electronic signature or binding agreement acceptance.

---

## Summary Matrix

| Blueprint | Industry | Architecture | Risk Tier | Primary Output Artifact | Prohibited Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AML Transaction Monitor** | Financial Services | Orchestrator-Worker | `T1` | Markdown SAR Dockets | External Wire Transfers |
| **Clinical Trial Intake** | Healthcare | Hierarchical Supervisor | `T1` | De-Identified Screening Dossier | Unmasked Patient PII Exposure |
| **Inventory Optimizer** | Retail & E-Commerce | Orchestrator-Worker | `T1` | Purchase Order Plan | Automated PO Submission |
| **CSPM Incident Triage** | Cybersecurity | Hierarchical Supervisor | `T1` | Incident Triage Dossier | Resource Termination / Deletion |
| **SCADA Telemetry Monitor** | Manufacturing | Single Focused Agent | `T1` | Maintenance Work Order | SCADA PLC Overrides |
| **Contract Risk Auditor** | Legal & Governance | Orchestrator-Worker | `T1` | Redline Advisory Memorandum | Electronic Signature Execution |

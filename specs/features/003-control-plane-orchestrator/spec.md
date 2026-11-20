# Feature Specification: Control Plane Lifecycle Orchestrator

**Feature Branch:** `003-control-plane-orchestrator`  
**Feature ID:** FEAT-003  
**Created:** 2026-11-20  
**Status:** Baselined  
**Classification:** Core Platform Back-End  

---

## 1. Problem Statement & Objective

Creating agents through ad-hoc scripting often results in unrecorded state transitions, skipped security checks, and unreproducible deployments.

The **Control Plane Lifecycle Orchestrator** governs the progression of every agent build through an 11-stage finite state machine (Intake, Feasibility, Spec Generation, Registry Resolution, Policy Check, Provisioning, Synthesis, Testing, Evaluation, Packaging, Promotion). All decisions, approvals, and transitions are recorded in an atomic SQLite database and append-only event stream.

---

## 2. User Scenarios & Prioritized User Stories

### User Story 1 — 11-Stage State Machine Progression (Priority: P1)
As an Agent Development Factory Operator, I want agent projects to transition through formal lifecycle states with strict entry and exit criteria, so that no stage is bypassed.

**Acceptance Criteria:**
* **Given** a new agent project intake,
* **When** `orchestrator.advance_stage()` is called,
* **Then** the stage machine transitions linearly from `INTAKE` through `PACKAGING`, halting at `WAITING_FOR_APPROVAL` if risk is Medium/High.

### User Story 2 — Persistent Task Ledger & Audit Event Stream (Priority: P1)
As a Compliance Auditor, I want an append-only event record of all stage transitions, so that the historical provenance of every agent release can be verified.

**Acceptance Criteria:**
* **Given** any state change or evaluation event,
* **When** recorded by `TaskLedger`,
* **Then** the event is written to `data/factory_state.db` and appended to `data/task_events.jsonl` with an ISO-8601 timestamp and SHA-256 payload digest.

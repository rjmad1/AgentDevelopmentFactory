# Factory Deployment Architecture

**Document Version:** 1.1.0  
**Date:** November 20, 2026  
**Status:** BASELINED & APPROVED  
**Provenance:** Promoted from historical baseline `FACTORY_DEPLOYMENT_ARCHITECTURE.md`  

---

## 1. Supported Deployment Topologies

The Factory packages synthesized agents into portable, self-contained artifacts capable of running across three independent deployment targets:

1. **Standalone Local Process (Target 1 - Primary):**
   - Packaged as a clean Python package (`src/agent.py`, `manifest.json`, `requirements.lock`).
   - Executed via `python -m src.agent` in an isolated virtual environment.
   - Zero external daemon or platform dependencies.
2. **Hermes Agent Harness (Target 2):**
   - Deployed as a managed task or skill profile within Hermes Agent (`hermes -p factory_agents`).
   - Integrated with Hermes CLI message board and tool routing.
3. **Containerized Microservice (Target 3):**
   - Deployed via lightweight OCI-compliant container using standard minimal base images (`python:3.11-slim`).
   - Ephemeral container instantiation with mounted input/output volumes.

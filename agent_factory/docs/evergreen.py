"""
Evergreen Technical Documentation Compiler Coupled to Declarative Schemas.
Automatically compiles Pydantic models, NIST catalogs, and scoring rubrics into markdown documentation.
Maintains a cryptographic schema manifest to ensure zero documentation drift and complete architectural transparency.
"""

import os
import json
import hashlib
import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from pydantic import BaseModel

from agent_factory.specs.schema import (
    UniversalAgentSpec,
    LimitsSpec,
    PolicySpec,
    AcceptanceSpec,
    EffectLevel,
    RiskTier,
)
from agent_factory.guardrails.nemo_nist import NistFrameworkCatalog, RailType


class SchemaManifestEntry(BaseModel):
    schema_name: str
    source_file: str
    sha256: str
    last_compiled_iso: str
    fields_count: int


class SchemaManifest(BaseModel):
    compiled_at_iso: str
    total_schemas: int
    schemas: Dict[str, SchemaManifestEntry]


class EvergreenDocCompiler:
    """
    Directly couples technical documentation generation to declarative schema definitions.
    Prevents architectural drift by calculating SHA-256 hashes and validating freshness.
    """

    @classmethod
    def compute_file_sha256(cls, path: Path) -> str:
        if not path.exists():
            return ""
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @classmethod
    def compile_all(cls, project_root: Path) -> SchemaManifest:
        """Compiles evergreen documentation for all declarative schemas in the platform."""
        root = Path(project_root).resolve()
        docs_dir = root / "docs" / "schemas"
        docs_dir.mkdir(parents=True, exist_ok=True)

        schemas_meta: Dict[str, SchemaManifestEntry] = {}
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # 1. Compile UniversalAgentSpec Schema Documentation
        spec_source = root / "agent_factory" / "specs" / "schema.py"
        spec_sha = cls.compute_file_sha256(spec_source)
        spec_md = cls._generate_universal_spec_doc()
        (docs_dir / "universal_spec.md").write_text(spec_md, encoding="utf-8")

        schemas_meta["UniversalAgentSpec"] = SchemaManifestEntry(
            schema_name="UniversalAgentSpec",
            source_file="agent_factory/specs/schema.py",
            sha256=spec_sha,
            last_compiled_iso=now_iso,
            fields_count=len(UniversalAgentSpec.model_fields),
        )

        # 2. Compile NIST AI RMF & Guardrails Catalog Documentation
        guardrails_source = root / "agent_factory" / "guardrails" / "nemo_nist.py"
        guardrails_sha = cls.compute_file_sha256(guardrails_source)
        guardrails_md = cls._generate_guardrails_doc()
        (docs_dir / "guardrails_and_nist.md").write_text(guardrails_md, encoding="utf-8")

        schemas_meta["NistGuardrailsCatalog"] = SchemaManifestEntry(
            schema_name="NistGuardrailsCatalog",
            source_file="agent_factory/guardrails/nemo_nist.py",
            sha256=guardrails_sha,
            last_compiled_iso=now_iso,
            fields_count=len(NistFrameworkCatalog.CONTROLS),
        )

        # 3. Compile Capability Registry MCP Tools Documentation
        cap_source = root / "data" / "capability_registry.json"
        cap_sha = cls.compute_file_sha256(cap_source)
        if cap_source.exists():
            cap_data = json.loads(cap_source.read_text(encoding="utf-8"))
            cap_md = cls._generate_capability_registry_doc(cap_data)
            (docs_dir / "capability_registry.md").write_text(cap_md, encoding="utf-8")
            tool_count = len(cap_data.get("tools", []))
        else:
            tool_count = 0

        schemas_meta["CapabilityRegistry"] = SchemaManifestEntry(
            schema_name="CapabilityRegistry",
            source_file="data/capability_registry.json",
            sha256=cap_sha,
            last_compiled_iso=now_iso,
            fields_count=tool_count,
        )

        # 4. Generate & Save Schema Manifest
        manifest = SchemaManifest(
            compiled_at_iso=now_iso,
            total_schemas=len(schemas_meta),
            schemas=schemas_meta,
        )

        manifest_file = root / "docs" / "schema_manifest.json"
        manifest_file.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
        return manifest

    @classmethod
    def verify_documentation_freshness(cls, project_root: Path) -> Tuple[bool, List[str]]:
        """
        Audits current schema files against schema_manifest.json.
        Returns: (is_fresh, drift_warnings)
        """
        root = Path(project_root).resolve()
        manifest_file = root / "docs" / "schema_manifest.json"

        if not manifest_file.exists():
            return False, ["Documentation manifest 'docs/schema_manifest.json' missing. Compilation required."]

        try:
            manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
            manifest = SchemaManifest(**manifest_data)
        except Exception as e:
            return False, [f"Corrupted schema manifest: {str(e)}"]

        drifts = []
        for name, entry in manifest.schemas.items():
            source_path = root / entry.source_file
            if not source_path.exists():
                drifts.append(f"Schema source file missing: {entry.source_file}")
                continue

            current_sha = cls.compute_file_sha256(source_path)
            if current_sha != entry.sha256:
                drifts.append(
                    f"SCHEMA DRIFT DETECTED in '{name}': source hash mutated from {entry.sha256[:8]} to {current_sha[:8]}. "
                    f"Documentation is stale. Run 'node scripts/generate-api-docs.js' to re-synchronize."
                )

        return (len(drifts) == 0), drifts

    @classmethod
    def _generate_universal_spec_doc(cls) -> str:
        lines = [
            "# Declarative Universal Agent Specification (UniversalAgentSpec)",
            "",
            "Authoritative schema definition governing agent contracts, risk classifications, resource boundaries, and state flows.",
            "",
            "## Schema Fields Overview",
            "",
            "| Field | Type | Required | Description |",
            "| :--- | :--- | :--- | :--- |",
        ]
        for name, field in UniversalAgentSpec.model_fields.items():
            is_req = "Yes" if field.is_required() else "No"
            desc = field.description or "Configurable specification attribute"
            lines.append(f"| `{name}` | `{field.annotation.__name__ if hasattr(field.annotation, '__name__') else str(field.annotation)}` | {is_req} | {desc} |")

        lines.extend([
            "",
            "## Risk Tier Matrix",
            "",
            "| Tier | Name | Containment Level | Human Approval Required | Max Wall Time |",
            "| :--- | :--- | :--- | :--- | :--- |",
            "| `T0` | Read-Only Informational | Ephemeral Sandbox | No | 30s |",
            "| `T1` | Contained Local Write | Sandboxed Local Workspace | Yes (Token Gated) | 60s |",
            "| `T2` | External Network Integration | Zero-Cost Allowlist Proxy | Yes (Token Gated) | 120s |",
            "| `T3` | High-Stakes Action / Deployment | Production Multi-Stage Gate | Mandatory Dual Signoff | 300s |",
            "",
            "## Effect Levels Hierarchy",
            "",
            "- `READ_PUBLIC`: Read-only access to unclassified local datasets.",
            "- `WRITE_LOCAL_DRAFT`: Write access strictly quarantined within workspace scratch/artifacts directory.",
            "- `NETWORK_EXTERNAL`: External network interaction (strictly constrained by constitutional $0.00 spend ceiling).",
            "- `ADMIN_MUTATION`: Elevated modification permissions requiring explicit human authorization token.",
            "",
        ])
        return "\n".join(lines)

    @classmethod
    def _generate_guardrails_doc(cls) -> str:
        lines = [
            "# NIST AI RMF Operational Safety Guardrail Catalog",
            "",
            "Direct mapping of programmable guardrails to the NIST AI Risk Management Framework (NIST AI 100-1) and NeMo architecture.",
            "",
            "## NIST AI RMF Controls Catalog",
            "",
            "| Control ID | Function | Title | Enforcement Rail | Primary Defense |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for code, ctrl in NistFrameworkCatalog.CONTROLS.items():
            rail_match = "INPUT" if "MP" in code else ("DIALOG" if "GV-1.2" in code else ("EXECUTION" if "MG-1.1" in code or "GV-1.3" in code else "OUTPUT"))
            code_val = ctrl.code if isinstance(ctrl.code, str) else getattr(ctrl.code, "value", str(ctrl.code))
            func_val = ctrl.function.value if hasattr(ctrl.function, "value") else str(ctrl.function)
            lines.append(f"| `{code_val}` | `{func_val}` | {ctrl.title} | `{rail_match}_RAIL` | {ctrl.description[:60]}... |")

        lines.extend([
            "",
            "## Four-Phase Guardrail Lifecycle",
            "",
            "1. **Input Rails (`MP-1.1`, `MP-2.3`, `GV-1.1`)**: Prompt injection sanitization, PII redaction, schema conformity.",
            "2. **Dialog Rails (`GV-1.2`, `MG-2.2`)**: State transition validation, intent drift detection.",
            "3. **Execution Rails (`GV-1.2`, `GV-1.3`, `MG-1.1`)**: Tool allowlist gating, path traversal defense, resource governor enforcement.",
            "4. **Output Rails (`MS-2.2`, `MS-2.7`, `MG-2.4`)**: Output schema compliance, secret leak interception, grounding verification.",
            "",
        ])
        return "\n".join(lines)

    @classmethod
    def _generate_capability_registry_doc(cls, registry_data: Dict[str, Any]) -> str:
        lines = [
            "# Universal MCP Capability Registry",
            "",
            "Catalog of registered Model Context Protocol (MCP) tools and native execution capabilities.",
            "",
            "| Tool Name | Provider | Effect Level | Containment | Spend Ceiling |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        tools = registry_data.get("tools", [])
        for t in tools:
            name = t.get("name", "unknown")
            provider = t.get("provider", "native")
            effect = t.get("effect_level", "READ_PUBLIC")
            boundary = t.get("containment_boundary", "workspace")
            lines.append(f"| `{name}` | `{provider}` | `{effect}` | {boundary} | $0.00 |")

        lines.append("")
        return "\n".join(lines)

"""
Unified Typed Capability Registry for the Agent Development Factory.
"""

from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import json
import datetime
from pydantic import BaseModel, Field


class CapabilityKind(str, Enum):
    MODEL = "MODEL"
    PROVIDER = "PROVIDER"
    HARNESS = "HARNESS"
    RUNTIME = "RUNTIME"
    FRAMEWORK = "FRAMEWORK"
    TOOL = "TOOL"
    MCP = "MCP"
    SKILL = "SKILL"
    EVALUATION = "EVALUATION"
    ARTIFACT = "ARTIFACT"


class CapabilityStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    ACTIVE = "ACTIVE"
    QUARANTINED = "QUARANTINED"
    DEPRECATED = "DEPRECATED"
    RETIRED = "RETIRED"


class CapabilityRecord(BaseModel):
    id: str = Field(..., description="Unique machine-readable capability identifier")
    kind: CapabilityKind
    name: str
    version: str = "1.0.0"
    provider: str = Field("local", description="Provider organization, repo, or service")
    description: str = ""
    license: str = "MIT"
    status: CapabilityStatus = CapabilityStatus.UNVERIFIED
    security_classification: str = "INTERNAL"
    permissions_required: List[str] = Field(default_factory=list)
    resource_requirements: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    registered_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    last_verified_at: Optional[str] = None
    verification_evidence: Optional[str] = None


class CapabilityRegistry:
    """Manages versioned, strongly typed capability discovery, validation, and resolution."""

    def __init__(self, persistence_path: Optional[Path] = None):
        self.persistence_path = Path(persistence_path) if persistence_path else None
        self._capabilities: Dict[str, CapabilityRecord] = {}
        if self.persistence_path and self.persistence_path.exists():
            self.load()

    def register(self, record: CapabilityRecord) -> None:
        self._capabilities[record.id] = record
        self._auto_save()

    def get(self, capability_id: str) -> Optional[CapabilityRecord]:
        return self._capabilities.get(capability_id)

    def list_all(
        self,
        kind: Optional[CapabilityKind] = None,
        status: Optional[CapabilityStatus] = None,
    ) -> List[CapabilityRecord]:
        results = list(self._capabilities.values())
        if kind:
            results = [c for c in results if c.kind == kind]
        if status:
            results = [c for c in results if c.status == status]
        return results

    def resolve(self, kind: CapabilityKind, criteria: Optional[Dict[str, Any]] = None) -> List[CapabilityRecord]:
        """Resolves active, verified capabilities matching specific criteria."""
        candidates = self.list_all(kind=kind, status=CapabilityStatus.ACTIVE)
        if not criteria:
            return candidates

        matched = []
        for c in candidates:
            match = True
            for k, v in criteria.items():
                if k in c.metadata:
                    if c.metadata[k] != v:
                        match = False
                        break
                elif getattr(c, k, None) != v:
                    match = False
                    break
            if match:
                matched.append(c)
        return matched

    def verify(self, capability_id: str, probe_fn: Callable[[], bool], evidence_desc: str = "Manual probe") -> bool:
        cap = self.get(capability_id)
        if not cap:
            return False
        try:
            success = probe_fn()
        except Exception:
            success = False

        if success:
            cap.status = CapabilityStatus.ACTIVE
            cap.last_verified_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
            cap.verification_evidence = evidence_desc
        else:
            cap.status = CapabilityStatus.UNVERIFIED
            cap.verification_evidence = f"Probe failed: {evidence_desc}"

        self._auto_save()
        return success

    def deprecate(self, capability_id: str, reason: str = "") -> bool:
        cap = self.get(capability_id)
        if not cap:
            return False
        cap.status = CapabilityStatus.DEPRECATED
        cap.metadata["deprecation_reason"] = reason
        self._auto_save()
        return True

    def _auto_save(self) -> None:
        if self.persistence_path:
            self.save()

    def save(self) -> None:
        if not self.persistence_path:
            return
        self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
        data = {cid: cap.model_dump(mode="json") for cid, cap in self._capabilities.items()}
        with open(self.persistence_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self) -> None:
        if not self.persistence_path or not self.persistence_path.exists():
            return
        with open(self.persistence_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._capabilities = {cid: CapabilityRecord(**cdata) for cid, cdata in data.items()}

"""Laya RLCD Decision Engine Liaison Adapter.

Connects the Agent Development Factory to the local Laya Intelligence Engine
(~/.laya/data/laya.db and ~/.laya/settings.json) to apply Reinforcement Learning
from Calibrated Decisions (RLCD) to code generation and evaluation quality gates.
"""

from __future__ import annotations

import json
import os
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class LayaRLCDWeights:
    """Calibrated decision weights for the 3 core evaluation rubrics."""
    weight_hallucination: float = 0.35
    weight_instruction: float = 0.35
    weight_security: float = 0.30
    prior_adjustment: float = 0.0
    confidence: float = 0.95
    source: str = "laya_db_calibrated"


@dataclass
class CalibratedDecision:
    """Result of an RLCD calibrated decision evaluation."""
    verdict: str  # PROMOTED | REJECTED_RETRY | BLOCKED
    composite_score: float
    raw_scores: Dict[str, float]
    weights_applied: LayaRLCDWeights
    threshold_applied: float
    reasons: List[str]
    rationale: str
    laya_feedback_logged: bool = False


class LayaAdapter:
    """Liaison between ADF and Laya Calibrated Decision Engine."""

    DEFAULT_SETTINGS_PATH = Path("~/.laya/settings.json").expanduser()
    DEFAULT_DB_PATH = Path("~/.laya/data/laya.db").expanduser()

    def __init__(
        self,
        settings_path: Optional[Path] = None,
        db_path: Optional[Path] = None,
    ) -> None:
        self.settings_path = Path(settings_path) if settings_path else self.DEFAULT_SETTINGS_PATH
        self.db_path = Path(db_path) if db_path else self.DEFAULT_DB_PATH
        self._cached_weights: Optional[LayaRLCDWeights] = None

    def is_laya_installed(self) -> bool:
        """Check if Laya configuration or database exists on the host."""
        return self.settings_path.exists() or self.db_path.exists()

    def get_calibrated_weights(self) -> LayaRLCDWeights:
        """Fetch or calculate RLCD calibrated weights from Laya's state.

        Analyzes recent feedback, audit records, and security rules in laya.db.
        If recent audit logs show heightened security incidents, security weight
        is dynamically calibrated higher.
        """
        if self._cached_weights:
            return self._cached_weights

        if not self.db_path.exists():
            # Fallback to standard calibrated defaults
            self._cached_weights = LayaRLCDWeights(
                weight_hallucination=0.35,
                weight_instruction=0.35,
                weight_security=0.30,
                prior_adjustment=0.0,
                confidence=0.90,
                source="default_canonical_prior",
            )
            return self._cached_weights

        try:
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            cur = conn.cursor()

            # Inspect audit_log for failure trends
            cur.execute(
                "SELECT success, count(*) FROM audit_log GROUP BY success"
            )
            rows = dict(cur.fetchall())
            total = sum(rows.values()) if rows else 0
            failures = rows.get(0, 0)

            # Inspect action_cards count
            cur.execute("SELECT count(*) FROM action_cards")
            action_count = cur.fetchone()[0]

            conn.close()

            # Calibrate weights based on failure ratios
            failure_rate = (failures / total) if total > 0 else 0.0
            sec_weight = 0.30 + min(0.10, failure_rate * 0.2)
            inst_weight = 0.35 - (sec_weight - 0.30) / 2
            hall_weight = 0.35 - (sec_weight - 0.30) / 2

            self._cached_weights = LayaRLCDWeights(
                weight_hallucination=round(hall_weight, 3),
                weight_instruction=round(inst_weight, 3),
                weight_security=round(sec_weight, 3),
                prior_adjustment=round(min(0.05, action_count * 0.001), 3),
                confidence=0.95,
                source=f"laya_db_historical({total}_events)",
            )
            return self._cached_weights
        except Exception:
            self._cached_weights = LayaRLCDWeights(
                weight_hallucination=0.35,
                weight_instruction=0.35,
                weight_security=0.30,
                prior_adjustment=0.0,
                confidence=0.85,
                source="fallback_safe_prior",
            )
            return self._cached_weights

    def evaluate_decision(
        self,
        hallucination_score: float,
        instruction_score: float,
        security_score: float,
        composite_threshold: float = 0.92,
        security_threshold: float = 1.00,
        context_notes: Optional[Dict[str, Any]] = None,
    ) -> CalibratedDecision:
        """Calibrate and decide promotion outcome using Laya RLCD.

        Enforces:
        1. Hard Security Gate: If security_score < security_threshold, instant BLOCKED.
        2. RLCD Weighted Score: w_H * s_H + w_I * s_I + w_S * s_S + prior
        3. Threshold Comparison: If composite_score >= composite_threshold, PROMOTED;
           otherwise REJECTED_RETRY for self-healing.
        """
        weights = self.get_calibrated_weights()
        reasons: List[str] = []

        # 1. Hard zero-tolerance security gate
        if security_score < security_threshold:
            reasons.append(
                f"Hard Security Boundary breached: score {security_score:.2f} < threshold {security_threshold:.2f}."
            )
            return CalibratedDecision(
                verdict="BLOCKED",
                composite_score=0.0,
                raw_scores={
                    "hallucination": hallucination_score,
                    "instruction": instruction_score,
                    "security": security_score,
                },
                weights_applied=weights,
                threshold_applied=composite_threshold,
                reasons=reasons,
                rationale="Security invariant failure cannot be self-healed automatically without human intervention.",
            )

        # 2. Compute RLCD composite score
        composite = (
            weights.weight_hallucination * hallucination_score
            + weights.weight_instruction * instruction_score
            + weights.weight_security * security_score
            + weights.prior_adjustment
        )
        composite = min(1.0, max(0.0, composite))

        if hallucination_score < 0.90:
            reasons.append(f"Hallucination score ({hallucination_score:.2f}) below passing bar (0.90).")
        if instruction_score < 0.90:
            reasons.append(f"Instruction following score ({instruction_score:.2f}) below passing bar (0.90).")

        verdict = "PROMOTED" if composite >= composite_threshold and not reasons else "REJECTED_RETRY"

        if verdict == "PROMOTED":
            rationale = (
                f"Candidate passes all 3 quality rubrics with RLCD composite score "
                f"{composite:.3f} >= threshold {composite_threshold:.2f}."
            )
        else:
            rationale = (
                f"Candidate scored {composite:.3f} < threshold {composite_threshold:.2f}. "
                f"Self-healing prompt remediation required."
            )

        logged = self.log_feedback_event(
            verdict=verdict,
            composite_score=composite,
            scores={"hallucination": hallucination_score, "instruction": instruction_score, "security": security_score},
            metadata=context_notes,
        )

        return CalibratedDecision(
            verdict=verdict,
            composite_score=round(composite, 3),
            raw_scores={
                "hallucination": hallucination_score,
                "instruction": instruction_score,
                "security": security_score,
            },
            weights_applied=weights,
            threshold_applied=composite_threshold,
            reasons=reasons,
            rationale=rationale,
            laya_feedback_logged=logged,
        )

    def log_feedback_event(
        self,
        verdict: str,
        composite_score: float,
        scores: Dict[str, float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Log decision card into Laya's audit ledger or fallback append-only ledger."""
        payload = {
            "source": "ADF_LLM_JUDGE_RLCD",
            "verdict": verdict,
            "composite_score": composite_score,
            "scores": scores,
            "metadata": metadata or {},
            "timestamp": time.time(),
        }

        # Try to record into Laya database if writable
        if self.db_path.exists():
            try:
                conn = sqlite3.connect(self.db_path, timeout=1.0)
                cur = conn.cursor()
                cur.execute(
                    """INSERT INTO audit_log (timestamp, step, model_used, processing_tier, success, metadata)
                       VALUES (datetime('now'), 'ADF_RLCD_JUDGE', 'laya_calibrated_decision', 'RLCD_GATE', ?, ?)""",
                    (1 if verdict == "PROMOTED" else 0, json.dumps(payload)),
                )
                conn.commit()
                conn.close()
                return True
            except Exception:
                pass

        # Fallback to local ADF audit file
        try:
            local_audit = Path("store/check_events.jsonl")
            if local_audit.parent.exists():
                with open(local_audit, "a", encoding="utf-8") as f:
                    f.write(json.dumps({"event_type": "LAYA_RLCD_JUDGE_DECISION", **payload}) + "\n")
            return True
        except Exception:
            return False

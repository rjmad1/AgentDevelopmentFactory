"""
Policy Enforcement Engine for Least-Privilege Authority and Path Boundaries.
"""

from pathlib import Path
from typing import List, Union
from agent_factory.specs.schema import EffectLevel, PolicySpec, LimitsSpec


class PolicyViolationError(PermissionError):
    """Raised when an agent attempts an action that violates its approved policy."""
    pass


class PolicyEnforcer:
    """Validates runtime actions, path boundaries, and resource limits against approved policy."""

    def __init__(self, workspace_root: Path, policy: PolicySpec, limits: LimitsSpec):
        self.workspace_root = workspace_root.resolve()
        self.policy = policy
        self.limits = limits

    def validate_path_access(self, target_path: Union[str, Path], write: bool = False) -> Path:
        """
        Validates that a file path is safe and permitted.
        Write operations MUST be contained strictly within the workspace_root.
        """
        p = Path(target_path)
        if not p.is_absolute():
            resolved = (self.workspace_root / p).resolve()
        else:
            resolved = p.resolve()

        # Check path traversal / boundary
        is_inside_workspace = str(resolved).startswith(str(self.workspace_root))

        if write:
            if not is_inside_workspace:
                raise PolicyViolationError(
                    f"Security Boundary Violation: Write attempted outside workspace at '{resolved}'."
                )
            if EffectLevel.WRITE_LOCAL_DRAFT not in self.policy.permitted_effects:
                raise PolicyViolationError(
                    "Policy Denial: WRITE_LOCAL_DRAFT permission is not granted in agent policy."
                )
        else:
            # Read operations
            if not is_inside_workspace:
                if EffectLevel.READ_PUBLIC not in self.policy.permitted_effects and EffectLevel.READ_PRIVATE not in self.policy.permitted_effects:
                    raise PolicyViolationError(
                        f"Policy Denial: Reading outside workspace at '{resolved}' without read permission."
                    )

        return resolved

    def validate_tool_invocation(self, tool_name: str, requested_effect: EffectLevel) -> None:
        """Asserts that the tool and its effect level are authorized."""
        if tool_name not in self.policy.permitted_tools:
            raise PolicyViolationError(
                f"Policy Denial: Tool '{tool_name}' is not in the permitted tools allowlist: {self.policy.permitted_tools}"
            )
        if requested_effect not in self.policy.permitted_effects:
            raise PolicyViolationError(
                f"Policy Denial: Tool '{tool_name}' requests effect '{requested_effect}', "
                f"which exceeds permitted effects: {self.policy.permitted_effects}"
            )

    def validate_spending(self, current_cost: float, additional_cost: float) -> None:
        """Enforces paid spend ceiling."""
        projected = current_cost + additional_cost
        if projected > self.limits.paid_spend_ceiling:
            raise PolicyViolationError(
                f"Budget Ceiling Exceeded: Projected spend ${projected:.4f} exceeds ceiling ${self.limits.paid_spend_ceiling:.4f}."
            )

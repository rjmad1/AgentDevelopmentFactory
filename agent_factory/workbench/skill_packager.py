"""
Skill Packaging Engine conforming to Agent Skills Specification (agentskills.io/specification [S8]).
Packages repeatable procedures and tool contracts as self-contained SKILL.md bundles.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import hashlib
from agent_factory.specs.schema import UniversalAgentSpec


class SkillPackager:
    """Packages universal agent specifications and procedures into portable SKILL.md bundles."""

    @classmethod
    def package_as_skill(
        cls,
        spec: UniversalAgentSpec,
        output_dir: Path,
        skill_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Synthesizes a standard Agent Skills bundle (SKILL.md) from UniversalAgentSpec.
        """
        output_dir = Path(output_dir)
        name = skill_name or spec.agent_id.replace("_", "-")
        skill_dir = output_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)

        skill_md_path = skill_dir / "SKILL.md"

        # 1. Frontmatter
        tools_list = "\n".join([f"  - {t}" for t in spec.policy.permitted_tools]) or "  - none"
        frontmatter = [
            "---",
            f"name: {name}",
            f'description: "{spec.purpose.replace(chr(34), chr(39))}"',
            f'version: "{spec.version}"',
            f'author: "{spec.owner}"',
            "tools_required:",
            tools_list,
            f"mode: {spec.policy.mode}",
            f"spend_ceiling: {spec.limits.paid_spend_ceiling}",
            "---",
            "",
        ]

        # 2. Body
        body = [
            f"# Skill: {name}",
            "",
            "## 1. Overview & Objective",
            f"{spec.purpose}",
            "",
            "## 2. Input Specifications",
        ]

        if spec.inputs:
            for inp_name, inp_spec in spec.inputs.items():
                body.append(f"* **`{inp_name}`** (`{inp_spec.type}`): {inp_spec.description or 'Target input parameter'}")
        else:
            body.append("* None required.")

        body.extend([
            "",
            "## 3. Standard Operating Procedure",
            "1. **Validation**: Validate format and schema of incoming inputs against containment boundaries.",
            "2. **Execution**: Execute designated tool actions within permitted effect levels.",
            "3. **Synthesis**: Aggregate results into declared output artifacts.",
            "4. **Verification**: Verify that output artifacts exist and contain non-empty data without secret leakage.",
            "",
            "## 4. Policy Constraints & Guardrails",
            f"* **Mode**: `{spec.policy.mode}`",
            f"* **Permitted Effects**: {', '.join([e.value for e in spec.policy.permitted_effects]) if spec.policy.permitted_effects else 'READ_PUBLIC'}",
            f"* **Max Steps**: {spec.limits.max_steps}",
            f"* **Max Tokens**: {spec.limits.max_tokens}",
            f"* **Wall-Clock Limit**: {spec.limits.max_wall_time_seconds}s",
            f"* **On Denial Action**: `{spec.policy.on_denial.value}`",
            "",
            "## 5. Output Deliverables",
        ])

        if spec.outputs:
            for out_name, out_spec in spec.outputs.items():
                body.append(f"* **`{out_name}`** (`{out_spec.type}` -> `{out_spec.path or 'stdout'}`): {out_spec.description or 'Generated artifact'}")
        else:
            body.append("* Primary terminal output report.")

        full_content = "\n".join(frontmatter + body) + "\n"
        with open(skill_md_path, "w", encoding="utf-8") as f:
            f.write(full_content)

        sha256 = hashlib.sha256(full_content.encode("utf-8")).hexdigest()

        return {
            "skill_name": name,
            "skill_dir": skill_dir,
            "skill_md_path": skill_md_path,
            "sha256": sha256,
            "version": spec.version,
        }

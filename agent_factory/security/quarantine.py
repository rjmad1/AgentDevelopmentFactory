"""
Skill and Capability Quarantine Pipeline with AST Security Auditing.
"""

import ast
from pathlib import Path
from typing import List, Dict, Any, Union


class SecurityFinding(Exception):
    """Raised when an unvetted script contains prohibited constructs."""
    pass


class SkillQuarantine:
    """Performs static Abstract Syntax Tree (AST) security audits on newly proposed tools/skills."""

    PROHIBITED_MODULES = {"ctypes", "winreg", "_winapi", "msvcrt"}
    PROHIBITED_CALLS = {"eval", "exec", "__import__"}

    @classmethod
    def audit_python_source(cls, source_code: str) -> List[str]:
        findings = []
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            return [f"Syntax Error in candidate source: {e.msg} at line {e.lineno}"]

        for node in ast.walk(tree):
            # Check prohibited module imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in cls.PROHIBITED_MODULES:
                        findings.append(f"Prohibited module import: '{alias.name}' at line {node.lineno}")
            elif isinstance(node, ast.ImportFrom):
                if node.module in cls.PROHIBITED_MODULES:
                    findings.append(f"Prohibited from-import: '{node.module}' at line {node.lineno}")

            # Check dangerous built-in execution calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in cls.PROHIBITED_CALLS:
                        findings.append(f"Dangerous dynamic call: '{node.func.id}()' at line {node.lineno}")
                elif isinstance(node.func, ast.Attribute):
                    # Flag os.system
                    if node.func.attr == "system" and isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
                        findings.append(f"Prohibited direct shell call: 'os.system()' at line {node.lineno}")

        return findings

    @classmethod
    def audit_file(cls, file_path: Union[str, Path]) -> List[str]:
        p = Path(file_path)
        if not p.exists() or p.suffix != ".py":
            return []
        with open(p, "r", encoding="utf-8") as f:
            code = f.read()
        return cls.audit_python_source(code)

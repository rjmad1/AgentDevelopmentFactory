"""
CLI Entrypoint for develop_an_agent_that_analyzes.
"""

import sys
import json
from pathlib import Path
from agent import run_agent

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m develop_an_agent_that_analyzes <csv_dataset_path> [output_dir] [threshold]")
        sys.exit(1)

    csv_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "artifacts"
    threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0

    try:
        result = run_agent(csv_path, out_dir, threshold)
        print(json.dumps(result, indent=2))
        sys.exit(0)
    except Exception as e:
        print(f"Agent Execution Error: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()

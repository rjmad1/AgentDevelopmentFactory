# Command-Line Interface (`src/cli.js`)

The Factory authoring slice provides a zero-dependency CLI for initializing immutable revisions, running deterministic verification checks, and auditing evidence logs.

---

## Synopsis

```bash
node src/cli.js <command> [options]
```

---

## Commands

### `init-revision`
Initializes a new immutable revision from a raw brief and structured requirements JSON.

```bash
node src/cli.js init-revision \
  --brief <path-to-brief.txt> \
  --requirements <path-to-requirements.json> \
  --revision-id <revision-identifier> \
  [--parent-rev <parent-revision-id>] \
  [--store-dir <custom-store-path>]
```

**Options:**
* `--brief <path>`: Path to brief text file.
* `--requirements <path>`: Path to structured requirements JSON.
* `--revision-id <id>`: 1-64 alphanumeric identifier without path traversal.
* `--parent-rev <id>`: Optional parent revision ID.
* `--store-dir <path>`: Custom storage directory (defaults to `./store`).

---

### `run-check`
Executes a deterministic check and records the outcome to `check_events.jsonl` and `evidence.json`.

```bash
node src/cli.js run-check \
  --revision <revision-id> \
  --check <check-id> \
  [--store-dir <custom-store-path>]
```

**Available Checks:**
* `CHK-STATIC-SCHEMA`: Verifies syntax and schema alignment.
* `CHK-REQUIREMENTS-TRIAGE`: Validates requirement confirmation assertions and flags inferred defaults.

---

### `inspect`
Displays metadata, requirement counts, and check statuses for a given revision.

```bash
node src/cli.js inspect --revision <revision-id> [--store-dir <path>]
```

---

### `verify-consistency`
Performs an audit between the append-only event log (`check_events.jsonl`) and the materialized ledger (`evidence.json`).

```bash
node src/cli.js verify-consistency --revision <revision-id> [--store-dir <path>]
```

"""
Durable State Ledger for Factory Control Plane (SQLite + JSON Lines).
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import datetime
from pydantic import BaseModel


class TaskRecord(BaseModel):
    task_id: str
    project_id: str
    stage: str
    status: str  # QUEUED, RUNNING, COMPLETED, FAILED, BLOCKED
    input_hash: str
    output_hash: Optional[str] = None
    evidence_ref: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    updated_at: str


class TaskLedger:
    """Provides atomic SQLite persistence and append-only event logging for factory tasks."""

    def __init__(self, db_path: Path, event_log_path: Optional[Path] = None):
        self.db_path = Path(db_path)
        self.event_log_path = Path(event_log_path) if event_log_path else self.db_path.parent / "task_events.jsonl"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    status TEXT NOT NULL,
                    input_hash TEXT NOT NULL,
                    output_hash TEXT,
                    evidence_ref TEXT,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks (project_id)")
            conn.commit()

    def record_task(
        self,
        task_id: str,
        project_id: str,
        stage: str,
        status: str,
        input_hash: str = "none",
        output_hash: Optional[str] = None,
        evidence_ref: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> TaskRecord:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO tasks (task_id, project_id, stage, status, input_hash, output_hash, evidence_ref, error_message, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(task_id) DO UPDATE SET
                    stage=excluded.stage,
                    status=excluded.status,
                    output_hash=excluded.output_hash,
                    evidence_ref=excluded.evidence_ref,
                    error_message=excluded.error_message,
                    updated_at=excluded.updated_at
                """,
                (task_id, project_id, stage, status, input_hash, output_hash, evidence_ref, error_message, now, now),
            )
            conn.commit()

        record = TaskRecord(
            task_id=task_id,
            project_id=project_id,
            stage=stage,
            status=status,
            input_hash=input_hash,
            output_hash=output_hash,
            evidence_ref=evidence_ref,
            error_message=error_message,
            created_at=now,
            updated_at=now,
        )

        self._append_event({
            "timestamp": now,
            "task_id": task_id,
            "project_id": project_id,
            "stage": stage,
            "status": status,
            "evidence_ref": evidence_ref,
        })
        return record

    def get_task(self, task_id: str) -> Optional[TaskRecord]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()
            if row:
                return TaskRecord(**dict(row))
        return None

    def list_project_tasks(self, project_id: str) -> List[TaskRecord]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE project_id = ? ORDER BY created_at ASC", (project_id,))
            return [TaskRecord(**dict(r)) for r in cursor.fetchall()]

    def _append_event(self, event: Dict[str, Any]) -> None:
        try:
            with open(self.event_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception:
            pass

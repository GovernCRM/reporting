import sqlite3
from pathlib import Path
import json
from uuid import uuid4
from datetime import datetime

DB_PATH = Path("db/reports.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            organization_id TEXT,
            name TEXT,
            created_at TEXT,
            query TEXT
        )""")
        conn.commit()

def save_report(org_id: str, name: str, query_dict: dict):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        report_id = str(uuid4())
        query_json = json.dumps(query_dict)
        cursor.execute(
            "INSERT INTO reports (id, organization_id, name, created_at, query) VALUES (?, ?, ?, ?, ?)",
            (report_id, org_id, name, datetime.utcnow().isoformat(), query_json)
        )
        conn.commit()

def get_reports(org_id: str):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, created_at, query FROM reports WHERE organization_id = ?", (org_id,))
        rows = cursor.fetchall()
        return [{"id": r[0], "name": r[1], "created_at": r[2], "query": json.loads(r[3])} for r in rows]

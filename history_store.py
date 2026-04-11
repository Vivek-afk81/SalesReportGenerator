import json
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
HISTORY_DIR = BASE_DIR / "report_history"
INDEX_FILE = HISTORY_DIR / "history_index.json"


def _ensure_history_dir():
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def _read_index():
    _ensure_history_dir()
    if not INDEX_FILE.exists():
        return []

    with open(INDEX_FILE, "r", encoding="utf-8") as history_file:
        try:
            return json.load(history_file)
        except json.JSONDecodeError:
            return []


def _write_index(history_entries):
    _ensure_history_dir()
    with open(INDEX_FILE, "w", encoding="utf-8") as history_file:
        json.dump(history_entries, history_file, indent=2)


def save_report_run(source_name, channel, df, audit, inventory_alerts):
    _ensure_history_dir()

    timestamp = datetime.now()
    run_id = timestamp.strftime("%Y%m%d_%H%M%S")
    summary = {
        "run_id": run_id,
        "timestamp": timestamp.isoformat(timespec="seconds"),
        "source_name": source_name,
        "channel": channel,
        "rows_uploaded": int(audit["total_rows"]),
        "valid_rows": int(audit["valid_count"]),
        "invalid_rows": int(audit["invalid_count"]),
        "duplicate_entries": int(audit["duplicate_entries"]),
        "empty_lines": int(audit["empty_lines"]),
        "transactions": int(len(df)),
        "revenue": float(df["Price"].sum()) if not df.empty else 0.0,
        "at_risk_count": int((inventory_alerts["Risk Level"] != "Healthy").sum()) if not inventory_alerts.empty else 0,
    }

    details = {
        "summary": summary,
        "audit": {
            **audit,
            "invalid_ids": sorted(set(audit["invalid_ids"])),
        },
        "transactions": df.to_dict(orient="records"),
        "inventory_alerts": inventory_alerts.to_dict(orient="records"),
    }

    detail_file = HISTORY_DIR / f"{run_id}.json"
    with open(detail_file, "w", encoding="utf-8") as report_file:
        json.dump(details, report_file, indent=2, default=str)

    history_entries = _read_index()
    history_entries = [entry for entry in history_entries if entry["run_id"] != run_id]
    history_entries.insert(0, summary)
    _write_index(history_entries)

    return summary


def load_history():
    return _read_index()


def load_run_details(run_id):
    detail_file = HISTORY_DIR / f"{run_id}.json"
    if not detail_file.exists():
        return None

    with open(detail_file, "r", encoding="utf-8") as report_file:
        return json.load(report_file)

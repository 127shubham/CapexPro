from __future__ import annotations

import csv
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable


DEFAULT_DB_PATH = Path("data/expenses.db")
DEFAULT_RECEIPTS_DIR = Path("receipts")


@dataclass
class Expense:
    expense_date: date
    category: str
    amount: float
    vendor: str = ""
    description: str = ""
    payment_method: str = ""
    receipt_path: str = ""


def init_db(db_path: Path = DEFAULT_DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                vendor TEXT,
                description TEXT,
                payment_method TEXT,
                receipt_path TEXT,
                created_at TEXT NOT NULL
            )
            """
        )


def save_receipt(file_name: str, file_bytes: bytes, receipts_dir: Path = DEFAULT_RECEIPTS_DIR) -> str:
    receipts_dir.mkdir(parents=True, exist_ok=True)
    safe_name = Path(file_name).name.replace(" ", "_")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    target = receipts_dir / f"{stamp}_{safe_name}"
    target.write_bytes(file_bytes)
    return str(target)


def add_expense(expense: Expense, db_path: Path = DEFAULT_DB_PATH) -> None:
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO expenses (
                expense_date, category, amount, vendor, description,
                payment_method, receipt_path, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                expense.expense_date.isoformat(),
                expense.category,
                expense.amount,
                expense.vendor,
                expense.description,
                expense.payment_method,
                expense.receipt_path,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )


def get_monthly_expenses(year: int, month: int, db_path: Path = DEFAULT_DB_PATH) -> list[dict]:
    init_db(db_path)
    prefix = f"{year:04d}-{month:02d}"
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, expense_date, category, amount, vendor, description,
                   payment_method, receipt_path, created_at
            FROM expenses
            WHERE expense_date LIKE ?
            ORDER BY expense_date DESC, id DESC
            """,
            (f"{prefix}%",),
        ).fetchall()
    return [dict(r) for r in rows]


def get_monthly_total(year: int, month: int, db_path: Path = DEFAULT_DB_PATH) -> float:
    init_db(db_path)
    prefix = f"{year:04d}-{month:02d}"
    with sqlite3.connect(db_path) as conn:
        value = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE expense_date LIKE ?",
            (f"{prefix}%",),
        ).fetchone()[0]
    return float(value)


def get_monthly_category_totals(year: int, month: int, db_path: Path = DEFAULT_DB_PATH) -> list[tuple[str, float]]:
    init_db(db_path)
    prefix = f"{year:04d}-{month:02d}"
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT category, COALESCE(SUM(amount), 0) AS total
            FROM expenses
            WHERE expense_date LIKE ?
            GROUP BY category
            ORDER BY total DESC
            """,
            (f"{prefix}%",),
        ).fetchall()
    return [(str(r[0]), float(r[1])) for r in rows]


def export_expenses_csv(rows: Iterable[dict], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "id",
        "expense_date",
        "category",
        "amount",
        "vendor",
        "description",
        "payment_method",
        "receipt_path",
        "created_at",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in columns})
    return output_path

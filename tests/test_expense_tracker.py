from datetime import date
from pathlib import Path

from src.expense_tracker import (
    Expense,
    add_expense,
    export_expenses_csv,
    get_monthly_category_totals,
    get_monthly_expenses,
    get_monthly_total,
    save_receipt,
)


def test_add_and_aggregate_expenses(tmp_path: Path) -> None:
    db_path = tmp_path / "expenses.db"

    add_expense(
        Expense(date(2026, 1, 10), "Travel", 1200.0, vendor="Airline"),
        db_path=db_path,
    )
    add_expense(
        Expense(date(2026, 1, 15), "Food", 200.0, vendor="Cafe"),
        db_path=db_path,
    )
    add_expense(
        Expense(date(2026, 2, 1), "Travel", 999.0, vendor="Rail"),
        db_path=db_path,
    )

    jan_total = get_monthly_total(2026, 1, db_path=db_path)
    jan_rows = get_monthly_expenses(2026, 1, db_path=db_path)
    jan_categories = dict(get_monthly_category_totals(2026, 1, db_path=db_path))

    assert jan_total == 1400.0
    assert len(jan_rows) == 2
    assert jan_categories["Travel"] == 1200.0
    assert jan_categories["Food"] == 200.0


def test_receipt_and_csv_export(tmp_path: Path) -> None:
    receipt_path = save_receipt("invoice.pdf", b"hello", receipts_dir=tmp_path / "receipts")
    assert Path(receipt_path).exists()

    rows = [
        {
            "id": 1,
            "expense_date": "2026-01-10",
            "category": "Travel",
            "amount": 100.0,
            "vendor": "Airline",
            "description": "Flight",
            "payment_method": "Company Card",
            "receipt_path": receipt_path,
            "created_at": "2026-01-10T12:00:00",
        }
    ]

    csv_file = export_expenses_csv(rows, tmp_path / "exports" / "jan.csv")
    assert csv_file.exists()
    assert "Travel" in csv_file.read_text(encoding="utf-8")

# CapexPro Expense Capture Tool

A lightweight expense monitoring tool for company owners and finance teams.

## What it does

- Captures company expenses such as travel, hotel, food, etc.
- Supports receipt/invoice upload for every expense.
- Allows manual expense entry with optional supporting document upload.
- Tracks monthly company expenses with category-wise and overall totals.
- Lets users export monthly expenses to CSV for accounting workflows.

## Tech stack

- **Streamlit** for the web UI
- **SQLite** for local persistence

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app starts at the URL shown by Streamlit (typically `http://localhost:8501`).

## Project structure

- `app.py`: Streamlit UI and workflow
- `src/expense_tracker.py`: expense data model and SQLite operations
- `tests/test_expense_tracker.py`: unit tests for core logic
- `receipts/`: uploaded invoices/receipts (created automatically)

## Notes

- Uploaded files are copied to `receipts/` and linked to each expense record.
- Database file defaults to `data/expenses.db` and is created automatically.

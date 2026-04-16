from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from src.expense_tracker import (
    Expense,
    add_expense,
    export_expenses_csv,
    get_monthly_category_totals,
    get_monthly_expenses,
    get_monthly_total,
    save_receipt,
)


st.set_page_config(page_title="CapexPro", layout="wide")
st.title("CapexPro - Company Expense Capture")
st.caption("Track monthly company costs from receipts/invoices and manual entries.")

st.sidebar.header("Month Filter")
selected_month = st.sidebar.date_input("Select any date in month", value=date.today())
selected_year = selected_month.year
selected_month_num = selected_month.month

with st.form("expense_form", clear_on_submit=True):
    st.subheader("Add Expense")
    col1, col2, col3 = st.columns(3)

    with col1:
        expense_date = st.date_input("Expense date", value=date.today())
        category = st.selectbox(
            "Category",
            [
                "Travel",
                "Hotel",
                "Food",
                "Transport",
                "Office Supplies",
                "Software",
                "Utilities",
                "Other",
            ],
        )

    with col2:
        amount = st.number_input("Amount", min_value=0.0, step=0.01, format="%.2f")
        vendor = st.text_input("Vendor / Merchant")

    with col3:
        payment_method = st.selectbox(
            "Payment method",
            ["", "Company Card", "Bank Transfer", "Cash", "UPI", "Other"],
        )
        receipt = st.file_uploader("Upload receipt/invoice", type=["pdf", "png", "jpg", "jpeg"])

    description = st.text_area("Description / Notes")
    submitted = st.form_submit_button("Save Expense")

    if submitted:
        if amount <= 0:
            st.error("Amount must be greater than zero.")
        else:
            receipt_path = ""
            if receipt is not None:
                receipt_path = save_receipt(receipt.name, receipt.getvalue())

            add_expense(
                Expense(
                    expense_date=expense_date,
                    category=category,
                    amount=amount,
                    vendor=vendor,
                    description=description,
                    payment_method=payment_method,
                    receipt_path=receipt_path,
                )
            )
            st.success("Expense saved successfully.")

st.divider()

monthly_total = get_monthly_total(selected_year, selected_month_num)
category_totals = get_monthly_category_totals(selected_year, selected_month_num)
rows = get_monthly_expenses(selected_year, selected_month_num)

metric_col1, metric_col2 = st.columns(2)
metric_col1.metric("Monthly Total", f"{monthly_total:,.2f}")
metric_col2.metric("Entries", len(rows))

st.subheader("Category Totals")
if category_totals:
    category_df = pd.DataFrame(category_totals, columns=["Category", "Total"])
    st.bar_chart(category_df.set_index("Category"))
    st.dataframe(category_df, use_container_width=True)
else:
    st.info("No expenses recorded for this month yet.")

st.subheader("Monthly Expense Records")
if rows:
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    csv_path = export_expenses_csv(
        rows,
        Path("exports") / f"expenses_{selected_year}_{selected_month_num:02d}.csv",
    )

    with csv_path.open("rb") as f:
        st.download_button(
            label="Download monthly CSV",
            data=f.read(),
            file_name=csv_path.name,
            mime="text/csv",
        )

    with st.expander("Receipt links"):
        for row in rows:
            if row.get("receipt_path"):
                st.write(f"- #{row['id']}: {row['receipt_path']}")
else:
    st.info("No expense entries available for selected month.")

import streamlit as st
import pandas as pd
import re
from datetime import datetime

st.title("📊 Transaction Analyzer")

with st.expander("ℹ️ What this tool does"):
    st.markdown("""
    This app analyzes your transaction history over a selected date range, showing you:
    - Credit and debit totals
    - Net difference
    - A breakdown by vendor
    - An optional CSV export
    """)

with st.expander("ℹ️ How to use"):
    st.markdown("""
    Upload a CSV file with a maximum file size of 5MB. The file must have 4 columns titled:
    1. Transaction date
    2. Company
        ->This is the raw transaction label from your bank
    3. Credit
    4. Debit
    """)

st.set_page_config(page_title="Transaction Analyzer", page_icon="📊")

uploaded_file = st.file_uploader("Upload your transactions CSV file", type="csv")

if uploaded_file:
  df = pd.read_csv(uploaded_file)

  required_cols = {"Transaction date", "Company", "Credit", "Debit"}
  if not required_cols.issubset(df.columns):
      st.error("❌ Uploaded file is missing required columns: 'Transaction date', 'Company', 'Credit', 'Debit'. Make sure your columns are titled with these exact phrases.")
      st.stop()

  if uploaded_file.size > 5_000_000:
      st.error("File size cannot exceed 5MB.")
      st.stop()

  df["Transaction date"] = pd.to_datetime(df["Transaction date"])
    
  start_date = st.date_input("What date do you want to start the scanning? (enter your date in the form: yyyy-mm-dd): ")
  end_date = st.date_input("What date do you want to end the scanning? (enter your date in the form: yyyy-mm-dd): ")
  end_date = datetime.combine(end_date, datetime.max.time())
  start_date = datetime.combine(start_date, datetime.min.time())

  if start_date > end_date:
    st.error("❌ End date must be after start date.")
  
  else:
        
    st.success(f"📆 Scanning transactions from {start_date} to {end_date}")

    df["Credit"] = df["Credit"].fillna(0)
    df["Debit"] = df["Debit"].fillna(0)

    df["Net"] = df["Credit"] - df["Debit"]

    def extract_vendor(company):
        # Remove E-TRANSFER codes
        company = re.sub(r'E-TRANSFER\d+', '', company)
        # Remove card numbers like 4506*********547
        company = re.sub(r'\d{4}\*+\d*', '', company)
        # Remove long numeric prefixes
        company = re.sub(r'^\d{6,}\s*', '', company)
        # Remove 'MEMO EMPTX-' transaction IDs
        company = re.sub(r'MEMO EMPTX-\d+\s*', '', company)
        # Grab last 3 meaningful words
        return " ".join(company.split()[-3:])

    df["Vendor"] = df["Company"].apply(extract_vendor)
    
    @st.cache_data
    def summarize_credit(df, start_date, end_date):
        mask = (df["Transaction date"] >= start_date) & (df["Transaction date"] <= end_date)
        subset = df[mask].copy()
        return subset["Credit"].sum()

    @st.cache_data
    def summarize_debit(df, start_date, end_date):
        mask = (df["Transaction date"] >= start_date) & (df["Transaction date"] <= end_date)
        subset = df[mask].copy()
        return subset["Debit"].sum()

    @st.cache_data
    def summarize_net(df, start_date, end_date):
        mask = (df["Transaction date"] >= start_date) & (df["Transaction date"] <= end_date)
        subset = df[mask].copy()
        return subset["Net"].sum()

    @st.cache_data
    def summarize_transactions(df, start_date, end_date):
        mask = (df["Transaction date"] >= start_date) & (df["Transaction date"] <= end_date)
        subset = df[mask].copy()
        summary = (
        subset.groupby("Vendor")[["Credit", "Debit", "Net"]]
        .sum()
        .reset_index()
        .sort_values(by="Net", ascending=False)
        .reset_index(drop=True)
    )
        return summary
    
    summary = summarize_transactions(df, start_date, end_date)

    summary.insert(0, "#", range(1, len(summary) + 1))
    summary = summary.set_index("#")

    if not summary.empty:
        st.write("### 💼 Vendor Breakdown")
        st.dataframe(summary)

        col1, col2, col3 = st.columns(3)
        df.columns = df.columns.str.strip()
        col1.metric("Total Credit", f"${summarize_credit(df, start_date, end_date):,.2f}")
        col2.metric("Total Debit", f"${summarize_debit(df, start_date, end_date):,.2f}")
        col3.metric("Net", f"${summarize_net(df, start_date, end_date):,.2f}")

        csv = summary.reset_index().to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Vendor Summary as CSV", csv, "vendor_summary.csv", "text/csv")
    else:
        st.warning("⚠️ No data in the selected date range.")

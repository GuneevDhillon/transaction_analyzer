import streamlit as st
import pandas as pd
import re

st.title("📊 Transaction Analyzer")

# Upload CSV
uploaded_file = st.file_uploader("Upload your transactions CSV file", type="csv")

if uploaded_file:
  df = pd.read_csv(uploaded_file)

  df["Transaction date"] = pd.to_datetime(df["Transaction date"])
    
  start_date = st.date_input("What date do you want to start the scanning? (enter your date in the form: yyyy-mm-dd): ")
  end_date = st.date_input("What date do you want to end the scanning? (enter your date in the form: yyyy-mm-dd): ")
  st.metric(f"Processing transactions from {start_date} to {end_date}...")

  df["Credit"] = df["Credit"].fillna(0)
  df["Debit"] = df["Debit"].fillna(0)

  df["Net"] = df["Credit"] - df["Debit"]

  df["Vendor"] = df["Company"].apply(lambda name: " ".join(name.split()[-5:]))

  def extract_vendor(company):
      # Remove E-TRANSFER codes
      company = re.sub(r'E-TRANSFER\d+', '', company)
      # Remove card numbers like 4506*********547
      company = re.sub(r'\d{4}\*+\d*', '', company)
      # Remove long numeric prefixes
      company = re.sub(r'^\d{6,}\s*', '', company)
      # Remove 'MEMO EMPTX-' transaction IDs
      company = re.sub(r'MEMO EMPTX-\d+\s*', '', company)
      # Grab last 4 meaningful words
      return " ".join(company.split()[-3:])

  df["Vendor"] = df["Company"].apply(extract_vendor)

  net_by_vendor = df.groupby("Vendor")["Net"].sum().reset_index()
  net_by_vendor = net_by_vendor.sort_values(by="Net", ascending = False)

  def summarize_credit(df, start_date, end_date):
      mask = (df["Transaction date"] >= start_date) & (df["Transaction date"] <= end_date)
      subset = df[mask]
      return subset["Credit"].sum()

  def summarize_debit(df, start_date, end_date):
      mask = (df["Transaction date"] >= start_date) & (df["Transaction date"] <= end_date)
      subset = df[mask]
      return subset["Debit"].sum()

  def summarize_net(df, start_date, end_date):
      mask = (df["Transaction date"] >= start_date) & (df["Transaction date"] <= end_date)
      subset = df[mask]
      return subset["Net"].sum()

  def summarize_transactions(df, start_date, end_date):
      mask = (df["Transaction date"] >= start_date) & (df["Transaction date"] <= end_date)
      subset = df[mask]
      return subset.groupby("Vendor")[["Credit", "Debit", "Net"]].sum().reset_index()

  st.metric(summarize_transactions(df,start_date,end_date))
  st.metric(f"Total Credit: {summarize_credit(df,start_date,end_date):.2f}")
  st.metric(f"Total Debit: {summarize_debit(df,start_date,end_date):.2f}")
  st.metric(f"Net: {summarize_net(df, start_date, end_date):.2f}")
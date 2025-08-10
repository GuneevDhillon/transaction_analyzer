# Transaction Analyzer

## About the app
A Streamlit web app that helps you analyze transaction history from a CSV file. 
It summarizes credits, debits, net totals, and vendor breakdowns for any custom date range.

## Demo
👉 [Try it Live](https://your-username-your-repo-name.streamlit.app)

## Features
- Upload a CSV of transactions
- Filter by date range
- Get total credit, debit, and net income
- See a vendor-wise breakdown
- Export results as CSV

## How to use
1. Prepare a CSV file with the following **required columns**:
   - `Transaction date` (in YYYY-MM-DD format)
   - `Company`
   - `Credit`
   - `Debit`
2. Go to the live app link
3. Upload your CSV
4. Select your desired date range
5. View results and optionally export them

## Installation (for local development)
git clone https://github.com/yourusername/transaction-analyzer.git
cd transaction-analyzer
pip install -r requirements.txt
streamlit run transaction_analyzer.py

## Example CSV file format
Transaction date,Company,Credit,Debit
2023-01-10,RBC ROYAL BANK,1000.00,0.00
2023-01-12,DOORDASH,0.00,42.50

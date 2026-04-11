SalesReportGenerator

SalesReportGenerator is a Python sales reporting project that now works more like a lightweight operations tool. It validates incoming product data, generates reports, highlights inventory risk, and keeps a local history of processed runs so you can review past results later.

Features

- Reads product IDs from a `.txt` file
- Matches valid IDs with a predefined product catalog
- Generates CSV, JSON, and Excel reports
- Shows a redesigned Streamlit dashboard with a cleaner analytics layout
- Audits uploaded data for invalid IDs, duplicate entries, and empty lines
- Flags inventory risk based on stock remaining after processing
- Stores every successful run in a local `report_history` folder
- Lets you inspect previous runs from the dashboard
- Logs file and processing activity with Python logging

Sample Input

Your input file should contain one product ID per line:

P001
P005
P003

How to Run the CLI

1. Install dependencies:

   `pip install -r requirements.txt`

2. Run the report generator:

   `python main.py`

3. Optional custom export names:

   `python main.py product_sales.txt --csv my_sales.csv --json my_sales.json --excel my_sales.xlsx`

How to Run the Dashboard

`streamlit run app.py`

History Storage

- Each successful run is saved locally in `report_history`
- A summary index is stored in `report_history/history_index.json`
- Full run details are stored as separate JSON files for later inspection

What Problems This Solves

- Data quality report:
  catches invalid product IDs, duplicate entries, and blank rows before they quietly damage the report
- Inventory alerts:
  highlights products that may need reorder attention instead of only showing raw sales output
- Run history:
  helps compare uploads over time and keeps a record of what was processed

Generated Files

- `product_sales.csv`
- `product_sales.json`
- `product_sales.xlsx`
- `sales_processor.log`
- `report_history/history_index.json`
- `report_history/<run_id>.json`

Made for learning, with stronger focus on solving real reporting and operations problems.

SalesReportGenerator

SalesReportGenerator is a Python-based script that reads product sales data from a text file, processes the transactions, and exports the results into CSV, JSON, and Excel formats. It also logs important activities to help track the processing flow.

Features:-

Reads product IDs from a .txt file

Matches them with predefined product data

Generates sales records with current date and metadata

Saves the output in:

CSV

JSON

Excel

Logs operations using Python’s logging module

Command-line interface (CLI) for flexible usage

Sample Input

Your input file (e.g., product_sales.txt) should contain one product ID per line:

P001  
P005  
P003  

How to Run

Make sure you have Python 3 installed.Then install the required library:

pip install pandas openpyxl

Run the script using:

python sales_report_generator.py

You can also provide custom file names using arguments:

python sales_report_generator.py product_sales.txt --csv my_sales.csv --json my_sales.json --excel my_sales.xlsx

Arguments

Argument

Description

Default

input_file

Path to text file containing product IDs

product_sales.txt

--csv

Output CSV file name

product_sales.csv

--json

Output JSON file name

product_sales.json

--excel

Output Excel file name

product_sales.xlsx

📝 Example Output

CSV file:

current_date, sale_id, product_id, product_name, ...
2025-04-05, 1, P001, Wireless Headphones, ...

🔒 Logging

A log file sales_processor.log is automatically created to track:

File not found errors

Saved file paths

Processing status


Made by Vivek_afk81 for practice and fun!

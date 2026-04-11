import argparse
import csv
import datetime
import json
import logging

import pandas as pd

from history_store import save_report_run


logging.basicConfig(
    filename="sales_processor.log",
    level=logging.INFO,
    format="%(asctime)s-%(levelname)s-%(message)s",
)

PRODUCT_DATA = {
    "P001": ["Wireless Headphones", 100, "Audio", "Sony", 5000, 4.5],
    "P002": ["Laptop Backpack", 60, "Accessories", "Samsonite", 3000, 4.2],
    "P003": ["Bluetooth Speaker", 50, "Audio", "JBL", 4000, 4.7],
    "P004": ["USB Flash Drive", 20, "Storage", "SanDisk", 10000, 4.4],
    "P005": ["Mobile Phone Case", 15, "Accessories", "Spigen", 7500, 4.1],
    "P006": ["Wireless Mouse", 30, "Peripherals", "Logitech", 6000, 4.6],
    "P007": ["Laptop Stand", 40, "Accessories", "AmazonBasics", 3500, 4.3],
    "P008": ["HDMI Cable", 15, "Cables", "Belkin", 12000, 4.5],
    "P009": ["Smartphone", 600, "Electronics", "Samsung", 2000, 4.8],
    "P010": ["External Hard Drive", 100, "Storage", "Western Digital", 50000, 4.5],
}

REPORT_COLUMNS = [
    "Date",
    "Sale ID",
    "Product ID",
    "Name",
    "Price",
    "Category",
    "Brand",
    "Stock",
    "Rating",
]


def read_product_ids(input_file="product_sales.txt"):
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            return file.readlines()
    except FileNotFoundError:
        logging.error("File not found: %s", input_file)
        return []


def audit_product_ids(product_ids):
    cleaned_ids = []
    invalid_ids = []
    empty_lines = 0

    for raw_id in product_ids:
        product_id = raw_id.strip()
        if not product_id:
            empty_lines += 1
            continue

        cleaned_ids.append(product_id)
        if product_id not in PRODUCT_DATA:
            invalid_ids.append(product_id)

    duplicate_entries = pd.Series(cleaned_ids).duplicated().sum() if cleaned_ids else 0
    valid_ids = [product_id for product_id in cleaned_ids if product_id in PRODUCT_DATA]

    return {
        "total_rows": len(product_ids),
        "valid_count": len(valid_ids),
        "invalid_count": len(invalid_ids),
        "empty_lines": empty_lines,
        "duplicate_entries": int(duplicate_entries),
        "invalid_ids": invalid_ids,
        "valid_ids": valid_ids,
    }


def process_transactions(product_ids):
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    rows = []

    for sale_id, product_id in enumerate(product_ids, start=1):
        product = PRODUCT_DATA[product_id]
        rows.append(
            [
                current_date,
                sale_id,
                product_id,
                product[0],
                product[1],
                product[2],
                product[3],
                product[4],
                product[5],
            ]
        )

    return pd.DataFrame(rows, columns=REPORT_COLUMNS)


def build_inventory_alerts(df):
    if df.empty:
        return pd.DataFrame(
            columns=["Product ID", "Name", "Brand", "Sold", "Current Stock", "Remaining Stock", "Risk Level"]
        )

    inventory_view = df.groupby(["Product ID", "Name", "Brand", "Stock"], as_index=False).agg(
        Sold=("Sale ID", "count")
    )
    inventory_view["Remaining Stock"] = inventory_view["Stock"] - inventory_view["Sold"]
    inventory_view["Risk Level"] = "Healthy"

    watch_mask = (inventory_view["Stock"] <= 5000) | (inventory_view["Remaining Stock"] <= 1000)
    low_mask = (inventory_view["Stock"] <= 3000) | (inventory_view["Remaining Stock"] <= 500)
    critical_mask = inventory_view["Remaining Stock"] <= 0

    inventory_view.loc[watch_mask, "Risk Level"] = "Watch"
    inventory_view.loc[low_mask, "Risk Level"] = "Low Stock"
    inventory_view.loc[critical_mask, "Risk Level"] = "Critical"

    return inventory_view.rename(columns={"Stock": "Current Stock"}).sort_values(
        by=["Remaining Stock", "Sold"], ascending=[True, False]
    )


def print_data_quality_report(audit):
    print("\nData Quality Report")
    print(f"- Rows uploaded: {audit['total_rows']}")
    print(f"- Valid product IDs: {audit['valid_count']}")
    print(f"- Invalid product IDs: {audit['invalid_count']}")
    print(f"- Empty lines: {audit['empty_lines']}")
    print(f"- Duplicate entries: {audit['duplicate_entries']}")

    if audit["invalid_ids"]:
        unique_invalid_ids = ", ".join(sorted(set(audit["invalid_ids"])))
        print(f"- Skipped invalid IDs: {unique_invalid_ids}")
        logging.warning("Skipped invalid product IDs: %s", unique_invalid_ids)


def print_inventory_alerts(inventory_alerts):
    at_risk_items = inventory_alerts[inventory_alerts["Risk Level"] != "Healthy"]
    print("\nInventory Alerts")

    if at_risk_items.empty:
        print("- No products from this run are currently flagged as inventory risks.")
        return

    for _, row in at_risk_items.iterrows():
        print(
            f"- {row['Product ID']} | {row['Name']} | "
            f"Remaining stock: {row['Remaining Stock']} | Risk: {row['Risk Level']}"
        )
    logging.info("Inventory alerts generated for current run")


def save_csv(df, output_file="product_sales.csv"):
    df.to_csv(output_file, index=False, quoting=csv.QUOTE_MINIMAL)
    logging.info("CSV file saved: %s", output_file)


def save_json(df, output_file="product_sales.json"):
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(df.to_dict(orient="records"), json_file, indent=4)
    logging.info("JSON file saved: %s", output_file)


def save_excel(df, output_file="product_sales.xlsx"):
    df.to_excel(output_file, index=False, engine="openpyxl")
    logging.info("Excel file saved: %s", output_file)


def main():
    parser = argparse.ArgumentParser(description="Process product sales transactions.")
    parser.add_argument(
        "input_file",
        type=str,
        nargs="?",
        default="product_sales.txt",
        help="Text file containing one product ID per line. Default: product_sales.txt",
    )
    parser.add_argument("--csv", type=str, default="product_sales.csv", help="CSV output file name.")
    parser.add_argument("--json", type=str, default="product_sales.json", help="JSON output file name.")
    parser.add_argument("--excel", type=str, default="product_sales.xlsx", help="Excel output file name.")

    args = parser.parse_args()
    raw_product_ids = read_product_ids(args.input_file)
    if not raw_product_ids:
        print("No product data found. Check whether the input file exists and has content.")
        return

    audit = audit_product_ids(raw_product_ids)
    print_data_quality_report(audit)

    if not audit["valid_ids"]:
        print("\nNo valid product IDs found after validation. Check the input file and try again.")
        logging.warning("Processing stopped because no valid product IDs were found after validation")
        return

    report_df = process_transactions(audit["valid_ids"])
    inventory_alerts = build_inventory_alerts(report_df)

    save_csv(report_df, args.csv)
    save_json(report_df, args.json)
    save_excel(report_df, args.excel)

    history_summary = save_report_run(args.input_file, "cli", report_df, audit, inventory_alerts)
    logging.info("History entry created: %s", history_summary["run_id"])

    print_inventory_alerts(inventory_alerts)
    print(f"\nHistory saved for run: {history_summary['run_id']}")
    print("Processing complete. Check the output files and report_history folder.")


if __name__ == "__main__":
    main()

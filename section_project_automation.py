import csv
import json
import datetime
import pandas as pd
import logging
import openpyxl
import argparse
from pathlib import Path

logging.basicConfig(filename="sales_processor.log", level=logging.INFO,format="%(asctime)s-%(levelname)s-%(message)s")       #you can't directly replace the logging format string with an f-string

#Product_data


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
 # reads the product ids from the text file
def read_product_ids(input_file="product_sales.txt"):
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]
    
    except FileNotFoundError:
        logging.error(f"File not found are you sure you have the correct file_name : {input_file}")
        return []
    
# this function will process transactions and will return a structured data
def process_transactions(product_ids):
    csv_data=[]
    current_date=datetime.date.today().strftime("%Y-%m-%d")

    for sale_id, product_id in enumerate(product_ids, start=1):
        product_id=product_id.strip()

        if product_id in PRODUCT_DATA:
            product_name=PRODUCT_DATA[product_id][0]
            product_price=PRODUCT_DATA[product_id][1]
            product_category=PRODUCT_DATA[product_id][2]
            product_brand=PRODUCT_DATA[product_id][3]
            stock_availablity=PRODUCT_DATA[product_id][4]
            ratings=PRODUCT_DATA[product_id][5]
            csv_data.append([current_date, sale_id, product_id, product_name, product_price,product_category,product_brand,stock_availablity,ratings])
        else:
            print(f"warning: {product_id} is not a valid product ID")

    return csv_data

#saving the data to a csv data

def save_csv(data, output_file="product_sales.csv"):
    with open(output_file, "w", newline='', encoding="utf-8") as csv_file:
        csv_writer=csv.writer(csv_file)
        csv_writer.writerow(["current_date", "sale_id", "product_id", "product_name", "product_price","product_category","product_brand","stock availablity","ratings"])
        csv_writer.writerows(data)
    logging.info(f"CSV file saved: {output_file}")

#saving the data to json

def save_json(data, output_file="product_sales.json"):
    json_data = [
        {
            "current_date": row[0],  # Converts the date to string format
            "sale_id": row[1],
            "product_id": row[2],
            "product_name": row[3],
            "product_price": row[4],
            "product_category":row[5],
            "product_brand":row[6],
            "stock_availabilty":row[7],
            "ratings":row[8]
        }
        for row in data
    ] 
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(json_data,json_file,indent=4) # this line of code writes a  JSON representation of json_data to a file.
    logging.info(f"json file saved : {output_file}")

#saving the data to an excel file

def save_excel(data, output_file="product_sales.xlsx"):
    df=pd.DataFrame(data,columns=["current_date", "sale_id", "product_id", "product_name", "product_price","product_category","product_brand","stock availablity","ratings"])
    df.to_excel(output_file, index=False,engine="openpyxl")
    logging.info(f"excel file saved: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Process product sales transactions.")
    parser.add_argument("input_file", type=str, nargs="?", default="product_sales.txt",help="This is the text file where we will read product IDs from. If you do not provide one, we will use. Default: product_sales.txt")
    parser.add_argument("--csv", type=str, default="product_sales.csv",help="Tell me where to store the CSV file! If you skip this, I'll save it as 'product_sales.csv'. Default: product_sales.csv")
    parser.add_argument("--json", type=str, default="product_sales.json",help="Again with the same question if you do not provide me the name I'll save it as  product_sales.json. Default: product_sales.json")
    parser.add_argument("--excel", type=str, default="product_sales.xlsx",help="for the last time i am asking at this point just tell me the name you want to use. Default: product_sales.xlsx")
    
    args = parser.parse_args()
    product_ids = read_product_ids(args.input_file)
    if not product_ids:
        print("No valid product IDs found.Check again is the file present in your system")
        return
    
    processed_data = process_transactions(product_ids)
    if args.csv:
        save_csv(processed_data, args.csv)
    if args.json:
        save_json(processed_data, args.json)
    if args.excel:
        save_excel(processed_data, args.excel)
    
    print("Processing complete. Checkout the output files.")

if __name__ == "__main__":
    main()



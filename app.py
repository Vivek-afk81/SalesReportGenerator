import streamlit as st
import pandas as pd
import datetime


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


def process_transactions(product_ids):
    data = []
    current_date = datetime.date.today().strftime("%Y-%m-%d")

    for sale_id, product_id in enumerate(product_ids, start=1):
        product_id = product_id.strip()

        if product_id in PRODUCT_DATA:
            product = PRODUCT_DATA[product_id]

            data.append([
                current_date,
                sale_id,
                product_id,
                product[0],  # name
                product[1],  # price
                product[2],  # category    # will improve this in future 
                product[3],  # brand
                product[4],  # stock
                product[5],  # rating
            ])

    columns = [
        "Date", "Sale ID", "Product ID", "Name",
        "Price", "Category", "Brand", "Stock", "Rating"
    ]

    return pd.DataFrame(data, columns=columns)


st.title(" Sales Report Dashboard ")

uploaded_file = st.file_uploader(
    "Upload product_sales.txt file",
    type=["txt"]
)

if uploaded_file is not None:
    product_ids = uploaded_file.read().decode("utf-8").splitlines()

    df = process_transactions(product_ids)

    st.success("Processing Complete!")

    st.dataframe(df)

else:
    st.info("Please upload a .txt file containing product IDs.")

import streamlit as st
import pandas as pd
import datetime
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
    }
    .stDataFrame {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

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
                current_date, sale_id, product_id, product[0], product[1],
                product[2], product[3], product[4], product[5]
            ])

    columns = ["Date", "Sale ID", "Product ID", "Name", "Price", 
               "Category", "Brand", "Stock", "Rating"]
    return pd.DataFrame(data, columns=columns)


# Header
st.markdown('<p class="main-header"> Sales Analytics Dashboard</p>', unsafe_allow_html=True)
st.markdown("### Transform your sales data into actionable insights")
st.divider()

# Sidebar
with st.sidebar:
    st.header(" Configuration")
    st.markdown("---")
    
    uploaded_file = st.file_uploader(
        " Upload Sales Data",
        type=["txt"],
        help="Upload a .txt file containing product IDs (one per line)"
    )
    
    if uploaded_file:
        st.success(" File uploaded successfully!")
        
        st.markdown("---")
        st.markdown("###  Export Options")
        st.caption("Process your data first to enable downloads")
    
    st.markdown("---")
    st.info(" **Tip:** Upload a .txt file with Product IDs to generate comprehensive sales reports.")

# Main content area
if uploaded_file is not None:
    product_ids = uploaded_file.read().decode("utf-8").splitlines()
    df = process_transactions(product_ids)

    if not df.empty:
        # Key Metrics Section
        st.markdown("##  Key Performance Indicators")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_sales = len(df)
            st.metric(
                label="Total Transactions",
                value=f"{total_sales:,}",
                delta="All time"
            )
        
        with col2:
            total_revenue = df['Price'].sum()
            st.metric(
                label="Total Revenue",
                value=f"${total_revenue:,.2f}",
                delta=f"${total_revenue/total_sales:.2f} avg"
            )
        
        with col3:
            unique_products = df['Product ID'].nunique()
            st.metric(
                label="Unique Products",
                value=unique_products,
                delta=f"{(unique_products/10)*100:.0f}% catalog"
            )
        
        with col4:
            avg_rating = df['Rating'].mean()
            st.metric(
                label="Avg Rating",
                value=f"{avg_rating:.2f}⭐",
                delta=f"{avg_rating-4:.2f}" if avg_rating > 4 else f"{avg_rating-4:.2f}"
            )

        st.divider()

        # Analytics Section
        st.markdown("##  Sales Analytics")
        
        tab1, tab2, tab3 = st.tabs([" Data Overview", "📦 Category Insights", "🏷️ Brand Analysis"])
        
        with tab1:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### Transaction Details")
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )
            
            with col2:
                st.markdown("### Quick Stats")
                
                st.markdown("** Revenue by Product**")
                top_products = df.groupby('Name')['Price'].sum().sort_values(ascending=False).head(5)
                for product, revenue in top_products.items():
                    st.markdown(f"- {product}: ${revenue:,.2f}")
                
                st.markdown("---")
                st.markdown("** Top Rated Products**")
                top_rated = df.nlargest(5, 'Rating')[['Name', 'Rating']]
                for _, row in top_rated.iterrows():
                    st.markdown(f"- {row['Name']}: {row['Rating']}⭐")
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Sales by Category")
                category_sales = df.groupby('Category').agg({
                    'Sale ID': 'count',
                    'Price': 'sum'
                }).rename(columns={'Sale ID': 'Count', 'Price': 'Revenue'})
                st.dataframe(category_sales, use_container_width=True)
            
            with col2:
                st.markdown("### Category Distribution")
                category_counts = df['Category'].value_counts()
                st.bar_chart(category_counts)
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Sales by Brand")
                brand_sales = df.groupby('Brand').agg({
                    'Sale ID': 'count',
                    'Price': 'sum',
                    'Rating': 'mean'
                }).rename(columns={'Sale ID': 'Count', 'Price': 'Revenue', 'Rating': 'Avg Rating'})
                st.dataframe(brand_sales, use_container_width=True)
            
            with col2:
                st.markdown("### Brand Performance")
                brand_revenue = df.groupby('Brand')['Price'].sum().sort_values(ascending=True)
                st.bar_chart(brand_revenue)

        st.divider()

        # Download Section
        st.markdown("##  Export Your Data")
        st.markdown("Download your processed sales data in your preferred format")
        
        col1, col2, col3 = st.columns(3)

        with col1:
            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label=" Download CSV",
                data=csv_data,
                file_name=f"sales_report_{datetime.date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            json_data = df.to_json(orient="records", indent=4)
            st.download_button(
                label=" Download JSON",
                data=json_data,
                file_name=f"sales_report_{datetime.date.today()}.json",
                mime="application/json",
                use_container_width=True
            )

        with col3:
            excel_buffer = BytesIO()
            df.to_excel(excel_buffer, index=False, engine="openpyxl")
            st.download_button(
                label=" Download Excel",
                data=excel_buffer.getvalue(),
                file_name=f"sales_report_{datetime.date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    else:
        st.warning(" No valid product IDs found in the uploaded file.")

else:
    # Welcome screen
    st.markdown("##  Welcome to Sales Analytics Dashboard")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Get Started in 3 Easy Steps:
        
        1. ** Upload** your sales data file (.txt format with product IDs)
        2. ** Analyze** comprehensive insights and metrics
        3. ** Download** reports in CSV, JSON, or Excel format
        
        ---
        
        #### ✨ Features:
        - Real-time sales analytics
        - Category and brand insights
        - Top performing products
        - Multiple export formats
        - Interactive visualizations
        """)
    
    with col2:
        st.info("""
        ** File Format**
        
        Your .txt file should contain one Product ID per line:
```
        P001
        P002
        P003
        ...
```
        """)
        
        st.success("""
        **Available Products**
        
        P001-P010 in our catalog covering Audio, Storage, Accessories, and more!
        """)

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <small>Sales Analytics Dashboard v2.0 | Built with Streamlit | © 2025</small>
    </div>
""", unsafe_allow_html=True)
import datetime
import hashlib
from io import BytesIO

import pandas as pd
import streamlit as st

from history_store import load_history, load_run_details, save_report_run


st.set_page_config(
    page_title="Sales Operations Hub",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(247, 196, 122, 0.20), transparent 28%),
            radial-gradient(circle at top right, rgba(46, 108, 179, 0.18), transparent 25%),
            linear-gradient(180deg, #f6f1e8 0%, #fbfaf6 50%, #f0eee8 100%);
    }
    .hero-card, .panel-card, .mini-card {
        background: rgba(255, 255, 255, 0.86);
        border: 1px solid rgba(24, 51, 77, 0.10);
        border-radius: 20px;
        box-shadow: 0 18px 40px rgba(39, 60, 81, 0.08);
        backdrop-filter: blur(8px);
    }
    .hero-card {
        padding: 1.8rem 1.8rem 1.4rem 1.8rem;
    }
    .panel-card {
        padding: 1.2rem 1.2rem 0.6rem 1.2rem;
        margin-bottom: 1rem;
    }
    .mini-card {
        padding: 1rem 1.1rem;
        min-height: 120px;
    }
    .eyebrow {
        text-transform: uppercase;
        font-size: 0.78rem;
        letter-spacing: 0.12rem;
        color: #a15c28;
        font-weight: 700;
    }
    .hero-title {
        font-size: 3rem;
        line-height: 1;
        color: #17324d;
        font-weight: 800;
        margin: 0.35rem 0 0.6rem 0;
    }
    .hero-copy {
        color: #46607d;
        font-size: 1.02rem;
        line-height: 1.6;
    }
    .pill {
        display: inline-block;
        padding: 0.3rem 0.75rem;
        margin: 0 0.4rem 0.45rem 0;
        border-radius: 999px;
        background: #eef3f8;
        color: #244463;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .card-label {
        color: #6f7f91;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.08rem;
        margin-bottom: 0.45rem;
    }
    .card-value {
        color: #17324d;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
    }
    .card-note {
        color: #7a8797;
        font-size: 0.92rem;
        margin-top: 0.35rem;
    }
    .section-title {
        color: #17324d;
        font-weight: 800;
        font-size: 1.25rem;
        margin-bottom: 0.75rem;
    }
    .risk-watch {
        color: #8f5a11;
        font-weight: 700;
    }
    .risk-low {
        color: #a64521;
        font-weight: 700;
    }
    .risk-critical {
        color: #98222b;
        font-weight: 800;
    }
    [data-testid="stMetricValue"] {
        color: #17324d;
    }
    </style>
    """,
    unsafe_allow_html=True,
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


def save_run_once(source_name, file_signature, df, audit, inventory_alerts):
    if st.session_state.get("last_saved_signature") == file_signature:
        return st.session_state.get("last_history_summary")

    history_summary = save_report_run(source_name, "dashboard", df, audit, inventory_alerts)
    st.session_state["last_saved_signature"] = file_signature
    st.session_state["last_history_summary"] = history_summary
    return history_summary


def metric_card(label, value, note):
    st.markdown(
        f"""
        <div class="mini-card">
            <div class="card-label">{label}</div>
            <p class="card-value">{value}</p>
            <div class="card-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero(history_entries):
    total_runs = len(history_entries)
    stored_revenue = sum(entry["revenue"] for entry in history_entries) if history_entries else 0

    left, right = st.columns([1.6, 1])
    with left:
        st.markdown(
            """
            <div class="hero-card">
                <div class="eyebrow">Sales Operations Hub</div>
                <div class="hero-title">Turn uploads into decisions, not just files.</div>
                <div class="hero-copy">
                    Validate incoming sales data, spot inventory pressure, and keep a searchable run history
                    so teams can compare today's report with what happened before.
                </div>
                <div style="margin-top: 1rem;">
                    <span class="pill">Data Quality</span>
                    <span class="pill">Inventory Risk</span>
                    <span class="pill">Run History</span>
                    <span class="pill">Multi-format Export</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Stored Activity</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Saved Runs", total_runs)
        with c2:
            st.metric("Stored Revenue", f"${stored_revenue:,.0f}")
        latest_label = history_entries[0]["timestamp"].replace("T", " ") if history_entries else "No runs yet"
        st.caption(f"Latest saved report: {latest_label}")
        st.markdown("</div>", unsafe_allow_html=True)


def render_quality_panel(audit):
    st.markdown('<div class="section-title">Data Quality Check</div>', unsafe_allow_html=True)
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        metric_card("Rows Uploaded", audit["total_rows"], "All lines from the source file")
    with q2:
        metric_card("Valid IDs", audit["valid_count"], "Rows that matched the catalog")
    with q3:
        metric_card("Invalid IDs", audit["invalid_count"], "Rows skipped from processing")
    with q4:
        metric_card("Duplicates", audit["duplicate_entries"], "Repeated product references")

    if audit["empty_lines"] > 0:
        st.warning(f"Found {audit['empty_lines']} empty line(s) in the uploaded file.")

    if audit["invalid_ids"]:
        st.error("Skipped invalid product IDs: " + ", ".join(sorted(set(audit["invalid_ids"]))))
    else:
        st.success("No invalid product IDs were found in the uploaded file.")


def render_inventory_panel(inventory_alerts):
    st.markdown('<div class="section-title">Inventory Pressure</div>', unsafe_allow_html=True)
    at_risk_items = inventory_alerts[inventory_alerts["Risk Level"] != "Healthy"].copy()
    if at_risk_items.empty:
        st.success("No products from this upload are currently flagged as inventory risks.")
        return

    def style_risk(value):
        if value == "Critical":
            return "color: #98222b; font-weight: 800;"
        if value == "Low Stock":
            return "color: #a64521; font-weight: 700;"
        if value == "Watch":
            return "color: #8f5a11; font-weight: 700;"
        return ""

    st.warning("These products need attention because their stock position is weak.")
    st.dataframe(
        at_risk_items.style.applymap(style_risk, subset=["Risk Level"]),
        use_container_width=True,
        hide_index=True,
    )
    st.caption("Risk levels are based on current stock and remaining stock after processing this upload.")


def render_history_panel(history_entries):
    st.markdown('<div class="section-title">Recent Report History</div>', unsafe_allow_html=True)
    if not history_entries:
        st.info("No saved history yet. Process a file to create the first stored run.")
        return

    history_df = pd.DataFrame(history_entries)
    display_df = history_df[["timestamp", "source_name", "channel", "transactions", "revenue", "at_risk_count"]].copy()
    display_df.columns = ["Timestamp", "Source", "Channel", "Transactions", "Revenue", "At Risk"]
    display_df["Revenue"] = display_df["Revenue"].map(lambda value: f"${value:,.2f}")
    st.dataframe(display_df.head(8), use_container_width=True, hide_index=True)


def render_selected_history(history_entries):
    if not history_entries:
        return

    options = {
        f"{entry['timestamp'].replace('T', ' ')} | {entry['source_name']} | {entry['channel']}": entry["run_id"]
        for entry in history_entries
    }
    selected_label = st.sidebar.selectbox("Open saved run", list(options.keys()))
    details = load_run_details(options[selected_label])
    if not details:
        return

    st.sidebar.markdown("---")
    st.sidebar.caption("Saved run details")
    st.sidebar.write(f"Transactions: {details['summary']['transactions']}")
    st.sidebar.write(f"Revenue: ${details['summary']['revenue']:,.2f}")
    st.sidebar.write(f"At risk items: {details['summary']['at_risk_count']}")

    with st.expander("Inspect selected history run", expanded=False):
        hist_col1, hist_col2, hist_col3 = st.columns(3)
        with hist_col1:
            st.metric("Valid Rows", details["summary"]["valid_rows"])
        with hist_col2:
            st.metric("Revenue", f"${details['summary']['revenue']:,.2f}")
        with hist_col3:
            st.metric("At Risk", details["summary"]["at_risk_count"])

        history_tabs = st.tabs(["Transactions", "Inventory Alerts", "Audit"])
        with history_tabs[0]:
            transactions_df = pd.DataFrame(details["transactions"])
            if transactions_df.empty:
                st.info("No transaction records were stored for this run.")
            else:
                st.dataframe(transactions_df, use_container_width=True, hide_index=True)
        with history_tabs[1]:
            inventory_df = pd.DataFrame(details["inventory_alerts"])
            if inventory_df.empty:
                st.info("No inventory alerts were stored for this run.")
            else:
                st.dataframe(inventory_df, use_container_width=True, hide_index=True)
        with history_tabs[2]:
            audit_df = pd.DataFrame(
                [{"Metric": key.replace("_", " ").title(), "Value": value} for key, value in details["audit"].items()]
            )
            st.dataframe(audit_df, use_container_width=True, hide_index=True)


history_entries = load_history()

with st.sidebar:
    st.markdown("### Control Center")
    uploaded_file = st.file_uploader(
        "Upload Sales Data",
        type=["txt"],
        help="Upload a .txt file containing product IDs, one per line.",
    )
    st.markdown("---")
    st.caption("Catalog coverage")
    st.write(f"{len(PRODUCT_DATA)} products across audio, accessories, storage, cables, and electronics.")
    st.caption("History storage")
    st.write("Every successful run is saved locally in the report history folder.")

render_hero(history_entries)
render_selected_history(history_entries)

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    file_signature = hashlib.md5(file_bytes).hexdigest()
    product_ids = file_bytes.decode("utf-8").splitlines()
    audit = audit_product_ids(product_ids)
    report_df = process_transactions(audit["valid_ids"])
    inventory_alerts = build_inventory_alerts(report_df)

    history_summary = None
    if not report_df.empty:
        history_summary = save_run_once(uploaded_file.name, file_signature, report_df, audit, inventory_alerts)
        history_entries = load_history()

    current_tab, history_tab = st.tabs(["Current Run", "History"])

    with current_tab:
        left, right = st.columns([1.3, 1])
        with left:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            render_quality_panel(audit)
            st.markdown("</div>", unsafe_allow_html=True)
        with right:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Run Snapshot</div>', unsafe_allow_html=True)
            snapshot_1, snapshot_2, snapshot_3 = st.columns(3)
            with snapshot_1:
                st.metric("Transactions", len(report_df))
            with snapshot_2:
                st.metric("Revenue", f"${report_df['Price'].sum():,.2f}" if not report_df.empty else "$0.00")
            with snapshot_3:
                risk_count = int((inventory_alerts["Risk Level"] != "Healthy").sum()) if not inventory_alerts.empty else 0
                st.metric("At Risk", risk_count)
            if history_summary:
                st.caption(f"Saved to history as run `{history_summary['run_id']}`")
            else:
                st.caption("No history entry created because there were no valid transactions.")
            st.markdown("</div>", unsafe_allow_html=True)

        if not report_df.empty:
            metric_cols = st.columns(4)
            total_revenue = report_df["Price"].sum()
            unique_products = report_df["Product ID"].nunique()
            avg_rating = report_df["Rating"].mean()
            top_brand = report_df.groupby("Brand")["Price"].sum().sort_values(ascending=False).index[0]

            with metric_cols[0]:
                metric_card("Revenue", f"${total_revenue:,.0f}", "Revenue from valid rows")
            with metric_cols[1]:
                metric_card("Unique Products", unique_products, "Catalog items touched in this run")
            with metric_cols[2]:
                metric_card("Avg Rating", f"{avg_rating:.2f}", "Product rating average")
            with metric_cols[3]:
                metric_card("Top Brand", top_brand, "Highest revenue brand this run")

            analytics_col, alerts_col = st.columns([1.35, 1])
            with analytics_col:
                st.markdown('<div class="panel-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Sales Analytics</div>', unsafe_allow_html=True)
                analytics_tabs = st.tabs(["Transactions", "Category Mix", "Brand Performance"])
                with analytics_tabs[0]:
                    st.dataframe(report_df, use_container_width=True, hide_index=True, height=380)
                with analytics_tabs[1]:
                    category_sales = report_df.groupby("Category").agg({"Sale ID": "count", "Price": "sum"}).rename(
                        columns={"Sale ID": "Count", "Price": "Revenue"}
                    )
                    chart_col, table_col = st.columns([1, 1])
                    with chart_col:
                        st.bar_chart(report_df["Category"].value_counts())
                    with table_col:
                        st.dataframe(category_sales, use_container_width=True)
                with analytics_tabs[2]:
                    brand_sales = report_df.groupby("Brand").agg(
                        {"Sale ID": "count", "Price": "sum", "Rating": "mean"}
                    ).rename(columns={"Sale ID": "Count", "Price": "Revenue", "Rating": "Avg Rating"})
                    chart_col, table_col = st.columns([1, 1])
                    with chart_col:
                        st.bar_chart(report_df.groupby("Brand")["Price"].sum().sort_values(ascending=True))
                    with table_col:
                        st.dataframe(brand_sales, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with alerts_col:
                st.markdown('<div class="panel-card">', unsafe_allow_html=True)
                render_inventory_panel(inventory_alerts)
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Export Current Run</div>', unsafe_allow_html=True)
            export_col1, export_col2, export_col3 = st.columns(3)
            with export_col1:
                st.download_button(
                    label="Download CSV",
                    data=report_df.to_csv(index=False).encode("utf-8"),
                    file_name=f"sales_report_{datetime.date.today()}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with export_col2:
                st.download_button(
                    label="Download JSON",
                    data=report_df.to_json(orient="records", indent=4),
                    file_name=f"sales_report_{datetime.date.today()}.json",
                    mime="application/json",
                    use_container_width=True,
                )
            with export_col3:
                excel_buffer = BytesIO()
                report_df.to_excel(excel_buffer, index=False, engine="openpyxl")
                st.download_button(
                    label="Download Excel",
                    data=excel_buffer.getvalue(),
                    file_name=f"sales_report_{datetime.date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("No valid product IDs were found after validation.")

    with history_tab:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        render_history_panel(history_entries)
        st.markdown("</div>", unsafe_allow_html=True)
else:
    intro_col, history_col = st.columns([1.2, 1])
    with intro_col:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">What Changed</div>
                <p class="hero-copy">
                    This dashboard now keeps a local memory of processed runs. That means you can upload a file,
                    export it, and later come back to compare performance, inspect past alerts, or audit old inputs.
                </p>
                <p class="hero-copy">
                    Start by uploading a text file of product IDs from the left sidebar. The app will validate it,
                    process transactions, save the result into history, and show a cleaner analytics view.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with history_col:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        render_history_panel(history_entries)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div style='text-align: center; color: #6d7a88; padding: 1rem 0 0.2rem 0;'>
        <small>Sales Operations Hub v3.0 | History-aware reporting with Streamlit</small>
    </div>
    """,
    unsafe_allow_html=True,
)

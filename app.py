import datetime
import hashlib
from io import BytesIO

import pandas as pd
import streamlit as st

from history_store import load_history, load_run_details, save_report_run


st.set_page_config(
    page_title="Sales Operations Hub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: #0f1117;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #161b27 !important;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    [data-testid="stSidebar"] * {
        color: #c8d0e0 !important;
    }
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        font-weight: 600 !important;
    }

    /* Hero */
    .hub-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.25rem;
    }
    .hub-badge {
        background: linear-gradient(135deg, #3b82f6, #6366f1);
        color: #fff;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
    }
    .hub-title {
        font-size: 1.9rem;
        font-weight: 700;
        color: #f0f4ff;
        letter-spacing: -0.02em;
        line-height: 1.1;
        margin: 0;
    }
    .hub-sub {
        color: #5a6680;
        font-size: 0.88rem;
        margin-top: 0.3rem;
    }

    /* Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1.25rem 1.4rem;
        margin-bottom: 1rem;
    }
    .glass-card-sm {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        height: 100%;
    }

    /* Section titles */
    .sec-title {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #4a5568;
        margin-bottom: 1rem;
    }

    /* Metric cards */
    .kpi-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 12px;
        padding: 1rem 1.1rem;
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 3px; height: 100%;
        background: linear-gradient(180deg, #3b82f6, #6366f1);
        border-radius: 3px 0 0 3px;
    }
    .kpi-label {
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #4a5568;
        margin-bottom: 0.4rem;
    }
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #e8edf8;
        line-height: 1;
        font-family: 'DM Mono', monospace;
    }
    .kpi-note {
        font-size: 0.78rem;
        color: #3d4a5c;
        margin-top: 0.35rem;
    }

    /* Risk badges */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-critical { background: rgba(220,38,38,0.15); color: #f87171; border: 1px solid rgba(220,38,38,0.25); }
    .badge-low      { background: rgba(234,88,12,0.15); color: #fb923c; border: 1px solid rgba(234,88,12,0.25); }
    .badge-watch    { background: rgba(202,138,4,0.15);  color: #facc15; border: 1px solid rgba(202,138,4,0.25); }
    .badge-healthy  { background: rgba(34,197,94,0.12);  color: #4ade80; border: 1px solid rgba(34,197,94,0.2); }

    /* Stat row for hero */
    .stat-row {
        display: flex;
        gap: 2rem;
        margin-top: 0.75rem;
    }
    .stat-item { display: flex; flex-direction: column; gap: 0.1rem; }
    .stat-num { font-size: 1.5rem; font-weight: 700; color: #e2e8f5; font-family: 'DM Mono', monospace; }
    .stat-lbl { font-size: 0.72rem; color: #4a5568; text-transform: uppercase; letter-spacing: 0.07em; font-weight: 600; }

    /* Divider */
    .divider { border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 0.75rem 0; }

    /* Override streamlit defaults for dark theme */
    [data-testid="stMetricValue"] { color: #e2e8f5 !important; }
    [data-testid="stMetricLabel"] { color: #4a5568 !important; }
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    div[data-testid="stTab"] button { color: #6b7280 !important; }
    div[data-testid="stTab"] button[aria-selected="true"] { color: #93c5fd !important; border-bottom-color: #3b82f6 !important; }
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

REPORT_COLUMNS = ["Date", "Sale ID", "Product ID", "Name", "Price", "Category", "Brand", "Stock", "Rating"]


def audit_product_ids(product_ids):
    cleaned_ids, invalid_ids = [], []
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
    valid_ids = [pid for pid in cleaned_ids if pid in PRODUCT_DATA]
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
        rows.append([current_date, sale_id, product_id, *product])
    return pd.DataFrame(rows, columns=REPORT_COLUMNS)


def build_inventory_alerts(df):
    if df.empty:
        return pd.DataFrame(columns=["Product ID", "Name", "Brand", "Sold", "Current Stock", "Remaining Stock", "Risk Level"])
    inv = df.groupby(["Product ID", "Name", "Brand", "Stock"], as_index=False).agg(Sold=("Sale ID", "count"))
    inv["Remaining Stock"] = inv["Stock"] - inv["Sold"]
    inv["Risk Level"] = "Healthy"
    inv.loc[(inv["Stock"] <= 5000) | (inv["Remaining Stock"] <= 1000), "Risk Level"] = "Watch"
    inv.loc[(inv["Stock"] <= 3000) | (inv["Remaining Stock"] <= 500), "Risk Level"] = "Low Stock"
    inv.loc[inv["Remaining Stock"] <= 0, "Risk Level"] = "Critical"
    return inv.rename(columns={"Stock": "Current Stock"}).sort_values(by=["Remaining Stock", "Sold"], ascending=[True, False])


def save_run_once(source_name, file_signature, df, audit, inventory_alerts):
    if st.session_state.get("last_saved_signature") == file_signature:
        return st.session_state.get("last_history_summary")
    history_summary = save_report_run(source_name, "dashboard", df, audit, inventory_alerts)
    st.session_state["last_saved_signature"] = file_signature
    st.session_state["last_history_summary"] = history_summary
    return history_summary


def kpi_card(label, value, note=""):
    note_html = f'<div class="kpi-note">{note}</div>' if note else ""
    st.markdown(
        f"""<div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {note_html}
        </div>""",
        unsafe_allow_html=True,
    )


def render_hero(history_entries):
    total_runs = len(history_entries)
    stored_revenue = sum(e["revenue"] for e in history_entries) if history_entries else 0
    latest = history_entries[0]["timestamp"].replace("T", " ")[:16] if history_entries else "—"

    st.markdown(
        f"""<div class="glass-card">
            <div class="hub-header">
                <span class="hub-badge">v3.0</span>
            </div>
            <div class="hub-title">Sales Operations Hub</div>
            <div class="stat-row">
                <div class="stat-item"><span class="stat-num">{total_runs}</span><span class="stat-lbl">Saved Runs</span></div>
                <div class="stat-item"><span class="stat-num">${stored_revenue:,.0f}</span><span class="stat-lbl">Stored Revenue</span></div>
                <div class="stat-item"><span class="stat-num">{latest}</span><span class="stat-lbl">Last Run</span></div>
                <div class="stat-item"><span class="stat-num">{len(PRODUCT_DATA)}</span><span class="stat-lbl">Products</span></div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )


def render_quality_panel(audit):
    st.markdown('<div class="sec-title">Data Quality</div>', unsafe_allow_html=True)
    q1, q2, q3, q4 = st.columns(4)
    with q1: kpi_card("Rows Uploaded", audit["total_rows"])
    with q2: kpi_card("Valid IDs", audit["valid_count"])
    with q3: kpi_card("Invalid IDs", audit["invalid_count"])
    with q4: kpi_card("Duplicates", audit["duplicate_entries"])

    if audit["empty_lines"] > 0:
        st.warning(f"{audit['empty_lines']} empty line(s) skipped.")
    if audit["invalid_ids"]:
        st.error("Invalid IDs skipped: " + ", ".join(sorted(set(audit["invalid_ids"]))))
    else:
        st.success("All product IDs validated successfully.")


def render_inventory_panel(inventory_alerts):
    st.markdown('<div class="sec-title">Inventory Pressure</div>', unsafe_allow_html=True)
    at_risk = inventory_alerts[inventory_alerts["Risk Level"] != "Healthy"].copy()
    if at_risk.empty:
        st.success("No inventory risks detected.")
        return

    def style_risk(val):
        colors = {"Critical": "color:#f87171;font-weight:700", "Low Stock": "color:#fb923c;font-weight:700", "Watch": "color:#facc15;font-weight:700"}
        return colors.get(val, "")

    st.dataframe(
        at_risk.style.applymap(style_risk, subset=["Risk Level"]),
        use_container_width=True, hide_index=True,
    )


def render_history_panel(history_entries):
    st.markdown('<div class="sec-title">Recent Runs</div>', unsafe_allow_html=True)
    if not history_entries:
        st.info("No saved runs yet.")
        return
    history_df = pd.DataFrame(history_entries)
    display_df = history_df[["timestamp", "source_name", "channel", "transactions", "revenue", "at_risk_count"]].copy()
    display_df.columns = ["Timestamp", "Source", "Channel", "Transactions", "Revenue", "At Risk"]
    display_df["Revenue"] = display_df["Revenue"].map(lambda v: f"${v:,.2f}")
    st.dataframe(display_df.head(8), use_container_width=True, hide_index=True)


def render_selected_history(history_entries):
    if not history_entries:
        return None, None

    options = {
        f"{e['timestamp'].replace('T', ' ')[:16]}  |  {e['source_name']}": e["run_id"]
        for e in history_entries
    }
    selected_label = st.sidebar.selectbox("Open saved run", list(options.keys()))
    details = load_run_details(options[selected_label])
    if not details:
        return None, None

    s = details["summary"]
    st.sidebar.markdown("---")
    st.sidebar.metric("Transactions", s["transactions"])
    st.sidebar.metric("Revenue", f"${s['revenue']:,.2f}")
    st.sidebar.metric("At Risk", s["at_risk_count"])

    return details, s


# ─── Main ──────────────────────────────────────────────────────────────────────

history_entries = load_history()

with st.sidebar:
    st.markdown("### Control Center")
    uploaded_file = st.file_uploader(
        "Upload Sales Data (.txt)",
        type=["txt"],
        help="One product ID per line.",
    )
    st.markdown("---")
    st.caption(f"{len(PRODUCT_DATA)} products in catalog")

render_hero(history_entries)
selected_details, selected_summary = render_selected_history(history_entries)

if selected_details:
    with st.expander("Inspect selected run", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Valid Rows", selected_summary["valid_rows"])
        with c2:
            st.metric("Revenue", f"${selected_summary['revenue']:,.2f}")
        with c3:
            st.metric("At Risk", selected_summary["at_risk_count"])
        t1, t2, t3 = st.tabs(["Transactions", "Inventory Alerts", "Audit"])
        with t1:
            df = pd.DataFrame(selected_details["transactions"])
            if not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No records stored for this run.")
        with t2:
            df = pd.DataFrame(selected_details["inventory_alerts"])
            if not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No alerts stored for this run.")
        with t3:
            df = pd.DataFrame([
                {"Metric": k.replace("_", " ").title(), "Value": v}
                for k, v in selected_details["audit"].items()
            ])
            st.dataframe(df, use_container_width=True, hide_index=True)

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
        # Quality + Snapshot row
        left, right = st.columns([1.3, 1])
        with left:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            render_quality_panel(audit)
            st.markdown("</div>", unsafe_allow_html=True)
        with right:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="sec-title">Run Snapshot</div>', unsafe_allow_html=True)
            s1, s2, s3 = st.columns(3)
            with s1: st.metric("Transactions", len(report_df))
            with s2: st.metric("Revenue", f"${report_df['Price'].sum():,.0f}" if not report_df.empty else "$0")
            with s3:
                risk_count = int((inventory_alerts["Risk Level"] != "Healthy").sum()) if not inventory_alerts.empty else 0
                st.metric("At Risk", risk_count)
            if history_summary:
                st.caption(f"Run ID: `{history_summary['run_id']}`")
            st.markdown("</div>", unsafe_allow_html=True)

        if not report_df.empty:
            # KPI strip
            total_revenue = report_df["Price"].sum()
            unique_products = report_df["Product ID"].nunique()
            avg_rating = report_df["Rating"].mean()
            top_brand = report_df.groupby("Brand")["Price"].sum().idxmax()

            k1, k2, k3, k4 = st.columns(4)
            with k1: kpi_card("Revenue", f"${total_revenue:,.0f}")
            with k2: kpi_card("Unique Products", unique_products)
            with k3: kpi_card("Avg Rating", f"{avg_rating:.2f}")
            with k4: kpi_card("Top Brand", top_brand)

            st.markdown("<br>", unsafe_allow_html=True)

            # Analytics + Alerts
            analytics_col, alerts_col = st.columns([1.35, 1])
            with analytics_col:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<div class="sec-title">Sales Analytics</div>', unsafe_allow_html=True)
                tab_tx, tab_cat, tab_brand = st.tabs(["Transactions", "Category Mix", "Brand Performance"])
                with tab_tx:
                    st.dataframe(report_df, use_container_width=True, hide_index=True, height=340)
                with tab_cat:
                    cat_sales = report_df.groupby("Category").agg({"Sale ID": "count", "Price": "sum"}).rename(columns={"Sale ID": "Count", "Price": "Revenue"})
                    c1, c2 = st.columns([1, 1])
                    with c1: st.bar_chart(report_df["Category"].value_counts())
                    with c2: st.dataframe(cat_sales, use_container_width=True)
                with tab_brand:
                    brand_sales = report_df.groupby("Brand").agg({"Sale ID": "count", "Price": "sum", "Rating": "mean"}).rename(columns={"Sale ID": "Count", "Price": "Revenue", "Rating": "Avg Rating"})
                    c1, c2 = st.columns([1, 1])
                    with c1: st.bar_chart(report_df.groupby("Brand")["Price"].sum().sort_values())
                    with c2: st.dataframe(brand_sales, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with alerts_col:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                render_inventory_panel(inventory_alerts)
                st.markdown("</div>", unsafe_allow_html=True)

            # Export
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="sec-title">Export</div>', unsafe_allow_html=True)
            e1, e2, e3 = st.columns(3)
            today = datetime.date.today()
            with e1:
                st.download_button("⬇ CSV", report_df.to_csv(index=False).encode(), f"sales_{today}.csv", "text/csv", use_container_width=True)
            with e2:
                st.download_button("⬇ JSON", report_df.to_json(orient="records", indent=4), f"sales_{today}.json", "application/json", use_container_width=True)
            with e3:
                buf = BytesIO()
                report_df.to_excel(buf, index=False, engine="openpyxl")
                st.download_button("⬇ Excel", buf.getvalue(), f"sales_{today}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("No valid product IDs found after validation.")

    with history_tab:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        render_history_panel(history_entries)
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    render_history_panel(history_entries)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    "<div style='text-align:center;color:#2d3748;padding:1.5rem 0 0.5rem;font-size:0.8rem;'>Sales Operations Hub v3.0</div>",
    unsafe_allow_html=True,
)
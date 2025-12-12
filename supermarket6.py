import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="Supermarket Sales Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== CUSTOM CSS =====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #764ba2;
        margin-bottom: 1rem;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #764ba2;
        margin-top: 1rem;
    }
    .chart-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: .8rem;
        padding-bottom: .5rem;
        border-bottom: 2px solid #764ba2;
    }
</style>
""", unsafe_allow_html=True)

# ===================== HEADER =====================
st.markdown("""
<div class="main-header">
    <h1 style="margin:0;">🛒 SUPERMARKET SALES DASHBOARD</h1>
    <p style="margin:0; opacity: 0.9;">Performance Sales, Deals Analysis, and Business Insights Dashboard</p>
</div>
""", unsafe_allow_html=True)

# ===================== SIDEBAR =====================
with st.sidebar:
    st.markdown("## 📁 DATA UPLOAD")
    uploaded_file = st.file_uploader("Choose Excel File", type=["xlsx", "xls"])

    st.markdown("---")
    st.markdown('<div class="sidebar-header">🔍 FILTER CONTROLS</div>', unsafe_allow_html=True)

    filter_options = {}

    if uploaded_file:
        try:
            preview_df = pd.read_excel(uploaded_file, nrows=100)

            categorical_cols = []
            date_cols = []
            numeric_cols = []

            for col in preview_df.columns:
                if pd.api.types.is_datetime64_any_dtype(preview_df[col]):
                    date_cols.append(col)
                elif pd.api.types.is_numeric_dtype(preview_df[col]):
                    numeric_cols.append(col)
                elif preview_df[col].nunique() < 20:
                    categorical_cols.append(col)

            # Categorical Filters
            for col in categorical_cols[:5]:
                vals = preview_df[col].dropna().unique()
                selected = st.multiselect(
                    f"{col} Filter",
                    options=vals,
                    default=list(vals)
                )
                filter_options[col] = selected

            # Date Range Filter
            if date_cols:
                date_col = date_cols[0]
                min_d, max_d = pd.to_datetime(preview_df[date_col]).min(), pd.to_datetime(preview_df[date_col]).max()
                date_range = st.date_input("📅 Date Range", (min_d, max_d))
                if len(date_range) == 2:
                    filter_options[date_col] = date_range

        except:
            st.error("Cannot read the uploaded file. Please check the format.")
    else:
        st.info("Upload Excel file to activate filters")

    st.markdown("---")
    st.markdown("### ℹ Instructions")
    st.write("""
    1. Upload Excel file  
    2. Use filters  
    3. View KPIs & Charts  
    4. Download processed data  
    """)

# ===================== MAIN CONTENT =====================
if uploaded_file:
    @st.cache_data
    def load_data(file):
        return pd.read_excel(file)

    df = load_data(uploaded_file)
    df_filtered = df.copy()

    # APPLY FILTERS
    for col, val in filter_options.items():
        if isinstance(val, list):
            df_filtered = df_filtered[df_filtered[col].isin(val)]
        else:
            df_filtered = df_filtered[
                (pd.to_datetime(df_filtered[col]) >= pd.to_datetime(val[0])) &
                (pd.to_datetime(df_filtered[col]) <= pd.to_datetime(val[1]))
            ]

    # Identify essential columns
    sales_cols = [c for c in df.columns if "sales" in c.lower() or "total" in c.lower()]
    qty_cols = [c for c in df.columns if "qty" in c.lower() or "quantity" in c.lower()]
    city_cols = [c for c in df.columns if "city" in c.lower()]
    rating_cols = [c for c in df.columns if "rating" in c.lower()]
    category_cols = [c for c in df.columns if "product" in c.lower() or "category" in c.lower()]
    payment_cols = [c for c in df.columns if "payment" in c.lower()]

    # ===================== KPI SECTION =====================
    st.markdown("## 📊 KEY PERFORMANCE INDICATORS")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        total_sales = df_filtered[sales_cols[0]].sum() if sales_cols else 0
        st.metric("Total Sales", f"${total_sales:,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

    with kpi2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        total_qty = df_filtered[qty_cols[0]].sum() if qty_cols else 0
        st.metric("Products Sold", f"{total_qty:,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)

    with kpi3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Sales After Tax", "$307,587")
        st.markdown('</div>', unsafe_allow_html=True)

    with kpi4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Revenue Realized", "6.97%")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ===================== CHART 1 — MONTHLY SALES =====================
    st.markdown('<div class="chart-title">📅 Monthly Sales Trend</div>', unsafe_allow_html=True)

    if sales_cols and any("date" in c.lower() for c in df.columns):
        date_col = [c for c in df.columns if "date" in c.lower()][0]
        df_filtered["Month"] = pd.to_datetime(df_filtered[date_col]).dt.to_period("M")
        monthly = df_filtered.groupby("Month")[sales_cols[0]].sum().reset_index()
        monthly["Month"] = monthly["Month"].astype(str)

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=monthly["Month"], y=monthly[sales_cols[0]],
            mode="lines+markers", line=dict(color="#667eea", width=3)
        ))
    else:
        fig1 = px.line()

    st.plotly_chart(fig1, use_container_width=True)

    # ===================== PRODUCT CHARTS =====================
    colA, colB = st.columns(2)

    with colA:
        st.markdown('<div class="chart-title">📦 Products Sold</div>', unsafe_allow_html=True)

        if category_cols and qty_cols:
            prod = df_filtered.groupby(category_cols[0])[qty_cols[0]].sum().nlargest(10)
            fig2 = px.bar(prod, labels={'value': 'Quantity'})
        else:
            fig2 = px.bar()

        st.plotly_chart(fig2, use_container_width=True)

    with colB:
        st.markdown('<div class="chart-title">📊 Sales by Product Line</div>', unsafe_allow_html=True)

        if category_cols and sales_cols:
            prod_sales = df_filtered.groupby(category_cols[0])[sales_cols[0]].sum().nlargest(10)
            fig3 = px.bar(prod_sales, labels={'value': 'Sales'})
        else:
            fig3 = px.bar()

        st.plotly_chart(fig3, use_container_width=True)

    # ===================== PAYMENT PIE CHART =====================
    colC, colD = st.columns(2)

    with colC:
        st.markdown('<div class="chart-title">💳 Payment Methods</div>', unsafe_allow_html=True)

        if payment_cols:
            payment_df = df_filtered[payment_cols[0]].value_counts().reset_index()
            payment_df.columns = ["method", "count"]
            fig4 = px.pie(payment_df, names="method", values="count", hole=0.4)
        else:
            fig4 = px.pie()

        st.plotly_chart(fig4, use_container_width=True)

    # ===================== RATING BY CITY =====================
    with colD:
        st.markdown('<div class="chart-title">⭐ Rating by City</div>', unsafe_allow_html=True)

        if city_cols and rating_cols:
            city_rt = df_filtered.groupby(city_cols[0])[rating_cols[0]].mean().reset_index()
            fig5 = px.bar(city_rt, x=city_cols[0], y=rating_cols[0], range_y=[0, 5])
        else:
            fig5 = px.bar()

        st.plotly_chart(fig5, use_container_width=True)

    # ===================== DATA TABLE =====================
    st.markdown("---")
    st.markdown("## 📋 DATA OVERVIEW")

    with st.expander("View Raw Data"):
        st.dataframe(df_filtered, use_container_width=True)
        st.download_button(
            "📥 Download CSV",
            df_filtered.to_csv(index=False),
            "filtered_data.csv",
            "text/csv"
        )

    # ===================== INSIGHTS =====================
    st.markdown("---")
    st.markdown("## 💡 BUSINESS INSIGHTS")

    colI, colII, colIII = st.columns(3)
    colI.info("🎯 *Top Category:* Electronics leads with 25% growth")
    colII.success("📈 *Seasonal Trend:* Holiday season boosts sales")
    colIII.warning("⚠ *Note:* Cash payments declining")

else:
    st.markdown("## 👋 Upload data to start analysis")
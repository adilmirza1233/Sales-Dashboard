import streamlit as st
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(
    page_title="Sales Dashboard",
    layout="wide"
)

# Title
st.title("📊 Superstore Sales Dashboard")
st.markdown("Interactive dashboard for analyzing sales performance, profit trends, and customer insights.")
st.markdown("""
<style>
.main {
    background-color: #f4f7fc;
}

h1 {
    color: #1565C0;
    text-align: center;
}

div[data-testid="metric-container"] {
    background: linear-gradient(135deg,#2196F3,#21CBF3);
    padding: 15px;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)


# Load Data
df = pd.read_csv("sales.csv", encoding="latin1")

# Date Conversion
df["Order Date"] = pd.to_datetime(df["Order Date"])

# ==========================
# SIDEBAR FILTERS
# ==========================

st.sidebar.title("🎛 Dashboard Filters")

region = st.sidebar.multiselect(
    "Region",
    df["Region"].unique()
)

category = st.sidebar.multiselect(
    "Category",
    df["Category"].unique()
)

# Smart Sub-Category Filter
if category:
    sub_categories = df[
        df["Category"].isin(category)
    ]["Sub-Category"].unique()
else:
    sub_categories = df["Sub-Category"].unique()

sub_category = st.sidebar.multiselect(
    "Sub-Category",
    sub_categories
)

# ==========================
# FILTER LOGIC
# ==========================

filtered_df = df.copy()

if region:
    filtered_df = filtered_df[
        filtered_df["Region"].isin(region)
    ]

if category:
    filtered_df = filtered_df[
        filtered_df["Category"].isin(category)
    ]

if sub_category:
    filtered_df = filtered_df[
        filtered_df["Sub-Category"].isin(sub_category)
    ]
# ==========================
# KPI CARDS
# ==========================

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_orders = filtered_df["Order ID"].nunique()

if total_sales > 0:
    profit_margin = (total_profit / total_sales) * 100
else:
    profit_margin = 0

best_category = (
    filtered_df.groupby("Category")["Sales"]
    .sum()
    .idxmax()
)

best_region = (
    filtered_df.groupby("Region")["Profit"]
    .sum()
    .idxmax()
)

# KPI Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💰 Total Sales", f"${total_sales:,.0f}")

with col2:
    st.metric("📈 Total Profit", f"${total_profit:,.0f}")

with col3:
    st.metric("📦 Total Orders", total_orders)

with col4:
    st.metric("📊 Profit Margin", f"{profit_margin:.2f}%")



# Second Row
col5,col6, col7 = st.columns(3)
with col5:
    st.metric("🌍 Best Region", best_region)

with col6:
    st.metric("🏆 Best Category", best_category)

with col7:
    st.metric("📋 Total Records", f"{len(filtered_df):,}")

tab1, tab2, tab3 = st.tabs([
    "📈 Sales",
    "👥 Customers",
    "📦 Products"
])

with tab1:
    fig = px.scatter(
        filtered_df,
        x="Discount",
        y="Profit",
        color="Category",
        title="Discount vs Profit"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("🏆 Top 10 Customers by Sales")
    top_customers = (
        filtered_df.groupby("Customer Name")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig = px.bar(
        top_customers,
        x="Customer Name",
        y="Sales",
        color="Customer Name",
        title="Top 10 Customers"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("👥 Sales by Customer Segment")
    seg_sales = (
        filtered_df.groupby("Segment")["Sales"]
        .sum()
        .reset_index()
    )
    fig = px.pie(
        seg_sales,
        names="Segment",
        values="Sales",
        title="Customer Segment Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("📦 Top 10 Products by Sales")
    top_products = (
        filtered_df.groupby("Product Name")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig = px.bar(
        top_products,
        x="Sales",
        y="Product Name",
        orientation="h",
        color="Sales",
        color_continuous_scale="Turbo",
        title="Top 10 Products"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Sub-Category wise Profit")
    sub_profit = (
        filtered_df.groupby("Sub-Category")["Profit"]
        .sum()
        .reset_index()
        .sort_values("Profit", ascending=False)
    )
    fig = px.bar(
        sub_profit,
        x="Profit",
        y="Sub-Category",
        orientation="h",
        color="Profit",
        color_continuous_scale="RdYlGn",
        title="Profit by Sub-Category"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    

# ==========================
# CHARTS
# ==========================

col1, col2 = st.columns(2)

# Sales by Category
category_sales = (
    filtered_df
    .groupby("Category")["Sales"]
    .sum()
    .reset_index()
)

fig1 = px.bar(
    category_sales,
    x="Category",
    y="Sales",
    title="Sales by Category",
    color="Sales",
    color_continuous_scale="Turbo"
)

col1.plotly_chart(
    fig1,
    use_container_width=True
)

# Profit by Category
category_profit = (
    filtered_df
    .groupby("Category")["Profit"]
    .sum()
    .reset_index()
)

fig2 = px.bar(
    category_profit,
    x="Category",
    y="Profit",
    title="Profit by Category",
    color="Profit",
    color_continuous_scale="Turbo"
)

col2.plotly_chart(
    fig2,
    use_container_width=True
)

# ==========================
# MONTHLY SALES TREND
# ==========================

filtered_df["Month"] = (
    filtered_df["Order Date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_sales = (
    filtered_df
    .groupby("Month")["Sales"]
    .sum()
    .reset_index()
)

fig3 = px.line(
    monthly_sales,
    x="Month",
    y="Sales",
    markers=True,
    title="📈 Monthly Sales Trend"
)

fig3.update_traces(line_width=4)

st.plotly_chart(
    fig3,
    use_container_width=True
)

st.subheader("🏆 Top 10 Customers")

top_customers = (
    filtered_df.groupby("Customer Name")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig4 = px.bar(
    top_customers,
    x="Customer Name",
    y="Sales",
    title="Top 10 Customers by Sales",
    color="Customer Name",
    color_continuous_scale="Turbo"
)

st.plotly_chart(fig4, use_container_width=True)

st.subheader("📦 Top 10 Products")

top_products = (
    filtered_df.groupby("Product Name")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig5 = px.bar(
    top_products,
    x="Product Name",
    y="Sales",
    title="Top 10 Products by Sales",
    color="Sales",
    color_continuous_scale="Turbo"
)

st.plotly_chart(fig5, use_container_width=True)

st.subheader("🌍 Region Wise Profit")

region_profit = (
    filtered_df.groupby("Region")["Profit"]
    .sum()
    .reset_index()
)

fig6 = px.pie(
    region_profit,
    names="Region",
    values="Profit",
    title="Profit Distribution by Region"
)

st.plotly_chart(fig6, use_container_width=True)
st.subheader("📋 Dataset Preview")

st.dataframe(filtered_df)

st.markdown("---")
st.markdown("Created by **Mirza Adil Beg** | Python • Pandas • Plotly • Streamlit")


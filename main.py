import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from functools import reduce

# PAGE CONFIG
st.set_page_config(
    page_title="ShopEasy Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 ShopEasy Sales Analytics & Inventory Dashboard")
st.markdown("Interactive Dashboard for Sales Analytics and Inventory Management")

st.divider()

# LOAD DATA
sales_df = pd.read_csv("sales_data.csv")
inventory_df = pd.read_csv("inventory_data.csv")

sales_df["Date"] = pd.to_datetime(sales_df["Date"])
sales_df["Revenue"] = sales_df["Quantity Sold"] * sales_df["Unit Price"]

# SIDEBAR FILTERS
st.sidebar.header("Sales Filters")
category_options = ["All"] + list(sales_df["Category"].unique())
selected_category = st.sidebar.selectbox(
    "Select Sales Category",
    category_options
)
date_range = st.sidebar.date_input(
    "Select Sales Date Range",
    value=(sales_df["Date"].min(), sales_df["Date"].max())
)

if len(date_range) != 2:
    st.stop()

start_date, end_date = date_range
if start_date > end_date:
    st.sidebar.error("Start Date cannot be greater than End Date")

# FILTER SALES DATA
filtered_sales = sales_df.copy()

if selected_category != "All":
    filtered_sales = filtered_sales[filtered_sales["Category"] == selected_category]

filtered_sales = filtered_sales[
    (filtered_sales["Date"] >= pd.to_datetime(start_date))
    &
    (filtered_sales["Date"] <= pd.to_datetime(end_date))
    ]

# Key Business Metrics
st.header("📈 Key Business Metrics")
total_revenue = filtered_sales["Revenue"].sum()
total_units = filtered_sales["Quantity Sold"].sum()
average_price = filtered_sales["Unit Price"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"RM {total_revenue:,.2f}")
col2.metric("Total Units Sold", f"{total_units:,}")
col3.metric("Average Selling Price", f"RM {average_price:.2f}")

# DATA TABLE
st.header("📋 Filtered Sales Dataset")
st.dataframe(filtered_sales, use_container_width=True)

# VISUALIZATION SECTION
st.header("📊 Sales Visualizations")

# Chart 1 - Revenue by Category
category_revenue = filtered_sales.groupby("Category")["Revenue"].sum()
fig1, ax1 = plt.subplots(figsize=(8, 5))
category_revenue.plot(
    kind="bar",
    ax=ax1
)
ax1.set_title("Revenue by Category")
ax1.set_xlabel("Category")
ax1.set_ylabel("Revenue (RM)")
st.pyplot(fig1)

# Chart 2 - Sales Trend Over Time
filtered_sales["Date"] = pd.to_datetime(filtered_sales["Date"], errors="coerce")
filtered_sales = filtered_sales.dropna(subset=["Date"])
# 按周分组，直接生成 "YYYY-WXX" 格式的字符串索引
trend_data = filtered_sales.groupby(filtered_sales["Date"].dt.strftime("%Y-W%U"))["Revenue"].sum()
fig2, ax2 = plt.subplots(figsize=(10, 5))
trend_data.plot(
    kind="line",
    marker="o",
    ax=ax2
)
# plt.xticks(rotation=45, ha="right")
ax2.set_title("Weekly Revenue Trend")
ax2.set_xlabel("Week")
ax2.set_ylabel("Revenue (RM)")
ax2.grid(True)
st.pyplot(fig2)

# # Chart 3 - Pie Chart
fig3, ax3 = plt.subplots(figsize=(7, 7))
category_revenue.plot(
    kind="pie",
    autopct="%1.1f%%",
    ax=ax3
)
ax3.set_ylabel("")
ax3.set_title("Revenue Share by Category")
st.pyplot(fig3)

# SIDEBAR FILTER
inventory_df["Date"] = pd.to_datetime(inventory_df["Date"])
st.sidebar.header("Inventory Filters")
inv_category_options = ["All"] + list(inventory_df["Category"].unique())
inv_selected_category = st.sidebar.selectbox(
    "Select Invertory Category",
    category_options
)
inv_date_range = st.sidebar.date_input(
    "Select Invertory Date Range",
    value=(inventory_df["Date"].min(), inventory_df["Date"].max())
)

if len(inv_date_range) != 2:
    st.stop()

inv_start_date, inv_end_date = inv_date_range
if inv_start_date > inv_end_date:
    st.sidebar.error("Start Date cannot be greater than End Date")

# FILTER SALES DATA
filtered_inventory = inventory_df.copy()
if inv_selected_category != "All":
    filtered_inventory = filtered_inventory[filtered_inventory["Category"] == inv_selected_category]

filtered_inventory = filtered_inventory[
    (filtered_inventory["Date"] >= pd.to_datetime(inv_start_date))
    &
    (filtered_inventory["Date"] <= pd.to_datetime(inv_end_date))
    ]

# INVENTORY MANAGEMENT
st.divider()
st.header("📦 Inventory Management")
threshold = st.slider(
    "Low Stock Threshold",
    min_value=1,
    max_value=100,
    value=20
)

# FUNCTIONAL PROGRAMMING
inventory_records = filtered_inventory.to_dict(orient="records")
low_stock_products = list(filter(lambda product: product["Stock Quantity"] < threshold, inventory_records))
low_stock_units = list(map(lambda product: product["Stock Quantity"], low_stock_products))
total_at_risk = reduce(lambda x, y: x + y, low_stock_units) if len(low_stock_units) > 0 else 0

# WARNING MESSAGE
if len(low_stock_products) > 0:
    st.warning(f"⚠ {len(low_stock_products)} products are below stock threshold.")
    st.write(f"Total Units at Risk: {total_at_risk}")
    st.dataframe(pd.DataFrame(low_stock_products), use_container_width=True)
else:
    st.success("✅ No low-stock products detected.")

# INVENTORY STATUS
filtered_inventory["Stock Status"] = np.where(
    filtered_inventory["Stock Quantity"] < threshold,
    "Low Stock",
    "Sufficient"
)

# Inventory Key Business Metrics
st.subheader("Inventory Key Business Metrics")
inventory_col1, inventory_col2, inventory_col3 = st.columns(3)
inventory_col1.metric("Total Products", f"{len(filtered_inventory)}")
inv = list(map(lambda product: product["Stock Quantity"], inventory_records))
total_inventory = reduce(lambda x, y: x + y, inv)
inventory_col2.metric("Total Inventory", f"{total_inventory}")
inventory_col3.metric("Median Inventory", f"{np.median(inv)}")


# STYLE FUNCTION
def highlight_stock(row):
    if row["Stock Status"] == "Sufficient":
        return ["background-color: #d4edda; color: #155724"] * len(row)
    elif row["Stock Status"] == "Low Stock":
        return ["background-color: #fff3cd; color: #856404"] * len(row)
    elif row["Stock Status"] == "Out of Stock":
        return ["background-color: #f8d7da; color: #721c24"] * len(row)
    else:
        return [""] * len(row)


# INVENTORY TABLE
st.subheader("Inventory Dataset")
styled_inventory = filtered_inventory.style.apply(highlight_stock, axis=1)
st.dataframe(styled_inventory, use_container_width=True)

# FOOTER
st.divider()
st.caption("Developed for ShopEasy Sdn Bhd | Principles of Programming Final Examination")

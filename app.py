import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Cohort Retention & CLTV Analysis", layout="wide")

@st.cache_data
def load_data():
    transactions = pd.read_csv("data/cleaned_customer_transactions.csv")
    cltv = pd.read_csv("reports/customer_cltv.csv")
    retention = pd.read_csv("reports/cohort_retention_matrix.csv")
    return transactions, cltv, retention

df, cltv, retention = load_data()

st.title("SaaS/E-Commerce Cohort Retention & CLTV Analysis")

total_customers = df["CustomerID"].nunique()
total_orders = df["InvoiceNo"].nunique()
total_revenue = df["Revenue"].sum()
aov = total_revenue / total_orders
repeat_rate = (df.groupby("CustomerID")["InvoiceNo"].nunique().gt(1).sum() / total_customers) * 100

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Customers", f"{total_customers:,}")
c2.metric("Orders", f"{total_orders:,}")
c3.metric("Revenue", f"₹{total_revenue:,.0f}")
c4.metric("AOV", f"₹{aov:,.0f}")
c5.metric("Repeat Rate", f"{repeat_rate:.1f}%")

st.subheader("Cohort Retention Matrix")
st.dataframe(retention, use_container_width=True)

st.subheader("Average Retention Curve")
month_cols = [c for c in retention.columns if c.startswith("Month_")]
avg_retention = retention[month_cols].mean()
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(range(1, len(avg_retention) + 1), avg_retention, marker="o")
ax.set_xlabel("Months Since First Purchase")
ax.set_ylabel("Retention %")
ax.grid(True)
st.pyplot(fig)

st.subheader("CLTV Segment Summary")
segment_summary = cltv.groupby("CLTVSegment", observed=False).agg(
    Customers=("CustomerID", "nunique"),
    Revenue=("HistoricalCLTV", "sum"),
    AverageCLTV=("HistoricalCLTV", "mean")
).reset_index()
st.dataframe(segment_summary, use_container_width=True)

st.subheader("Business Recommendations")
st.write("""
- Run re-engagement campaigns within 30 days after first purchase.
- Prioritize acquisition channels with higher CLTV, not only higher customer count.
- Offer loyalty benefits to high-value and very-high-value customers.
- Track cohort retention every month to identify early churn patterns.
""")
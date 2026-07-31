from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Customer Retention & CLTV Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# PATHS
# =========================================================
BASE_DIR = Path(__file__).resolve().parent


def find_file(filename: str, preferred_folders: Iterable[str] = ()) -> Path:
    """
    Find a required project file safely on local machine or Streamlit Cloud.

    Search order:
    1. Preferred folders under the app directory
    2. App directory root
    3. Recursive search inside the repository
    """
    candidates: list[Path] = []

    for folder in preferred_folders:
        candidates.append(BASE_DIR / folder / filename)

    candidates.append(BASE_DIR / filename)

    for path in candidates:
        if path.exists():
            return path

    matches = list(BASE_DIR.rglob(filename))
    if matches:
        return matches[0]

    searched = "\n".join(f"- {p}" for p in candidates)
    raise FileNotFoundError(
        f"Could not find required file: {filename}\n"
        f"Searched these locations first:\n{searched}"
    )


# =========================================================
# DATA LOADING
# =========================================================
@st.cache_data(show_spinner=False)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    transactions_path = find_file(
        "cleaned_customer_transactions.csv",
        preferred_folders=("data", "reports"),
    )

    cltv_path = find_file(
        "customer_cltv.csv",
        preferred_folders=("reports", "data"),
    )

    retention_path = find_file(
        "cohort_retention_matrix.csv",
        preferred_folders=("reports", "data"),
    )

    transactions = pd.read_csv(transactions_path)
    cltv = pd.read_csv(cltv_path)
    retention = pd.read_csv(retention_path)

    return transactions, cltv, retention


def prepare_data(
    transactions: pd.DataFrame,
    cltv: pd.DataFrame,
    retention: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    transactions = transactions.copy()
    cltv = cltv.copy()
    retention = retention.copy()

    # Dates
    if "InvoiceDate" in transactions.columns:
        transactions["InvoiceDate"] = pd.to_datetime(
            transactions["InvoiceDate"],
            errors="coerce",
            dayfirst=True,
        )

    for col in ("TransactionMonth", "CohortMonth"):
        if col in transactions.columns:
            transactions[col] = pd.to_datetime(
                transactions[col],
                errors="coerce",
            )

    for col in ("FirstPurchase", "LastPurchase"):
        if col in cltv.columns:
            cltv[col] = pd.to_datetime(
                cltv[col],
                errors="coerce",
            )

    if "CohortMonth" in retention.columns:
        retention["CohortMonth"] = pd.to_datetime(
            retention["CohortMonth"],
            errors="coerce",
        )

    # Numeric safety
    transaction_numeric = [
        "Quantity",
        "UnitPrice",
        "DiscountPercent",
        "Revenue",
        "CohortIndex",
    ]
    for col in transaction_numeric:
        if col in transactions.columns:
            transactions[col] = pd.to_numeric(
                transactions[col],
                errors="coerce",
            )

    cltv_numeric = [
        "TotalRevenue",
        "TotalOrders",
        "TotalQuantity",
        "AverageOrderValue",
        "CustomerLifespanMonths",
        "PurchaseFrequencyPerMonth",
        "HistoricalCLTV",
        "CLTVSegmentSort",
    ]
    for col in cltv_numeric:
        if col in cltv.columns:
            cltv[col] = pd.to_numeric(
                cltv[col],
                errors="coerce",
            )

    retention_month_columns = [
        c for c in retention.columns if c.startswith("Month_")
    ]
    for col in retention_month_columns:
        retention[col] = pd.to_numeric(
            retention[col],
            errors="coerce",
        )

    return transactions, cltv, retention


# =========================================================
# HELPERS
# =========================================================
def money(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "₹0"
    return f"₹{value:,.0f}"


def number(value: float | int | None, decimals: int = 0) -> str:
    if value is None or pd.isna(value):
        return "0"
    return f"{value:,.{decimals}f}"


def percent(value: float | int | None, decimals: int = 1) -> str:
    if value is None or pd.isna(value):
        return "0.0%"
    return f"{value:.{decimals}f}%"


def safe_distinct_count(df: pd.DataFrame, column: str) -> int:
    if column not in df.columns:
        return 0
    return int(df[column].nunique(dropna=True))


def ordered_segment_series(series: pd.Series) -> pd.Series:
    order = ["Low Value", "Medium Value", "High Value", "Very High Value"]
    return pd.Categorical(series, categories=order, ordered=True)


def apply_filters(
    transactions: pd.DataFrame,
    cltv: pd.DataFrame,
    year: str,
    region: str,
    channel: str,
    plan: str,
    segment: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:

    tx = transactions.copy()
    customer = cltv.copy()

    if year != "All" and "InvoiceDate" in tx.columns:
        tx = tx[tx["InvoiceDate"].dt.year == int(year)]

    # Apply customer-level filters first
    if region != "All" and "Region" in customer.columns:
        customer = customer[customer["Region"] == region]

    if channel != "All" and "AcquisitionChannel" in customer.columns:
        customer = customer[customer["AcquisitionChannel"] == channel]

    if plan != "All" and "SubscriptionPlan" in customer.columns:
        customer = customer[customer["SubscriptionPlan"] == plan]

    if segment != "All" and "CLTVSegment" in customer.columns:
        customer = customer[customer["CLTVSegment"] == segment]

    # Restrict transaction data to selected customers
    if "CustomerID" in customer.columns and "CustomerID" in tx.columns:
        valid_customers = set(customer["CustomerID"].astype(str))
        tx = tx[tx["CustomerID"].astype(str).isin(valid_customers)]

    return tx, customer


def repeat_customer_metrics(tx: pd.DataFrame) -> tuple[int, int, float]:
    if tx.empty or "CustomerID" not in tx.columns or "InvoiceNo" not in tx.columns:
        return 0, 0, 0.0

    orders_per_customer = (
        tx.groupby("CustomerID")["InvoiceNo"]
        .nunique()
    )

    repeat = int((orders_per_customer > 1).sum())
    one_time = int((orders_per_customer == 1).sum())
    total = int(len(orders_per_customer))
    rate = (repeat / total * 100) if total else 0.0

    return repeat, one_time, rate


# =========================================================
# LOAD DATA
# =========================================================
try:
    transactions, cltv, retention = load_data()
    transactions, cltv, retention = prepare_data(
        transactions,
        cltv,
        retention,
    )
except Exception as exc:
    st.error("The app could not load the project data files.")
    st.code(str(exc))

    st.markdown(
        """
### Expected repository structure

```text
your-repository/
│
├── app.py
├── data/
│   └── cleaned_customer_transactions.csv
│
└── reports/
    ├── customer_cltv.csv
    └── cohort_retention_matrix.csv
```

File names are case-sensitive on Streamlit Cloud.
"""
    )
    st.stop()


# =========================================================
# APP HEADER
# =========================================================
st.title("📊 Customer Retention & CLTV Analytics")
st.caption(
    "SaaS / E-Commerce Cohort Retention, Customer Lifetime Value "
    "and Customer Segmentation Dashboard"
)


# =========================================================
# SIDEBAR FILTERS
# =========================================================
st.sidebar.header("Dashboard Filters")

years = ["All"]
if "InvoiceDate" in transactions.columns:
    valid_years = (
        transactions["InvoiceDate"]
        .dropna()
        .dt.year
        .astype(int)
        .sort_values()
        .unique()
        .tolist()
    )
    years += [str(y) for y in valid_years]

regions = ["All"]
if "Region" in cltv.columns:
    regions += sorted(cltv["Region"].dropna().astype(str).unique().tolist())

channels = ["All"]
if "AcquisitionChannel" in cltv.columns:
    channels += sorted(
        cltv["AcquisitionChannel"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

plans = ["All"]
if "SubscriptionPlan" in cltv.columns:
    plans += sorted(
        cltv["SubscriptionPlan"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

segments = [
    "All",
    "Low Value",
    "Medium Value",
    "High Value",
    "Very High Value",
]

year_filter = st.sidebar.selectbox("Year", years)
region_filter = st.sidebar.selectbox("Region", regions)
channel_filter = st.sidebar.selectbox("Acquisition Channel", channels)
plan_filter = st.sidebar.selectbox("Subscription Plan", plans)
segment_filter = st.sidebar.selectbox("CLTV Segment", segments)

filtered_tx, filtered_cltv = apply_filters(
    transactions,
    cltv,
    year_filter,
    region_filter,
    channel_filter,
    plan_filter,
    segment_filter,
)

st.sidebar.divider()
st.sidebar.caption(
    f"Transactions: {len(filtered_tx):,} | "
    f"Customers: {safe_distinct_count(filtered_tx, 'CustomerID'):,}"
)


# =========================================================
# NAVIGATION
# =========================================================
page = st.sidebar.radio(
    "Analysis Page",
    [
        "Executive Overview",
        "Cohort Retention",
        "CLTV Analysis",
        "Customer Segmentation",
        "Customer Detail",
    ],
)


# =========================================================
# PAGE 1 — EXECUTIVE OVERVIEW
# =========================================================
if page == "Executive Overview":
    st.subheader("Executive Overview")
    st.caption("High-level customer and revenue performance")

    total_revenue = (
        filtered_tx["Revenue"].sum()
        if "Revenue" in filtered_tx.columns
        else 0
    )

    total_customers = safe_distinct_count(filtered_tx, "CustomerID")
    total_orders = safe_distinct_count(filtered_tx, "InvoiceNo")

    aov = total_revenue / total_orders if total_orders else 0

    repeat_customers, one_time_customers, repeat_rate = (
        repeat_customer_metrics(filtered_tx)
    )

    avg_cltv = (
        filtered_cltv["HistoricalCLTV"].mean()
        if "HistoricalCLTV" in filtered_cltv.columns
        and not filtered_cltv.empty
        else 0
    )

    k1, k2, k3, k4, k5, k6 = st.columns(6)

    k1.metric("Total Revenue", money(total_revenue))
    k2.metric("Total Customers", f"{total_customers:,}")
    k3.metric("Total Orders", f"{total_orders:,}")
    k4.metric("Average Order Value", money(aov))
    k5.metric("Repeat Customer Rate", percent(repeat_rate))
    k6.metric("Average Historical CLTV", money(avg_cltv))

    st.divider()

    left, right = st.columns(2)

    with left:
        st.markdown("#### Monthly Revenue Trend")

        if (
            "InvoiceDate" in filtered_tx.columns
            and "Revenue" in filtered_tx.columns
            and not filtered_tx.empty
        ):
            monthly = (
                filtered_tx.dropna(subset=["InvoiceDate"])
                .assign(
                    Month=lambda x: x["InvoiceDate"]
                    .dt.to_period("M")
                    .dt.to_timestamp()
                )
                .groupby("Month", as_index=False)["Revenue"]
                .sum()
                .set_index("Month")
            )
            st.line_chart(monthly)
        else:
            st.info("No revenue trend data is available for the selected filters.")

    with right:
        st.markdown("#### Revenue by Acquisition Channel")

        if (
            "AcquisitionChannel" in filtered_cltv.columns
            and "TotalRevenue" in filtered_cltv.columns
            and not filtered_cltv.empty
        ):
            channel_rev = (
                filtered_cltv
                .groupby("AcquisitionChannel")["TotalRevenue"]
                .sum()
                .sort_values(ascending=False)
            )
            st.bar_chart(channel_rev)
        else:
            st.info("Acquisition-channel data is unavailable.")

    left2, right2 = st.columns(2)

    with left2:
        st.markdown("#### Revenue by Customer Value Segment")

        if (
            "CLTVSegment" in filtered_cltv.columns
            and "TotalRevenue" in filtered_cltv.columns
            and not filtered_cltv.empty
        ):
            temp = filtered_cltv.copy()
            temp["CLTVSegment"] = ordered_segment_series(
                temp["CLTVSegment"]
            )

            segment_rev = (
                temp.groupby(
                    "CLTVSegment",
                    observed=False,
                )["TotalRevenue"]
                .sum()
            )

            st.bar_chart(segment_rev)
        else:
            st.info("CLTV segment data is unavailable.")

    with right2:
        st.markdown("#### Customer Distribution by Region")

        if (
            "Region" in filtered_cltv.columns
            and "CustomerID" in filtered_cltv.columns
            and not filtered_cltv.empty
        ):
            region_customers = (
                filtered_cltv.groupby("Region")["CustomerID"]
                .nunique()
                .sort_values(ascending=False)
            )
            st.bar_chart(region_customers)
        else:
            st.info("Region data is unavailable.")


# =========================================================
# PAGE 2 — COHORT RETENTION
# =========================================================
elif page == "Cohort Retention":
    st.subheader("Cohort Retention Analysis")
    st.caption(
        "Monthly customer retention and drop-off by acquisition cohort"
    )

    total_customers = safe_distinct_count(filtered_tx, "CustomerID")
    repeat_customers, one_time_customers, repeat_rate = (
        repeat_customer_metrics(filtered_tx)
    )

    a, b, c, d = st.columns(4)
    a.metric("Total Customers", f"{total_customers:,}")
    b.metric("Repeat Customers", f"{repeat_customers:,}")
    c.metric("Repeat Customer Rate", percent(repeat_rate))
    d.metric("One-Time Customers", f"{one_time_customers:,}")

    st.divider()

    month_cols = [
        c for c in retention.columns if c.startswith("Month_")
    ]

    month_cols = sorted(
        month_cols,
        key=lambda x: int(x.split("_")[1]),
    )

    if not month_cols:
        st.warning(
            "No Month_1, Month_2, ... columns were found in "
            "cohort_retention_matrix.csv."
        )
    else:
        heatmap = retention.copy()

        if "CohortMonth" in heatmap.columns:
            heatmap = heatmap.sort_values("CohortMonth")
            labels = heatmap["CohortMonth"].dt.strftime("%b %Y")
        else:
            labels = heatmap.index.astype(str)

        matrix = heatmap[month_cols].to_numpy(dtype=float)

        st.markdown("#### Monthly Customer Retention Heatmap")

        fig, ax = plt.subplots(
            figsize=(14, max(5, len(heatmap) * 0.45))
        )

        image = ax.imshow(
            matrix,
            aspect="auto",
            vmin=0,
            vmax=100,
        )

        ax.set_xticks(range(len(month_cols)))
        ax.set_xticklabels(
            [f"M{int(c.split('_')[1])}" for c in month_cols]
        )

        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels)

        ax.set_xlabel("Months Since First Purchase")
        ax.set_ylabel("Acquisition Cohort")

        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                value = matrix[i, j]
                if not np.isnan(value):
                    ax.text(
                        j,
                        i,
                        f"{value:.1f}",
                        ha="center",
                        va="center",
                        fontsize=7,
                    )

        fig.colorbar(
            image,
            ax=ax,
            label="Retention Rate (%)",
        )
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        st.markdown("#### Average Customer Retention Curve")

        retention_long = (
            retention[month_cols]
            .rename(
                columns={
                    c: int(c.split("_")[1])
                    for c in month_cols
                }
            )
        )

        avg_retention = retention_long.mean(axis=0, skipna=True)
        avg_retention.index.name = "MonthNumber"
        avg_retention.name = "RetentionRate"

        st.line_chart(avg_retention)


# =========================================================
# PAGE 3 — CLTV ANALYSIS
# =========================================================
elif page == "CLTV Analysis":
    st.subheader("Customer Lifetime Value Analysis")
    st.caption(
        "Customer value, revenue contribution and purchase behaviour"
    )

    if filtered_cltv.empty:
        st.warning("No customer data is available for the selected filters.")
        st.stop()

    avg_cltv = (
        filtered_cltv["HistoricalCLTV"].mean()
        if "HistoricalCLTV" in filtered_cltv.columns
        else 0
    )
    median_cltv = (
        filtered_cltv["HistoricalCLTV"].median()
        if "HistoricalCLTV" in filtered_cltv.columns
        else 0
    )
    max_cltv = (
        filtered_cltv["HistoricalCLTV"].max()
        if "HistoricalCLTV" in filtered_cltv.columns
        else 0
    )
    avg_lifespan = (
        filtered_cltv["CustomerLifespanMonths"].mean()
        if "CustomerLifespanMonths" in filtered_cltv.columns
        else 0
    )
    avg_freq = (
        filtered_cltv["PurchaseFrequencyPerMonth"].mean()
        if "PurchaseFrequencyPerMonth" in filtered_cltv.columns
        else 0
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Average Historical CLTV", money(avg_cltv))
    c2.metric("Median Historical CLTV", money(median_cltv))
    c3.metric("Maximum Historical CLTV", money(max_cltv))
    c4.metric(
        "Average Customer Lifespan",
        f"{number(avg_lifespan, 2)} months",
    )
    c5.metric(
        "Purchase Frequency / Month",
        number(avg_freq, 2),
    )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.markdown("#### Average CLTV by Acquisition Channel")

        if (
            "AcquisitionChannel" in filtered_cltv.columns
            and "HistoricalCLTV" in filtered_cltv.columns
        ):
            chart = (
                filtered_cltv
                .groupby("AcquisitionChannel")["HistoricalCLTV"]
                .mean()
                .sort_values(ascending=False)
            )
            st.bar_chart(chart)

    with right:
        st.markdown("#### CLTV Distribution")

        if "HistoricalCLTV" in filtered_cltv.columns:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.hist(
                filtered_cltv["HistoricalCLTV"].dropna(),
                bins=30,
            )
            ax.set_xlabel("Historical CLTV")
            ax.set_ylabel("Customers")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    st.markdown("#### Purchase Frequency vs Historical CLTV")

    if {
        "PurchaseFrequencyPerMonth",
        "HistoricalCLTV",
    }.issubset(filtered_cltv.columns):
        scatter_df = filtered_cltv[
            ["PurchaseFrequencyPerMonth", "HistoricalCLTV"]
        ].dropna()

        st.scatter_chart(
            scatter_df,
            x="PurchaseFrequencyPerMonth",
            y="HistoricalCLTV",
        )

    st.markdown("#### Top 10 Customers by Historical CLTV")

    top_columns = [
        c for c in [
            "CustomerID",
            "HistoricalCLTV",
            "TotalOrders",
            "AverageOrderValue",
            "CustomerLifespanMonths",
            "PurchaseFrequencyPerMonth",
            "CLTVSegment",
            "AcquisitionChannel",
            "Region",
        ]
        if c in filtered_cltv.columns
    ]

    top10 = (
        filtered_cltv
        .sort_values("HistoricalCLTV", ascending=False)
        .head(10)[top_columns]
        if "HistoricalCLTV" in filtered_cltv.columns
        else filtered_cltv.head(10)[top_columns]
    )

    st.dataframe(
        top10,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# PAGE 4 — CUSTOMER SEGMENTATION
# =========================================================
elif page == "Customer Segmentation":
    st.subheader("Customer Segmentation Analysis")
    st.caption(
        "Customer value groups, revenue contribution and segment behaviour"
    )

    if filtered_cltv.empty:
        st.warning("No customer data is available for the selected filters.")
        st.stop()

    segment_order = [
        "Low Value",
        "Medium Value",
        "High Value",
        "Very High Value",
    ]

    counts = (
        filtered_cltv["CLTVSegment"]
        .value_counts()
        .reindex(segment_order, fill_value=0)
        if "CLTVSegment" in filtered_cltv.columns
        else pd.Series(0, index=segment_order)
    )

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Low Value Customers", int(counts["Low Value"]))
    s2.metric("Medium Value Customers", int(counts["Medium Value"]))
    s3.metric("High Value Customers", int(counts["High Value"]))
    s4.metric("Very High Value Customers", int(counts["Very High Value"]))

    st.divider()

    left, right = st.columns(2)

    with left:
        st.markdown("#### Revenue Contribution by CLTV Segment")

        if {
            "CLTVSegment",
            "TotalRevenue",
        }.issubset(filtered_cltv.columns):
            segment_revenue = (
                filtered_cltv
                .groupby("CLTVSegment")["TotalRevenue"]
                .sum()
                .reindex(segment_order, fill_value=0)
            )
            st.bar_chart(segment_revenue)

    with right:
        st.markdown("#### Average CLTV by Segment")

        if {
            "CLTVSegment",
            "HistoricalCLTV",
        }.issubset(filtered_cltv.columns):
            avg_segment_cltv = (
                filtered_cltv
                .groupby("CLTVSegment")["HistoricalCLTV"]
                .mean()
                .reindex(segment_order)
            )
            st.bar_chart(avg_segment_cltv)

    st.markdown("#### Segment Profile")

    available_metrics = [
        c for c in [
            "HistoricalCLTV",
            "TotalOrders",
            "AverageOrderValue",
            "CustomerLifespanMonths",
            "PurchaseFrequencyPerMonth",
        ]
        if c in filtered_cltv.columns
    ]

    if "CLTVSegment" in filtered_cltv.columns and available_metrics:
        segment_profile = (
            filtered_cltv
            .groupby("CLTVSegment")[available_metrics]
            .mean()
            .reindex(segment_order)
            .round(2)
        )

        segment_profile.insert(
            0,
            "Customers",
            counts.reindex(segment_profile.index).values,
        )

        st.dataframe(
            segment_profile,
            use_container_width=True,
        )

    st.markdown("#### Customer Value Mix by Acquisition Channel")

    if {
        "AcquisitionChannel",
        "CLTVSegment",
        "CustomerID",
    }.issubset(filtered_cltv.columns):
        mix = pd.crosstab(
            filtered_cltv["AcquisitionChannel"],
            filtered_cltv["CLTVSegment"],
            normalize="index",
        ) * 100

        mix = mix.reindex(columns=segment_order, fill_value=0)
        st.bar_chart(mix)


# =========================================================
# PAGE 5 — CUSTOMER DETAIL
# =========================================================
elif page == "Customer Detail":
    st.subheader("Customer Detail Analysis")
    st.caption(
        "Customer-level revenue, orders, CLTV and purchase behaviour"
    )

    if filtered_cltv.empty:
        st.warning("No customer data is available for the selected filters.")
        st.stop()

    customer_ids = sorted(
        filtered_cltv["CustomerID"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_customer = st.selectbox(
        "Select Customer",
        customer_ids,
    )

    customer_row = filtered_cltv[
        filtered_cltv["CustomerID"].astype(str)
        == selected_customer
    ]

    customer_tx = filtered_tx[
        filtered_tx["CustomerID"].astype(str)
        == selected_customer
    ].copy()

    if customer_row.empty:
        st.warning("Customer details could not be found.")
        st.stop()

    row = customer_row.iloc[0]

    q1, q2, q3, q4, q5 = st.columns(5)

    q1.metric(
        "Historical CLTV",
        money(row.get("HistoricalCLTV", 0)),
    )
    q2.metric(
        "Total Orders",
        number(row.get("TotalOrders", 0), 0),
    )
    q3.metric(
        "Average Order Value",
        money(row.get("AverageOrderValue", 0)),
    )
    q4.metric(
        "Customer Lifespan (Months)",
        number(row.get("CustomerLifespanMonths", 0), 2),
    )
    q5.metric(
        "Purchase Frequency / Month",
        number(row.get("PurchaseFrequencyPerMonth", 0), 2),
    )

    st.divider()

    st.markdown("#### Customer Profile")

    profile_fields = [
        "CustomerID",
        "CLTVSegment",
        "AcquisitionChannel",
        "Region",
        "Country",
        "SubscriptionPlan",
        "FirstPurchase",
        "LastPurchase",
    ]

    profile_fields = [
        c for c in profile_fields
        if c in customer_row.columns
    ]

    profile = customer_row[profile_fields].copy()

    for col in ("FirstPurchase", "LastPurchase"):
        if col in profile.columns:
            profile[col] = profile[col].dt.strftime("%d %B %Y")

    st.dataframe(
        profile,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Customer Transaction History")

    history_fields = [
        "InvoiceNo",
        "InvoiceDate",
        "ProductCategory",
        "Quantity",
        "UnitPrice",
        "DiscountPercent",
        "Revenue",
        "PaymentMethod",
    ]

    history_fields = [
        c for c in history_fields
        if c in customer_tx.columns
    ]

    history = customer_tx[history_fields].copy()

    if "InvoiceDate" in history.columns:
        history = history.sort_values(
            "InvoiceDate",
            ascending=False,
        )
        history["InvoiceDate"] = (
            history["InvoiceDate"]
            .dt.strftime("%d %B %Y")
        )

    st.dataframe(
        history,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# FOOTER
# =========================================================
st.divider()

st.caption(
    "Customer Retention & CLTV Analytics | "
    "Python + Google Colab + Streamlit + Power BI"
)
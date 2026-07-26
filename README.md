# 📊 SaaS / E-Commerce Cohort Retention & CLTV Analysis

<p align="center">
  <b>From Raw Transactions to Retention Intelligence, Customer Value & Actionable Business Strategy</b>
</p>

<p align="center">
  Python • Google Colab • Pandas • Cohort Analysis • CLTV • Customer Segmentation • Power BI
</p>

---

## ✨ Project Snapshot

This project delivers an end-to-end customer analytics solution for a SaaS / e-commerce business environment.

It transforms raw transactional data into:

> **Clean Data → Cohorts → Retention → CLTV → Segments → Interactive Power BI Insights**

The goal is simple: **understand who the best customers are, how long they stay, what they are worth, and what the business should do next.**

---

## 🎯 Business Questions Answered

This project helps answer:

- Which customer cohorts retain best over time?
- Where does customer drop-off happen fastest?
- How many customers become repeat buyers?
- What is the average, median and maximum Customer Lifetime Value?
- Which customers and segments contribute the most value?
- Which acquisition channels attract high-value customers?
- How do regions and subscription plans differ in customer quality?
- What behaviours distinguish Low Value from Very High Value customers?

---

## 🧰 Tech Stack

| Technology | Role |
|---|---|
| **Python** | Core analysis and calculations |
| **Google Colab** | Cloud notebook execution |
| **Pandas** | Data cleaning, aggregation and transformation |
| **NumPy** | Numerical validation |
| **Matplotlib** | Analytical visualisations |
| **Power BI** | Interactive reporting and dashboard design |
| **CSV** | Data exchange between notebooks and dashboard |

---

# 🗺️ Analytics Journey

```text
┌──────────────────────────────┐
│ Raw Customer Transactions    │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ 01_data_cleaning.ipynb       │
│ Clean • Validate • Engineer  │
└──────────────┬───────────────┘
               │
               ▼
      cleaned_customer_transactions.csv
               │
        ┌──────┴─────────┐
        │                │
        ▼                ▼
┌───────────────┐   ┌──────────────────┐
│ Cohort        │   │ CLTV             │
│ Analysis      │   │ Analysis         │
└──────┬────────┘   └────────┬─────────┘
       │                     │
       ▼                     ▼
Retention Matrix        customer_cltv.csv
Retention Curve              │
Heatmap                      ▼
                    ┌────────────────────┐
                    │ Customer Segments  │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ Power BI Dashboard │
                    └────────────────────┘
```

---

# 📁 Repository Structure

```text
cohort-retention-cltv-analysis/
│
├── data/
│   ├── raw_customer_transactions.csv
│   └── cleaned_customer_transactions.csv
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_cohort_analysis.ipynb
│   ├── 03_cltv_analysis.ipynb
│   └── 04_customer_segmentation.ipynb
│
├── reports/
│   ├── cohort_retention_matrix.csv
│   ├── cohort_retention_long.csv
│   ├── average_retention_curve.csv
│   ├── cohort_kpis.csv
│   ├── customer_cltv.csv
│   ├── cltv_kpis.csv
│   ├── segment_customer_counts.csv
│   ├── segment_cltv_contribution.csv
│   ├── segment_revenue_contribution.csv
│   ├── segment_profile.csv
│   ├── channel_segment_mix.csv
│   ├── region_segment_mix.csv
│   └── subscription_plan_segment_mix.csv
│
├── images/
│   ├── retention_curve.png
│   ├── retention_heatmap.png
│   ├── cltv_distribution.png
│   ├── cltv_by_acquisition_channel.png
│   ├── customer_count_by_segment.png
│   └── cltv_contribution_by_segment.png
│
├── dashboard/
│   └── Power BI report files
│
├── requirements.txt
└── README.md
```

---

# 📓 Notebook 01 — Data Cleaning

**File:** `01_data_cleaning.ipynb`

The first stage creates a reliable analytical foundation.

### What happens here?

- Duplicate rows are removed
- Missing Customer IDs are handled
- Text columns are standardised
- Dates are parsed correctly
- Numeric columns are validated
- Invalid quantities and prices are removed
- Completed transactions are retained
- Revenue is recalculated
- Transaction month is created
- Cohort month is assigned
- Cohort index is generated

### Core Revenue Formula

```text
Revenue =
Quantity × Unit Price × (1 - Discount Percent / 100)
```

### Cohort Index Logic

```text
CohortIndex = 1  → Acquisition Month
CohortIndex = 2  → One Month Later
CohortIndex = 3  → Two Months Later
...
```

### Output

```text
cleaned_customer_transactions.csv
```

---

# 📓 Notebook 02 — Cohort Retention Analysis

**File:** `02_cohort_analysis.ipynb`

This notebook answers:

> **“After customers first purchase, how many return in later months?”**

### Main Analysis

- Acquisition cohort creation
- Customer counts by cohort month
- Retention matrix
- Long-format retention table
- Average retention curve
- Cohort heatmap
- Repeat vs one-time customer KPIs

### Retention Formula

```text
Retention Rate (%) =
Active Customers in Cohort Month
÷
Customers in Initial Cohort
× 100
```

### Validation Rule

Every cohort must begin at:

```text
Month 1 Retention = 100%
```

### Outputs

```text
cohort_customer_counts.csv
cohort_retention_matrix.csv
cohort_retention_long.csv
average_retention_curve.csv
cohort_kpis.csv
retention_curve.png
retention_heatmap.png
```

---

# 📓 Notebook 03 — Customer Lifetime Value Analysis

**File:** `03_cltv_analysis.ipynb`

> ⭐ **This is the main calculation notebook of the project.**

It converts transaction history into customer-level value metrics.

### Key Metrics

#### Average Order Value

```text
Average Order Value =
Total Revenue ÷ Total Orders
```

#### Customer Lifespan

```text
Customer Lifespan (Months) =
(Last Purchase Date - First Purchase Date)
÷ 30.44
```

#### Purchase Frequency

```text
Purchase Frequency / Month =
Total Orders ÷ Customer Lifespan
```

#### Historical CLTV

```text
Historical CLTV =
Average Order Value
× Purchase Frequency
× Customer Lifespan
```

---

## 💎 CLTV Segmentation

Customers are divided into four value tiers:

| Segment | Interpretation |
|---|---|
| **Low Value** | Low monetary contribution |
| **Medium Value** | Developing customer value |
| **High Value** | Strong customer contribution |
| **Very High Value** | Strategic / premium customers |

### Main Outputs

```text
customer_cltv.csv
cltv_kpis.csv
cltv_by_acquisition_channel.csv
cltv_by_region.csv
cltv_segment_profile.csv
top_10_cltv_customers.csv
cltv_distribution.png
cltv_by_acquisition_channel.png
```

---

# 📓 Notebook 04 — Customer Segmentation

**File:** `04_customer_segmentation.ipynb`

This notebook answers:

> **“How do customer behaviours differ across value segments?”**

### Segment Metrics

- Customer count
- Customer share %
- Total revenue
- Average CLTV
- Median CLTV
- Average orders
- Average order value
- Average lifespan
- Average purchase frequency

### Additional Analysis

```text
Acquisition Channel × CLTV Segment
Region × CLTV Segment
Subscription Plan × CLTV Segment
```

### Outputs

```text
segment_customer_counts.csv
segment_cltv_contribution.csv
segment_revenue_contribution.csv
segment_profile.csv
channel_segment_mix.csv
region_segment_mix.csv
subscription_plan_segment_mix.csv
customer_count_by_segment.png
cltv_contribution_by_segment.png
```

---

# 📊 Power BI Dashboard

The final dashboard turns the analytical outputs into a five-page decision-support system.

---

## 1️⃣ Executive Overview

### KPI Cards

- Total Revenue
- Total Customers
- Total Orders
- Average Order Value
- Repeat Customer Rate
- Average Historical CLTV

### Visuals

- Monthly Revenue Trend
- Revenue by Customer Value Segment
- Revenue by Acquisition Channel
- Customer Distribution by Region

---

## 2️⃣ Cohort Retention

### KPI Cards

- Total Customers
- Repeat Customers
- Repeat Customer Rate
- One-Time Customers

### Visuals

- Monthly Customer Retention Heatmap
- Average Customer Retention Curve

---

## 3️⃣ CLTV Analysis

### KPI Cards

- Average Historical CLTV
- Median Historical CLTV
- Maximum Historical CLTV
- Average Customer Lifespan
- Average Purchase Frequency

### Visuals

- CLTV Distribution
- Average CLTV by Acquisition Channel
- Purchase Frequency vs Historical CLTV
- Top 10 Customers by CLTV

---

## 4️⃣ Customer Segmentation

### Segment Cards

- Low Value Customers
- Medium Value Customers
- High Value Customers
- Very High Value Customers

### Visuals

- Revenue Contribution by CLTV Segment
- Customer Count and Revenue by Segment
- Segment Profile Matrix
- Customer Value Mix by Acquisition Channel

---

## 5️⃣ Customer Detail

### KPI Cards

- Historical CLTV
- Total Orders
- Average Order Value
- Customer Lifespan (Months)
- Purchase Frequency / Month

### Detail Views

- Customer Transaction History
- Customer Profile
- Customer ID selection

---

# 🧱 Power BI Data Model

```text
                  ┌──────────────┐
                  │   DimDate    │
                  └──────┬───────┘
                         │
                         ▼
                ┌─────────────────┐
                │ FactTransactions│
                └───────┬─────────┘
                        │
                        ▲
                 ┌──────┴───────┐
                 │ DimCustomer  │
                 └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │ CustomerCLTV │
                 └──────────────┘
```

Additional analytical tables:

```text
CohortRetention
RetentionLong
_Measures
```

---

# 🧮 Key DAX Measures

```DAX
Total Revenue =
SUM ( FactTransactions[Revenue] )
```

```DAX
Total Customers =
DISTINCTCOUNT ( FactTransactions[CustomerID] )
```

```DAX
Total Orders =
DISTINCTCOUNT ( FactTransactions[InvoiceNo] )
```

```DAX
Average Order Value =
DIVIDE (
    [Total Revenue],
    [Total Orders],
    0
)
```

```DAX
Repeat Customers =
COUNTROWS (
    FILTER (
        VALUES ( FactTransactions[CustomerID] ),
        CALCULATE (
            DISTINCTCOUNT ( FactTransactions[InvoiceNo] )
        ) > 1
    )
)
```

```DAX
Repeat Customer Rate =
DIVIDE (
    [Repeat Customers],
    [Total Customers],
    0
)
```

```DAX
Average Historical CLTV =
AVERAGE ( CustomerCLTV[HistoricalCLTV] )
```

```DAX
Median Historical CLTV =
MEDIAN ( CustomerCLTV[HistoricalCLTV] )
```

```DAX
Maximum Historical CLTV =
MAX ( CustomerCLTV[HistoricalCLTV] )
```

---

# 🔍 Analytical Story

The project follows a simple but powerful progression:

### 1. Who are the customers?

Identify customer profiles, regions, plans and acquisition channels.

### 2. Do they return?

Use cohort retention analysis to measure repeat behaviour over time.

### 3. What are they worth?

Calculate AOV, purchase frequency, lifespan and historical CLTV.

### 4. Which customers matter most?

Segment customers into Low, Medium, High and Very High Value groups.

### 5. What should the business do?

Use the Power BI dashboard to convert analysis into targeted action.

---

# 💡 Key Business Insights

The analytical framework supports insights such as:

- Retention typically declines after the initial acquisition month.
- Repeat customers are more strategically valuable than one-time buyers.
- Very High Value customers contribute a disproportionate share of total customer value.
- Higher purchase frequency strongly supports higher CLTV.
- Longer customer relationships increase total customer value.
- Acquisition channels differ in the quality of customers they attract.
- Segmentation allows more targeted marketing and retention strategies.
- Cohort analysis reveals whether newer customers are performing better or worse than older cohorts.

---

# 🚀 Recommended Business Actions

### 🛡️ Protect High-Value Customers
Build VIP, loyalty and personalised engagement programmes.

### 🔁 Increase Repeat Purchases
Use lifecycle campaigns, reminders and re-engagement offers.

### 🛒 Increase Average Order Value
Introduce bundles, cross-sell and upsell opportunities.

### 🎯 Optimise Acquisition Spend
Prioritise acquisition channels that consistently produce higher-CLTV customers.

### 🧩 Use Segment-Specific Campaigns
Avoid one-size-fits-all marketing.

### ⏱️ Focus on Early Retention
Intervene during the first few months, when customer drop-off is often strongest.

---

# ▶️ How to Run the Project

### Step 1

Run:

```text
01_data_cleaning.ipynb
```

Input:

```text
raw_customer_transactions.csv
```

Output:

```text
cleaned_customer_transactions.csv
```

### Step 2

Run:

```text
02_cohort_analysis.ipynb
```

Input:

```text
cleaned_customer_transactions.csv
```

### Step 3

Run:

```text
03_cltv_analysis.ipynb
```

Input:

```text
cleaned_customer_transactions.csv
```

Output:

```text
customer_cltv.csv
```

### Step 4

Run:

```text
04_customer_segmentation.ipynb
```

Input:

```text
customer_cltv.csv
```

### Step 5

Refresh the Power BI dashboard.

---

# ✅ Data Quality Checklist

Before publishing results, verify:

```text
✓ No blank Customer IDs
✓ No invalid invoice dates
✓ Quantity > 0
✓ Unit Price > 0
✓ Discount between 0 and 100
✓ Revenue > 0
✓ No duplicate transactions
✓ Cohort Month ≤ Transaction Month
✓ Cohort Index begins at 1
✓ Every cohort starts at 100% retention
✓ CustomerCLTV contains one row per customer
```

---

# 📦 Final Deliverables

- ✅ Raw transaction dataset
- ✅ Cleaned transaction dataset
- ✅ Four Google Colab notebooks
- ✅ Cohort retention matrix
- ✅ Retention curve
- ✅ Retention heatmap
- ✅ Customer CLTV dataset
- ✅ Customer segmentation outputs
- ✅ Power BI dashboard
- ✅ Business insights
- ✅ Recommendations
- ✅ Project documentation

---

# 🏁 Final Outcome

This project demonstrates a complete customer analytics workflow:

> **Data Preparation → Behaviour Analysis → Value Measurement → Segmentation → Business Intelligence**

It combines technical analytics with business storytelling to help decision-makers understand **retention, customer value, acquisition quality and growth opportunities**.

---

<p align="center">
  <b>Built with Python + Google Colab + Power BI</b>
</p>

<p align="center">
  <i>Turning customer transactions into retention intelligence and customer value strategy.</i>
</p>

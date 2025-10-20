
import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Plotly template
import plotly.io as pio
pio.templates.default = "plotly_white"

print("✅ Libraries imported successfully")

# %% [markdown]
# ---
# ## 1. Executive Summary {#executive-summary}
# 
# ### 🎯 Key Findings (To be populated after analysis)
# 
# 1. **[Finding 1]** - Impact and recommendation
# 2. **[Finding 2]** - Impact and recommendation
# 3. **[Finding 3]** - Impact and recommendation
# 4. **[Finding 4]** - Impact and recommendation
# 5. **[Finding 5]** - Impact and recommendation
# 
# ### 💡 Critical Recommendations
# 
# | Priority | Action Item | Expected Impact | Timeline |
# |----------|-------------|-----------------|----------|
# | 🔴 HIGH | [Action 1] | [Impact] | 30 days |
# | 🟠 MEDIUM | [Action 2] | [Impact] | 60 days |
# | 🟢 LOW | [Action 3] | [Impact] | 90 days |

# %% [markdown]
# ---
# ## 2. Data Loading & Validation {#data-loading}

# %%
# Connect to SQLite Database
conn = sqlite3.connect('../data/nike_sales.db')

# Load data
df = pd.read_sql_query("SELECT * FROM nike_sales_cleaned", conn)

# Display basic info
print("="*70)
print("DATA OVERVIEW")
print("="*70)
print(f"📊 Total Records: {len(df):,}")
print(f"📅 Date Range: {df['Order_Date'].min()} to {df['Order_Date'].max()}")
print(f"🏙️ Regions: {df['Region'].nunique()}")
print(f"👕 Product Lines: {df['Product_Line'].nunique()}")
print(f"💾 Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
print("="*70)

# Display first few rows
df.head()

# %%
# Data Quality Check
print("\n📋 DATA QUALITY REPORT")
print("="*70)
print("\nMissing Values:")
print(df.isnull().sum())
print("\nData Types:")
print(df.dtypes)
print("\nDuplicate Order IDs:", df['Order_ID'].duplicated().sum())
print("="*70)

# %% [markdown]
# ---
# ## 3. Business Performance Overview {#business-overview}
# 
# ### 🎯 Business Question:
# **"What is our current business health and are we meeting profitability targets?"**

# %%
# Calculate Key Business Metrics
total_revenue = df['Revenue'].sum()
total_profit = df['Profit'].sum()
overall_margin = (total_profit / total_revenue) * 100
avg_order_value = df['Revenue'].mean()
total_transactions = len(df)
total_units_sold = df['Units_Sold'].sum()
loss_transaction_count = df['Loss_Flag'].sum()
loss_transaction_rate = (loss_transaction_count / total_transactions) * 100
avg_discount = df['Discount_Applied'].mean()
revenue_per_unit = total_revenue / total_units_sold

print("="*70)
print("KEY PERFORMANCE INDICATORS (KPIs)")
print("="*70)
print(f"\n💰 Financial Metrics:")
print(f"   Total Revenue:        ₹{total_revenue:,.2f}")
print(f"   Total Profit:         ₹{total_profit:,.2f}")
print(f"   Overall Margin:       {overall_margin:.2f}%")
print(f"   Avg Order Value:      ₹{avg_order_value:,.2f}")
print(f"\n📊 Operational Metrics:")
print(f"   Total Transactions:   {total_transactions:,}")
print(f"   Total Units Sold:     {total_units_sold:,}")
print(f"   Revenue per Unit:     ₹{revenue_per_unit:,.2f}")
print(f"\n⚠️ Risk Metrics:")
print(f"   Loss Transactions:    {loss_transaction_count:,} ({loss_transaction_rate:.2f}%)")
print(f"   Avg Discount Applied: {avg_discount:.2f}%")
print("="*70)

# %%
# KPI Dashboard Visualization
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Total Revenue', 'Total Profit', 'Average Order Value', 'Loss Transaction Rate'),
    specs=[[{'type': 'indicator'}, {'type': 'indicator'}],
           [{'type': 'indicator'}, {'type': 'indicator'}]]
)

# Revenue
fig.add_trace(go.Indicator(
    mode = "number+delta",
    value = total_revenue,
    title = {'text': "Total Revenue (₹)"},
    number = {'prefix': "₹", 'valueformat': ",.0f"},
    domain = {'x': [0, 1], 'y': [0, 1]}
), row=1, col=1)

# Profit
fig.add_trace(go.Indicator(
    mode = "number+gauge",
    value = overall_margin,
    title = {'text': f"Profit Margin<br>₹{total_profit:,.0f}"},
    number = {'suffix': "%"},
    gauge = {'axis': {'range': [None, 50]},
             'bar': {'color': "darkgreen"},
             'steps': [
                 {'range': [0, 15], 'color': "lightcoral"},
                 {'range': [15, 25], 'color': "lightyellow"},
                 {'range': [25, 50], 'color': "lightgreen"}],
             'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 20}}
), row=1, col=2)

# AOV
fig.add_trace(go.Indicator(
    mode = "number",
    value = avg_order_value,
    title = {'text': "Average Order Value (₹)"},
    number = {'prefix': "₹", 'valueformat': ",.2f"},
), row=2, col=1)

# Loss Rate
fig.add_trace(go.Indicator(
    mode = "number+gauge",
    value = loss_transaction_rate,
    title = {'text': f"Loss Transaction Rate<br>{loss_transaction_count:,} orders"},
    number = {'suffix': "%"},
    gauge = {'axis': {'range': [0, 100]},
             'bar': {'color': "darkred"},
             'steps': [
                 {'range': [0, 10], 'color': "lightgreen"},
                 {'range': [10, 20], 'color': "lightyellow"},
                 {'range': [20, 100], 'color': "lightcoral"}],
             'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 15}}
), row=2, col=2)

fig.update_layout(height=600, title_text="<b>Business Performance Dashboard</b>", title_x=0.5)
fig.show()

# %% [markdown]
# ### 💡 Key Insight: Business Performance Overview
# 
# **Actionable Title:** *"[FILL AFTER RUNNING: e.g., 'Overall Margin at 18.5% — 1.5% Below Target, Review Discount Strategy']"*
# 
# **Analysis:**
# - Total revenue of ₹[X] indicates [strong/moderate/weak] performance
# - Profit margin of [X]% is [above/below] industry benchmark of 20%
# - Loss transaction rate of [X]% requires immediate attention if above 15%
# 
# **Recommendation:**
# - [ ] If margin < 20%: Reduce excessive discounting and optimize pricing
# - [ ] If loss rate > 15%: Implement stricter discount approval process
# - [ ] Focus on high-margin products to improve overall profitability

# %% [markdown]
# ---
# ## 4. Regional Performance Analysis {#regional-analysis}
# 
# ### 🎯 Business Question:
# **"Which regions are underperforming and where should we invest more resources?"**

# %%
# Regional Performance Metrics
regional_performance = df.groupby('Region').agg({
    'Revenue': 'sum',
    'Profit': 'sum',
    'Order_ID': 'count',
    'Units_Sold': 'sum',
    'Discount_Applied': 'mean'
}).round(2)

regional_performance.columns = ['Total_Revenue', 'Total_Profit', 'Transactions', 'Units_Sold', 'Avg_Discount']
regional_performance['Profit_Margin_%'] = ((regional_performance['Total_Profit'] / regional_performance['Total_Revenue']) * 100).round(2)
regional_performance['AOV'] = (regional_performance['Total_Revenue'] / regional_performance['Transactions']).round(2)
regional_performance['Revenue_%'] = ((regional_performance['Total_Revenue'] / regional_performance['Total_Revenue'].sum()) * 100).round(2)

# Sort by revenue
regional_performance = regional_performance.sort_values('Total_Revenue', ascending=False)

print("\n📊 REGIONAL PERFORMANCE SUMMARY")
print("="*70)
print(regional_performance)
print("="*70)

# %%
# Visualization: Revenue by Region with Profit Margin
fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Revenue Distribution by Region', 'Profit Margin by Region'),
    specs=[[{'type': 'bar'}, {'type': 'bar'}]]
)

# Revenue bars
fig.add_trace(
    go.Bar(
        x=regional_performance.index,
        y=regional_performance['Total_Revenue'],
        name='Revenue',
        text=regional_performance['Revenue_%'].apply(lambda x: f'{x}%'),
        textposition='outside',
        marker_color='steelblue'
    ),
    row=1, col=1
)

# Profit margin bars
colors = ['green' if x >= overall_margin else 'red' for x in regional_performance['Profit_Margin_%']]
fig.add_trace(
    go.Bar(
        x=regional_performance.index,
        y=regional_performance['Profit_Margin_%'],
        name='Profit Margin',
        text=regional_performance['Profit_Margin_%'].apply(lambda x: f'{x}%'),
        textposition='outside',
        marker_color=colors
    ),
    row=1, col=2
)

# Add average line to profit margin
fig.add_hline(y=overall_margin, line_dash="dash", line_color="red", 
              annotation_text=f"Avg: {overall_margin:.1f}%", 
              annotation_position="right", row=1, col=2)

fig.update_xaxes(title_text="Region", row=1, col=1)
fig.update_xaxes(title_text="Region", row=1, col=2)
fig.update_yaxes(title_text="Revenue (₹)", row=1, col=1)
fig.update_yaxes(title_text="Profit Margin (%)", row=1, col=2)

fig.update_layout(
    height=500,
    title_text="<b>Regional Performance: Revenue vs Profitability</b>",
    title_x=0.5,
    showlegend=False
)

fig.show()

# %%
# Regional Comparison: AOV and Transaction Count
fig = go.Figure()

fig.add_trace(go.Bar(
    x=regional_performance.index,
    y=regional_performance['AOV'],
    name='Average Order Value',
    marker_color='lightseagreen',
    yaxis='y',
    text=regional_performance['AOV'].apply(lambda x: f'₹{x:,.0f}'),
    textposition='outside'
))

fig.add_trace(go.Scatter(
    x=regional_performance.index,
    y=regional_performance['Transactions'],
    name='Transaction Count',
    mode='lines+markers',
    marker=dict(size=12, color='coral'),
    yaxis='y2',
    line=dict(width=3)
))

fig.update_layout(
    title='<b>Regional Comparison: AOV vs Transaction Volume</b>',
    title_x=0.5,
    xaxis=dict(title='Region'),
    yaxis=dict(title='Average Order Value (₹)', side='left'),
    yaxis2=dict(title='Number of Transactions', overlaying='y', side='right'),
    legend=dict(x=0.01, y=0.99),
    height=500,
    hovermode='x unified'
)

fig.show()

# %% [markdown]
# ### 💡 Key Insight: Regional Performance
# 
# **Actionable Title:** *"[FILL: e.g., 'Mumbai Generates 35% of Revenue But Delhi Has 15% Higher AOV — Replicate Premium Strategy']"*
# 
# **Analysis:**
# - **Top Performing Region:** [Region] with ₹[X] revenue ([X]% of total)
# - **Highest Margin Region:** [Region] at [X]% (vs avg [X]%)
# - **Highest AOV Region:** [Region] at ₹[X] (vs avg ₹[X])
# - **Underperforming Region:** [Region] - [X]% below average margin
# 
# **Recommendations:**
# 1. **Invest More:** Increase inventory and marketing in [top revenue region]
# 2. **Improve Margins:** In [low margin region], reduce discounts by [X]%
# 3. **Increase AOV:** In [low AOV region], implement bundle deals and upselling
# 4. **Best Practices:** Study [highest margin region]'s strategy and replicate

# %% [markdown]
# ---
# ## 5. Product Line Strategy {#product-analysis}
# 
# ### 🎯 Business Question:
# **"Which product lines should we prioritize and are we allocating resources effectively?"**

# %%
# Product Line Performance
product_performance = df.groupby('Product_Line').agg({
    'Revenue': 'sum',
    'Profit': 'sum',
    'Order_ID': 'count',
    'Units_Sold': 'sum',
    'Discount_Applied': 'mean'
}).round(2)

product_performance.columns = ['Total_Revenue', 'Total_Profit', 'Transactions', 'Units_Sold', 'Avg_Discount']
product_performance['Profit_Margin_%'] = ((product_performance['Total_Profit'] / product_performance['Total_Revenue']) * 100).round(2)
product_performance['Revenue_per_Transaction'] = (product_performance['Total_Revenue'] / product_performance['Transactions']).round(2)
product_performance['Revenue_%'] = ((product_performance['Total_Revenue'] / product_performance['Total_Revenue'].sum()) * 100).round(2)

product_performance = product_performance.sort_values('Total_Revenue', ascending=False)

print("\n📊 PRODUCT LINE PERFORMANCE")
print("="*70)
print(product_performance)
print("="*70)

# %%
# Product Portfolio Matrix (Revenue vs Profit Margin)
fig = px.scatter(
    product_performance.reset_index(),
    x='Total_Revenue',
    y='Profit_Margin_%',
    size='Units_Sold',
    color='Product_Line',
    text='Product_Line',
    title='<b>Product Portfolio Matrix: Revenue vs Profitability</b>',
    labels={
        'Total_Revenue': 'Total Revenue (₹)',
        'Profit_Margin_%': 'Profit Margin (%)',
        'Units_Sold': 'Units Sold'
    },
    size_max=60
)

# Add quadrant lines
avg_revenue = product_performance['Total_Revenue'].mean()
avg_margin = product_performance['Profit_Margin_%'].mean()

fig.add_hline(y=avg_margin, line_dash="dash", line_color="gray", 
              annotation_text=f"Avg Margin: {avg_margin:.1f}%")
fig.add_vline(x=avg_revenue, line_dash="dash", line_color="gray",
              annotation_text=f"Avg Revenue: ₹{avg_revenue:,.0f}")

# Add quadrant labels
fig.add_annotation(x=product_performance['Total_Revenue'].max() * 0.9, 
                   y=product_performance['Profit_Margin_%'].max() * 0.95,
                   text="⭐ Stars<br>(High Revenue, High Margin)", showarrow=False,
                   bgcolor="lightgreen", opacity=0.7)

fig.add_annotation(x=product_performance['Total_Revenue'].min() * 1.1, 
                   y=product_performance['Profit_Margin_%'].max() * 0.95,
                   text="💎 Cash Cows<br>(Low Revenue, High Margin)", showarrow=False,
                   bgcolor="lightyellow", opacity=0.7)

fig.add_annotation(x=product_performance['Total_Revenue'].max() * 0.9, 
                   y=product_performance['Profit_Margin_%'].min() * 1.05,
                   text="⚠️ Question Marks<br>(High Revenue, Low Margin)", showarrow=False,
                   bgcolor="lightcoral", opacity=0.7)

fig.update_traces(textposition='top center')
fig.update_layout(height=600, showlegend=True)
fig.show()

# %%
# Product Line Revenue Breakdown with Volume
fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Revenue Contribution', 'Units Sold Distribution'),
    specs=[[{'type': 'pie'}, {'type': 'pie'}]]
)

fig.add_trace(
    go.Pie(
        labels=product_performance.index,
        values=product_performance['Total_Revenue'],
        textinfo='label+percent',
        textposition='inside',
        marker=dict(colors=px.colors.qualitative.Set3)
    ),
    row=1, col=1
)

fig.add_trace(
    go.Pie(
        labels=product_performance.index,
        values=product_performance['Units_Sold'],
        textinfo='label+percent',
        textposition='inside',
        marker=dict(colors=px.colors.qualitative.Pastel)
    ),
    row=1, col=2
)

fig.update_layout(
    title_text="<b>Product Line: Revenue vs Volume Analysis</b>",
    title_x=0.5,
    height=500
)

fig.show()

# %% [markdown]
# ### 💡 Key Insight: Product Line Strategy
# 
# **Actionable Title:** *"[FILL: e.g., 'Footwear Generates 45% Revenue with 22% Margin — Increase Inventory by 20%']"*
# 
# **Product Portfolio Classification:**
# 
# **⭐ Stars (High Revenue, High Margin):**
# - [Product]: Focus and expand - highest ROI
# 
# **💎 Cash Cows (Low Revenue, High Margin):**
# - [Product]: Increase marketing to drive volume
# 
# **⚠️ Question Marks (High Revenue, Low Margin):**
# - [Product]: Optimize pricing or reduce costs
# 
# **🔻 Dogs (Low Revenue, Low Margin):**
# - [Product]: Consider discontinuation or repositioning
# 
# **Recommendations:**
# 1. **Double Down:** Increase marketing budget for [Star products] by [X]%
# 2. **Optimize Pricing:** In [Question Mark products], reduce discounts by [X]%
# 3. **Cross-Sell:** Bundle [low volume, high margin] with [high volume products]
# 4. **Review Portfolio:** Consider phasing out products with <[X]% margin

# %% [markdown]
# ---
# ## 6. Pricing & Discount Optimization {#pricing-analysis}
# 
# ### 🎯 Business Question:
# **"Are we over-discounting and how does discount level impact profitability?"**

# %%
# Discount Analysis
discount_bins = [0, 10, 20, 30, 40, 100]
discount_labels = ['0-10%', '10-20%', '20-30%', '30-40%', '40%+']
df['Discount_Tier'] = pd.cut(df['Discount_Applied'], bins=discount_bins, labels=discount_labels, include_lowest=True)

discount_analysis = df.groupby('Discount_Tier').agg({
    'Revenue': 'sum',
    'Profit': 'sum',
    'Order_ID': 'count',
    'Units_Sold': 'sum'
}).round(2)

discount_analysis['Profit_Margin_%'] = ((discount_analysis['Profit'] / discount_analysis['Revenue']) * 100).round(2)
discount_analysis['Avg_Revenue_per_Order'] = (discount_analysis['Revenue'] / discount_analysis['Order_ID']).round(2)

print("\n📊 DISCOUNT TIER ANALYSIS")
print("="*70)
print(discount_analysis)
print("="*70)

# %%
# Discount Impact Visualization
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        'Revenue by Discount Tier',
        'Profit Margin by Discount Tier',
        'Transaction Volume by Discount',
        'Discount vs Profit Correlation'
    ),
    specs=[[{'type': 'bar'}, {'type': 'bar'}],
           [{'type': 'bar'}, {'type': 'scatter'}]]
)

# Revenue by discount tier
fig.add_trace(
    go.Bar(x=discount_analysis.index, y=discount_analysis['Revenue'],
           marker_color='steelblue', name='Revenue',
           text=discount_analysis['Revenue'].apply(lambda x: f'₹{x/1000:.0f}K'),
           textposition='outside'),
    row=1, col=1
)

# Profit margin by discount tier
colors_margin = ['green' if x >= overall_margin else 'red' for x in discount_analysis['Profit_Margin_%']]
fig.add_trace(
    go.Bar(x=discount_analysis.index, y=discount_analysis['Profit_Margin_%'],
           marker_color=colors_margin, name='Margin',
           text=discount_analysis['Profit_Margin_%'].apply(lambda x: f'{x:.1f}%'),
           textposition='outside'),
    row=1, col=2
)

# Transaction volume
fig.add_trace(
    go.Bar(x=discount_analysis.index, y=discount_analysis['Order_ID'],
           marker_color='coral', name='Transactions',
           text=discount_analysis['Order_ID'],
           textposition='outside'),
    row=2, col=1
)

# Scatter: Discount vs Profit
fig.add_trace(
    go.Scatter(x=df['Discount_Applied'], y=df['Profit'],
               mode='markers', marker=dict(size=3, color='purple', opacity=0.5),
               name='Individual Orders'),
    row=2, col=2
)

fig.update_xaxes(title_text="Discount Tier", row=1, col=1)
fig.update_xaxes(title_text="Discount Tier", row=1, col=2)
fig.update_xaxes(title_text="Discount Tier", row=2, col=1)
fig.update_xaxes(title_text="Discount Applied (%)", row=2, col=2)

fig.update_yaxes(title_text="Revenue (₹)", row=1, col=1)
fig.update_yaxes(title_text="Profit Margin (%)", row=1, col=2)
fig.update_yaxes(title_text="Transactions", row=2, col=1)
fig.update_yaxes(title_text="Profit (₹)", row=2, col=2)

fig.update_layout(
    height=800,
    title_text="<b>Discount Strategy Impact Analysis</b>",
    title_x=0.5,
    showlegend=False
)

fig.show()

# %%
# Loss Transaction Analysis by Discount
loss_by_discount = df.groupby('Discount_Tier')['Loss_Flag'].agg(['sum', 'count'])
loss_by_discount['Loss_Rate_%'] = ((loss_by_discount['sum'] / loss_by_discount['count']) * 100).round(2)

fig = go.Figure()

fig.add_trace(go.Bar(
    x=loss_by_discount.index,
    y=loss_by_discount['Loss_Rate_%'],
    marker_color=['green' if x < 10 else 'orange' if x < 20 else 'red' 
                  for x in loss_by_discount['Loss_Rate_%']],
    text=loss_by_discount['Loss_Rate_%'].apply(lambda x: f'{x}%'),
    textposition='outside'
))

fig.add_hline(y=15, line_dash="dash", line_color="red",
              annotation_text="15% Threshold", annotation_position="right")

fig.update_layout(
    title='<b>⚠️ Loss Transaction Rate by Discount Tier — Cap Discounts to Protect Margins</b>',
    title_x=0.5,
    xaxis_title='Discount Tier',
    yaxis_title='Loss Transaction Rate (%)',
    height=500
)

fig.show()

# %% [markdown]
# ### 💡 Key Insight: Discount Strategy
# 
# **Actionable Title:** *"[FILL: e.g., 'Discounts Above 30% Lead to 45% Loss Rate — Implement Maximum 25% Discount Cap']"*
# 
# **Analysis:**
# - **Optimal Discount Range:** [X-Y]% drives volume while maintaining [Z]% margin
# - **Danger Zone:** Discounts above [X]% result in [Y]% loss rate
# - **Sweet Spot:** [X-Y]% discount tier generates [highest revenue/best margin/optimal balance]
# 
# **Profit Erosion:**
# - Every 10% increase in discount reduces margin by approximately [X]%
# - [X]% of all loss transactions occur in the [Y]% discount tier
# 
# **Recommendations:**
# 1. **Implement Cap:** Maximum discount of [X]% across all products
# 2. **Approval Process:** Discounts above [X]% require manager approval
# 3. **Alternative Strategies:** Replace high discounts with:
#    - Bundle deals (maintain margin, increase AOV)
#    - Loyalty points (customer retention without immediate margin hit)
#    - Free shipping thresholds (increase basket size)
# 4. **Dynamic Pricing:** Test [X]% discount in [optimal range] for [specific products]

# %% [markdown]
# ---
# ## 7. Customer Behavior Analysis {#customer-analysis}
# 
# ### 🎯 Business Question:
# **"Who are our most valuable customers and how do buying patterns differ?"**

# %%
# Gender Category Analysis
gender_analysis = df.groupby('Gender_Category').agg({
    'Revenue': ['sum', 'mean'],
    'Profit': 'sum',
    'Order_ID': 'count',
    'Units_Sold': 'sum',
    'Discount_Applied': 'mean'
}).round(2)

gender_analysis.columns = ['Total_Revenue', 'AOV', 'Total_Profit', 'Transactions', 'Units_Sold', 'Avg_Discount']
gender_analysis['Profit_Margin_%'] = ((gender_analysis['Total_Profit'] / gender_analysis['Total_Revenue']) * 100).round(2)
gender_analysis['Revenue_%'] = ((gender_analysis['Total_Revenue'] / gender_analysis['Total_Revenue'].sum()) * 100).round(2)

print("\n📊 CUSTOMER ANALYSIS BY GENDER")
print("="*70)
print(gender_analysis)
print("="*70)

# %%
# Gender Comparison Dashboard
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        'Revenue Distribution',
        'Average Order Value',
        'Transaction Volume',
        'Profit Margin Comparison'
    ),
    specs=[[{'type': 'pie'}, {'type': 'bar'}],
           [{'type': 'bar'}, {'type': 'bar'}]]
)

# Revenue distribution pie
fig.add_trace(
    go.Pie(labels=gender_analysis.index, values=gender_analysis['Total_Revenue'],
           textinfo='label+percent', hole=0.3),
    row=1, col=1
)

# AOV comparison
fig.add_trace(
    go.Bar(x=gender_analysis.index, y=gender_analysis['AOV'],
           marker_color=['#FF69B4', '#1E90FF', '#9370DB'],
           text=gender_analysis['AOV'].apply(lambda x: f'₹{x:,.0f}'),
           textposition='outside'),
    row=1, col=2
)

# Transaction volume
fig.add_trace(
    go.Bar(x=gender_analysis.index, y=gender_analysis['Transactions'],
           marker_color=['#FFB6C1', '#87CEEB', '#DDA0DD'],
           text=gender_analysis['Transactions'],
           textposition='outside'),
    row=2, col=1
)

# Profit margin
fig.add_trace(
    go.Bar(x=gender_analysis.index, y=gender_analysis['Profit_Margin_%'],
           marker_color=['#FF1493', '#4169E1', '#8A2BE2'],
           text=gender_analysis['Profit_Margin_%'].apply(lambda x: f'{x:.1f}%'),
           textposition='outside'),
    row=2, col=2
)

fig.update_xaxes(title_text="Gender", row=1, col=2)
fig.update_xaxes(title_text="Gender", row=2, col=1)
fig.update_xaxes(title_text="Gender", row=2, col=2)

fig.update_yaxes(title_text="AOV (₹)", row=1, col=2)
fig.update_yaxes(title_text="Transactions", row=2, col=1)
fig.update_yaxes(title_text="Profit Margin (%)", row=2, col=2)

fig.update_layout(
    height=800,
    title_text="<b>Customer Behavior Analysis by Gender Category</b>",
    title_x=0.5,
    showlegend=False
)

fig.show()

# %%
# Product Line Preference by Gender
gender_product = pd.crosstab(df['Gender_Category'], df['Product_Line'], 
                             values=df['Revenue'], aggfunc='sum')
gender_product_pct = gender_product.div(gender_product.sum(axis=1), axis=0) * 100

fig = go.Figure()

for product in gender_product_pct.columns:
    fig.add_trace(go.Bar(
        name=product,
        x=gender_product_pct.index,
        y=gender_product_pct[product],
        text=gender_product_pct[product].apply(lambda x: f'{x:.1f}%'),
        textposition='inside'
    ))

fig.update_layout(
    title='<b>Product Line Preference by Gender Category (% of Revenue)</b>',
    title_x=0.5,
    xaxis_title='Gender Category',
    yaxis_title='Revenue Distribution (%)',
    barmode='stack',
    height=500,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

fig.show()

# %% [markdown]
# ### 💡 Key Insight: Customer Behavior
# 
# **Actionable Title:** *"[FILL: e.g., 'Men Generate 58% of Revenue with 12% Higher AOV — Launch Premium Men's Collection']"*
# 
# **Analysis:**
# - **Highest Revenue Segment:** [Gender] contributes [X]% of total revenue
# - **Highest AOV:** [Gender] at ₹[X] vs [Gender] at ₹[Y] ([Z]% difference)
# - **Transaction Frequency:** [Gender] has [X]% more transactions
# - **Product Preferences:** [Gender] prefers [Product Lines], [Gender] prefers [Product Lines]
# 
# **Strategic Insights:**
# - High AOV + Low Volume = Premium segment opportunity
# - Low AOV + High Volume = Mass market, focus on bundles
# - Product preferences reveal cross-sell opportunities
# 
# **Recommendations:**
# 1. **For [High AOV Gender]:** Launch premium line, VIP program, exclusive collections
# 2. **For [High Volume Gender]:** Bundle deals, loyalty rewards, subscription model
# 3. **Cross-Sell:** Promote [popular products from Gender A] to [Gender B]
# 4. **Marketing Split:** Allocate budget proportional to revenue: [X]% to [Gender], [Y]% to [Gender]

# %% [markdown]
# ---
# ## 8. Time-Based Trends {#time-analysis}
# 
# ### 🎯 Business Question:
# **"What are our sales patterns and when should we run promotions vs full-price sales?"**

# %%
# Prepare time-based data
df['Order_Date'] = pd.to_datetime(df['Order_Date'])
df['Year_Month'] = df['Order_Date'].dt.to_period('M').astype(str)
df['Month'] = df['Order_Date'].dt.month
df['Month_Name'] = df['Order_Date'].dt.strftime('%B')
df['Day_of_Week'] = df['Order_Date'].dt.day_name()
df['Week_Number'] = df['Order_Date'].dt.isocalendar().week

# Monthly trends
monthly_trends = df.groupby('Year_Month').agg({
    'Revenue': 'sum',
    'Profit': 'sum',
    'Order_ID': 'count',
    'Units_Sold': 'sum'
}).round(2)

monthly_trends['Profit_Margin_%'] = ((monthly_trends['Profit'] / monthly_trends['Revenue']) * 100).round(2)

# Calculate MoM growth
monthly_trends['Revenue_Growth_%'] = monthly_trends['Revenue'].pct_change() * 100
monthly_trends['Revenue_Growth_%'] = monthly_trends['Revenue_Growth_%'].round(2)

print("\n📊 MONTHLY PERFORMANCE TRENDS")
print("="*70)
print(monthly_trends.tail(10))  # Show last 10 months
print("="*70)

# %%
# Revenue and Profit Trend Over Time
fig = make_subplots(
    rows=2, cols=1,
    subplot_titles=('Monthly Revenue & Profit Trend', 'Month-over-Month Growth Rate'),
    specs=[[{"secondary_y": True}], [{"secondary_y": False}]],
    vertical_spacing=0.15
)

# Revenue line
fig.add_trace(
    go.Scatter(x=monthly_trends.index, y=monthly_trends['Revenue'],
               name='Revenue', mode='lines+markers',
               line=dict(color='steelblue', width=3),
               marker=dict(size=8)),
    row=1, col=1, secondary_y=False
)

# Profit line
fig.add_trace(
    go.Scatter(x=monthly_trends.index, y=monthly_trends['Profit'],
               name='Profit', mode='lines+markers',
               line=dict(color='green', width=3),
               marker=dict(size=8)),
    row=1, col=1, secondary_y=True
)

# MoM Growth
colors_growth = ['green' if x >= 0 else 'red' for x in monthly_trends['Revenue_Growth_%']]
fig.add_trace(
    go.Bar(x=monthly_trends.index, y=monthly_trends['Revenue_Growth_%'],
           name='MoM Growth', marker_color=colors_growth,
           text=monthly_trends['Revenue_Growth_%'].apply(lambda x: f'{x:.1f}%' if pd.notna(x) else ''),
           textposition='outside'),
    row=2, col=1
)

# Add zero line to growth chart
fig.add_hline(y=0, line_dash="dash", line_color="black", row=2, col=1)

fig.update_xaxes(title_text="Month", row=1, col=1)
fig.update_xaxes(title_text="Month", row=2, col=1)
fig.update_yaxes(title_text="Revenue (₹)", row=1, col=1, secondary_y=False)
fig.update_yaxes(title_text="Profit (₹)", row=1, col=1, secondary_y=True)
fig.update_yaxes(title_text="Growth Rate (%)", row=2, col=1)

fig.update_layout(
    height=800,
    title_text="<b>Sales Performance Trends Over Time</b>",
    title_x=0.5,
    hovermode='x unified'
)

fig.show()

# %%
# Day of Week Analysis
dow_analysis = df.groupby('Day_of_Week').agg({
    'Revenue': 'sum',
    'Order_ID': 'count',
    'Units_Sold': 'sum'
}).round(2)

# Order days properly
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_analysis = dow_analysis.reindex(day_order)
dow_analysis['AOV'] = (dow_analysis['Revenue'] / dow_analysis['Order_ID']).round(2)

fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Revenue by Day of Week', 'Transaction Volume by Day'),
    specs=[[{'type': 'bar'}, {'type': 'bar'}]]
)

fig.add_trace(
    go.Bar(x=dow_analysis.index, y=dow_analysis['Revenue'],
           marker_color='teal',
           text=dow_analysis['Revenue'].apply(lambda x: f'₹{x/1000:.0f}K'),
           textposition='outside'),
    row=1, col=1
)

fig.add_trace(
    go.Bar(x=dow_analysis.index, y=dow_analysis['Order_ID'],
           marker_color='coral',
           text=dow_analysis['Order_ID'],
           textposition='outside'),
    row=1, col=2
)

fig.update_xaxes(title_text="Day of Week", row=1, col=1)
fig.update_xaxes(title_text="Day of Week", row=1, col=2)
fig.update_yaxes(title_text="Revenue (₹)", row=1, col=1)
fig.update_yaxes(title_text="Transactions", row=1, col=2)

fig.update_layout(
    height=500,
    title_text="<b>Weekly Sales Pattern Analysis</b>",
    title_x=0.5,
    showlegend=False
)

fig.show()

# %%
# Seasonal Analysis by Month
month_analysis = df.groupby('Month_Name').agg({
    'Revenue': 'sum',
    'Profit': 'sum',
    'Order_ID': 'count'
}).round(2)

# Order months properly
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']
month_analysis = month_analysis.reindex([m for m in month_order if m in month_analysis.index])
month_analysis['Profit_Margin_%'] = ((month_analysis['Profit'] / month_analysis['Revenue']) * 100).round(2)

fig = go.Figure()

fig.add_trace(go.Bar(
    x=month_analysis.index,
    y=month_analysis['Revenue'],
    name='Revenue',
    marker_color='skyblue',
    yaxis='y',
    text=month_analysis['Revenue'].apply(lambda x: f'₹{x/1000:.0f}K'),
    textposition='outside'
))

fig.add_trace(go.Scatter(
    x=month_analysis.index,
    y=month_analysis['Profit_Margin_%'],
    name='Profit Margin',
    mode='lines+markers',
    marker=dict(size=10, color='darkgreen'),
    line=dict(width=3, color='darkgreen'),
    yaxis='y2'
))

fig.update_layout(
    title='<b>Seasonal Performance: Revenue and Margin by Month</b>',
    title_x=0.5,
    xaxis=dict(title='Month'),
    yaxis=dict(title='Revenue (₹)', side='left'),
    yaxis2=dict(title='Profit Margin (%)', overlaying='y', side='right'),
    legend=dict(x=0.01, y=0.99),
    height=500,
    hovermode='x unified'
)

fig.show()

# %% [markdown]
# ### 💡 Key Insight: Time-Based Patterns
# 
# **Actionable Title:** *"[FILL: e.g., 'Q4 Revenue Down 22% YoY — Launch Black Friday Campaign 2 Weeks Earlier']"*
# 
# **Monthly Trends:**
# - **Peak Months:** [Months] with ₹[X] average revenue
# - **Low Months:** [Months] with ₹[X] average revenue ([Y]% below peak)
# - **Growth Trajectory:** [Positive/Negative/Flat] with [X]% MoM average growth
# - **Declining Months:** [List months with negative MoM growth]
# 
# **Weekly Patterns:**
# - **Best Days:** [Days] generate [X]% of weekly revenue
# - **Slow Days:** [Days] show [X]% lower transaction volume
# - **Weekend vs Weekday:** [X]% difference in AOV
# 
# **Seasonal Insights:**
# - **High Season:** [Months] - increase inventory by [X]%
# - **Low Season:** [Months] - run promotional campaigns
# - **Margin Patterns:** [Months] have [X]% higher margins (less discounting needed)
# 
# **Recommendations:**
# 1. **Inventory Planning:** 
#    - Increase stock [X]% before [peak months]
#    - Reduce stock [X]% during [low months]
# 2. **Promotion Timing:**
#    - Run major sales during [low months] to boost volume
#    - Minimize discounts during [high months] to maximize margin
# 3. **Staffing Optimization:**
#    - Increase staff on [high-traffic days] by [X]%
#    - Reduce operational hours on [slow days]
# 4. **Campaign Calendar:**
#    - Launch [Product Line] campaign in [Month]
#    - Pre-season sales in [Month] to clear inventory

# %% [markdown]
# ---
# ## 9. Advanced Analytics: High-Value Customer & Loss Analysis {#advanced-analysis}
# 
# ### 🎯 Business Question:
# **"Who are our most profitable customers and what's causing loss-making transactions?"**

# %%
# High-Value Transaction Analysis (Top 20% by Revenue)
revenue_threshold = df['Revenue'].quantile(0.8)
df['High_Value'] = df['Revenue'] >= revenue_threshold

high_value_analysis = df.groupby('High_Value').agg({
    'Revenue': ['sum', 'mean', 'count'],
    'Profit': 'sum',
    'Units_Sold': 'sum'
}).round(2)

high_value_analysis.columns = ['Total_Revenue', 'Avg_Revenue', 'Transaction_Count', 'Total_Profit', 'Units_Sold']
high_value_analysis['Revenue_Contribution_%'] = ((high_value_analysis['Total_Revenue'] / df['Revenue'].sum()) * 100).round(2)

print("\n📊 HIGH-VALUE CUSTOMER ANALYSIS (Top 20%)")
print("="*70)
print(high_value_analysis)
print("="*70)

# %%
# Pareto Chart: Revenue Concentration
fig = go.Figure()

# Calculate cumulative percentage
df_sorted = df.sort_values('Revenue', ascending=False).reset_index(drop=True)
df_sorted['Cumulative_Revenue'] = df_sorted['Revenue'].cumsum()
df_sorted['Cumulative_Pct'] = (df_sorted['Cumulative_Revenue'] / df_sorted['Revenue'].sum()) * 100
df_sorted['Transaction_Pct'] = ((df_sorted.index + 1) / len(df_sorted)) * 100

fig.add_trace(go.Scatter(
    x=df_sorted['Transaction_Pct'],
    y=df_sorted['Cumulative_Pct'],
    mode='lines',
    line=dict(color='steelblue', width=3),
    name='Cumulative Revenue'
))

# Add 80/20 reference lines
fig.add_hline(y=80, line_dash="dash", line_color="red",
              annotation_text="80% Revenue", annotation_position="left")
fig.add_vline(x=20, line_dash="dash", line_color="red",
              annotation_text="20% Transactions", annotation_position="top")

# Shade the area
fig.add_shape(type="rect", x0=0, y0=0, x1=20, y1=80,
              fillcolor="lightgreen", opacity=0.2, line_width=0)

fig.update_layout(
    title='<b>Pareto Analysis: 80/20 Rule — Focus on High-Value Customers</b>',
    title_x=0.5,
    xaxis_title='Cumulative % of Transactions',
    yaxis_title='Cumulative % of Revenue',
    height=500,
    hovermode='x unified'
)

fig.show()

# %%
# Loss Transaction Deep Dive
loss_transactions = df[df['Loss_Flag'] == True]

loss_analysis = loss_transactions.groupby(['Region', 'Product_Line']).agg({
    'Order_ID': 'count',
    'Revenue': 'sum',
    'Profit': 'sum',
    'Discount_Applied': 'mean'
}).round(2)

loss_analysis = loss_analysis.sort_values('Order_ID', ascending=False).head(10)
loss_analysis.columns = ['Loss_Count', 'Revenue', 'Total_Loss', 'Avg_Discount']

print("\n📊 TOP 10 LOSS-MAKING COMBINATIONS (Region × Product)")
print("="*70)
print(loss_analysis)
print("="*70)

# %%
# Loss Transaction Heatmap
loss_pivot = df.pivot_table(
    values='Loss_Flag',
    index='Region',
    columns='Product_Line',
    aggfunc='sum',
    fill_value=0
)

fig = go.Figure(data=go.Heatmap(
    z=loss_pivot.values,
    x=loss_pivot.columns,
    y=loss_pivot.index,
    colorscale='Reds',
    text=loss_pivot.values,
    texttemplate='%{text}',
    textfont={"size": 12},
    colorbar=dict(title="Loss Count")
))

fig.update_layout(
    title='<b>⚠️ Loss Transaction Heatmap: Region × Product Line</b>',
    title_x=0.5,
    xaxis_title='Product Line',
    yaxis_title='Region',
    height=500
)

fig.show()

# %%
# Discount vs Profit Scatter (Loss vs Profitable)
fig = px.scatter(
    df.sample(min(5000, len(df))),  # Sample for performance
    x='Discount_Applied',
    y='Profit',
    color='Loss_Flag',
    color_discrete_map={True: 'red', False: 'green'},
    title='<b>Discount Impact: Profitable vs Loss-Making Transactions</b>',
    labels={'Discount_Applied': 'Discount Applied (%)', 'Profit': 'Profit (₹)', 'Loss_Flag': 'Loss Transaction'},
    opacity=0.6,
    height=600
)

fig.add_hline(y=0, line_dash="dash", line_color="black", annotation_text="Break-even")

fig.update_layout(title_x=0.5)
fig.show()

# %% [markdown]
# ### 💡 Key Insight: High-Value Customers & Loss Prevention
# 
# **Actionable Title:** *"[FILL: e.g., 'Top 20% of Customers Generate 67% Revenue — Launch VIP Loyalty Program']"*
# 
# **High-Value Customer Insights:**
# - **Revenue Concentration:** Top [X]% of transactions generate [Y]% of revenue
# - **Average Transaction:** High-value customers spend ₹[X] vs ₹[Y] for regular customers
# - **Volume:** Only [X] transactions account for [Y]% of total profit
# - **Characteristics:** Primarily from [Region], buying [Product Lines]
# 
# **Loss Transaction Patterns:**
# - **Primary Cause:** [X]% of losses occur when discount > [Y]%
# - **Hotspot:** [Region] + [Product Line] = [X] loss transactions
# - **Average Loss:** ₹[X] per loss transaction, totaling ₹[Y]
# - **Prevention Opportunity:** Eliminating top 10 loss combinations saves ₹[X]
# 
# **Recommendations:**
# 
# **For High-Value Customers:**
# 1. **VIP Program:** Create tiered loyalty (Bronze/Silver/Gold) for top 20%
# 2. **Personalized Service:** Dedicated account managers for ₹[X]+ annual customers
# 3. **Exclusive Access:** Early product launches, limited editions
# 4. **Retention Strategy:** Quarterly check-ins, special birthday offers
# 
# **For Loss Prevention:**
# 1. **Immediate Actions:**
#    - Block discounts > [X]% in [Region] for [Product Line]
#    - Implement manager approval for [specific combinations]
# 2. **System Changes:**
#    - Real-time margin calculator at checkout
#    - Automated alerts when margin < [X]%
# 3. **Policy Updates:**
#    - Maximum discount matrix by Region × Product
#    - Salesperson commission tied to profit, not just revenue
# 4. **Cost Review:**
#    - Investigate [Product Line] costs in [Region]
#    - Negotiate better supplier terms for high-loss items

# %% [markdown]
# ---
# ## 10. Executive Summary & Strategic Recommendations {#recommendations}

# %%
# Generate Final Summary Statistics
summary_stats = {
    'Total Revenue': f"₹{total_revenue:,.0f}",
    'Total Profit': f"₹{total_profit:,.0f}",
    'Overall Margin': f"{overall_margin:.2f}%",
    'Total Transactions': f"{total_transactions:,}",
    'Average Order Value': f"₹{avg_order_value:,.2f}",
    'Loss Transaction Rate': f"{loss_transaction_rate:.2f}%",
    'Top Region': regional_performance.index[0],
    'Top Product': product_performance.index[0],
    'Peak Month': month_analysis['Revenue'].idxmax() if len(month_analysis) > 0 else 'N/A'
}

print("\n" + "="*70)
print("EXECUTIVE SUMMARY - KEY PERFORMANCE INDICATORS")
print("="*70)
for key, value in summary_stats.items():
    print(f"{key:.<30} {value:>30}")
print("="*70)

# %% [markdown]
# ## 📊 Executive Summary
# 
# ### Business Health Score: [Calculate: 0-100 based on margins, growth, loss rate]
# 
# ---
# 
# ## 🎯 TOP 5 KEY FINDINGS
# 
# ### 1. Regional Performance
# **Finding:** *[FILL: e.g., "Mumbai dominates with 35% of revenue, but Delhi has 18% higher profit margins"]*
# 
# **Business Impact:** 
# - Revenue concentration risk in single region
# - Margin optimization opportunity in high-volume markets
# 
# **Action Required:** Replicate Delhi's margin strategy in Mumbai to unlock ₹[X] additional profit
# 
# ---
# 
# ### 2. Product Portfolio Optimization
# **Finding:** *[FILL: e.g., "Footwear generates 45% revenue with 22% margin, while Accessories have 28% margin but only 8% revenue"]*
# 
# **Business Impact:**
# - Underutilized high-margin product line
# - Over-reliance on single product category
# 
# **Action Required:** Increase Accessories marketing budget by [X]% to boost volume while maintaining margins
# 
# ---
# 
# ### 3. Discount Strategy Crisis
# **Finding:** *[FILL: e.g., "Discounts above 30% result in 45% loss rate; 15% of all transactions are unprofitable"]*
# 
# **Business Impact:**
# - ₹[X] in unnecessary profit erosion
# - Margin compression threatening business sustainability
# 
# **Action Required:** Implement immediate 25% discount cap, projected to save ₹[X] annually
# 
# ---
# 
# ### 4. Customer Segmentation Opportunity
# **Finding:** *[FILL: e.g., "Top 20% of customers generate 67% of revenue; Men have 15% higher AOV than Women"]*
# 
# **Business Impact:**
# - High customer concentration = retention risk
# - Untapped potential in different customer segments
# 
# **Action Required:** Launch VIP program for top 20% and gender-specific marketing campaigns
# 
# ---
# 
# ### 5. Seasonal Revenue Volatility
# **Finding:** *[FILL: e.g., "Q4 revenue down 22% YoY; weekends generate 30% more sales than weekdays"]*
# 
# **Business Impact:**
# - Predictable cash flow challenges
# - Inefficient resource allocation
# 
# **Action Required:** Implement counter-seasonal promotions and optimize staffing by day-of-week patterns
# 
# ---
# 
# ## 🚀 STRATEGIC RECOMMENDATIONS
# 
# ### Immediate Actions (Next 30 Days)
# 
# | Priority | Action | Owner | Expected Impact | Cost |
# |----------|--------|-------|-----------------|------|
# | 🔴 **CRITICAL** | Cap maximum discount at 25% | Sales | Save ₹[X]/month | $0 |
# | 🔴 **CRITICAL** | Launch VIP program for top 20% | Marketing | +15% retention | $[X] |
# | 🟠 **HIGH** | Reallocate marketing: +20% to Accessories | Marketing | +₹[X] revenue | $[X] |
# | 🟠 **HIGH** | Implement margin calculator at POS | IT | Reduce loss rate by 50% | $[X] |
# 
# ### Short-Term Initiatives (60-90 Days)
# 
# 1. **Product Strategy**
#    - Expand [high-margin product] inventory by 25%
#    - Phase out [low-margin product] from [underperforming region]
#    - Launch bundle deals: [Product A] + [Product B] at 15% discount
# 
# 2. **Regional Expansion**
#    - Open pop-up stores in [high-potential region]
#    - Test premium pricing strategy in [high-AOV region]
#    - Investigate [low-margin region] operational costs
# 
# 3. **Customer Retention**
#    - Implement tiered loyalty program (Bronze/Silver/Gold)
#    - Launch gender-specific email campaigns
#    - Create refer-a-friend program with ₹[X] credit
# 
# 4. **Operational Efficiency**
#    - Adjust staffing: +30% on weekends, -20% on [slow days]
#    - Automate inventory reordering for top 20 SKUs
#    - Implement dynamic pricing for [specific products]
# 
# ### Long-Term Strategy (6-12 Months)
# 
# 1. **Market Expansion**
#    - Enter [new region] with pilot program
#    - Launch e-commerce platform to reach beyond current 5 cities
#    - Partnership with [complementary brand] for co-marketing
# 
# 2. **Data Infrastructure**
#    - Implement real-time dashboard for daily KPI tracking
#    - Build predictive model for demand forecasting
#    - Customer segmentation ML model for personalized marketing
# 
# 3. **Product Innovation**
#    - Develop private label line with 35%+ margins
#    - Launch subscription box service for loyal customers
#    - Expand into [adjacent product category]
# 
# ---
# 
# ## 💰 PROJECTED FINANCIAL IMPACT (12-Month)
# 
# | Initiative | Revenue Impact | Margin Impact | Total Profit Impact |
# |------------|----------------|---------------|---------------------|
# | Discount optimization | -5% revenue | +3% margin | +₹[X] |
# | VIP program | +8% revenue | +1% margin | +₹[X] |
# | Product mix shift | +3% revenue | +2% margin | +₹[X] |
# | Regional expansion | +12% revenue | 0% margin | +₹[X] |
# | **TOTAL PROJECTED** | **+18% revenue** | **+6% margin** | **+₹[X]** |
# 
# ---
# 
# ## ⚠️ RISKS & MITIGATION
# 
# ### Risk 1: Customer Backlash from Discount Reduction
# **Mitigation:** 
# - Phase in discount caps over 3 months
# - Replace discounts with value-adds (free shipping, loyalty points)
# - Communicate "everyday low prices" instead of heavy promotions
# 
# ### Risk 2: Revenue Dip During Strategy Shift
# **Mitigation:**
# - Maintain 90-day cash reserve
# - Start with pilot programs in [low-risk region]
# - Monitor daily KPIs with clear rollback triggers
# 
# ### Risk 3: Competition Response
# **Mitigation:**
# - Focus on differentiation (quality, service) vs price wars
# - Build customer loyalty before competitors react
# - Patent/trademark unique product innovations
# 
# ---
# 
# ## 📈 SUCCESS METRICS & MONITORING
# 
# ### Weekly KPIs to Track:
# - [ ] Revenue vs target (±5% tolerance)
# - [ ] Profit margin (target: [X]%)
# - [ ] Loss transaction rate (target: <10%)
# - [ ] Average Order Value trend
# - [ ] Top 20% customer retention rate
# 
# ### Monthly Review:
# - [ ] Regional performance variance analysis
# - [ ] Product line profitability review
# - [ ] Discount compliance audit
# - [ ] Customer segmentation analysis
# - [ ] Competitive landscape assessment
# 
# ### Quarterly Business Review:
# - [ ] Strategic initiative progress
# - [ ] Financial projections vs actuals
# - [ ] Market expansion readiness
# - [ ] Technology roadmap updates
# - [ ] Organizational capability assessment
# 
# ---
# 
# ## 🎓 LESSONS LEARNED & BEST PRACTICES
# 
# ### What Worked:
# 1. Data-driven decision making revealed hidden profit leaks
# 2. Customer segmentation uncovered high-value opportunities
# 3. Regional analysis exposed margin optimization potential
# 
# ### What Didn't Work:
# 1. Excessive discounting eroded margins without sustainable volume gains
# 2. One-size-fits-all strategy missed regional nuances
# 3. Lack of real-time monitoring delayed corrective actions
# 
# ### Best Practices Going Forward:
# 1. **Profit-First Mindset:** Revenue growth without margin is unsustainable
# 2. **Customer Lifetime Value:** Focus on retention over acquisition
# 3. **Data-Driven Culture:** Weekly KPI reviews, rapid experimentation
# 4. **Regional Customization:** Tailor strategies to local market dynamics
# 5. **Continuous Optimization:** Monthly strategy reviews, quarterly pivots
# 
# ---
# 
# ## 📞 NEXT STEPS
# 
# ### Week 1:
# - [ ] Present findings to executive team
# - [ ] Get approval for immediate action items
# - [ ] Form cross-functional task force
# 
# ### Week 2-4:
# - [ ] Implement discount cap system
# - [ ] Launch VIP program pilot
# - [ ] Begin marketing budget reallocation
# 
# ### Month 2
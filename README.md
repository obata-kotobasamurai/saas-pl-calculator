# SaaS P&L Calculator

Interactive web app for modeling your SaaS P&L and projecting the path to ¥100M ARR in 3 years.

## Features

- **Dynamic Pricing**: Adjust prices for Small, Mid, and Enterprise customer segments
- **Team Planning**: Configure headcount by role for each year
- **Sales Modeling**: Set deals per rep, win rates, and sales cycles
- **Interactive Visualizations**: Real-time charts showing revenue, profitability, and customer growth
- **Unit Economics**: Automatic CAC, LTV, and LTV:CAC calculations
- **Scenario Planning**: Instantly see impact of any assumption changes

## Quick Start

### 1. Install Dependencies

```bash
cd saas-pl-calculator
pip3 install -r requirements.txt
```

### 2. Run the App

```bash
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## How to Use

### Sidebar Controls

**Pricing Strategy**:
- Adjust annual contract values for each customer segment
- Set implementation fee percentage

**Customer Mix**:
- Define what % of customers fall into each segment

**Sales Assumptions**:
- Deals closed per sales rep per quarter
- Win rate and sales cycle length

**Team Size**:
- Configure headcount for Sales, CS, Engineering, and G&A for each year
- Set annual compensation per role

**Retention Metrics**:
- Monthly churn rate
- Annual expansion rate (upsells/cross-sells)

**Other Costs**:
- Monthly overhead (office, tools, etc.)
- COGS as % of revenue

### Dashboard Tabs

1. **Revenue Projections**: ARR growth chart with ¥100M goal line
2. **P&L Statement**: Quarterly revenue vs costs, margin trends
3. **Customers & Unit Economics**: Customer growth, CAC, LTV, LTV:CAC
4. **Summary Table**: Annual and monthly breakdowns

## Business Model Assumptions

This calculator is optimized for **high-touch enterprise SaaS** with:
- Heavy customization per customer
- Continuous customer success engagement
- Sales-led growth (not PLG)
- Long sales cycles (3-6 months typical)
- High ACV, high touch model (similar to Palantir)

## Tips

- Start conservative, then create optimistic scenarios
- For enterprise SaaS, typical targets:
  - LTV:CAC ratio > 3x
  - CAC payback < 12 months
  - Gross margin > 70%
  - Net retention > 100%
- Adjust team hiring based on customer load (e.g., 1 CS per 10-20 customers)

## Customization

The app is built with clean Python code. Easy to extend:
- Modify `app.py` to add new metrics or visualizations
- All calculations are in the `calculate_pl()` function
- Uses Plotly for interactive charts (easily customizable)

## Next Steps

- Run different scenarios (conservative/moderate/aggressive)
- Export data for board presentations
- Iterate on pricing strategy based on market feedback
- Refine team hiring plan as you learn CAC and close rates

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# Page config
st.set_page_config(page_title="SaaS P&L 計算機", layout="wide", initial_sidebar_state="expanded")

# Title
st.title("🚀 SaaS P&L 計算機")
st.markdown("**目標: 3年で年間経常収益（ARR）1億円**")
st.markdown("---")

# Sidebar for inputs
st.sidebar.header("📊 設定")

# === FOUNDERS SECTION ===
st.sidebar.subheader("👨‍💼 創業者")
num_founders = st.sidebar.number_input("創業者数", min_value=1, max_value=10, value=2, step=1)
founder_salary = 1_000_000  # Fixed at ¥1M per year
st.sidebar.write(f"創業者報酬: ¥{founder_salary:,}/年/人 (固定)")
st.sidebar.write(f"創業者もセールス活動を行います")

# === PRICING SECTION ===
st.sidebar.subheader("💰 価格戦略")

small_price = st.sidebar.slider(
    "スモール顧客（年間契約額）",
    min_value=500_000,
    max_value=5_000_000,
    value=1_500_000,
    step=100_000,
    format="¥%d"
)

mid_price = st.sidebar.slider(
    "ミドル顧客（年間契約額）",
    min_value=2_000_000,
    max_value=15_000_000,
    value=5_000_000,
    step=500_000,
    format="¥%d"
)

enterprise_price = st.sidebar.slider(
    "エンタープライズ顧客（年間契約額）",
    min_value=10_000_000,
    max_value=50_000_000,
    value=20_000_000,
    step=1_000_000,
    format="¥%d"
)

implementation_fee_pct = st.sidebar.slider(
    "導入費用（ACVに対する%）",
    min_value=0,
    max_value=100,
    value=30,
    step=5,
    format="%d%%"
)

# === CUSTOMER MIX ===
st.sidebar.subheader("👥 顧客構成")
small_mix = st.sidebar.slider("スモール顧客 %", 0, 100, 50, 5)
mid_mix = st.sidebar.slider("ミドル顧客 %", 0, 100, 35, 5)
enterprise_mix = 100 - small_mix - mid_mix
st.sidebar.write(f"エンタープライズ: {enterprise_mix}%")

# === SALES ASSUMPTIONS ===
st.sidebar.subheader("📈 セールス前提")

deals_per_rep_q = st.sidebar.slider(
    "1人あたり四半期受注数",
    min_value=1,
    max_value=10,
    value=3,
    step=1
)

# === TEAM SIZE ===
st.sidebar.subheader("👔 年度別チーム規模")
st.sidebar.write("※創業者除く追加採用人数")

col1, col2, col3 = st.sidebar.columns(3)
with col1:
    st.write("**1年目**")
    sales_y1 = st.number_input("営業", 0, 50, 0, key="sales_y1")
    cs_y1 = st.number_input("CS", 0, 50, 0, key="cs_y1")
    eng_y1 = st.number_input("エンジニア", 0, 50, 2, key="eng_y1")
    ga_y1 = st.number_input("管理", 0, 20, 0, key="ga_y1")

with col2:
    st.write("**2年目**")
    sales_y2 = st.number_input("営業", 0, 50, 2, key="sales_y2")
    cs_y2 = st.number_input("CS", 0, 50, 2, key="cs_y2")
    eng_y2 = st.number_input("エンジニア", 0, 50, 4, key="eng_y2")
    ga_y2 = st.number_input("管理", 0, 20, 1, key="ga_y2")

with col3:
    st.write("**3年目**")
    sales_y3 = st.number_input("営業", 0, 50, 4, key="sales_y3")
    cs_y3 = st.number_input("CS", 0, 50, 4, key="cs_y3")
    eng_y3 = st.number_input("エンジニア", 0, 50, 6, key="eng_y3")
    ga_y3 = st.number_input("管理", 0, 20, 2, key="ga_y3")

# === COMPENSATION ===
st.sidebar.subheader("💴 年間給与（役職別）")
sales_comp = st.sidebar.number_input("営業担当 (¥)", 5_000_000, 20_000_000, 8_000_000, 500_000)
cs_comp = st.sidebar.number_input("CSマネージャー (¥)", 4_000_000, 15_000_000, 6_000_000, 500_000)
eng_comp = st.sidebar.number_input("エンジニア (¥)", 6_000_000, 20_000_000, 9_000_000, 500_000)
ga_comp = st.sidebar.number_input("管理部門 (¥)", 4_000_000, 15_000_000, 6_000_000, 500_000)

# === CHURN & EXPANSION ===
st.sidebar.subheader("📉 リテンション指標")
monthly_churn = st.sidebar.slider("月次解約率 %", 0.0, 10.0, 2.0, 0.5)
annual_expansion = st.sidebar.slider("年間拡張率 %", 0, 50, 10, 5)

# === OTHER COSTS ===
st.sidebar.subheader("💸 その他コスト")
monthly_overhead = st.sidebar.number_input("月次固定費 (¥)", 0, 5_000_000, 500_000, 100_000)
cogs_pct = st.sidebar.slider("売上原価（売上に対する%）", 0, 50, 15, 5)

# ============================================
# CALCULATION ENGINE
# ============================================

def calculate_pl():
    """Calculate monthly P&L for 36 months"""

    months = 36
    data = []

    # Calculate blended ACV
    blended_acv = (
        small_price * (small_mix / 100) +
        mid_price * (mid_mix / 100) +
        enterprise_price * (enterprise_mix / 100)
    )

    # Team by month
    team_by_month = []
    for month in range(months):
        year = month // 12
        if year == 0:
            team = {'sales': sales_y1, 'cs': cs_y1, 'eng': eng_y1, 'ga': ga_y1}
        elif year == 1:
            team = {'sales': sales_y2, 'cs': cs_y2, 'eng': eng_y2, 'ga': ga_y2}
        else:
            team = {'sales': sales_y3, 'cs': cs_y3, 'eng': eng_y3, 'ga': ga_y3}
        team_by_month.append(team)

    # Initialize
    active_customers = 0
    mrr = 0
    total_customers_acquired = 0

    for month in range(months):
        quarter = month // 3

        # New customers this month (deals close at end of quarter)
        # Founders also do sales, so total sales people = hired sales + founders
        new_customers = 0
        if month % 3 == 2:  # End of quarter
            team = team_by_month[month]
            total_sales_people = team['sales'] + num_founders
            new_customers = total_sales_people * deals_per_rep_q
            total_customers_acquired += new_customers

        # Churn
        churned_customers = active_customers * (monthly_churn / 100)

        # Net customers
        active_customers = active_customers - churned_customers + new_customers

        # MRR calculation
        mrr_from_new = new_customers * (blended_acv / 12)
        mrr_churn = churned_customers * (blended_acv / 12)

        # Expansion (annual, so 1/12 per month)
        mrr_expansion = mrr * (annual_expansion / 100 / 12) if month > 0 else 0

        mrr = mrr - mrr_churn + mrr_from_new + mrr_expansion
        mrr = max(0, mrr)  # No negative MRR

        arr = mrr * 12

        # Implementation fees (one-time)
        impl_fees = new_customers * blended_acv * (implementation_fee_pct / 100)

        # Total revenue
        total_revenue = mrr + impl_fees

        # Costs
        team = team_by_month[month]
        personnel_costs = (
            team['sales'] * sales_comp / 12 +
            team['cs'] * cs_comp / 12 +
            team['eng'] * eng_comp / 12 +
            team['ga'] * ga_comp / 12 +
            num_founders * founder_salary / 12  # Add founder compensation
        )

        cogs = mrr * (cogs_pct / 100)
        total_costs = personnel_costs + cogs + monthly_overhead

        # Profit
        gross_profit = total_revenue - cogs
        operating_profit = total_revenue - total_costs

        gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        operating_margin = (operating_profit / total_revenue * 100) if total_revenue > 0 else 0

        data.append({
            'month': month + 1,
            'year': (month // 12) + 1,
            'quarter': f"Y{(month // 12) + 1}Q{(month % 12 // 3) + 1}",
            'new_customers': new_customers,
            'churned_customers': churned_customers,
            'active_customers': active_customers,
            'mrr': mrr,
            'arr': arr,
            'impl_fees': impl_fees,
            'total_revenue': total_revenue,
            'cogs': cogs,
            'personnel_costs': personnel_costs,
            'overhead': monthly_overhead,
            'total_costs': total_costs,
            'gross_profit': gross_profit,
            'operating_profit': operating_profit,
            'gross_margin': gross_margin,
            'operating_margin': operating_margin,
            'team_size': team['sales'] + team['cs'] + team['eng'] + team['ga'] + num_founders
        })

    return pd.DataFrame(data)

# Calculate
df = calculate_pl()

# ============================================
# DISPLAY RESULTS
# ============================================

# Key Metrics
col1, col2, col3, col4 = st.columns(4)

final_arr = df.iloc[-1]['arr']
year3_arr = df[df['year'] == 3]['arr'].iloc[-1]
goal_pct = (year3_arr / 100_000_000) * 100

with col1:
    st.metric("3年目のARR", f"¥{year3_arr/1_000_000:.1f}M", f"目標の{goal_pct:.0f}%")
with col2:
    st.metric("最終MRR", f"¥{df.iloc[-1]['mrr']/1_000_000:.1f}M")
with col3:
    final_customers = df.iloc[-1]['active_customers']
    st.metric("アクティブ顧客数（3年目終了時）", f"{final_customers:.0f}")
with col4:
    final_margin = df.iloc[-1]['operating_margin']
    st.metric("営業利益率（最終）", f"{final_margin:.1f}%")

st.markdown("---")

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📈 売上予測", "💰 損益計算書", "👥 顧客・ユニットエコノミクス", "📊 サマリーテーブル"])

with tab1:
    st.subheader("3年間のARR成長")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['month'],
        y=df['arr'],
        mode='lines',
        name='ARR',
        line=dict(color='#00CC96', width=3),
        fill='tozeroy'
    ))

    # Add goal line
    fig.add_hline(y=100_000_000, line_dash="dash", line_color="red",
                  annotation_text="目標 ¥100M", annotation_position="right")

    fig.update_layout(
        xaxis_title="月",
        yaxis_title="ARR (¥)",
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    # MRR vs Implementation Fees
    st.subheader("月次売上内訳")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=df['month'], y=df['mrr'], name='MRR', marker_color='lightblue'))
    fig2.add_trace(go.Bar(x=df['month'], y=df['impl_fees'], name='導入費用', marker_color='orange'))
    fig2.update_layout(barmode='stack', height=400, xaxis_title="月", yaxis_title="売上 (¥)")
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("収益性分析")

    # Quarterly summary
    quarterly = df.groupby('quarter').agg({
        'total_revenue': 'sum',
        'total_costs': 'sum',
        'operating_profit': 'sum'
    }).reset_index()

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=quarterly['quarter'], y=quarterly['total_revenue'],
                          name='売上', marker_color='green'))
    fig3.add_trace(go.Bar(x=quarterly['quarter'], y=quarterly['total_costs'],
                          name='費用', marker_color='red'))
    fig3.add_trace(go.Scatter(x=quarterly['quarter'], y=quarterly['operating_profit'],
                              name='営業利益', mode='lines+markers',
                              line=dict(color='blue', width=3)))

    fig3.update_layout(height=400, xaxis_title="四半期", yaxis_title="金額 (¥)")
    st.plotly_chart(fig3, use_container_width=True)

    # Margin trend
    st.subheader("利益率推移")
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=df['month'], y=df['gross_margin'],
                              name='粗利率 %', mode='lines', line=dict(color='green')))
    fig4.add_trace(go.Scatter(x=df['month'], y=df['operating_margin'],
                              name='営業利益率 %', mode='lines', line=dict(color='blue')))
    fig4.update_layout(height=400, xaxis_title="月", yaxis_title="利益率 %")
    st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.subheader("顧客数の成長")

    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(x=df['month'], y=df['active_customers'],
                              mode='lines', name='アクティブ顧客数',
                              line=dict(color='purple', width=3), fill='tozeroy'))
    fig5.update_layout(height=400, xaxis_title="月", yaxis_title="顧客数")
    st.plotly_chart(fig5, use_container_width=True)

    # Unit Economics
    st.subheader("ユニットエコノミクス")
    col1, col2, col3 = st.columns(3)

    # Calculate CAC
    total_sales_cost = df['personnel_costs'].sum() * (sales_y1 + sales_y2 + sales_y3 + num_founders * 3) / (3 * (sales_y1 + sales_y2 + sales_y3 + cs_y1 + cs_y2 + cs_y3 + eng_y1 + eng_y2 + eng_y3 + ga_y1 + ga_y2 + ga_y3 + num_founders))
    total_customers = df['new_customers'].sum()
    cac = total_sales_cost / total_customers if total_customers > 0 else 0

    # Blended ACV
    blended_acv = (
        small_price * (small_mix / 100) +
        mid_price * (mid_mix / 100) +
        enterprise_price * (enterprise_mix / 100)
    )

    # LTV (simplified)
    avg_customer_lifetime_months = 1 / (monthly_churn / 100) if monthly_churn > 0 else 60
    ltv = (blended_acv / 12) * avg_customer_lifetime_months

    with col1:
        st.metric("ブレンドACV", f"¥{blended_acv/1_000_000:.2f}M")
    with col2:
        st.metric("推定CAC", f"¥{cac/1_000_000:.2f}M")
    with col3:
        ltv_cac = ltv / cac if cac > 0 else 0
        st.metric("LTV:CAC比率", f"{ltv_cac:.1f}x")

with tab4:
    st.subheader("年次サマリー")

    annual = df.groupby('year').agg({
        'new_customers': 'sum',
        'active_customers': 'last',
        'arr': 'last',
        'total_revenue': 'sum',
        'total_costs': 'sum',
        'operating_profit': 'sum',
        'team_size': 'last'
    }).reset_index()

    annual['operating_margin_%'] = (annual['operating_profit'] / annual['total_revenue'] * 100).round(1)
    annual['arr'] = (annual['arr'] / 1_000_000).round(1)
    annual['total_revenue'] = (annual['total_revenue'] / 1_000_000).round(1)
    annual['total_costs'] = (annual['total_costs'] / 1_000_000).round(1)
    annual['operating_profit'] = (annual['operating_profit'] / 1_000_000).round(1)

    annual.columns = ['年', '新規顧客数', 'アクティブ顧客数（期末）', 'ARR (¥M)',
                      '売上 (¥M)', '費用 (¥M)', '営業利益 (¥M)', 'チーム規模', '営業利益率 %']

    st.dataframe(annual, use_container_width=True, hide_index=True)

    # Full monthly table (expandable)
    with st.expander("月次データ詳細を表示"):
        display_df = df[['month', 'quarter', 'new_customers', 'active_customers',
                         'mrr', 'arr', 'total_revenue', 'total_costs', 'operating_profit',
                         'operating_margin']].copy()
        display_df['mrr'] = (display_df['mrr'] / 1_000_000).round(2)
        display_df['arr'] = (display_df['arr'] / 1_000_000).round(2)
        display_df['total_revenue'] = (display_df['total_revenue'] / 1_000_000).round(2)
        display_df['total_costs'] = (display_df['total_costs'] / 1_000_000).round(2)
        display_df['operating_profit'] = (display_df['operating_profit'] / 1_000_000).round(2)
        display_df['operating_margin'] = display_df['operating_margin'].round(1)

        display_df.columns = ['月', '四半期', '新規顧客', 'アクティブ顧客',
                              'MRR (¥M)', 'ARR (¥M)', '売上 (¥M)', '費用 (¥M)',
                              '営業利益 (¥M)', '営業利益率 %']

        st.dataframe(display_df, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown("💡 **ヒント**: サイドバーのスライダーを調整して、各種前提条件が1億円ARR達成にどう影響するか確認できます")

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# --- 页面配置 ---
st.set_page_config(page_title="保险方案对比神器", page_icon="🛡️", layout="wide")

# --- 侧边栏：客户与产品信息 ---
st.sidebar.title("🛡️  E&S Agency 工具箱")

# 1. 新增：客户资料录入
st.sidebar.header("👤 客户档案 (Client Profile)")
client_name = st.sidebar.text_input("客户姓名", placeholder="例如: Mr. Frankeez")
client_age = st.sidebar.number_input("客户年龄", min_value=0, max_value=100, value=30)
client_gender = st.sidebar.selectbox("性别", ["男", "女"])
consultant_name = st.sidebar.text_input("顾问名字", value="Frankeez Lee")

st.sidebar.markdown("---")

# 2. 保单数据输入
st.sidebar.header("📝 输入保单信息")

def user_input_features(label_suffix):
    st.sidebar.subheader(f"方案 {label_suffix}")
    # 让用户可以输入具体的产品名，例如 "HealthAssured"
    default_name = f"Allianz 方案 {label_suffix}"
    name = st.sidebar.text_input(f"产品名称 ({label_suffix})", value=default_name, key=f"name_{label_suffix}")
    type_ = st.sidebar.selectbox(f"险种类型 ({label_suffix})", ["医疗卡 (Medical)", "人寿 (Life)", "重疾 (CI)", "储蓄 (Savings)"], key=f"type_{label_suffix}")
    
    premium = st.sidebar.number_input(f"年缴保费 RM ({label_suffix})", min_value=0, value=3000, key=f"prem_{label_suffix}")
    years = st.sidebar.number_input(f"缴费年限 ({label_suffix})", min_value=1, value=20, key=f"year_{label_suffix}")
    coverage = st.sidebar.number_input(f"保障额度 RM ({label_suffix})", min_value=0, value=500000, help="可以是年度限额或人寿保额", key=f"cov_{label_suffix}")
    cash_value = st.sidebar.number_input(f"预估现金价值/无理赔奖励 RM ({label_suffix})", min_value=0, value=0, help="填入Cash Value 或 NCB", key=f"cv_{label_suffix}")
    
    # 新增：产品特色备注 (用于记录图片里的那些亮点)
    remarks = st.sidebar.text_area(f"特色/备注 ({label_suffix})", height=100, placeholder="例如: 20% Co-insurance 折扣, 基因测试...", key=f"rem_{label_suffix}")
    
    total_cost = premium * years
    return name, type_, premium, years, total_cost, coverage, cash_value, remarks

# 获取两份保单的数据
name_a, type_a, prem_a, year_a, total_a, cov_a, cv_a, rem_a = user_input_features("A")
st.sidebar.markdown("---")
name_b, type_b, prem_b, year_b, total_b, cov_b, cv_b, rem_b = user_input_features("B")

# --- 主界面：分析报告 ---

# 动态标题
title_text = f"为 {client_name} 定制的保障分析报告" if client_name else "智能保单对比分析"
st.title(f"📊 {title_text}")
st.caption(f"顾问: {consultant_name} | 日期: {datetime.now().strftime('%Y-%m-%d')}")
st.markdown("---")

# 1. 核心数据对比卡片
col1, col2 = st.columns(2)

with col1:
    st.info(f"📋 **{name_a}**")
    st.metric("总投入成本", f"RM {total_a:,.0f}", delta=f"年缴 RM {prem_a:,.0f}")
    st.metric("保障额度 (Limit/Sum Assured)", f"RM {cov_a:,.0f}")
    if rem_a:
        st.markdown(f"**亮点:** {rem_a}")

with col2:
    st.success(f"📋 **{name_b}**")
    st.metric("总投入成本", f"RM {total_b:,.0f}", delta=f"年缴 RM {prem_b:,.0f}")
    st.metric("保障额度 (Limit/Sum Assured)", f"RM {cov_b:,.0f}")
    if rem_b:
        st.markdown(f"**亮点:** {rem_b}")

st.markdown("---")

# 2. 详细对比表格
st.subheader("🔎 详细参数横向测评")

# 计算数据
profit_a = cv_a - (prem_a * min(20, year_a))
profit_b = cv_b - (prem_b * min(20, year_b))

comparison_data = {
    "对比维度": ["产品类型", "缴费年限", "年缴保费", "累计总保费", "保障额度", "现金价值/奖励", "特色备注"],
    f"{name_a}": [type_a, f"{year_a} 年", f"RM {prem_a:,.0f}", f"RM {total_a:,.0f}", f"RM {cov_a:,.0f}", f"RM {cv_a:,.0f}", rem_a],
    f"{name_b}": [type_b, f"{year_b} 年", f"RM {prem_b:,.0f}", f"RM {total_b:,.0f}", f"RM {cov_b:,.0f}", f"RM {cv_b:,.0f}", rem_b]
}

df = pd.DataFrame(comparison_data)
st.table(df)

# 3. 可视化分析
st.subheader("📈 视觉化分析")
tab1, tab2 = st.tabs(["💰 资金与保障", "🕸️ 综合优势雷达"])

with tab1:
    chart_data = pd.DataFrame({
        "方案": [name_a, name_a, name_b, name_b],
        "类型": ["总保费 (Cost)", "保障额度 (Cover)", "总保费 (Cost)", "保障额度 (Cover)"],
        "金额": [total_a, cov_a, total_b, cov_b]
    })
    fig_bar = px.bar(chart_data, x="方案", y="金额", color="类型", barmode="group", 
                     title="投入 vs 保障 (RM)", text_auto='.2s', color_discrete_sequence=["#FF6B6B", "#4ECDC4"])
    st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    # 简单的雷达图评分逻辑
    max_prem = max(prem_a, prem_b) if max(prem_a, prem_b) > 0 else 1
    max_cov = max(cov_a, cov_b) if max(cov_a, cov_b) > 0 else 1
    
    def get_score(val, max_val, is_cost=False):
        if is_cost: return (1 - (val / max_val)) * 100 if max_val > 0 else 0
        return (val / max_val) * 100
    
    categories = ['保费优势(越低越好)', '保障额度', '现金价值/奖励', '缴费轻松度']
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=[
        get_score(prem_a, max_prem, is_cost=True), get_score(cov_a, max_cov), 50, get_score(30-year_a, 30)
    ], theta=categories, fill='toself', name=name_a))
    
    fig_radar.add_trace(go.Scatterpolar(r=[
        get_score(prem_b, max_prem, is_cost=True), get_score(cov_b, max_cov), 80, get_score(30-year_b, 30)
    ], theta=categories, fill='toself', name=name_b))
    
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
    st.plotly_chart(fig_radar, use_container_width=True)

# --- 保存功能 ---
st.markdown("---")
st.subheader("💾 保存客户档案")

# 准备下载数据
csv = df.to_csv(index=False).encode('utf-8')
file_name_clean = f"{client_name}_保单分析.csv" if client_name else "保单分析_E&S.csv"

st.download_button(
    label="📥 下载分析报告 (Excel/CSV)",
    data=csv,
    file_name=file_name_clean,
    mime='text/csv',
    help="点击下载将数据保存到您的设备"
)

st.caption("Frankeez Lee  | Powered by Python Streamlit")

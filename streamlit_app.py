import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 页面配置 ---
st.set_page_config(page_title="保险方案对比神器", page_icon="🛡️", layout="wide")

# --- 标题与简介 ---
st.title("🛡️ 智能保单对比分析工具")
st.markdown("### 为客户清晰展示两份方案的核心差异")
st.markdown("---")

# --- 侧边栏：数据输入 ---
st.sidebar.header("📝 输入保单信息")

def user_input_features(label_suffix):
    st.sidebar.subheader(f"保单 {label_suffix} 信息")
    name = st.sidebar.text_input(f"产品名称 ({label_suffix})", value=f"方案 {label_suffix}")
    type_ = st.sidebar.selectbox(f"险种类型 ({label_suffix})", ["定期寿险", "终身寿险", "重疾险", "储蓄/年金险"], key=f"type_{label_suffix}")
    # 注意：这里的默认值改为了常见的马币数值，你可以自己调整
    premium = st.sidebar.number_input(f"年缴保费 ({label_suffix})", min_value=0, value=3000, key=f"prem_{label_suffix}")
    years = st.sidebar.number_input(f"缴费年限 ({label_suffix})", min_value=1, value=20, key=f"year_{label_suffix}")
    coverage = st.sidebar.number_input(f"身故/重疾保额 ({label_suffix})", min_value=0, value=500000, key=f"cov_{label_suffix}")
    cash_value_20 = st.sidebar.number_input(f"第20年预估现金价值 ({label_suffix})", min_value=0, value=0, help="查阅计划书利益演示表", key=f"cv_{label_suffix}")
    
    # 计算总投入
    total_cost = premium * years
    return name, type_, premium, years, total_cost, coverage, cash_value_20

# 获取两份保单的数据
name_a, type_a, prem_a, year_a, total_a, cov_a, cv_a = user_input_features("A")
st.sidebar.markdown("---")
name_b, type_b, prem_b, year_b, total_b, cov_b, cv_b = user_input_features("B")

# --- 主界面：数据展示 ---

# 1. 核心数据对比卡片
col1, col2 = st.columns(2)

with col1:
    st.info(f"📋 **{name_a}**")
    st.metric("总投入成本", f"RM {total_a:,.0f}", delta=f"每年缴 RM {prem_a:,.0f}")
    st.metric("基础保额", f"RM {cov_a:,.0f}")
    # 避免除以0的错误
    leverage = cov_a/total_a if total_a > 0 else 0
    st.metric("杠杆倍数 (保额/总保费)", f"{leverage:.1f} 倍")

with col2:
    st.success(f"📋 **{name_b}**")
    st.metric("总投入成本", f"RM {total_b:,.0f}", delta=f"每年缴 RM {prem_b:,.0f}")
    st.metric("基础保额", f"RM {cov_b:,.0f}")
    leverage_b = cov_b/total_b if total_b > 0 else 0
    st.metric("杠杆倍数 (保额/总保费)", f"{leverage_b:.1f} 倍")

st.markdown("---")

# 2. 详细对比表格
st.subheader("📊 详细参数横向测评")

# 计算第20年的简单盈亏
profit_a = cv_a - (prem_a * min(20, year_a))
profit_b = cv_b - (prem_b * min(20, year_b))

comparison_data = {
    "对比维度": ["险种类型", "缴费年限", "年缴保费", "累计总保费", "基础保额", "第20年现金价值", "净收益/成本 (第20年)"],
    f"{name_a}": [
        type_a, 
        f"{year_a} 年", 
        f"RM {prem_a:,.0f}", 
        f"RM {total_a:,.0f}", 
        f"RM {cov_a:,.0f}", 
        f"RM {cv_a:,.0f}",
        f"RM {profit_a:,.0f}" 
    ],
    f"{name_b}": [
        type_b, 
        f"{year_b} 年", 
        f"RM {prem_b:,.0f}", 
        f"RM {total_b:,.0f}", 
        f"RM {cov_b:,.0f}", 
        f"RM {cv_b:,.0f}",
        f"RM {profit_b:,.0f}"
    ]
}

df = pd.DataFrame(comparison_data)
st.table(df)

# 3. 可视化图表
st.subheader("📈 视觉化分析")

tab1, tab2 = st.tabs(["💰 投入与保障对比", "🕸️ 综合能力雷达图"])

with tab1:
    # 柱状图数据准备
    chart_data = pd.DataFrame({
        "方案": [name_a, name_a, name_b, name_b],
        "类型": ["总保费 (成本)", "基础保额 (保障)", "总保费 (成本)", "基础保额 (保障)"],
        "金额": [total_a, cov_a, total_b, cov_b]
    })
    
    fig_bar = px.bar(chart_data, x="方案", y="金额", color="类型", barmode="group", 
                     title="投入成本 vs 保障额度 (RM)", text_auto='.2s',
                     color_discrete_sequence=["#FF6B6B", "#4ECDC4"])
    st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    # 雷达图数据
    max_prem = max(prem_a, prem_b) if max(prem_a, prem_b) > 0 else 1
    max_cov = max(cov_a, cov_b) if max(cov_a, cov_b) > 0 else 1
    max_cv = max(cv_a, cv_b) if max(cv_a, cv_b) > 0 else 1
    
    def get_score(val, max_val, is_cost=False):
        if is_cost:
            return (1 - (val / max_val)) * 100 if max_val > 0 else 0
        return (val / max_val) * 100
    
    # 重新计算杠杆率用于评分
    lev_a = cov_a/total_a if total_a > 0 else 0
    lev_b = cov_b/total_b if total_b > 0 else 0
    max_lev = max(lev_a, lev_b) if max(lev_a, lev_b) > 0 else 1

    categories = ['低保费优势', '高保额优势', '现金价值', '杠杆率', '缴费轻松度']
    
    fig_radar = go.Figure()
    
    fig_radar.add_trace(go.Scatterpolar(
        r=[
            get_score(prem_a, max_prem, is_cost=True),
            get_score(cov_a, max_cov),
            get_score(cv_a, max_cv),
            get_score(lev_a, max_lev), 
            get_score(30-year_a, 30) 
        ],
        theta=categories,
        fill='toself',
        name=name_a
    ))
    
    fig_radar.add_trace(go.Scatterpolar(
        r=[
            get_score(prem_b, max_prem, is_cost=True),
            get_score(cov_b, max_cov),
            get_score(cv_b, max_cv),
            get_score(lev_b, max_lev),
            get_score(30-year_b, 30)
        ],
        theta=categories,
        fill='toself',
        name=name_b
    ))
    
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True)
    st.plotly_chart(fig_radar, use_container_width=True)

# --- 结语 ---
st.markdown("---")
st.caption("注：此工具仅用于辅助演示，具体利益请以 Allianz 或相关保险合同为准。")

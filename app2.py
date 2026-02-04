import streamlit as st
import pandas as pd
import plotly.express as px

# Set Page Config
st.set_page_config(page_title="Jesuit Tuition Comparison", layout="wide")

# Branding Colors
USF_GREEN = "#00543C" 
SECONDARY_GRAY = "#D3D3D3"

st.title("🎓 Jesuit University Cost Comparison & Trends")
st.markdown("""
Compare the **Total Cost of Attendance (TCOA)** and track **tuition growth** across all 27 US Jesuit institutions.
""")

# Full Data for all 27 Jesuit Institutions
data = {
    'Institution': [
        'Univ. of San Francisco', 'Georgetown', 'Boston College', 'Fordham', 
        'Loyola Marymount', 'Santa Clara', 'College of the Holy Cross', 
        'Fairfield', 'Loyola Maryland', 'Gonzaga', 'Seattle Univ.', 
        'Saint Louis Univ.', 'St. Joseph’s', 'Univ. of Scranton', 'Marquette', 
        'Loyola Chicago', 'Xavier', 'John Carroll', 'Regis Univ.', 
        'Creighton', 'Le Moyne', 'Rockhurst', 'Canisius', 'Detroit Mercy', 
        'Loyola New Orleans', 'Saint Peter’s', 'Spring Hill'
    ],
    '2025-26': [92602, 96492, 91792, 98331, 94598, 88650, 90350, 84780, 83620, 82689, 79928, 77917, 75202, 73296, 72666, 74673, 70930, 66500, 65500, 65413, 60300, 59300, 57200, 55100, 75000, 63831, 46800],
    '2024-25': [89470, 92563, 88632, 94100, 91200, 86694, 87295, 81913, 80792, 79893, 77225, 75282, 72659, 70817, 70209, 72148, 68531, 64251, 63285, 63201, 58261, 57295, 55266, 53237, 72464, 61672, 45217],
    '2023-24': [85200, 88560, 84200, 90200, 87500, 83142, 83722, 78560, 77485, 76623, 74063, 72200, 69685, 67917, 67335, 69195, 65725, 61621, 60695, 60614, 55875, 54949, 53004, 51059, 69500, 59148, 43367],
    '2022-23': [82100, 84500, 80300, 86400, 84100, 78849, 80392, 75437, 74406, 73579, 71121, 69331, 66916, 65219, 64660, 66444, 63114, 59174, 58285, 58207, 53655, 52767, 50900, 49031, 66740, 56800, 41645]
}

df_raw = pd.DataFrame(data)

# Sidebar
st.sidebar.header("Settings")
selected_year = st.sidebar.selectbox("Select Year for Cost View:", options=['2025-26', '2024-25', '2023-24', '2022-23'])
metric_type = st.sidebar.radio("Metric Type:", ("Annual Cost", "Projected 4-Year Total"))
selected_schools = st.sidebar.multiselect("Select Schools:", options=df_raw['Institution'].tolist(), default=df_raw['Institution'].tolist())

# Tabs for Views
tab1, tab2 = st.tabs(["📊 Cost Comparison", "📈 Trend Analysis"])

with tab1:
    # Process Cost Data
    df_cost = df_raw[['Institution', selected_year]].copy()
    df_cost.columns = ['Institution', 'Val']
    if metric_type == "Projected 4-Year Total":
        df_cost['Val'] = df_cost['Val'].apply(lambda x: round(sum(x * (1.035**i) for i in range(4))))
    
    filtered_cost = df_cost[df_cost['Institution'].isin(selected_schools)].sort_values(by='Val', ascending=False)
    usf_val = df_cost.loc[df_cost['Institution'] == 'Univ. of San Francisco', 'Val'].values[0]
    filtered_cost['Difference from USF'] = filtered_cost['Val'] - usf_val

    col1, col2 = st.columns([2, 1])
    with col1:
        color_map = {s: SECONDARY_GRAY for s in filtered_cost['Institution']}
        color_map['Univ. of San Francisco'] = USF_GREEN
        fig = px.bar(filtered_cost, x='Institution', y='Val', color='Institution', color_discrete_map=color_map, text_auto='.2s', title=f"Cost Comparison ({selected_year})")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Comparison Table")
        st.dataframe(filtered_cost.rename(columns={'Val': 'Annual TCOA'}), hide_index=True)

with tab2:
    st.subheader("Tuition Growth Trends (2022 - 2026)")
    # Melt data for Trends
    df_trends = df_raw.melt(id_vars='Institution', var_name='Year', value_name='Cost')
    df_trends = df_trends[df_trends['Institution'].isin(selected_schools)]
    
    # Line chart showing trends
    fig_trends = px.line(
        df_trends, x='Year', y='Cost', color='Institution',
        markers=True, title="Year-over-Year TCOA Growth"
    )
    # Highlight USF with a thicker line
    fig_trends.update_traces(line=dict(width=5), selector=dict(name='Univ. of San Francisco'))
    st.plotly_chart(fig_trends, use_container_width=True)
    
    st.write("💡 Note: Thick line represents University of San Francisco's cost trajectory.")

st.info(f"💡 For **{selected_year}**, the cost at USF is **${usf_val:,.0f}**.")
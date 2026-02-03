import streamlit as st
import pandas as pd
import plotly.express as px

# Set Page Config
st.set_page_config(page_title="Jesuit Tuition Comparison", layout="wide")

# App Header
st.title("🎓 Jesuit University Cost Comparison (2025-26)")
st.markdown("""
This app compares the **Total Cost of Attendance (TCOA)** across US Jesuit institutions, 
benchmarked against the **University of San Francisco**.
""")

# Data Dictionary
data = {
    'Institution': [
        'Fordham', 'Georgetown', 'Loyola Marymount', 'Univ. of San Francisco', 
        'Boston College', 'Santa Clara', 'College of the Holy Cross', 'Fairfield',
        'Loyola Maryland', 'Gonzaga', 'Seattle Univ.', 'Saint Louis Univ.',
        'St. Joseph’s', 'Univ. of Scranton', 'Marquette', 'Loyola Chicago',
        'Xavier', 'John Carroll', 'Regis', 'Creighton', 
        'Le Moyne', 'Rockhurst', 'Canisius', 'Detroit Mercy', 
        'Loyola New Orleans', 'Saint Peter’s', 'Spring Hill'
    ],
    'Annual_TCOA': [
        98331, 96492, 94598, 92602, 91792, 88650, 90350, 84780,
        83620, 82689, 79928, 77917, 75202, 73296, 72666, 74673,
        70930, 66500, 65500, 65413, 60300, 59300, 57200, 55100,
        75000, 63831, 46800
    ]
}

df = pd.DataFrame(data)

# Calculate 4-Year Projection (3.5% annual inflation)
def calc_total(initial):
    return round(sum(initial * (1.035**i) for i in range(4)))

df['4_Year_Total'] = df['Annual_TCOA'].apply(calc_total)

# --- Sidebar Controls ---
st.sidebar.header("Comparison Settings")
metric = st.sidebar.radio("Select Metric:", ("Annual Cost (2025-26)", "Projected 4-Year Cost"))
col_to_use = 'Annual_TCOA' if "Annual" in metric else '4_Year_Total'

selected_schools = st.sidebar.multiselect(
    "Select Schools to Compare:", 
    options=df['Institution'].tolist(),
    default=['Univ. of San Francisco', 'Santa Clara', 'Georgetown', 'Boston College', 'Loyola Chicago']
)

# Filter Data
filtered_df = df[df['Institution'].isin(selected_schools)].sort_values(by=col_to_use, ascending=False)

# --- Calculations ---
usf_val = df.loc[df['Institution'] == 'Univ. of San Francisco', col_to_use].values[0]
filtered_df['Diff_from_USF'] = filtered_df[col_to_use] - usf_val

# --- Visuals ---
col1, col2 = st.columns([2, 1])

with col1:
    fig = px.bar(
        filtered_df, 
        x='Institution', 
        y=col_to_use, 
        color='Institution',
        text_auto='.2s',
        title=f"Comparison: {metric}"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Comparison Table")
    st.dataframe(
        filtered_df[['Institution', col_to_use, 'Diff_from_USF']],
        column_config={
            col_to_use: st.column_config.NumberColumn(format="$%d"),
            "Diff_from_USF": st.column_config.NumberColumn(format="$%d")
        },
        hide_index=True
    )

st.info(f"💡 At USF, the {metric} is **${usf_val:,.0f}**.")
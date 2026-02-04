import streamlit as st
import pandas as pd
import plotly.express as px

# Set Page Config
st.set_page_config(page_title="Jesuit Tuition Comparison", layout="wide")

# Official USF Green (#00543C)
USF_GREEN = "#00543C"
SECONDARY_GRAY = "#D3D3D3"

st.title("🎓 Jesuit University Cost Comparison")
st.markdown("""
Compare the **Total Cost of Attendance (TCOA)** across US Jesuit institutions, 
benchmarked against the **University of San Francisco**.
""")

# Expanded Data with Historical Years
# Rates represent estimated Total Cost of Attendance (Tuition + Room/Board + Fees)
data = {
    'Institution': [
        'Univ. of San Francisco', 'Georgetown', 'Boston College', 
        'Santa Clara', 'Loyola Chicago', 'Fordham', 'Loyola Marymount'
    ],
    '2025-26': [92602, 96492, 91792, 88650, 74673, 98331, 94598],
    '2024-25': [89470, 92563, 88632, 86694, 74020, 94100, 91200],
    '2023-24': [85200, 88560, 84200, 83142, 71410, 90200, 87500],
    '2022-23': [82100, 84500, 80300, 78849, 67818, 86400, 84100]
}

df_raw = pd.DataFrame(data)

# --- Sidebar Controls ---
st.sidebar.header("Comparison Settings")

# 1. Select the Year
selected_year = st.sidebar.selectbox(
    "Select Academic Year:",
    options=['2025-26', '2024-25', '2023-24', '2022-23'],
    index=0
)

# 2. Select Metric (Annual or 4-Year)
metric_type = st.sidebar.radio("Select Metric View:", ("Annual Cost", "Projected 4-Year Total"))

# Process Data based on selection
df = df_raw[['Institution', selected_year]].copy()
df.columns = ['Institution', 'Selected_Value']

if metric_type == "Projected 4-Year Total":
    # 4-year projection assumes 3.5% annual inflation from the selected year's baseline
    df['Selected_Value'] = df['Selected_Value'].apply(lambda x: round(sum(x * (1.035**i) for i in range(4))))

# 3. Default to all schools
selected_schools = st.sidebar.multiselect(
    "Select Schools to Compare:",
    options=df['Institution'].tolist(),
    default=df['Institution'].tolist()
)

# Filter and Calculate Difference
filtered_df = df[df['Institution'].isin(selected_schools)].sort_values(by='Selected_Value', ascending=False)
usf_val = df.loc[df['Institution'] == 'Univ. of San Francisco', 'Selected_Value'].values[0]
filtered_df['Difference from USF'] = filtered_df['Selected_Value'] - usf_val

# --- Visuals ---
color_map = {school: SECONDARY_GRAY for school in filtered_df['Institution']}
color_map['Univ. of San Francisco'] = USF_GREEN

col1, col2 = st.columns([2, 1])

with col1:
    fig = px.bar(
        filtered_df, 
        x='Institution', 
        y='Selected_Value',
        color='Institution',
        color_discrete_map=color_map,
        text_auto='.2s',
        title=f"TCOA Comparison for {selected_year}"
    )
    # Style: Bold USF label on the X-Axis
    fig.update_xaxes(tickfont=dict(size=12, color='black'))
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Comparison Table")
    # Rename columns for display
    display_df = filtered_df.copy()
    display_df.columns = ["Jesuit Institution", "Annual TCOA", "Difference from USF"]
    
    st.dataframe(
        display_df,
        column_config={
            "Annual TCOA": st.column_config.NumberColumn(format="$%d"),
            "Difference from USF": st.column_config.NumberColumn(format="$%d")
        },
        hide_index=True
    )

    # Download Button
    csv = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Download CSV", data=csv, file_name=f'jesuit_costs_{selected_year}.csv')

st.info(f"💡 For **{selected_year}**, the cost at USF is **${usf_val:,.0f}**.")
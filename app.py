import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="UAC Care Pipeline Dashboard", layout="wide")

st.title("UAC Care Pipeline Analytics")
st.markdown("### Care Transition Efficiency & Placement Outcome Analytics")

DATA_FILE = "uac_data.csv"

def load_and_clean_data(filepath):
    df = pd.read_csv(filepath)
    
    df = df.dropna(subset=['Date'])
    
    df['Date'] = pd.to_datetime(df['Date'], format='%B %d, %Y')
    
    df = df.sort_values('Date').reset_index(drop=True)
    
    numeric_cols = [
        'Children apprehended and placed in CBP custody',
        'Children in CBP custody',
        'Children transferred out of CBP custody',
        'Children in HHS Care',
        'Children discharged from HHS Care'
    ]
    
    for col in numeric_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(float)
    
    df = df.fillna(0)
    
    return df

def calculate_derived_metrics(df):
    df = df.copy()
    
    df['Intake'] = df['Children apprehended and placed in CBP custody']
    df['Transfers'] = df['Children transferred out of CBP custody']
    df['CBP_Custody'] = df['Children in CBP custody']
    df['HHS_Care'] = df['Children in HHS Care']
    df['Discharges'] = df['Children discharged from HHS Care']
    
    df['Transfer_Efficiency_Ratio'] = (df['Transfers'] / df['CBP_Custody'].replace(0, pd.NA)).fillna(0)
    
    df['Discharge_Effectiveness'] = (df['Discharges'] / df['HHS_Care'].replace(0, pd.NA)).fillna(0)
    
    df['Total_Entries'] = df['Intake']
    df['Total_Exits'] = df['Transfers'] + df['Discharges']
    df['Pipeline_Throughput'] = (df['Total_Exits'] / df['Total_Entries'].replace(0, pd.NA)).fillna(0)
    
    df['Daily_Net_Change'] = df['Intake'] - df['Discharges']
    
    df['Active_Load'] = df['CBP_Custody'] + df['HHS_Care']
    
    df['DayOfWeek'] = df['Date'].dt.day_name()
    df['Is_Weekend'] = df['Date'].dt.dayofweek >= 5
    
    return df

df = load_and_clean_data(DATA_FILE)
df = calculate_derived_metrics(df)

with st.sidebar:
    st.header("Filters")
    
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    
    date_range = st.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)
        df_filtered = df.loc[mask].copy()
    else:
        df_filtered = df.copy()
    
    st.markdown("---")
    st.subheader("Threshold Settings")
    
    CBP_CUSTODY_THRESHOLD = st.number_input(
        "CBP Custody Alert Threshold",
        min_value=0,
        value=300,
        step=10
    )
    
    TRANSFER_EFFICIENCY_THRESHOLD = st.number_input(
        "Transfer Efficiency Alert Threshold (%)",
        min_value=0,
        max_value=100,
        value=30,
        step=5
    )

avg_transfer_efficiency = df_filtered['Transfer_Efficiency_Ratio'].mean() * 100
avg_discharge_effectiveness = df_filtered['Discharge_Effectiveness'].mean() * 100
avg_throughput = df_filtered['Pipeline_Throughput'].mean()
current_active_load = df_filtered['Active_Load'].iloc[-1] if not df_filtered.empty else 0

st.markdown("### Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Avg Transfer Efficiency Ratio",
        f"{avg_transfer_efficiency:.1f}%",
        delta_color="normal"
    )

with col2:
    st.metric(
        "Avg Discharge Effectiveness",
        f"{avg_discharge_effectiveness:.1f}%",
        delta_color="normal"
    )

with col3:
    st.metric(
        "Avg Pipeline Throughput",
        f"{avg_throughput:.2f}x",
        delta_color="normal"
    )

with col4:
    st.metric(
        "Current Active Load",
        f"{int(current_active_load):,}",
        delta_color="inverse"
    )

st.markdown("---")

max_cbp_custody = df_filtered['CBP_Custody'].max()
min_transfer_efficiency = df_filtered['Transfer_Efficiency_Ratio'].min() * 100

if max_cbp_custody > CBP_CUSTODY_THRESHOLD:
    st.error(f"🚨 ALERT: CBP Custody ({int(max_cbp_custody):,}) exceeds threshold ({CBP_CUSTODY_THRESHOLD})!")
elif max_cbp_custody > CBP_CUSTODY_THRESHOLD * 0.8:
    st.warning(f"⚠️ WARNING: CBP Custody ({int(max_cbp_custody):,}) is approaching threshold ({CBP_CUSTODY_THRESHOLD})")

if min_transfer_efficiency < TRANSFER_EFFICIENCY_THRESHOLD:
    st.error(f"🚨 ALERT: Transfer Efficiency dropped to {min_transfer_efficiency:.1f}% (below {TRANSFER_EFFICIENCY_THRESHOLD}%)!")
elif min_transfer_efficiency < TRANSFER_EFFICIENCY_THRESHOLD * 1.2:
    st.warning(f"⚠️ WARNING: Transfer Efficiency ({min_transfer_efficiency:.1f}%) is approaching threshold ({TRANSFER_EFFICIENCY_THRESHOLD}%)")

st.markdown("### Care Pipeline Visualization")
st.markdown("Intake vs Discharges Over Time")

fig_pipeline = go.Figure()

fig_pipeline.add_trace(go.Scatter(
    x=df_filtered['Date'],
    y=df_filtered['Intake'],
    mode='lines+markers',
    name='Intake',
    line=dict(color='#FF6B6B', width=2),
    marker=dict(size=6)
))

fig_pipeline.add_trace(go.Scatter(
    x=df_filtered['Date'],
    y=df_filtered['Discharges'],
    mode='lines+markers',
    name='Discharges',
    line=dict(color='#4ECDC4', width=2),
    marker=dict(size=6)
))

fig_pipeline.update_layout(
    xaxis_title="Date",
    yaxis_title="Number of Children",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    template="plotly_white",
    height=400,
    hovermode="x unified"
)

st.plotly_chart(fig_pipeline, use_container_width=True)

st.markdown("---")
st.markdown("### Bottleneck Detection")
st.markdown("CBP Custody vs HHS Care Accumulation")

fig_bottleneck = go.Figure()

fig_bottleneck.add_trace(go.Scatter(
    x=df_filtered['Date'],
    y=df_filtered['CBP_Custody'],
    mode='lines',
    name='CBP Custody',
    fill='tozeroy',
    line=dict(color='#FF6B6B', width=2),
    fillcolor='rgba(255, 107, 107, 0.3)'
))

fig_bottleneck.add_trace(go.Scatter(
    x=df_filtered['Date'],
    y=df_filtered['HHS_Care'],
    mode='lines',
    name='HHS Care',
    fill='tozeroy',
    line=dict(color='#4ECDC4', width=2),
    fillcolor='rgba(78, 205, 196, 0.3)'
))

fig_bottleneck.update_layout(
    xaxis_title="Date",
    yaxis_title="Number of Children",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    template="plotly_white",
    height=400,
    hovermode="x unified"
)

st.plotly_chart(fig_bottleneck, use_container_width=True)

st.markdown("---")
st.markdown("### Temporal Analysis")
st.markdown("Performance by Day of Week")

weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

weekday_stats = df_filtered.groupby('DayOfWeek').agg({
    'Intake': 'mean',
    'Discharges': 'mean',
    'Transfer_Efficiency_Ratio': 'mean',
    'Discharge_Effectiveness': 'mean'
}).reindex(weekday_order)

fig_weekday = go.Figure()

fig_weekday.add_trace(go.Bar(
    name='Avg Intake',
    x=weekday_order,
    y=weekday_stats['Intake'],
    marker_color='#FF6B6B'
))

fig_weekday.add_trace(go.Bar(
    name='Avg Discharges',
    x=weekday_order,
    y=weekday_stats['Discharges'],
    marker_color='#4ECDC4'
))

fig_weekday.update_layout(
    xaxis_title="Day of Week",
    yaxis_title="Average Count",
    barmode='group',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    template="plotly_white",
    height=400
)

st.plotly_chart(fig_weekday, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    weekend_performance = df_filtered.groupby('Is_Weekend').agg({
        'Transfer_Efficiency_Ratio': 'mean',
        'Discharge_Effectiveness': 'mean'
    }).reset_index()
    
    weekend_performance['Day Type'] = weekend_performance['Is_Weekend'].map({True: 'Weekend', False: 'Weekday'})
    
    fig_efficiency = px.bar(
        weekend_performance,
        x='Day Type',
        y='Transfer_Efficiency_Ratio',
        title='Transfer Efficiency: Weekday vs Weekend',
        color='Day Type',
        color_discrete_map={'Weekday': '#4ECDC4', 'Weekend': '#FF6B6B'},
        text_auto='.1%'
    )
    fig_efficiency.update_layout(template="plotly_white", height=300)
    st.plotly_chart(fig_efficiency, use_container_width=True)

with col2:
    fig_discharge = px.bar(
        weekend_performance,
        x='Day Type',
        y='Discharge_Effectiveness',
        title='Discharge Effectiveness: Weekday vs Weekend',
        color='Day Type',
        color_discrete_map={'Weekday': '#4ECDC4', 'Weekend': '#FF6B6B'},
        text_auto='.1%'
    )
    fig_discharge.update_layout(template="plotly_white", height=300)
    st.plotly_chart(fig_discharge, use_container_width=True)

st.markdown("---")
st.markdown("### Raw Data")

st.dataframe(
    df_filtered[[
        'Date', 'Intake', 'Transfers', 'CBP_Custody', 'HHS_Care', 'Discharges',
        'Transfer_Efficiency_Ratio', 'Discharge_Effectiveness', 'Pipeline_Throughput',
        'Daily_Net_Change', 'Active_Load'
    ]].style.format({
        'Transfer_Efficiency_Ratio': '{:.2%}',
        'Discharge_Effectiveness': '{:.2%}',
        'Pipeline_Throughput': '{:.2f}',
        'Daily_Net_Change': '{:.0f}'
    }),
    use_container_width=True
)

with st.expander("Data Summary Statistics"):
    st.write(df_filtered[[
        'Intake', 'Transfers', 'CBP_Custody', 'HHS_Care', 'Discharges',
        'Transfer_Efficiency_Ratio', 'Discharge_Effectiveness', 'Pipeline_Throughput'
    ]].describe())

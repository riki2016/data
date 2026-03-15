import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# =====================================
# Assume 'df' and 'metriche' are already defined
# df['Data'] is datetime
# metriche is a list of metrics
# =====================================

st.title("Weekly Training + Test vs League Match")

# 1. PREPARAZIONE DATI SETTIMANALI
df_weekly = df.copy()
df_weekly['Week'] = df_weekly['Data'].dt.to_period('W').apply(lambda r: r.start_time)

df_training = df_weekly[df_weekly['Competition'] == 'Full Training']
df_league = df_weekly[df_weekly['Competition'] == 'League']
df_test = df_weekly[df_weekly['Competition'] == 'Test Match']
df_train_test = pd.concat([df_training, df_test])

# 2. USER SELECTION
selected_metric = st.selectbox("Select Metric", metriche)

# 3. AGGREGAZIONE DATI
train_agg = df_train_test.groupby('Week')[selected_metric].sum().reset_index()
league_agg = df_league.groupby('Week').agg({
    selected_metric: 'sum',
    'Opponent': 'first'
}).reset_index()

ratio_texts = []
for week in train_agg['Week']:
    train_val = train_agg.loc[train_agg['Week'] == week, selected_metric].values[0]
    league_row = league_agg.loc[league_agg['Week'] == week, selected_metric]

    if not league_row.empty and league_row.values[0] > 0:
        ratio = train_val / league_row.values[0]
        ratio_texts.append(f"{ratio:.2f}x")
    else:
        ratio_texts.append("")

# 4. CREAZIONE GRAFICO
fig_week = go.Figure()

# Barre Training + Test
fig_week.add_trace(go.Bar(
    x=train_agg['Week'],
    y=train_agg[selected_metric],
    name='Full Training + Test',
    marker_color='rgba(0,180,0,0.85)',
    text=ratio_texts,
    textposition='inside',
    insidetextanchor='middle',
    textfont=dict(color='white', size=11)
))

# Barre League Match
fig_week.add_trace(go.Bar(
    x=league_agg['Week'],
    y=league_agg[selected_metric],
    name='League Match',
    marker_color='rgba(255,0,0,0.85)',
    text=league_agg['Opponent'],
    textposition='inside',
    insidetextanchor='middle',
    textfont=dict(color='white', size=11)
))

# Layout
fig_week.update_layout(
    title=f'{selected_metric} - Weekly Training + Test vs League Match',
    barmode='group',
    hovermode='x unified',
    template='plotly_white',
    xaxis=dict(
        type="date",
        dtick="M1",
        tickformat="%b %Y",
        rangeslider=dict(visible=True, thickness=0.05),
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(step="all", label="All")
            ])
        )
    ),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

# 5. SHOW PLOT
st.plotly_chart(fig_week, use_container_width=True)
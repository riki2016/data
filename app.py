# ================== LIBRERIE ==================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Dashboard Performance Atletica", layout="wide")

st.title("Dashboard Performance Atletica")



# ================== 2. PREPARAZIONE DATI ==================

df_raw['Data'] = pd.to_datetime(df_raw['Data'])

mask_match_valid = (
    (df_raw['Competition'].isin(['League', 'Test Match'])) &
    (df_raw['Time'] == 'Full Match')
)

mask_training = df_raw['Competition'] == 'Full Training'

df = df_raw[mask_match_valid | mask_training].copy()
df = df.sort_values('Data')

df_team_avg = df[df['PLAYER'] == 'Team Average'].copy()

players = [p for p in df['PLAYER'].dropna().unique().tolist() if p != 'Team Average']
players.insert(0, 'Team Average')

metriche = [m for m in df.select_dtypes(include='number').columns.tolist() if m != 'Vel Max']

competitions = df['Competition'].dropna().unique()

color_map = {
    'League': 'rgba(255,0,0,0.85)',
    'Full Training': 'rgba(0,180,0,0.85)',
    'Test Match': 'rgba(0,0,255,0.85)'
}

# ================== 3. SIDEBAR CONTROLLI ==================

st.sidebar.header("Filtri")

giocatore = st.sidebar.selectbox("Giocatore", players)
metrica = st.sidebar.selectbox("Metrica", metriche)

# ================== 4. GRAFICO ==================

df_plot = df[df['PLAYER'] == giocatore].copy()

fig = go.Figure()

# ---- BARRE ----
for comp in competitions:

    df_comp = df_plot[df_plot['Competition'] == comp]

    if df_comp.empty:
        continue

    fig.add_trace(go.Bar(
        x=df_comp['Data'],
        y=df_comp[metrica],
        name=comp,
        marker_color=color_map.get(comp, 'gray'),
        width=24*60*60*1000,
        text=df_comp['Opponent'] if comp in ['League','Test Match'] else None,
        textposition='inside',
        insidetextanchor='middle',
        textfont=dict(color='white', size=11)
    ))

    fig.add_trace(go.Scatter(
        x=df_comp['Data'],
        y=df_comp[metrica],
        mode='text',
        text=[f'{v:.0f}' for v in df_comp[metrica]],
        textposition='top center',
        showlegend=False
    ))

# ---- TEAM AVERAGE ----
if not df_team_avg.empty and giocatore != 'Team Average':

    fig.add_trace(go.Scatter(
        x=df_team_avg['Data'],
        y=df_team_avg[metrica],
        mode='markers',
        name='Team Average (Ref)',
        marker=dict(
            symbol='asterisk',
            size=10,
            color='black',
            line=dict(width=1.5)
        )
    ))

# ---- LAYOUT ----

fig.update_layout(
    title=f"{metrica} - {giocatore}",
    barmode='overlay',
    hovermode='x unified',
    template='plotly_white',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    xaxis=dict(
        type="date",
        rangeslider=dict(visible=True)
    ),
    margin=dict(l=40, r=40, t=80, b=40)
)

st.plotly_chart(fig, use_container_width=True)

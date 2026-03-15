# ================== WEEKLY DASHBOARD ==================

st.header("Weekly Training + Test vs League Match")

# ================== 1. PREPARAZIONE DATI ==================

df_weekly = df.copy()

df_weekly['Week'] = df_weekly['Data'].dt.to_period('W').apply(lambda r: r.start_time)

df_training = df_weekly[df_weekly['Competition'] == 'Full Training']
df_league = df_weekly[df_weekly['Competition'] == 'League']
df_test = df_weekly[df_weekly['Competition'] == 'Test Match']

df_train_test = pd.concat([df_training, df_test])

fig_week = go.Figure()
trace_map_week = []

# ================== 2. COSTRUZIONE TRACCE ==================

for metrica in metriche:

    current_traces = []

    train_agg = df_train_test.groupby('Week')[metrica].sum().reset_index()

    league_agg = df_league.groupby('Week').agg({
        metrica: 'sum',
        'Opponent': 'first'
    }).reset_index()

    ratio_texts = []

    for week in train_agg['Week']:

        train_val = train_agg.loc[train_agg['Week'] == week, metrica].values[0]

        league_row = league_agg.loc[league_agg['Week'] == week, metrica]

        if not league_row.empty and league_row.values[0] > 0:
            ratio = train_val / league_row.values[0]
            ratio_texts.append(f"{ratio:.2f}x")
        else:
            ratio_texts.append("")

    # TRAINING + TEST
    fig_week.add_trace(go.Bar(
        x=train_agg['Week'],
        y=train_agg[metrica],
        name='Full Training + Test',
        marker_color='rgba(0,180,0,0.85)',
        text=ratio_texts,
        textposition='inside',
        insidetextanchor='middle',
        textfont=dict(color='white', size=11),
        visible=(metrica == metriche[0])
    ))

    current_traces.append(len(fig_week.data)-1)

    # LEAGUE MATCH
    fig_week.add_trace(go.Bar(
        x=league_agg['Week'],
        y=league_agg[metrica],
        name='League Match',
        marker_color='rgba(255,0,0,0.85)',
        text=league_agg['Opponent'],
        textposition='inside',
        insidetextanchor='middle',
        textfont=dict(color='white', size=11),
        visible=(metrica == metriche[0])
    ))

    current_traces.append(len(fig_week.data)-1)

    trace_map_week.append(current_traces)

# ================== 3. MENU METRICHE ==================

buttons_week = []

for i, metrica in enumerate(metriche):

    visible_list = [False] * len(fig_week.data)

    for idx in trace_map_week[i]:
        visible_list[idx] = True

    buttons_week.append(dict(
        label=metrica,
        method='update',
        args=[
            {'visible': visible_list},
            {'title': f'{metrica} - Weekly Training + Test vs League Match'}
        ]
    ))

# ================== 4. LAYOUT ==================

fig_week.update_layout(

    title=f'{metriche[0]} - Weekly Training + Test vs League Match',

    barmode='group',
    hovermode='x unified',
    template='plotly_white',

    updatemenus=[dict(
        buttons=buttons_week,
        direction="down",
        showactive=True,
        x=0,
        y=1.25
    )],

    xaxis=dict(
        type="date",
        dtick="M1",
        tickformat="%b %Y",
        rangeslider=dict(visible=True, thickness=0.05),

        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(step="all", label="Tutto")
            ])
        )
    ),

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

# ================== STREAMLIT OUTPUT ==================

st.plotly_chart(fig_week, use_container_width=True)
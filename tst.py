import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Dados de exemplo
x = list(range(10))
y = [1000000, 1300000, 900000, 850000, 800000, 400000, 450000, 1200000, 1400000, 500000]

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=x,
    y=y,
    mode='lines+markers',
    name='Transactions',
    line=dict(color='blue', width=2, shape='spline'),  # linha curva
    marker=dict(color='blue', size=4),
))

# Estilo semelhante ao RubyScore
fig.update_layout(
    plot_bgcolor='#0f0f0f',
    paper_bgcolor='#0f0f0f',
    font=dict(color='white', family='Space Grotesk, sans-serif'),
    xaxis=dict(
        title='TX',
        color='white',
        gridcolor='rgba(255, 255, 255, 0.05)',
        showline=True,
        linewidth=1,
        linecolor='white'
    ),
    yaxis=dict(
        title='Wallets',
        color='white',
        gridcolor='rgba(255, 255, 255, 0.05)',
        showline=True,
        linewidth=1,
        linecolor='white'
    ),
    margin=dict(l=40, r=40, t=40, b=40),
    height=400
)

st.plotly_chart(fig, use_container_width=True)



import plotly.graph_objects as go

def build_chart(history: list):
    x = list(range(len(history)))
    fig = go.Figure()

    # Area fill
    fig.add_trace(go.Scatter(
        x=x, y=history,
        fill='tozeroy',
        mode='lines+markers',
        line=dict(color='#00d4ff', width=2.5, shape='spline'),
        fillcolor='rgba(0,212,255,0.07)',
        marker=dict(size=5, color='#00d4ff', line=dict(color='#020b18', width=1)),
        name='Vehicles',
    ))

    # Prediction point
    if len(history) >= 2:
        fig.add_trace(go.Scatter(
            x=[len(history)],
            y=[round(history[-1] * 1.05)],
            mode='markers',
            marker=dict(size=10, color='#ff8c00', symbol='diamond',
                        line=dict(color='#020b18', width=1)),
            name='Forecast',
        ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#4a7fa5', size=11),
        xaxis=dict(gridcolor='#0d3a5c', zeroline=False, title='Frame'),
        yaxis=dict(gridcolor='#0d3a5c', zeroline=False, title='Count'),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#4a7fa5')),
        margin=dict(l=10, r=10, t=10, b=10),
        height=240,
    )
    return fig

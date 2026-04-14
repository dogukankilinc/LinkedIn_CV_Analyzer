import plotly.graph_objects as go

def create_radar_chart(scores: dict):
    # Extract values
    val_ai = scores.get('ai', {}).get('percentage', 0)
    val_sm = scores.get('system_modeling', {}).get('percentage', 0)
    val_es = scores.get('embedded_systems', {}).get('percentage', 0)

    categories = ['Yapay Zeka', 'Sistem Modelleme', 'Gömülü Sistemler']
    values = [val_ai, val_sm, val_es]

    # Close the loop
    categories = [*categories, categories[0]]
    values = [*values, values[0]]

    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='CV Skoru',
                line_color='#0076A8',
                fillcolor='rgba(0, 118, 168, 0.4)'
            )
        ],
        layout=go.Layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False,
            margin=dict(l=40, r=40, t=20, b=20)
        )
    )
    return fig

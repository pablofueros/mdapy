"""Compare linear and directional interpretations of angular values."""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from mdapy import DataColumn, max_diss_alg

PAGE_COLOR = "#e9edf2"
PLOT_COLOR = "#f2f4f7"
GRID_COLOR = "#c8d0da"

angles = np.array([350.0, 10.0, 180.0, 90.0])
seed_index = 0
n_clusters = 3

linear_selected, linear_indices = max_diss_alg(
    DataColumn(angles), n_clusters=n_clusters, seed_index=seed_index
)
directional_selected, directional_indices = max_diss_alg(
    DataColumn(angles, directional=True),
    n_clusters=n_clusters,
    seed_index=seed_index,
)

print(f"Angles: {angles.tolist()}")
print(f"Linear interpretation: {linear_indices}")
print(f"Directional interpretation: {directional_indices}")

assert linear_indices == [0, 1, 2]
assert directional_indices == [0, 2, 3]
np.testing.assert_array_equal(linear_selected[:, 0], angles[linear_indices])
np.testing.assert_array_equal(directional_selected[:, 0], angles[directional_indices])

candidate_mask = np.arange(len(angles)) != seed_index


def add_selection(fig: go.Figure, indices: list[int], column: int) -> None:
    """Add one interpretation of the angular selection to a polar subplot."""
    fig.add_trace(
        go.Scatterpolar(
            theta=angles[candidate_mask],
            r=np.ones(candidate_mask.sum()),
            mode="markers",
            name="Observations",
            legendgroup="observations",
            showlegend=column == 1,
            marker={
                "color": "#aeb7c2",
                "line": {"color": "#6f7b87", "width": 1},
                "size": 13,
            },
            hovertemplate="Angle=%{theta:.0f}°<extra></extra>",
        ),
        row=1,
        col=column,
    )
    fig.add_trace(
        go.Scatterpolar(
            theta=angles[indices[1:]],
            r=np.ones(len(indices) - 1),
            mode="markers+text",
            name="Selected observations",
            legendgroup="selected",
            showlegend=column == 1,
            text=[str(order) for order in range(2, len(indices) + 1)],
            textposition="top center",
            marker={
                "color": "#263746",
                "line": {"color": "#101820", "width": 1},
                "size": 14,
            },
            hovertemplate="Selection %{text}<br>Angle=%{theta:.0f}°<extra></extra>",
        ),
        row=1,
        col=column,
    )
    fig.add_trace(
        go.Scatterpolar(
            theta=[angles[seed_index]],
            r=[1],
            mode="markers+text",
            name="Seed",
            legendgroup="seed",
            showlegend=column == 1,
            text=["1"],
            textposition="top center",
            marker={
                "color": "#f7f8fa",
                "line": {"color": "#101820", "width": 1.5},
                "size": 17,
                "symbol": "star",
            },
            hovertemplate="Seed · selection 1<br>Angle=%{theta:.0f}°<extra></extra>",
        ),
        row=1,
        col=column,
    )


fig = make_subplots(
    rows=1,
    cols=2,
    specs=[[{"type": "polar"}, {"type": "polar"}]],
    subplot_titles=("Linear", "Directional"),
)
add_selection(fig, linear_indices, 1)
add_selection(fig, directional_indices, 2)

polar_style = {
    "bgcolor": PLOT_COLOR,
    "angularaxis": {
        "direction": "clockwise",
        "rotation": 90,
        "gridcolor": GRID_COLOR,
    },
    "radialaxis": {
        "range": [0.72, 1.2],
        "showticklabels": False,
        "gridcolor": GRID_COLOR,
    },
}
fig.update_layout(
    template="plotly_white",
    paper_bgcolor=PAGE_COLOR,
    title={"text": "Selection order from a 350° seed", "x": 0.5, "xanchor": "center"},
    polar=polar_style,
    polar2=polar_style,
    legend={"orientation": "h", "y": -0.03, "x": 0.5, "xanchor": "center"},
    margin={"t": 100, "b": 120},
)
fig.add_annotation(
    text=(
        "Linear values place 10° far from 350°. As directions, their shortest "
        "distance is only 20°, so 180° is selected next."
    ),
    x=0.5,
    y=-0.16,
    xref="paper",
    yref="paper",
    showarrow=False,
)

fig.show()

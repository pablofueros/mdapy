"""Select and inspect representative sea states in an interactive polar plot."""

from pathlib import Path

import numpy as np
import plotly.graph_objects as go

from mdapy import DataColumn, max_diss_alg

PAGE_COLOR = "#e9edf2"
PLOT_COLOR = "#f2f4f7"
GRID_COLOR = "#c8d0da"

data_path = Path(__file__).parent / "data" / "datawave.npz"
rng = np.random.default_rng(42)
sample_size = 10_000
n_clusters = 10

with np.load(data_path) as datawave:
    source_indices = rng.choice(len(datawave["tp"]), size=sample_size, replace=False)
    direction = datawave["dir"][source_indices]
    peak_period = datawave["tp"][source_indices]

seed_index = int(np.argmax(peak_period))
selected, selected_indices = max_diss_alg(
    DataColumn(direction, directional=True),
    DataColumn(peak_period),
    n_clusters=n_clusters,
    seed_index=seed_index,
)
selected_source_indices = source_indices[selected_indices]

print(f"Sample indices: {selected_indices}")
print(f"Source indices: {selected_source_indices.tolist()}")

candidate_mask = np.arange(len(direction)) != seed_index
candidate_customdata = np.column_stack(
    (np.arange(len(direction))[candidate_mask], source_indices[candidate_mask])
)
selected_customdata = np.column_stack(
    (
        np.arange(2, len(selected) + 1),
        np.asarray(selected_indices[1:]),
        selected_source_indices[1:],
    )
)

fig = go.Figure(
    data=[
        go.Scatterpolar(
            theta=direction[candidate_mask],
            r=peak_period[candidate_mask],
            customdata=candidate_customdata,
            mode="markers",
            name="Sampled observations",
            marker={"color": "#8f9aa7", "opacity": 0.28, "size": 5},
            hovertemplate=(
                "Direction=%{theta:.1f}°<br>Peak period=%{r:.2f} s"
                "<br>Sample index=%{customdata[0]}"
                "<br>Source index=%{customdata[1]}<extra></extra>"
            ),
        ),
        go.Scatterpolar(
            theta=selected[1:, 0],
            r=selected[1:, 1],
            customdata=selected_customdata,
            mode="markers+text",
            name="Selected observations",
            text=[str(order) for order in range(2, len(selected) + 1)],
            textposition="top center",
            marker={
                "color": "#263746",
                "line": {"color": "#101820", "width": 1},
                "size": 13,
            },
            hovertemplate=(
                "Selection %{customdata[0]}<br>Direction=%{theta:.1f}°"
                "<br>Peak period=%{r:.2f} s"
                "<br>Sample index=%{customdata[1]}"
                "<br>Source index=%{customdata[2]}<extra></extra>"
            ),
        ),
        go.Scatterpolar(
            theta=[selected[0, 0]],
            r=[selected[0, 1]],
            customdata=[[selected_indices[0], selected_source_indices[0]]],
            mode="markers+text",
            name="Seed",
            text=["1"],
            textposition="top center",
            marker={
                "color": "#f7f8fa",
                "line": {"color": "#101820", "width": 1.5},
                "size": 17,
                "symbol": "star",
            },
            hovertemplate=(
                "Seed · selection 1<br>Direction=%{theta:.1f}°"
                "<br>Peak period=%{r:.2f} s"
                "<br>Sample index=%{customdata[0]}"
                "<br>Source index=%{customdata[1]}<extra></extra>"
            ),
        ),
    ]
)

fig.update_layout(
    template="plotly_white",
    paper_bgcolor=PAGE_COLOR,
    title={
        "text": f"{n_clusters} representative sea states from {sample_size:,} observations",
        "x": 0.5,
        "xanchor": "center",
    },
    polar={
        "bgcolor": PLOT_COLOR,
        "angularaxis": {
            "direction": "clockwise",
            "rotation": 90,
            "gridcolor": GRID_COLOR,
        },
        "radialaxis": {
            "title": {"text": "Peak period (s)"},
            "gridcolor": GRID_COLOR,
        },
    },
    legend={"orientation": "h", "y": -0.1, "x": 0.5, "xanchor": "center"},
    margin={"t": 90, "b": 90},
)

fig.show()

"""Visualize the selection order with an interactive Plotly animation."""

import numpy as np
import plotly.graph_objects as go

from mdapy import DataColumn, max_diss_alg

PAGE_COLOR = "#e9edf2"
PLOT_COLOR = "#f2f4f7"
GRID_COLOR = "#c8d0da"

rng = np.random.default_rng(42)
points = np.vstack(
    (
        rng.normal(loc=(-2.0, -1.0), scale=(0.8, 0.6), size=(100, 2)),
        rng.normal(loc=(2.0, 1.0), scale=(1.0, 0.7), size=(120, 2)),
        rng.normal(loc=(0.0, 3.5), scale=(0.7, 0.5), size=(80, 2)),
    )
)

center = points.mean(axis=0)
seed_index = int(np.argmin(np.linalg.norm(points - center, axis=1)))

selected, indices = max_diss_alg(
    DataColumn(points[:, 0]),
    DataColumn(points[:, 1]),
    n_clusters=12,
    seed_index=seed_index,
)

candidate_mask = np.arange(len(points)) != seed_index
selection_order = [str(order) for order in range(2, len(selected) + 1)]


def observations_trace() -> go.Scatter:
    """Build the background sample shown in every animation frame."""
    return go.Scatter(
        x=points[candidate_mask, 0],
        y=points[candidate_mask, 1],
        mode="markers",
        name="Observations",
        marker={"color": "#aeb7c2", "size": 7},
        hovertemplate="x=%{x:.3f}<br>y=%{y:.3f}<extra></extra>",
    )


def selection_trace(count: int) -> go.Scatter:
    """Build the selected-observation trace for one animation frame."""
    return go.Scatter(
        x=selected[1:count, 0],
        y=selected[1:count, 1],
        mode="markers+text",
        name="Selected observations",
        text=selection_order[: count - 1],
        textposition="top right",
        marker={
            "color": "#263746",
            "line": {"color": "#101820", "width": 1},
            "size": 11,
        },
        hovertemplate="Selection %{text}<br>x=%{x:.3f}<br>y=%{y:.3f}<extra></extra>",
    )


def seed_trace() -> go.Scatter:
    """Build the seed trace shown in every animation frame."""
    return go.Scatter(
        x=[selected[0, 0]],
        y=[selected[0, 1]],
        mode="markers+text",
        name="Seed",
        text=["1"],
        textposition="top right",
        marker={
            "color": "#f7f8fa",
            "line": {"color": "#101820", "width": 1.5},
            "size": 16,
            "symbol": "star",
        },
        hovertemplate="Seed · selection 1<br>x=%{x:.3f}<br>y=%{y:.3f}<extra></extra>",
    )


def frame_data(count: int) -> list[go.Scatter]:
    """Return a complete frame so animation never drops the sample."""
    return [observations_trace(), selection_trace(count), seed_trace()]


fig = go.Figure(
    data=frame_data(1),
    frames=[
        go.Frame(
            data=frame_data(count),
            name=str(count),
            layout={"title": {"text": f"Selection {count}/{len(selected)}"}},
        )
        for count in range(1, len(selected) + 1)
    ],
)

fig.update_layout(
    template="plotly_white",
    paper_bgcolor=PAGE_COLOR,
    plot_bgcolor=PLOT_COLOR,
    title={"text": f"Selection 1/{len(selected)}", "x": 0.05},
    xaxis={"title": "First variable", "gridcolor": GRID_COLOR},
    yaxis={"title": "Second variable", "gridcolor": GRID_COLOR},
    legend={"orientation": "h", "y": 1.08, "x": 1, "xanchor": "right"},
    margin={"t": 110, "b": 100},
    updatemenus=[
        {
            "type": "buttons",
            "direction": "left",
            "x": 0,
            "y": -0.16,
            "buttons": [
                {
                    "label": "Play",
                    "method": "animate",
                    "args": [
                        None,
                        {
                            "frame": {"duration": 800, "redraw": True},
                            "transition": {"duration": 200},
                            "fromcurrent": True,
                        },
                    ],
                },
                {
                    "label": "Pause",
                    "method": "animate",
                    "args": [[None], {"frame": {"duration": 0}, "mode": "immediate"}],
                },
            ],
        }
    ],
    sliders=[
        {
            "active": 0,
            "currentvalue": {"prefix": "Selection: "},
            "pad": {"t": 45},
            "steps": [
                {
                    "label": str(count),
                    "method": "animate",
                    "args": [
                        [str(count)],
                        {
                            "frame": {"duration": 0, "redraw": True},
                            "mode": "immediate",
                            "transition": {"duration": 0},
                        },
                    ],
                }
                for count in range(1, len(selected) + 1)
            ],
        }
    ],
)

print(f"Seed index: {seed_index}")
print(f"Selected indices: {indices}")

fig.show()

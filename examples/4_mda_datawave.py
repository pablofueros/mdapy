"""Select representative observations from a real wave dataset."""

from pathlib import Path
from typing import cast

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.projections.polar import PolarAxes

from mdapy import DataColumn, max_diss_alg

plt.rcParams["toolbar"] = "None"

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

selected_theta = np.deg2rad(selected[:, 0])
candidate_mask = np.arange(len(direction)) != seed_index

fig, raw_ax = plt.subplots(figsize=(8, 7), subplot_kw={"projection": "polar"})
ax = cast(PolarAxes, raw_ax)
ax.scatter(
    np.deg2rad(direction[candidate_mask]),
    peak_period[candidate_mask],
    color="0.72",
    alpha=0.2,
    edgecolor="none",
    s=12,
)
ax.scatter(
    selected_theta[1:],
    selected[1:, 1],
    color="0.18",
    edgecolor="0.05",
    linewidth=0.7,
    s=120,
    zorder=3,
)
ax.scatter(
    selected_theta[0],
    selected[0, 1],
    color="white",
    edgecolor="0.05",
    linewidth=1.2,
    marker="*",
    s=180,
    zorder=4,
)

ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)
ax.set_rlabel_position(225)
ax.set_rgrids([5, 10, 15, 20], labels=["5 s", "10 s", "15 s", "20 s"])
ax.grid(color="0.87", linewidth=0.8)
ax.spines["polar"].set_color("0.55")
ax.set_title(
    f"{n_clusters} representative sea states from {sample_size:,} observations",
    fontsize=13,
    pad=32,
)
fig.text(
    0.5,
    0.025,
    "Gray: sampled observations · Dark: selected observations · Star: seed",
    ha="center",
    fontsize=9,
    color="0.25",
)
fig.subplots_adjust(left=0.08, right=0.9, top=0.84, bottom=0.1)

plt.show()

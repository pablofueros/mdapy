"""Compare linear and directional interpretations of angular values."""

import matplotlib.pyplot as plt
import numpy as np

from mdapy import DataColumn, max_diss_alg

plt.rcParams["toolbar"] = "None"

angles = np.array([350.0, 10.0, 180.0, 90.0])
seed_index = 0
n_clusters = 3

linear_selected, linear_indices = max_diss_alg(
    DataColumn(angles),
    n_clusters=n_clusters,
    seed_index=seed_index,
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

theta = np.deg2rad(angles)
radius = np.ones_like(theta)
candidate_mask = np.arange(len(angles)) != seed_index


def plot_selection(ax, indices: list[int], title: str) -> None:
    ax.scatter(
        theta[candidate_mask],
        radius[candidate_mask],
        color="0.78",
        edgecolor="0.45",
        s=90,
        zorder=2,
    )
    ax.scatter(
        theta[indices[1:]],
        radius[indices[1:]],
        color="0.18",
        edgecolor="0.05",
        linewidth=0.8,
        s=100,
        zorder=3,
    )
    ax.scatter(
        theta[seed_index],
        radius[seed_index],
        color="white",
        edgecolor="0.05",
        linewidth=1.2,
        marker="*",
        s=190,
        zorder=4,
    )

    for order, index in enumerate(indices, start=1):
        ax.annotate(
            str(order),
            (theta[index], radius[index]),
            xytext=(0, 15),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.set_title(title, fontsize=12, pad=12)
    ax.set(
        rlim=(0.72, 1.2),
        rticks=[],
    )
    ax.set_thetagrids([0, 90, 180, 270], labels=["", "90°", "180°", "270°"])
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.grid(color="0.88", linewidth=0.8)
    ax.spines["polar"].set_color("0.55")


fig, axes = plt.subplots(
    1,
    2,
    figsize=(9, 5.5),
    subplot_kw={"projection": "polar"},
)
plot_selection(axes[0], linear_indices, "Linear")
plot_selection(axes[1], directional_indices, "Directional")

fig.suptitle("Selection order from a 350° seed", fontsize=13, y=0.96)
fig.text(
    0.5,
    0.055,
    "Linear values place 10° far from 350°. As directions, their shortest "
    "distance is only 20°, so 180° is selected next.",
    ha="center",
    va="center",
    fontsize=9,
    color="0.25",
)
fig.subplots_adjust(left=0.06, right=0.94, top=0.84, bottom=0.16, wspace=0.3)

plt.show()

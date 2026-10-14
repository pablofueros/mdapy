"""Visualize the selection order in a two-dimensional dataset."""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button

from mdapy import DataColumn, max_diss_alg

plt.rcParams["toolbar"] = "None"

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

fig, ax = plt.subplots(figsize=(9, 6))
candidate_mask = np.arange(len(points)) != seed_index
ax.scatter(
    points[candidate_mask, 0],
    points[candidate_mask, 1],
    color="0.82",
    s=16,
)
selection = ax.scatter(
    [],
    [],
    color="0.18",
    edgecolor="0.05",
    linewidth=0.8,
    s=55,
)
ax.scatter(
    selected[0, 0],
    selected[0, 1],
    color="white",
    edgecolor="0.05",
    linewidth=1.2,
    marker="*",
    s=150,
    zorder=3,
)

annotations = [
    ax.annotate(
        str(order),
        (x, y),
        xytext=(5, 5),
        textcoords="offset points",
        fontsize=9,
        visible=order == 1,
    )
    for order, (x, y) in enumerate(selected, start=1)
]

visible_count = [1]
playing = [False]


def update_plot() -> None:
    count = visible_count[0]
    selection.set_offsets(selected[1:count])
    for position, annotation in enumerate(annotations, start=1):
        annotation.set_visible(position <= count)
    ax.set_title(
        f"Selection {count}/{len(selected)}",
        fontsize=13,
        loc="left",
        pad=10,
    )
    fig.canvas.draw_idle()


def pause() -> None:
    timer.stop()
    playing[0] = False
    play_button.label.set_text("Play")
    fig.canvas.draw_idle()


def advance() -> None:
    if visible_count[0] >= len(selected):
        pause()
        return
    visible_count[0] += 1
    update_plot()


def show_previous(_event: object) -> None:
    pause()
    visible_count[0] = max(1, visible_count[0] - 1)
    update_plot()


def show_next(_event: object) -> None:
    pause()
    advance()


def toggle_play(_event: object) -> None:
    if playing[0]:
        pause()
        return
    if visible_count[0] >= len(selected):
        visible_count[0] = 1
        update_plot()
    playing[0] = True
    play_button.label.set_text("Pause")
    fig.canvas.draw_idle()
    timer.start()


def reset(_event: object) -> None:
    pause()
    visible_count[0] = 1
    update_plot()


fig.text(
    0.5,
    0.145,
    "Gray: observations · Dark: selected observations · Star: seed · "
    "Numbers: selection order",
    ha="center",
    fontsize=9,
    color="0.25",
)
fig.subplots_adjust(left=0.1, right=0.97, top=0.92, bottom=0.24)
previous_button = Button(
    fig.add_axes((0.18, 0.055, 0.14, 0.05)),
    "Previous",
    color="0.96",
    hovercolor="0.88",
)
next_button = Button(
    fig.add_axes((0.35, 0.055, 0.14, 0.05)),
    "Next",
    color="0.96",
    hovercolor="0.88",
)
play_button = Button(
    fig.add_axes((0.52, 0.055, 0.14, 0.05)),
    "Play",
    color="0.96",
    hovercolor="0.88",
)
reset_button = Button(
    fig.add_axes((0.69, 0.055, 0.14, 0.05)),
    "Reset",
    color="0.96",
    hovercolor="0.88",
)

for button in (previous_button, next_button, play_button, reset_button):
    button.label.set_fontsize(9)
    for spine in button.ax.spines.values():
        spine.set_color("0.65")
        spine.set_linewidth(0.8)

previous_button.on_clicked(show_previous)
next_button.on_clicked(show_next)
play_button.on_clicked(toggle_play)
reset_button.on_clicked(reset)

timer = fig.canvas.new_timer(interval=800)
timer.add_callback(advance)

ax.set(
    xlabel="First variable",
    ylabel="Second variable",
)
ax.spines[["top", "right"]].set_visible(False)
ax.tick_params(labelsize=9)
update_plot()

print(f"Seed index: {seed_index}")
print(f"Selected indices: {indices}")

plt.show()

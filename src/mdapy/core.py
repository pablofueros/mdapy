"""Internal numerical core shared by the column and tuple APIs."""

import numpy as np
from numpy.typing import NDArray


def _distances_to_point(
    data: NDArray,
    point_index: int,
    deviations: list[float],
    dir_indices: list[int] | None,
) -> NDArray:
    """Calculate every observation's distance to one selected point."""
    differences = data - data[point_index]
    for column in dir_indices or []:
        differences[:, column] = (differences[:, column] + 180) % 360 - 180
    return np.linalg.norm(differences / deviations, axis=1)


def _select_indices(
    data: NDArray,
    deviations: list[float],
    dir_indices: list[int] | None,
    n_clusters: int,
    seed_index: int,
    *,
    show_progress: bool = False,
) -> list[int]:
    """Update nearest distances only against the last selected observation."""
    indices = [seed_index]
    selected = np.zeros(len(data), dtype=bool)
    selected[seed_index] = True
    nearest = np.full(len(data), np.inf)

    while len(indices) < n_clusters:
        distances = _distances_to_point(data, indices[-1], deviations, dir_indices)
        np.minimum(nearest, distances, out=nearest)
        # Negative infinity excludes selected rows even when all others coincide.
        nearest[selected] = -np.inf
        # argmax returns the first input index for an exact tie, as historically.
        next_index = int(np.argmax(nearest))
        if show_progress:
            for point_index in range(len(data)):
                if selected[point_index]:
                    continue
                progress = (point_index + 1) / len(data) * 100
                print(
                    f"Finding cluster nº{len(indices) + 1} --> {progress:.2f}%",
                    end="\r",
                )
        indices.append(next_index)
        selected[next_index] = True

    return indices

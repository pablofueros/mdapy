"""Internal numerical core shared by the column and tuple APIs."""

import numpy as np
from numpy.typing import NDArray


def _distances_to_point(
    data: NDArray[np.float32],
    point_index: int,
    denominators: NDArray[np.float64],
    dir_indices: list[int] | None,
) -> NDArray[np.float64]:
    """Vectorize differences while preserving the historical norm reduction."""
    point = data[point_index]
    # Contiguous rows keep the same dot-product layout as the scalar reference.
    normalized = np.empty(data.shape, dtype=np.float32)
    for column in range(data.shape[1]):
        difference = data[:, column] - point[column]
        if dir_indices is not None and column in dir_indices:
            # NumPy 1.x and 2.x promote scalar float32 + integer differently.
            angular_dtype = np.asarray(np.float32(0) + 180).dtype
            difference = (difference.astype(angular_dtype) + 180) % 360 - 180
        # Scalar normalization uses float64 before storing back into float32.
        normalized[:, column] = difference.astype(np.float64) / denominators[column]

    # norm(axis=1) uses a different reduction and can alter float32 near ties.
    return np.fromiter(
        (np.linalg.norm(row) for row in normalized),
        dtype=np.float64,
        count=len(data),
    )


def _select_indices(
    data: NDArray[np.float32],
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
    denominators = np.sqrt(2) * np.asarray(deviations, dtype=np.float64)

    while len(indices) < n_clusters:
        distances = _distances_to_point(data, indices[-1], denominators, dir_indices)
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

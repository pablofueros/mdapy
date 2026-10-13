"""Public API for selecting maximally dissimilar observations."""

from functools import cached_property
from numbers import Integral

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.stats import circstd

from . import legacy


class DataColumn:
    """One scalar variable, optionally interpreted as angles in degrees."""

    def __init__(self, array: ArrayLike, *, directional: bool = False) -> None:
        if not isinstance(directional, bool):
            raise TypeError("directional must be a bool")
        values = np.asarray(array, dtype=np.float32)
        if values.ndim != 1:
            raise ValueError("Each data column must be one-dimensional")
        if not np.isfinite(values).all():
            raise ValueError("Data columns must contain only finite values")
        self.np_array: NDArray[np.float32] = values
        self.directional = directional

    def __len__(self) -> int:
        return len(self.np_array)

    @cached_property
    def standard_deviation(self) -> float:
        if self.directional:
            return float(circstd(self.np_array, high=360, low=0))
        return float(np.std(self.np_array))


_LEGACY_HINT = (
    "The tuple-based API is available from mdapy.legacy: "
    "from mdapy.legacy import max_diss_alg"
)


def max_diss_alg(
    *columns: DataColumn,
    n_clusters: int | None = None,
    seed_index: int = 0,
    **kwargs: object,
) -> tuple[NDArray[np.float32], list[int]]:
    """Select observations using columns and the maximum dissimilarity algorithm.

    ``n_clusters`` is required. Directional columns use degrees with a period
    of 360. Returns selected rows in selection order and their input indices.
    """
    if "data_tuple" in kwargs or "dir_indices" in kwargs:
        raise TypeError(_LEGACY_HINT)
    if kwargs:
        unexpected = next(iter(kwargs))
        raise TypeError(f"Unexpected keyword argument: {unexpected}")
    if columns and not all(isinstance(col, DataColumn) for col in columns):
        raise TypeError(f"Expected DataColumn arguments. {_LEGACY_HINT}")
    if not columns:
        raise ValueError("At least one DataColumn is required")
    if n_clusters is None:
        raise TypeError("n_clusters is required")
    if isinstance(n_clusters, bool) or not isinstance(n_clusters, Integral):
        raise TypeError("n_clusters must be an integer")
    if isinstance(seed_index, bool) or not isinstance(seed_index, Integral):
        raise TypeError("seed_index must be an integer")

    n_points = len(columns[0])
    if any(len(col) != n_points for col in columns):
        raise ValueError("All data columns must have the same length")
    if not 1 <= n_clusters <= n_points:
        raise ValueError("n_clusters must be between 1 and the number of rows")
    if not 0 <= seed_index < n_points:
        raise ValueError("seed_index is out of bounds")
    for index, col in enumerate(columns):
        if not np.isfinite(col.standard_deviation) or col.standard_deviation <= 0:
            raise ValueError(f"Column {index} has zero or undefined deviation")

    arrays = tuple(col.np_array for col in columns)
    dir_indices = [i for i, col in enumerate(columns) if col.directional]
    return legacy.max_diss_alg(
        arrays, int(n_clusters), int(seed_index), dir_indices, show_progress=False
    )

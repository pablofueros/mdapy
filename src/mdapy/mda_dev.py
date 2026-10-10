from functools import cached_property

import numpy as np
import numpy.typing as npt
from scipy.stats import circstd


class DataColumn:
    def __init__(self, array: npt.ArrayLike, *, directional: bool = False) -> None:
        self.np_array = self._process_and_validate_array(array)
        self.directional = directional

    def __len__(self) -> int:
        return self.np_array.size

    def _process_and_validate_array(self, array: npt.ArrayLike) -> npt.NDArray:
        np_array = np.asarray(array, dtype=np.float32)
        self._check_nan_values(np_array)
        self._check_dimensionality(np_array)
        return np_array

    def _check_nan_values(self, array: npt.NDArray) -> None:
        if np.isnan(array).any():
            raise ValueError("The data contains NaN values")

    def _check_dimensionality(self, array: npt.NDArray) -> None:
        if array.ndim != 1:
            raise ValueError("The data must be a 1D array")

    @cached_property
    def standard_deviation(self) -> np.float32:
        if self.directional:
            return circstd(self.np_array, high=360)
        return np.std(self.np_array)


def max_diss_alg(
    *columns: DataColumn,
    n_clusters: int = 10,
    seed_index: int = 0,
) -> tuple[npt.NDArray, npt.NDArray]:
    """
    Find dissimilar points using the Maximum Dissimilarity Algorithm.

    Args:
        *columns: Variable number of DataColumn objects containing arrays and their types.
        n_clusters: Number of dissimilar points to find.
        seed_index: Index of the first point to start the algorithm.

    Returns:
        tuple: (Selected points as NDArray, Indices of selected points as list)

    Example:
        >>> position = DataColumn(array1)  # regular data
        >>> theta = DataColumn(array2, directional=True)  # directional data
        >>> result = max_diss_alg(position, theta, n_clusters=5)

    Raises:
        - ValueError: If any column is not a DataColumn object.
        - ValueError: If no data columns are provided.
        - ValueError: If data columns have different lengths.
        - ValueError: If the seed index is out of bounds.
    """

    # Check if all columns are DataColumn objects
    if any(not isinstance(col, DataColumn) for col in columns):
        raise ValueError("All columns must be DataColumn objects")

    # Check if at least one data column is provided
    if not columns:
        raise ValueError("At least one data column must be provided")

    # Check if all data columns have the same length
    if len({len(col) for col in columns}) > 1:
        raise ValueError("All data columns must have the same length")

    # Check if the seed index is valid
    if seed_index < 0 or seed_index >= len(columns[0]):
        raise ValueError("The seed index is out of bounds")

    # Save the indices of the directional columns
    dir_indices = np.where([col.directional for col in columns])[0]

    # Initialize the data matrix and the subset indices
    matrix = np.array([col.np_array for col in columns]).T
    subset_indices = np.zeros(n_clusters, dtype=np.int32)

    # Set the seed index as the first point in the subset
    next_index = seed_index

    for ind in range(n_clusters):
        subset_indices[ind] = next_index

    # finder = MaximumDissimilarityFinder(matrix)
    # while len(subset_indices) < n_clusters:
    #     next_point_index = finder.find_next_point(subset_indices)
    #     if next_point_index > -1:
    #         subset_indices.append(next_point_index)

    # while len(subset_indices) < n_clusters:
    #     max_dist = next_point_index = -1
    #     for i_point in range(len(matrix)):
    #         if i_point in subset_indices:
    #             continue
    #         distance = distance_to_subset(matrix, i_point, subset_indices)
    #         if distance > max_dist:
    #             max_dist = distance
    #             next_point_index = i_point
    #     # Add the point with the maximum distance to the subset
    #     if next_point_index > -1:
    #         subset_indices.append(next_point_index)

    return matrix[subset_indices], subset_indices

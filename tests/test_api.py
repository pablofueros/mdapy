import numpy as np
import pytest

from mdapy import DataColumn, max_diss_alg
from mdapy.legacy import max_diss_alg as legacy_max_diss_alg


def test_column_api_selects_same_points_as_legacy(capsys):
    values = [0, 2, 5, 9]
    selected, indices = max_diss_alg(DataColumn(values), n_clusters=3)
    legacy_selected, legacy_indices = legacy_max_diss_alg(
        (values,), 3, show_progress=False
    )

    assert indices == [0, 3, 2] == legacy_indices
    np.testing.assert_array_equal(selected, legacy_selected)
    assert capsys.readouterr().out == ""


def test_directional_column_uses_shortest_angular_distance():
    values = [350, 10, 180]
    _, indices = max_diss_alg(DataColumn(values, directional=True), n_clusters=2)
    assert indices == [0, 2]


def test_mixed_columns_match_legacy_selection():
    heights = [1.0, 2.0, 5.0, 3.0]
    directions = [350.0, 10.0, 180.0, 90.0]
    selected, indices = max_diss_alg(
        DataColumn(heights),
        DataColumn(directions, directional=True),
        n_clusters=3,
        seed_index=1,
    )
    legacy_selected, legacy_indices = legacy_max_diss_alg(
        (heights, directions), 3, seed_index=1, dir_indices=[1], show_progress=False
    )
    assert indices == legacy_indices
    np.testing.assert_array_equal(selected, legacy_selected)


def test_seed_index_changes_selection_order():
    selected, indices = max_diss_alg(
        DataColumn([0, 2, 5, 9]), n_clusters=3, seed_index=2
    )

    assert indices == [2, 0, 3]
    assert selected.shape == (3, 1)
    np.testing.assert_array_equal(selected[:, 0], [5, 0, 9])


def test_equal_distances_select_first_input_index():
    _, indices = max_diss_alg(DataColumn([-2, 0, 2]), n_clusters=3, seed_index=1)

    assert indices == [1, 0, 2]


def test_mixed_columns_select_by_nearest_selected_point():
    # From 350°, 10° is only 20° away. After selecting 180°, the point at
    # 90° is farther from its nearest selected point than the point at 10°.
    selected, indices = max_diss_alg(
        DataColumn([0, 0, 4, 4]),
        DataColumn([350, 10, 180, 90], directional=True),
        n_clusters=3,
    )

    assert indices == [0, 2, 3]
    np.testing.assert_array_equal(selected, [[0, 350], [4, 180], [4, 90]])


def test_rescaling_one_column_preserves_selection_order():
    linear = [0, 3, 1, 2]
    angles = DataColumn([0, 10, 20, 170], directional=True)

    _, original_indices = max_diss_alg(DataColumn(linear), angles, n_clusters=3)
    _, scaled_indices = max_diss_alg(
        DataColumn([100 * value for value in linear]), angles, n_clusters=3
    )

    assert original_indices == scaled_indices == [0, 3, 1]


@pytest.mark.parametrize(
    "args, kwargs",
    [
        ((([0, 1, 2],), 2), {}),
        ((([0, 1, 2],),), {"n_clusters": 2}),
        ((), {"data_tuple": ([0, 1, 2],), "n_clusters": 2}),
        ((([0, 1, 2],),), {"n_clusters": 2, "dir_indices": [0]}),
    ],
)
def test_old_api_call_points_to_legacy(args, kwargs):
    with pytest.raises(TypeError, match="from mdapy.legacy import max_diss_alg"):
        max_diss_alg(*args, **kwargs)


def test_column_api_rejects_missing_or_out_of_range_cluster_count():
    column = DataColumn([0, 1, 2])
    with pytest.raises(TypeError, match="n_clusters is required"):
        max_diss_alg(column)
    with pytest.raises(ValueError, match="n_clusters must be between"):
        max_diss_alg(column, n_clusters=4)


def test_column_api_rejects_invalid_columns():
    with pytest.raises(ValueError, match="same length"):
        max_diss_alg(DataColumn([0, 1]), DataColumn([0, 1, 2]), n_clusters=1)
    with pytest.raises(ValueError, match="finite"):
        DataColumn([0, np.inf])
    with pytest.raises(ValueError, match="zero or undefined deviation"):
        max_diss_alg(DataColumn([1, 1]), n_clusters=1)


@pytest.mark.parametrize("scale", [1e-30, 1e20])
def test_deviation_is_calculated_before_float32_conversion(scale):
    values = np.array([0, scale, 2 * scale], dtype=np.float64)
    selected, indices = max_diss_alg(DataColumn(values), n_clusters=3)
    legacy_selected, legacy_indices = legacy_max_diss_alg(
        (values,), 3, show_progress=False
    )

    assert indices == legacy_indices == [0, 2, 1]
    assert selected.dtype == np.float32
    np.testing.assert_array_equal(selected, legacy_selected)

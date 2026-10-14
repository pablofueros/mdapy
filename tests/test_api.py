import numpy as np
import pytest

from mdapy import DataColumn, max_diss_alg


@pytest.mark.parametrize("dtype", [np.int64, np.float32, np.float64])
@pytest.mark.parametrize("directional", [False, True])
def test_column_owns_data_and_keeps_cached_deviation_consistent(dtype, directional):
    original = [350, 10, 180, 90] if directional else [0, 2, 5, 9]
    expected_indices = [0, 2, 3] if directional else [0, 3, 2]
    values = np.array(original, dtype=dtype)
    column = DataColumn(values, directional=directional)
    deviation = column.standard_deviation

    assert column.values.dtype == values.dtype
    assert not np.shares_memory(column.values, values)
    assert values.flags.writeable
    values[:] = 0

    np.testing.assert_array_equal(column.values, original)
    assert column.standard_deviation == deviation
    points, indices = max_diss_alg(column, n_clusters=3)
    assert indices == expected_indices
    np.testing.assert_array_equal(
        points[:, 0], np.array(original, dtype=np.float32)[expected_indices]
    )


def test_column_rejects_writes_through_public_array():
    column = DataColumn([0, 2, 5, 9])
    deviation = column.standard_deviation
    values = column.values

    with pytest.raises(ValueError, match="read-only"):
        values[0] = 100
    with pytest.raises(ValueError, match="WRITEABLE"):
        values.setflags(write=True)

    np.testing.assert_array_equal(column.values, [0, 2, 5, 9])
    assert column.standard_deviation == deviation


@pytest.mark.parametrize(
    "attribute, replacement", [("values", np.array([1, 2, 3])), ("directional", True)]
)
def test_column_public_properties_cannot_be_reassigned(attribute, replacement):
    column = DataColumn([0, 1, 2])
    with pytest.raises(AttributeError, match=attribute):
        setattr(column, attribute, replacement)


def test_column_api_selects_expected_points_without_progress(capsys):
    values = [0, 2, 5, 9]
    selected, indices = max_diss_alg(DataColumn(values), n_clusters=3)

    assert indices == [0, 3, 2]
    np.testing.assert_array_equal(selected[:, 0], [0, 9, 5])
    assert capsys.readouterr().out == ""


def test_column_api_can_show_progress(capsys):
    max_diss_alg(DataColumn([0, 1, 2]), n_clusters=2, show_progress=True)

    assert "Finding cluster nº2" in capsys.readouterr().out


@pytest.mark.parametrize("show_progress", [1, None])
def test_column_api_rejects_non_boolean_progress(show_progress):
    with pytest.raises(TypeError, match="show_progress must be a bool"):
        max_diss_alg(
            DataColumn([0, 1, 2]),
            n_clusters=2,
            show_progress=show_progress,
        )


def test_directional_column_uses_shortest_angular_distance():
    values = [350, 10, 180]
    _, indices = max_diss_alg(DataColumn(values, directional=True), n_clusters=2)
    assert indices == [0, 2]


def test_mixed_columns_select_expected_points():
    heights = [1.0, 2.0, 5.0, 3.0]
    directions = [350.0, 10.0, 180.0, 90.0]
    selected, indices = max_diss_alg(
        DataColumn(heights),
        DataColumn(directions, directional=True),
        n_clusters=3,
        seed_index=1,
    )

    assert indices == [1, 2, 3]
    np.testing.assert_array_equal(selected, [[2, 10], [5, 180], [3, 90]])


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
    "args, kwargs, message",
    [
        (
            (([0, 1, 2],), 2),
            {},
            "required keyword-only argument: 'n_clusters'",
        ),
        (
            (([0, 1, 2],),),
            {"n_clusters": 2},
            "from mdapy.legacy import max_diss_alg",
        ),
        (
            (),
            {"data_tuple": ([0, 1, 2],), "n_clusters": 2},
            "from mdapy.legacy import max_diss_alg",
        ),
        (
            (([0, 1, 2],),),
            {"n_clusters": 2, "dir_indices": [0]},
            "from mdapy.legacy import max_diss_alg",
        ),
    ],
)
def test_old_api_call_points_to_legacy(args, kwargs, message):
    with pytest.raises(TypeError, match=message):
        max_diss_alg(*args, **kwargs)


def test_column_api_rejects_out_of_range_cluster_count():
    column = DataColumn([0, 1, 2])
    with pytest.raises(ValueError, match="n_clusters must be between"):
        max_diss_alg(column, n_clusters=4)


def test_column_api_rejects_invalid_columns():
    with pytest.raises(ValueError, match="same length"):
        max_diss_alg(DataColumn([0, 1]), DataColumn([0, 1, 2]), n_clusters=1)
    with pytest.raises(ValueError, match="finite"):
        DataColumn([0, np.inf])
    empty = DataColumn([])
    with pytest.raises(ValueError, match="n_clusters must be between"):
        max_diss_alg(empty, n_clusters=1)


@pytest.mark.parametrize("directional", [False, True])
def test_algorithm_rejects_zero_deviation(directional):
    column = DataColumn([1, 1], directional=directional)
    with pytest.raises(ValueError, match="zero or undefined deviation"):
        max_diss_alg(column, n_clusters=1)


@pytest.mark.parametrize("scale", [1e-30, 1e20])
def test_deviation_is_calculated_before_float32_conversion(scale):
    values = np.array([0, scale, 2 * scale], dtype=np.float64)
    selected, indices = max_diss_alg(DataColumn(values), n_clusters=3)

    assert indices == [0, 2, 1]
    assert selected.dtype == np.float32
    np.testing.assert_array_equal(selected[:, 0], values[indices].astype(np.float32))

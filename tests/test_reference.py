"""Compare production APIs with the independent, unmodified historical core."""

import contextlib
import gc
import importlib.util
import json
import os
import weakref
from pathlib import Path

import numpy as np
import pytest

from mdapy import DataColumn, core, max_diss_alg
from mdapy.core import _distances_to_point
from mdapy.legacy import max_diss_alg as legacy_max_diss_alg

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / "benchmarks/cases.json").read_text())


@pytest.fixture(scope="module")
def reference():
    path = ROOT / "benchmarks/algorithms/v0_1_2.py"
    spec = importlib.util.spec_from_file_location("mda_reference", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    yield module
    module.DataMatrix.distance_between.cache_clear()


def assert_matches_reference(reference, arrays, directional, count, seed):
    with open(os.devnull, "w") as sink, contextlib.redirect_stdout(sink):
        expected_points, expected_indices = reference.max_diss_alg(
            arrays, count, seed, directional
        )
    columns = tuple(
        DataColumn(array, directional=index in directional)
        for index, array in enumerate(arrays)
    )
    points, indices = max_diss_alg(*columns, n_clusters=count, seed_index=seed)
    legacy_points, legacy_indices = legacy_max_diss_alg(
        arrays, count, seed, directional, show_progress=False
    )
    assert indices == legacy_indices == expected_indices
    assert points.dtype == legacy_points.dtype == np.float32
    np.testing.assert_array_equal(points, expected_points)
    np.testing.assert_array_equal(legacy_points, expected_points)
    reference.DataMatrix.distance_between.cache_clear()
    return indices


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
def test_reference_cases(reference, case):
    arrays = tuple(np.asarray(array, dtype=np.float64) for array in case["columns"])
    indices = assert_matches_reference(
        reference,
        arrays,
        case["directional"],
        len(case["expected"]),
        case["seed_index"],
    )
    assert indices == case["expected"]


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
@pytest.mark.parametrize("dimensions", [1, 3, 5])
@pytest.mark.parametrize("use_angles", [False, True])
def test_seeded_data_matches_reference(reference, dtype, dimensions, use_angles):
    rng = np.random.default_rng(20261012)
    directional = list(range(0, dimensions, 2)) if use_angles else []
    arrays = tuple(
        (
            rng.uniform(-720, 720, 24) if index in directional else rng.normal(size=24)
        ).astype(dtype)
        for index in range(dimensions)
    )
    for seed in (0, 11):
        for count in (1, 7, 24):
            assert_matches_reference(reference, arrays, directional, count, seed)


@pytest.mark.parametrize("dtype", [np.float32, np.float64])
@pytest.mark.parametrize("dimensions", [1, 2, 3, 5, 17])
def test_batched_distances_preserve_reference_rounding(reference, dtype, dimensions):
    rng = np.random.default_rng(20261012)
    directional = list(range(1, dimensions, 2))
    arrays = tuple(
        (
            rng.uniform(-720, 720, 100)
            if index in directional
            else rng.normal(size=100)
        ).astype(dtype)
        for index in range(dimensions)
    )
    matrix = reference.DataMatrix(arrays, directional)
    denominators = np.sqrt(2) * np.asarray(matrix.std_list, dtype=np.float64)
    distances = _distances_to_point(matrix.data, 11, denominators, directional)
    expected = np.array(
        [
            reference.distance(row, matrix.data[11], directional, matrix.std_list)
            for row in matrix.data
        ]
    )
    np.testing.assert_array_equal(distances, expected)


@pytest.mark.parametrize("use_legacy", [False, True])
def test_selection_does_not_retain_working_matrix(monkeypatch, use_legacy):
    matrices = []
    original = core._distances_to_point

    def observe_matrix(data, *args):
        matrices.append(weakref.ref(data))
        return original(data, *args)

    monkeypatch.setattr(core, "_distances_to_point", observe_matrix)
    values = np.array([0.0, 1.0, 2.0])
    if use_legacy:
        legacy_max_diss_alg((values,), 3, show_progress=False)
    else:
        max_diss_alg(DataColumn(values), n_clusters=3)
    gc.collect()
    assert matrices
    assert all(reference() is None for reference in matrices)

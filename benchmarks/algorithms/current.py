"""Adapt the public checkout API without copying its algorithm."""

from mdapy import DataColumn, max_diss_alg as select


def max_diss_alg(data_tuple, n_clusters, seed_index=0, dir_indices=None):
    directional = set(dir_indices or [])
    columns = tuple(
        DataColumn(array, directional=index in directional)
        for index, array in enumerate(data_tuple)
    )
    return select(*columns, n_clusters=n_clusters, seed_index=seed_index)

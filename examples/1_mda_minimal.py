"""Run a small maximum-dissimilarity selection that is easy to debug.

Suggested debugger path:

1. Step into ``max_diss_alg`` to see input validation and data preparation.
2. In ``_select_indices``, stop before the ``while`` loop.
3. Follow ``distances``, ``nearest`` and ``next_index`` during each iteration.
"""

import numpy as np

from mdapy import DataColumn, max_diss_alg

values = np.array([0.0, 2.0, 5.0, 9.0])

selected, indices = max_diss_alg(
    DataColumn(values),
    n_clusters=3,
    seed_index=0,
)

print(f"Input values: {values.tolist()}")
print(f"Selected indices: {indices}")
print(f"Selected values: {selected[:, 0].tolist()}")

assert indices == [0, 3, 2]
np.testing.assert_array_equal(selected[:, 0], [0.0, 9.0, 5.0])

# 👋 Welcome to the mdapy repository

## Installation

The new `DataColumn` API is currently under development. Install this checkout to try it:

```bash
pip install -e .
```

The previously published distribution is named `ihc-mdapy` and uses the
tuple-based API shown in the legacy section below.

---

## 📋 The Maximum Dissimilarity Algorithm
The Maximum Dissimilarity Algorithm is a technique used to select a specified number of data points from a larger dataset in such a way that the selected points are maximally dissimilar to each other. The algorithm is particularly useful in scenarios where you need to create diverse subsets of data for analysis or for initializing cluster centroids in clustering algorithms.

In this case, directional variables can also be considered, in which case, the distance between two angles is calculated as the shortest distance between the two angles in a circle. For example, the distance between 350° and 10° is 20°, not 340°. This is the approach used in this implementation of the algorithm (see [Guanche et al. (2013)](#1) for more details).

### Algorithm steps

1. Start with the observation at `seed_index` (default `0`).
2. For each unselected observation, find its distance to the nearest selected observation.
3. Select the observation with the greatest nearest distance. Repeat until `n_clusters` observations have been selected.

Distances are Euclidean after dividing each column's difference by its
standard deviation and `sqrt(2)`. Directional differences use the shortest
arc in degrees, and their standard deviation is circular. If two candidates
have exactly the same distance, the one appearing first in the input is
selected.

---

## Usage

Pass one `DataColumn` per variable. Each column must be one-dimensional, have
the same number of observations, and contain only finite values. Columns with
zero or undefined standard deviation are rejected. Directional columns are
angles in degrees. `n_clusters` is required and must be between 1 and the
number of observations; `seed_index` must be a valid input position.

Each `DataColumn` owns a copy of its input, preserving the input dtype.
Changing the original array does not change the column. Its `np_array`
property returns a read-only view, and neither `np_array` nor `directional`
can be reassigned. Create a new `DataColumn` to use different values or a
different directional interpretation. This keeps its cached standard
deviation consistent with its data; it requires an additional copy per column.

```python
from mdapy import DataColumn, max_diss_alg

tp = [14.93, 10.42, 7.46, 7.63, 12.20, 12.05, 14.49, 8.62]
hs = [1.82, 1.45, 0.26, 0.90, 1.30, 5.71, 1.40, 2.18]
direction = [268, 272, 289, 293, 276, 273, 276, 292]

points, indices = max_diss_alg(
    DataColumn(tp),
    DataColumn(hs),
    DataColumn(direction, directional=True),
    n_clusters=3,
)
```

Standard deviations are calculated using the input dtype, as in the legacy API.
The working matrix is then converted to `float32`. `points` is a `float32` NumPy array
of shape `(n_clusters, n_columns)` in selection order.
`indices` is a list of positions in the original input. The first position is
`seed_index` (default `0`).

### Legacy tuple API

Existing tuple-based calls can use an explicit import:

```python
from mdapy.legacy import max_diss_alg

points, indices = max_diss_alg((tp, hs, direction), 3, seed_index=0, dir_indices=[2])
```

Passing a tuple to `mdapy.max_diss_alg` raises an error explaining this import.

---

## ©️ Credits
Developed and maintained by 👨‍💻 [Pablo Garcia](https://github.com/pablofueros) @ 🏢 [IHCantabria](https://github.com/IHCantabria).

---

## 📚 References
<a id="1">[1]</a> Guanche, Y., Guanche, R., Camus, P., Mendez, F. J., & Medina, R. (2013). A multivariate approach to estimate design loads for offshore wind turbines. Wind Energy, 16(7), 1091-1106. (Apen)

---

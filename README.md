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

### Algorithm Steps
1. **Initialization**: Start with an empty subset, S. Choose the first data point arbitrarily or based on some criteria and add it to S.

2. **Iteration**: Repeat the following steps until you have selected the desired number of data points (n).

3. **Finding the Most Dissimilar Point**: For each data point not in S, calculate the minimum distance from that point to the points in S.

4. **Selecting the Maximum Dissimilarity Point**: Choose the data point with the greatest dissimilarity (maximum distance calculated in the previous step) and include it in subset S.

5. **Output**: Return the subset S, which contains n data points that are maximally dissimilar to each other.

---

## Usage

Pass one `DataColumn` per variable. Each column must contain one finite value
per observation. Directional columns are angles in degrees; `n_clusters` is
required and must be between 1 and the number of observations.

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

`points` is a `(n_clusters, n_columns)` NumPy array in selection order.
`indices` is a list of positions in the original input. The first position is
`seed_index` (default `0`).

### Legacy tuple API

Existing tuple-based calls can use an explicit import:

```python
from mdapy.legacy import max_diss_alg

points, indices = max_diss_alg(
    (tp, hs, direction), 3, seed_index=0, dir_indices=[2]
)
```

Passing a tuple to `mdapy.max_diss_alg` raises an error explaining this import.

---

## ©️ Credits
Developed and maintained by 👨‍💻 [Pablo Garcia](https://github.com/pablofueros) @ 🏢 [IHCantabria](https://github.com/IHCantabria).

---

## 📚 References
<a id="1">[1]</a> Guanche, Y., Guanche, R., Camus, P., Mendez, F. J., & Medina, R. (2013). A multivariate approach to estimate design loads for offshore wind turbines. Wind Energy, 16(7), 1091-1106. (Apen)

---

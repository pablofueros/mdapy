from time import perf_counter

import matplotlib.pyplot as plt
import numpy as np

from mdapy import DataColumn, max_diss_alg

with np.load("examples/data/datawave.npz") as datawave:
    indices = np.random.default_rng(42).integers(0, len(datawave["tp"]), 10_000)
    direction = datawave["dir"][indices]
    tp = datawave["tp"][indices]

seed_index = int(np.argmax(tp))
start = perf_counter()
selected, _ = max_diss_alg(
    DataColumn(direction, directional=True),
    DataColumn(tp),
    n_clusters=10,
    seed_index=seed_index,
)
print(f"Elapsed time: {perf_counter() - start:.2f} seconds")

plt.plot(direction, tp, ".", alpha=0.1)
plt.plot(selected[:, 0], selected[:, 1], "x", c="r")
plt.show()

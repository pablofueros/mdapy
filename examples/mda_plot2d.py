from time import perf_counter

import matplotlib.pyplot as plt
import numpy as np

from mdapy import DataColumn, max_diss_alg

rng = np.random.default_rng(42)
N_SAMPLES = 10_000

with np.load("examples/data/datawave.npz") as datawave:
    N_OBSERVATIONS = len(datawave["tp"])
    indices = rng.choice(N_OBSERVATIONS, size=N_SAMPLES, replace=False)
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

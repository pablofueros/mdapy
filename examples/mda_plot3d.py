import matplotlib.pyplot as plt
import numpy as np

from mdapy import DataColumn, max_diss_alg

with np.load("examples/data/datawave.npz") as datawave:
    indices = np.random.default_rng(42).integers(0, len(datawave["tp"]), 10_000)
    direction = datawave["dir"][indices]
    tp = datawave["tp"][indices]
    hs = datawave["hs"][indices]

# Select the seed point index and the number of clusters
seed_index = int(np.argmax(tp))
n_clusters = 10

# Select observations from three columns
clustered_data, _ = max_diss_alg(
    DataColumn(hs),
    DataColumn(tp),
    DataColumn(direction, directional=True),
    n_clusters=n_clusters,
    seed_index=seed_index,
)

# Plot the data points and the clustered ones
fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
ax.scatter(tp, direction, hs, c="b", marker=".", alpha=0.1)
ax.scatter(
    clustered_data[:, 1], clustered_data[:, 2], clustered_data[:, 0], c="r", marker="x"
)
plt.show()

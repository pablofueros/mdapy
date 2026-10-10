from time import time

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

from mdapy import max_diss_alg

# Load wave data (140_256 hours)
datawave = np.load("examples/data/datawave.npz")

# Generate a random sample of N_SHORT data points
indices = np.random.randint(0, 140_256, N_SHORT := 10_000)
dir: NDArray = datawave["dir"][indices]
tp: NDArray = datawave["tp"][indices]

# Select the seed point index and the number of clusters
seed_index = np.argmax(tp).astype(int)
n_clusters = 10

# Cluster the data array (2D)
time_start = time()
clustered_data, _ = max_diss_alg((dir, tp), n_clusters, seed_index, dir_indices=[0])
time_end = time()

print(f"Elapsed time: {time_end - time_start:.2f} seconds")
raise SystemExit

# Plot the data points and the clustered ones
plt.plot(dir, tp, ".", alpha=0.1)
plt.plot(clustered_data[:, 0], clustered_data[:, 1], "x", c="r")
plt.show()

import numpy as np


def angular_distance(point1, point2):
    dist = ((point1 - point2) + 180) % 360 - 180
    return np.linalg.norm(dist)


def regular_distance(point1, point2):
    dist = point1 - point2
    return np.linalg.norm(dist)

import numpy as np

from mdapy.core import _distances_to_point

# Common variable used in tests
std_list = [1 / np.sqrt(2)] * 2


def distance(point1, point2, directional):
    data = np.array([point1, point2], dtype=np.float32)
    denominators = np.sqrt(2) * np.asarray(std_list)
    return _distances_to_point(data, 1, denominators, directional)[0]


def test_distance_for_scalar():
    point1 = np.array([0, 0])
    point2 = np.array([1, 1])
    result = distance(point1, point2, None)
    assert result == np.float32(np.sqrt(2))


def test_distance_for_directional():
    point1 = np.array([0, -5])
    point2 = np.array([10, 5])
    result = distance(point1, point2, [0, 1])
    assert result == np.float32(np.sqrt(200))


def test_distance_for_scalar_and_directional():
    point1 = np.array([1, -5])
    point2 = np.array([-1, 5])
    result = distance(point1, point2, [0, 1])
    assert result == np.float32(np.sqrt(104))

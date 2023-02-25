import numpy as np
from scipy.spatial.distance import cdist
from itertools import permutations

"""
FORKED

TODO: update the function implementing vector
"""

def find_path(points):

    points_array = np.array([(p[0], p[1]) for p in points])

    distances = cdist(points_array, points_array)

    def route_distace(route):
        return sum([distances[route[i], route[i+1]] for i in range(len(route) - 1)])
    
    all_route = permutations(range(len(points)))

    shortest_route = min(all_route, key=route_distace)

    shortest_path = [points[i] for i in shortest_route]

    return shortest_path
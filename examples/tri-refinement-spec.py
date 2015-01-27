# Provided by Liu Benyuan in https://github.com/inducer/meshpy/pull/11

from __future__ import division

import meshpy.triangle as triangle
import numpy as np
from matplotlib.path import Path

def round_trip_connect(start, end):
    return [(i, i+1) for i in range(start, end)] + [(end, start)]

def main():
    points = [(1, 0), (1, 1), (-1, 1), (-1, -1), (1, -1), (1, 0)]
    facets = round_trip_connect(0, len(points)-1)

    circ_start = len(points)
    points.extend(
            (3 * np.cos(angle), 3 * np.sin(angle))
            for angle in np.linspace(0, 2*np.pi, 30, endpoint=False))
    facets.extend(round_trip_connect(circ_start, len(points)-1))

    markers = [2,2,2,2,2,2]
    markers.extend(list(np.ones(30, dtype='int')))
    markers = [int(i) for i in markers]

    info = triangle.MeshInfo()
    info.set_points(points)
    info.set_facets(facets, facet_markers=markers)
    #
    info.regions.resize(1)
    # points [x,y] in region, + region number, + regional area constraints
    info.regions[0] = ([0,0] + [1,0.05])

    mesh = triangle.build(info, volume_constraints=True, max_volume=0.1)

    mesh_points = np.array(mesh.points)
    mesh_tris = np.array(mesh.elements)
    mesh_attr = np.array(mesh.point_markers)
    print(mesh_attr)

    import matplotlib.pyplot as plt
    plt.triplot(mesh_points[:, 0], mesh_points[:, 1], mesh_tris)
    plt.xlabel('x')
    plt.ylabel('y')
    #
    fig = plt.gcf()
    fig.set_size_inches(4.2, 4.2)
    plt.savefig('sec5-meshpy-triangle-ex4.pdf')

if __name__ == "__main__":
    main()

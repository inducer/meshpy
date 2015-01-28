# Provided by Liu Benyuan in https://github.com/inducer/meshpy/pull/11

from __future__ import division

import meshpy.triangle as triangle
import numpy as np

def round_trip_connect(start, end):
    return [(i, i+1) for i in range(start, end)] + [(end, start)]

def refinement_func(tri_points, area):
    max_area=0.1
    return bool(area>max_area);

def main():
    points = [(1, 0), (1, 1), (-1, 1), (-1, -1), (1, -1), (1, 0)]
    facets = round_trip_connect(0, len(points)-1)
    markers = [2,2,2,2,2,2]

    outter_start = len(points)
    points.extend([(2, 0), (2, 2), (-2, 2), (-2, -2), (2, -2), (2, 0)])
    facets.extend(round_trip_connect(outter_start, len(points) - 1))
    markers.extend([3,3,3,3,3,3])

    # build
    info = triangle.MeshInfo()
    info.set_points(points)
    info.set_holes([(0, 0)])
    info.set_facets(facets, facet_markers=markers)

    #
    mesh = triangle.build(info, refinement_func=refinement_func)

    #
    mesh_points = np.array(mesh.points)
    mesh_tris = np.array(mesh.elements)
    mesh_attr = np.array(mesh.point_markers)

    print(mesh_attr)

    import matplotlib.pyplot as plt
    plt.triplot(mesh_points[:, 0], mesh_points[:, 1], mesh_tris)
    plt.xlabel('x')
    plt.ylabel('y')
    #
    n = np.size(mesh_attr);
    inner_nodes = [i for i in range(n) if mesh_attr[i]==2]
    outer_nodes = [i for i in range(n) if mesh_attr[i]==3]
    plt.plot(mesh_points[inner_nodes, 0], mesh_points[inner_nodes, 1], 'ro')
    plt.plot(mesh_points[outer_nodes, 0], mesh_points[outer_nodes, 1], 'go')
    plt.axis([-2.5, 2.5, -2.5, 2.5])
    #plt.show()
    #
    fig = plt.gcf()
    fig.set_size_inches(4.2, 4.2)
    plt.savefig('sec5-meshpy-triangle-ex5.pdf')

if __name__ == "__main__":
    main()

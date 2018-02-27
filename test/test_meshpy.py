from __future__ import division, absolute_import, print_function

__copyright__ = "Copyright (C) 2013 Andreas Kloeckner"

__license__ = """
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from six.moves import range


# {{{ triangle

def test_triangle_refine():
    import meshpy.triangle as triangle
    import math

    segments = 50

    points = [(1, 0), (1, 1), (-1, 1), (-1, -1), (1, -1)]
    n_outer_points = len(points)

    for i in range(0, segments):
        angle = i * 2 * math.pi / segments
        points.append((0.5 * math.cos(angle), 0.5 * math.sin(angle)))

    def round_trip_connect(start, end):
        result = []
        for i in range(start, end):
            result.append((i, i+1))
        result.append((end, start))
        return result

    def needs_refinement(vertices, area):
        vert_origin, vert_destination, vert_apex = vertices
        bary_x = (vert_origin.x + vert_destination.x + vert_apex.x) / 3
        bary_y = (vert_origin.y + vert_destination.y + vert_apex.y) / 3

        dist_center = math.sqrt(bary_x**2 + bary_y**2)
        max_area = 100*(math.fabs(0.002 * (dist_center-0.3)) + 0.0001)
        return area > max_area

    info = triangle.MeshInfo()
    info.set_points(points)
    info.set_holes([(0, 0)])
    info.set_facets(
        round_trip_connect(0, n_outer_points-1)
        +
        round_trip_connect(n_outer_points, len(points)-1))

    mesh = triangle.build(info, refinement_func=needs_refinement)

    triangle.write_gnuplot_mesh("triangles-unrefined.dat", mesh)

    mesh.element_volumes.setup()

    for i in range(len(mesh.elements)):
        mesh.element_volumes[i] = -1
    for i in range(0, len(mesh.elements), 10):
        mesh.element_volumes[i] = 1e-8

    mesh = triangle.refine(mesh)

# }}}


# {{{ tetgen

def test_tetgen():
    from meshpy.tet import MeshInfo, build
    mesh_info = MeshInfo()

    mesh_info.set_points([
        (0, 0, 0),
        (2, 0, 0),
        (2, 2, 0),
        (0, 2, 0),
        (0, 0, 12),
        (2, 0, 12),
        (2, 2, 12),
        (0, 2, 12),
        ])

    mesh_info.set_facets([
        [0, 1, 2, 3],
        [4, 5, 6, 7],
        [0, 4, 5, 1],
        [1, 5, 6, 2],
        [2, 6, 7, 3],
        [3, 7, 4, 0],
        ])

    build(mesh_info)


def test_torus():
    from math import pi, cos, sin
    from meshpy.tet import MeshInfo, build
    from meshpy.geometry import generate_surface_of_revolution, \
            EXT_CLOSED_IN_RZ, GeometryBuilder

    big_r = 3
    little_r = 2.9

    points = 50
    dphi = 2*pi/points

    rz = [(big_r+little_r*cos(i*dphi), little_r*sin(i*dphi))
            for i in range(points)]

    geob = GeometryBuilder()
    geob.add_geometry(*generate_surface_of_revolution(rz,
            closure=EXT_CLOSED_IN_RZ, radial_subdiv=20))

    mesh_info = MeshInfo()
    geob.set(mesh_info)

    build(mesh_info)


def test_tetgen_points():
    from meshpy.tet import MeshInfo, build, Options

    import numpy as np
    points = np.random.randn(10000, 3)

    mesh_info = MeshInfo()
    mesh_info.set_points(points)
    options = Options("")
    mesh = build(mesh_info, options=options)

    print(len(mesh.points))
    print(len(mesh.elements))

    #mesh.write_vtk("test.vtk")

# }}}


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        exec(sys.argv[1])
    else:
        from pytest import main
        main([__file__])

# vim: foldmethod=marker

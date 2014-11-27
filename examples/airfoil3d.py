from __future__ import absolute_import
from __future__ import print_function
from six.moves import zip
def main():
    import numpy
    #from math import pi, cos, sin
    from meshpy.tet import MeshInfo, build
    from meshpy.geometry import GeometryBuilder, Marker, \
            generate_extrusion, make_box

    from meshpy.naca import get_naca_points

    geob = GeometryBuilder()

    box_marker = Marker.FIRST_USER_MARKER

    wing_length = 2
    wing_subdiv = 5

    rz_points = [
            (0, -wing_length*1.05),
            (0.7, -wing_length*1.05),
            ] + [
                (r, x) for x, r in zip(
                    numpy.linspace(-wing_length, 0, wing_subdiv, endpoint=False),
                    numpy.linspace(0.8, 1, wing_subdiv, endpoint=False))
            ] + [(1, 0)] + [
                (r, x) for x, r in zip(
                    numpy.linspace(wing_length, 0, wing_subdiv, endpoint=False),
                    numpy.linspace(0.8, 1, wing_subdiv, endpoint=False))
            ][::-1] + [
            (0.7, wing_length*1.05),
            (0, wing_length*1.05)
            ]

    geob.add_geometry(*generate_extrusion(
        rz_points=rz_points,
        base_shape=get_naca_points("0012", verbose=False, number_of_points=20),
        ring_markers=(wing_subdiv*2+4)*[box_marker]))

    from meshpy.tools import make_swizzle_matrix
    swizzle_matrix = make_swizzle_matrix("z:x,y:y,x:z")
    geob.apply_transform(lambda p: numpy.dot(swizzle_matrix, p))

    def deform_wing(p):
        x, y, z = p
        return numpy.array([
            x,
            y + 0.1*abs(x/wing_length)**2,
            z + 0.8*abs(x/wing_length) ** 1.2])

    geob.apply_transform(deform_wing)

    points, facets, _, facet_markers = make_box(
            numpy.array([-wing_length-1, -1, -1.5]),
            numpy.array([wing_length+1, 1, 3]))

    geob.add_geometry(points, facets, facet_markers=facet_markers)

    mesh_info = MeshInfo()
    geob.set(mesh_info)
    mesh_info.set_holes([(0, 0, 0.5)])

    mesh = build(mesh_info)
    print("%d elements" % len(mesh.elements))
    mesh.write_vtk("airfoil3d.vtk")


if __name__ == "__main__":
    main()

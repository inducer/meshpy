from __future__ import absolute_import
from __future__ import print_function
def main():
    import numpy
    from meshpy.tet import MeshInfo, build
    from meshpy.geometry import GeometryBuilder, Marker, make_box

    geob = GeometryBuilder()

    box_marker = Marker.FIRST_USER_MARKER
    extent_small = 0.3*numpy.ones(3, dtype=numpy.float64)
    points, facets, _, _ = \
            make_box(-extent_small, extent_small)

    geob.add_geometry(points, facets, facet_markers=box_marker)

    points, facets, _, facet_markers = \
            make_box(numpy.array([-1, -1, -1]), numpy.array([1, 1, 5]))

    geob.add_geometry(points, facets, facet_markers=facet_markers)

    mesh_info = MeshInfo()
    geob.set(mesh_info)
    #mesh_info.set_holes([(0, 0, 0)])

    # region attributes
    mesh_info.regions.resize(1)
    mesh_info.regions[0] = (
            # point in region
            [0, 0, 0] + [
                # region number
                1,
                # max volume in region
                0.001])

    mesh = build(mesh_info, max_volume=0.06,
            volume_constraints=True, attributes=True)
    print(("%d elements" % len(mesh.elements)))
    mesh.write_vtk("box-in-box.vtk")


if __name__ == "__main__":
    main()

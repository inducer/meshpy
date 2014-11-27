from __future__ import absolute_import
from __future__ import print_function
def main():
    from ply import parse_ply
    import sys
    data = parse_ply(sys.argv[1])

    from meshpy.geometry import GeometryBuilder

    builder = GeometryBuilder()
    builder.add_geometry(
            points=[pt[:3] for pt in data["vertex"].data],
            facets=[fd[0] for fd in data["face"].data])
    builder.wrap_in_box(1)

    from meshpy.tet import MeshInfo, build
    mi = MeshInfo()
    builder.set(mi)
    mi.set_holes([builder.center()])
    mesh = build(mi)
    print("%d elements" % len(mesh.elements))
    mesh.write_vtk("out.vtk")


if __name__ == "__main__":
    main()

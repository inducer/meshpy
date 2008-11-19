def main():
    from ply import parse_ply
    import sys
    data = parse_ply(sys.argv[1])

    from meshpy.tet import MeshInfo, build, Options

    mi = MeshInfo()
    mi.set_points([pt[:3] for pt in data["vertex"].data])
    mi.set_facets([fd[0] for fd in data["face"].data])
    mesh = build(mi)
    mesh.write_vtk("out.vtk")


if __name__ == "__main__":
    main()

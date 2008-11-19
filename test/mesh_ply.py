def main():
    from ply import parse_ply
    import sys
    data = parse_ply(sys.argv[1])

    from meshpy.tet import MeshInfo, build, Options

    #points, facets, facet_holestarts, markers =

    
    import numpy
    ply_points = numpy.array([pt[:3] for pt in data["vertex"].data])
    ply_facets = numpy.array([fd[0] for fd in data["face"].data])
    a, b = numpy.min(ply_points, axis=0), numpy.max(ply_points, axis=0)

    a = a - 1
    b = b + 1

    #    7--------6
    #   /|       /|
    #  4--------5 |  z
    #  | |      | |  ^
    #  | 3------|-2  | y
    #  |/       |/   |/
    #  0--------1    +--->x

    bbox_points = [
            (a[0],a[1],a[2]),
            (b[0],a[1],a[2]),
            (b[0],b[1],a[2]),
            (a[0],b[1],a[2]),
            (a[0],a[1],b[2]),
            (b[0],a[1],b[2]),
            (b[0],b[1],b[2]),
            (a[0],b[1],b[2]),
            ]

    bbox_facets = [
            (0,1,2,3),
            (0,1,5,4),
            (1,2,6,5),
            (7,6,2,3),
            (7,3,0,4),
            (4,5,6,7)
            ]

    mi = MeshInfo()
    mi.set_points(bbox_points+list(ply_points))
    mi.set_facets(bbox_facets+list((ply_facets + len(bbox_points))))
    mi.set_holes([(a+b)/2])
    mesh = build(mi)
    mesh.write_vtk("out.vtk")


if __name__ == "__main__":
    main()

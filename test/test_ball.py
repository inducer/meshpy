def main():
    from math import pi, cos, sin
    from meshpy.tet import MeshInfo, build, generate_surface_of_revolution,\
            EXT_OPEN

    r = 3

    points = 10
    dphi = pi/points

    def truncate(r):
        if abs(r) < 1e-10:
            return 0
        else:
            return r

    rz = [(truncate(r*sin(i*dphi)), r*cos(i*dphi)) for i in range(points+1)]

    mesh_info = MeshInfo()
    points, facets = generate_surface_of_revolution(rz,
            closure=EXT_OPEN, radial_subdiv=10)

    mesh_info.set_points(points)
    mesh_info.set_facets(facets, [1 for i in range(len(facets))])
    mesh = build(mesh_info)
    mesh.write_vtk("ball.vtk")

    #mesh.write_neu(file("torus.neu", "w"),
            #{1: ("pec", 0)})




if __name__ == "__main__":
    main()

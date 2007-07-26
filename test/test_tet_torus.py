def main():
    from math import pi, cos, sin
    from meshpy.tet import MeshInfo, build, generate_surface_of_revolution,\
            EXT_CLOSED_IN_RZ

    big_r = 3
    little_r = 2.9

    points = 50
    dphi = 2*pi/points

    rz = [(big_r+little_r*cos(i*dphi), little_r*sin(i*dphi))
            for i in range(points)]

    mesh_info = MeshInfo()
    points, facets = generate_surface_of_revolution(rz,
            closure=EXT_CLOSED_IN_RZ, radial_subdiv=20)

    mesh_info.set_points(points)
    mesh_info.set_facets(facets, len(facets) *[1])
    mesh_info.save_nodes("torus")
    mesh_info.save_poly("torus")
    mesh = build(mesh_info)
    mesh.write_vtk("torus.vtk")
    mesh.save_elements("torus_mesh")
    mesh.save_nodes("torus_mesh")

    mesh.write_neu(file("torus.neu", "w"),
            {1: ("pec", 0)})




if __name__ == "__main__":
    main()


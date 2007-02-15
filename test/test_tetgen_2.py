from meshpy.tet import MeshInfo, build, generate_surface_of_revolution




def main():
    simple_rz = [
        (0,0),
        (1,1),
        (1,2),
        (0,3),
        ]
    mesh_info = MeshInfo()
    points, facets = generate_surface_of_revolution(simple_rz)

    mesh_info.set_points(points)
    mesh_info.set_facets(facets, [0 for i in range(len(facets))])
    #mesh_info.save_nodes("test")
    #mesh_info.save_poly("test")
    #mesh_info.load_poly("test")
    mesh = build(mesh_info)
    mesh.write_vtk("my_mesh.vtk")
    #mesh.save_elements("gun")
    #mesh.save_nodes("gun")




if __name__ == "__main__":
    main()

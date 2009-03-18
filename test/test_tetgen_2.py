



def main():
    from meshpy.tet import MeshInfo, build
    from meshpy.geometry import \
            generate_surface_of_revolution, \
            GeometryBuilder

    simple_rz = [
        (0,0),
        (1,1),
        (1,2),
        (0,3),
        ]


    geob = GeometryBuilder()
    geob.add_geometry(*generate_surface_of_revolution(simple_rz))

    mesh_info = MeshInfo()
    geob.set(mesh_info)

    #mesh_info.save_nodes("test")
    #mesh_info.save_poly("test")
    #mesh_info.load_poly("test")
    mesh = build(mesh_info)
    mesh.write_vtk("my_mesh.vtk")
    #mesh.save_elements("gun")
    #mesh.save_nodes("gun")




if __name__ == "__main__":
    main()

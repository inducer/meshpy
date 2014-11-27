def main():
    from math import pi, cos, sin
    from meshpy.tet import MeshInfo, build
    from meshpy.geometry import \
            generate_surface_of_revolution, EXT_OPEN, \
            GeometryBuilder

    r = 1
    l = 1

    rz = [(0,0), (r,0), (r,l), (0,l)]

    geob = GeometryBuilder()
    geob.add_geometry(*generate_surface_of_revolution(rz,
            radial_subdiv=20, ring_markers=[1,2,3]))

    mesh_info = MeshInfo()
    geob.set(mesh_info)

    mesh = build(mesh_info, max_volume=0.01)
    mesh.write_vtk("cylinder.vtk")
    mesh.write_neu(open("cylinder.neu", "w"), {
        1: ("minus_z", 1),
        2: ("outer", 2),
        3: ("plus_z", 3),
        })

if __name__ == "__main__":
    main()

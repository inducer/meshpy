def main():
    from math import cos, pi, sin

    from meshpy.geometry import (
        EXT_CLOSED_IN_RZ,
        GeometryBuilder,
        generate_surface_of_revolution,
    )
    from meshpy.tet import MeshInfo, build

    big_r = 3
    little_r = 2.9

    points = 50
    dphi = 2 * pi / points

    rz = [
        (big_r + little_r * cos(i * dphi), little_r * sin(i * dphi))
        for i in range(points)
    ]

    geob = GeometryBuilder()
    geob.add_geometry(
        *generate_surface_of_revolution(rz, closure=EXT_CLOSED_IN_RZ,
            radial_subdiv=20)
    )

    mesh_info = MeshInfo()
    geob.set(mesh_info)

    mesh_info.save_nodes("torus")
    mesh_info.save_poly("torus")
    mesh = build(mesh_info)
    mesh.write_vtk("torus.vtk")
    mesh.save_elements("torus_mesh")
    mesh.save_nodes("torus_mesh")

    mesh.write_neu(open("torus.neu", "w"), {1: ("pec", 0)})


if __name__ == "__main__":
    main()

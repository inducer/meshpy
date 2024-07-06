def main():
    from math import cos, pi, sin

    from meshpy.geometry import (
        EXT_OPEN,
        GeometryBuilder,
        generate_surface_of_revolution,
    )
    from meshpy.tet import MeshInfo, build

    r = 3

    points = 10
    dphi = pi / points

    def truncate(r):
        if abs(r) < 1e-10:
            return 0
        else:
            return r

    rz = [(truncate(r * sin(i * dphi)), r * cos(i * dphi))
            for i in range(points + 1)]

    geob = GeometryBuilder()
    geob.add_geometry(
        *generate_surface_of_revolution(rz, closure=EXT_OPEN, radial_subdiv=10)
    )

    mesh_info = MeshInfo()
    geob.set(mesh_info)

    mesh = build(mesh_info)
    mesh.write_vtk("ball.vtk")

    # mesh.write_neu(file("torus.neu", "w"),
    # {1: ("pec", 0)})


if __name__ == "__main__":
    main()

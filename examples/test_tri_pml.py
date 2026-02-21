def main():
    from meshpy import triangle

    points = [
        (-5, -1),
        (-1, -1),
        (0, -1),
        (0, 0),
        (1, 0),
        (5, 0),
        (5, 1),
        (1, 1),
        (-1, 1),
        (-5, 1),
    ]

    def round_trip_connect(seq):
        n = len(seq)
        return [(seq[i], seq[(i + 1) % n]) for i in range(n)]

    info = triangle.MeshInfo()
    info.set_points(points)

    info.set_facets(
        round_trip_connect([0, 1, 8, 9])
        + round_trip_connect([1, 2, 3, 4, 7, 8])
        + round_trip_connect([4, 5, 6, 7])
    )
    info.regions.resize(3)
    info.regions[0] = (-2, 0, 1, 0.1)
    info.regions[1] = (-0.5, 0, 0, 0.01)
    info.regions[2] = (1.5, 0.5, 1, 0.1)

    mesh = triangle.build(info)

    triangle.write_gnuplot_mesh("triangles.dat", mesh)

    with open("tri_pml.enu", "w") as f:
        mesh.write_neu(f)


if __name__ == "__main__":
    main()

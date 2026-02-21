def main():
    import numpy as np

    from meshpy import triangle

    points = [(1, 1), (-1, 1), (-1, -1), (1, -1)]

    rng = np.random.default_rng(seed=42)
    points.extend(0.1 * rng.normal(size=(100, 2)))

    def round_trip_connect(start, end):
        result = [(i, i + 1) for i in range(start, end)]
        result.append((end, start))
        return result

    info = triangle.MeshInfo()
    info.set_points(points)
    info.set_facets(round_trip_connect(0, 3))

    mesh = triangle.build(
        info, allow_volume_steiner=False, allow_boundary_steiner=False
    )

    triangle.write_gnuplot_mesh("triangles.dat", mesh)


if __name__ == "__main__":
    main()

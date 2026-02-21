def main():
    from meshpy import triangle

    points = [(1, 1), (-1, 1), (-1, -1), (1, -1)]

    def round_trip_connect(start, end):
        result = [(i, i + 1) for i in range(start, end)]
        result.append((end, start))
        return result

    info = triangle.MeshInfo()
    info.set_points(points)
    info.set_facets(round_trip_connect(0, len(points) - 1))

    mesh = triangle.build(info, max_volume=1e-3, min_angle=25)

    print("A")
    triangle.write_gnuplot_mesh("triangles.dat", mesh)


if __name__ == "__main__":
    main()

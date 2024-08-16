def main():
    import meshpy.triangle as triangle

    info = triangle.MeshInfo()
    info.set_points([(1.5, 1), (-1.2, 1), (-1, -1), (1, -1)])
    info.set_facets([(0, 1), (1, 2), (2, 3), (3, 0)])

    mesh = triangle.build(info, max_volume=1e-3, min_angle=25)

    print(
        f"""
        <?xml version="1.0" encoding="UTF-8"?>

        <dolfin xmlns:dolfin="http://www.fenics.org/dolfin/">
          <mesh celltype="triangle" dim="2">
            <vertices size="{len(mesh.points)}">
        """
    )

    for i, pt in enumerate(mesh.points):
        print(f'<vertex index="{i}" x="{pt[0]}" y="{pt[1]}"/>')

    print(
        f"""
        </vertices>
        <cells size="{len(mesh.elements)}">
        """
    )

    for i, element in enumerate(mesh.elements):
        print(
            f'<triangle index="{i}" '
            f'v0="{element[0]}" v1="{element[1]}" v2="{element[2]}"/>'
        )

    print(
        """
            </cells>
          </mesh>
        </dolfin>
        """
    )


if __name__ == "__main__":
    main()

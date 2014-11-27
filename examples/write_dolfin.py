from __future__ import absolute_import
from __future__ import print_function
def main():
    import meshpy.triangle as triangle

    info = triangle.MeshInfo()
    info.set_points([ (1.5,1),(-1.2,1),(-1,-1),(1,-1)])
    info.set_facets([(0, 1), (1, 2), (2, 3), (3, 0)])

    mesh = triangle.build(info, max_volume=1e-3, min_angle=25)

    print("""
        <?xml version="1.0" encoding="UTF-8"?>

        <dolfin xmlns:dolfin="http://www.fenics.org/dolfin/">
          <mesh celltype="triangle" dim="2">
            <vertices size="%d">
        """ % len(mesh.points))

    for i, pt in enumerate(mesh.points):
      print('<vertex index="%d" x="%g" y="%g"/>' % (
              i, pt[0], pt[1]))

    print("""
        </vertices>
        <cells size="%d">
        """ % len(mesh.elements))

    for i, element in enumerate(mesh.elements):
      print('<triangle index="%d" v0="%d" v1="%d" v2="%d"/>' % (
              i, element[0], element[1], element[2]))

    print("""
            </cells>
          </mesh>
        </dolfin>
        """)

if __name__ == "__main__":
    main()


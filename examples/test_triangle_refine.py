from __future__ import absolute_import
from __future__ import print_function
from six.moves import range
def main():
    import meshpy.triangle as triangle
    import math
    import pickle

    segments = 50

    points = [ (1,0),(1,1),(-1,1),(-1,-1),(1,-1),(1,0) ]

    for i in range( 0, segments + 1 ):
      angle = i * 2 * math.pi / segments
      points.append( ( 0.5 * math.cos( angle ), 0.5 * math.sin( angle ) ) )

    def round_trip_connect(start, end):
      result = []
      for i in range(start, end):
        result.append((i, i+1))
      result.append((end, start))
      return result

    def needs_refinement(vertices, area ):
        vert_origin, vert_destination, vert_apex = vertices
        bary_x = (vert_origin.x + vert_destination.x + vert_apex.x) / 3
        bary_y = (vert_origin.y + vert_destination.y + vert_apex.y) / 3

        dist_center = math.sqrt( bary_x**2 + bary_y**2 )
        max_area = 100*(math.fabs( 0.002 * (dist_center-0.5) ) + 0.0001)
        return area > max_area

    info = triangle.MeshInfo()
    info.set_points(points)
    info.set_holes([(0,0)])
    info.set_facets(round_trip_connect(0, len(points)-1))

    mesh = triangle.build(info, refinement_func=needs_refinement,
            )

    triangle.write_gnuplot_mesh("triangles-unrefined.dat", mesh)
    print(len(mesh.elements))

    mesh.element_volumes.setup()

    for i in range(len(mesh.elements)):
        mesh.element_volumes[i] = -1
    for i in range(0, len(mesh.elements), 10):
        mesh.element_volumes[i] = 1e-8

    mesh = triangle.refine(mesh)
    print(len(mesh.elements))

    triangle.write_gnuplot_mesh("triangles.dat", mesh)

if __name__ == "__main__":
    main()

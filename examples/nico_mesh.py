from __future__ import absolute_import
from six.moves import range
def main():
    import meshpy.triangle as triangle
    import math

    points = [ (1,1),(-1,1),(-1,-1),(1,-1) ]

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

        dist_center = math.sqrt( (bary_x-1)**2 + (bary_y-1)**2 )
        max_area = math.fabs( 0.05 * (dist_center-0.5) ) + 0.01
        return area > max_area

    info = triangle.MeshInfo()
    info.set_points(points)
    info.set_facets(round_trip_connect(0, len(points)-1))

    mesh = triangle.build(info, refinement_func=needs_refinement)

    mesh.write_neu(open("nico.neu", "w"))
    triangle.write_gnuplot_mesh("triangles.dat", mesh)

if __name__ == "__main__":
    main()

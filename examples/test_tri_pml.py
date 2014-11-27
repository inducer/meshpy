from __future__ import absolute_import
from six.moves import range
def main():
    import meshpy.triangle as triangle
    import math
    import pickle

    segments = 50

    points = [(-5,-1), (-1,-1), (0,-1), (0,0), (1,0), (5,0), (5,1), (1,1),
      (-1,1), (-5,1)]

    def round_trip_connect(seq):
      result = []
      for i in range(len(seq)):
        result.append((seq[i], seq[(i+1)%len(seq)]))
      return result

    info = triangle.MeshInfo()
    info.set_points(points)

    info.set_facets(
            round_trip_connect([0,1,8,9])
            +round_trip_connect([1,2,3,4,7,8])
            +round_trip_connect([4,5,6,7])
            )
    info.regions.resize(3)
    info.regions[0] = (-2,0,     1,0.1)
    info.regions[1] = (-0.5,0,   0,0.01)
    info.regions[2] = (1.5,0.5,  1,0.1)

    mesh = triangle.build(info)

    triangle.write_gnuplot_mesh("triangles.dat", mesh)

    mesh.write_neu(open("tri_pml.neu", "w"))




if __name__ == "__main__":
    main()

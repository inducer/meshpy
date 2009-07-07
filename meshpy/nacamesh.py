from __future__ import division

import numpy
import numpy.linalg as la

def airfoil_from_generator():
    from meshpy import naca
    return naca.generate_naca(naca_digits="0012", number_of_points=50,
            sharp_trailing_edge=True, uniform_distribution=False,
            verbose=True)

def round_trip_connect(seq):
  result = []
  for i in range(len(seq)):
    result.append((i, (i+1)%len(seq)))
  return result

def needs_refinement(vertices, area):
    barycenter =  sum(numpy.array(v) for v in vertices)/3

    pt_back = numpy.array([1,0])

    max_area_front = 0.002*la.norm(barycenter) + 1e-5
    max_area_back = 0.02*la.norm(barycenter-pt_back) + 1e-3
    return bool(area > min(max_area_front, max_area_back))

def main():
    import sys
    points = airfoil_from_generator()

    from meshpy.geometry import GeometryBuilder
    from meshpy.triangle import write_gnuplot_mesh

    builder = GeometryBuilder()
    builder.add_geometry(points=points, 
            facets=round_trip_connect(points))
    builder.wrap_in_box(2)

    from meshpy.triangle import MeshInfo, build
    mi = MeshInfo()
    builder.set(mi)
    mi.set_holes([builder.center()])
    mesh = build(mi, refinement_func=needs_refinement)

    #print [tuple(x) for x in mesh.points]
    #print [tuple(x) for x in mesh.elements]

    print "%d elements" % len(mesh.elements)

    write_gnuplot_mesh("naca-mesh.dat", mesh)
    return mesh


if __name__ == "__main__":
    main()

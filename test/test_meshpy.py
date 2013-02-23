from __future__ import division

__copyright__ = "Copyright (C) 2013 Andreas Kloeckner"

__license__ = """
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""




# {{{ triangle

def test_triangle_refine():
    import meshpy.triangle as triangle
    import math

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

    mesh = triangle.build(info, refinement_func=needs_refinement)

    triangle.write_gnuplot_mesh("triangles-unrefined.dat", mesh)

    mesh.element_volumes.setup()

    for i in range(len(mesh.elements)):
        mesh.element_volumes[i] = -1
    for i in range(0, len(mesh.elements), 10):
        mesh.element_volumes[i] = 1e-8

    mesh = triangle.refine(mesh)

# }}}

# {{{ tetgen

def test_tetgen():
    from meshpy.tet import MeshInfo, build
    mesh_info = MeshInfo()

    mesh_info.set_points([
        (0,0,0),
        (2,0,0),
        (2,2,0),
        (0,2,0),
        (0,0,12),
        (2,0,12),
        (2,2,12),
        (0,2,12),
        ])

    mesh_info.set_facets([
        [0,1,2,3],
        [4,5,6,7],
        [0,4,5,1],
        [1,5,6,2],
        [2,6,7,3],
        [3,7,4,0],
        ])

    build(mesh_info)




def test_torus():
    from math import pi, cos, sin
    from meshpy.tet import MeshInfo, build
    from meshpy.geometry import generate_surface_of_revolution,\
            EXT_CLOSED_IN_RZ, GeometryBuilder

    big_r = 3
    little_r = 2.9

    points = 50
    dphi = 2*pi/points

    rz = [(big_r+little_r*cos(i*dphi), little_r*sin(i*dphi))
            for i in range(points)]

    geob = GeometryBuilder()
    geob.add_geometry(*generate_surface_of_revolution(rz,
            closure=EXT_CLOSED_IN_RZ, radial_subdiv=20))

    mesh_info = MeshInfo()
    geob.set(mesh_info)

    build(mesh_info)

# }}}

# {{{ gmsh

def search_on_path(filenames):
    """Find file on system path."""
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52224

    from os.path import exists, abspath, join
    from os import pathsep, environ

    search_path = environ["PATH"]

    paths = search_path.split(pathsep)
    for path in paths:
        for filename in filenames:
            if exists(join(path, filename)):
                return abspath(join(path, filename))




GMSH_SPHERE = """
x = 0; y = 1; z = 2; r = 3; lc = 0.3;

p1 = newp; Point(p1) = {x,  y,  z,  lc} ;
p2 = newp; Point(p2) = {x+r,y,  z,  lc} ;
p3 = newp; Point(p3) = {x,  y+r,z,  lc} ;
p4 = newp; Point(p4) = {x,  y,  z+r,lc} ;
p5 = newp; Point(p5) = {x-r,y,  z,  lc} ;
p6 = newp; Point(p6) = {x,  y-r,z,  lc} ;
p7 = newp; Point(p7) = {x,  y,  z-r,lc} ;

c1 = newreg; Circle(c1) = {p2,p1,p7};
c2 = newreg; Circle(c2) = {p7,p1,p5};
c3 = newreg; Circle(c3) = {p5,p1,p4};
c4 = newreg; Circle(c4) = {p4,p1,p2};
c5 = newreg; Circle(c5) = {p2,p1,p3};
c6 = newreg; Circle(c6) = {p3,p1,p5};
c7 = newreg; Circle(c7) = {p5,p1,p6};
c8 = newreg; Circle(c8) = {p6,p1,p2};
c9 = newreg; Circle(c9) = {p7,p1,p3};
c10 = newreg; Circle(c10) = {p3,p1,p4};
c11 = newreg; Circle(c11) = {p4,p1,p6};
c12 = newreg; Circle(c12) = {p6,p1,p7};

l1 = newreg; Line Loop(l1) = {c5,c10,c4};   Ruled Surface(newreg) = {l1};
l2 = newreg; Line Loop(l2) = {c9,-c5,c1};   Ruled Surface(newreg) = {l2};
l3 = newreg; Line Loop(l3) = {c12,-c8,-c1}; Ruled Surface(newreg) = {l3};
l4 = newreg; Line Loop(l4) = {c8,-c4,c11};  Ruled Surface(newreg) = {l4};
l5 = newreg; Line Loop(l5) = {-c10,c6,c3};  Ruled Surface(newreg) = {l5};
l6 = newreg; Line Loop(l6) = {-c11,-c3,c7}; Ruled Surface(newreg) = {l6};
l7 = newreg; Line Loop(l7) = {-c2,-c7,-c12};Ruled Surface(newreg) = {l7};
l8 = newreg; Line Loop(l8) = {-c6,-c9,c2};  Ruled Surface(newreg) = {l8};
"""




def test_gmsh():
    if search_on_path(["gmsh"]) is None:
        from pytest import skip
        skip("gmsh not found")

    from meshpy.gmsh_reader import generate_gmsh, GmshMeshReceiverBase
    mr = GmshMeshReceiverBase()
    generate_gmsh(mr, GMSH_SPHERE, 3)

# }}}




if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        exec(sys.argv[1])
    else:
        from py.test.cmdline import main
        main([__file__])

# vim: foldmethod=marker

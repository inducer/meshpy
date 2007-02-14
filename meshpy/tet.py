from meshpy.common import MeshInfoBase, dump_array
import meshpy._tetgen as internals





class MeshInfo(internals.MeshInfo, MeshInfoBase):
    def set_facets(self, facets, facet_markers=None):
        if facet_markers:
            assert len(facet_markers) == len(facets)

        self.facets.resize(len(facets))

        for i, vlist in enumerate(facets):
            facet = self.facets[i]
            polys = facet.polygons
            polys.resize(1)
            poly = facet.polygons[0]
            poly.vertices.resize(len(vlist))
            for j, pt_idx in enumerate(vlist):
                poly.vertices[j] = pt_idx

        if facet_markers:
            self.facet_markers.setup()
            for i, mark in enumerate(facet_markers):
                self.facet_markers[i] = mark

    def dump(self):
        for name in ["points"]:
            dump_array(name, getattr(self, name))
        for ifacet, facet in enumerate(self.facets):
            print "facet %d:" % ifacet
            for ipolygon, polygon in enumerate(facet.polygons):
                print "  polygon %d: vertices [%s]" % \
                        (ipolygon, ",".join(str(vi) for vi in polygon.vertices))

    def write_vtk(self, filename):
        import pyvtk
        vtkelements = pyvtk.VtkData(
            pyvtk.UnstructuredGrid(
              self.points, 
              tetra=self.elements),
            "Mesh")
        vtkelements.tofile(filename)





class Options(internals.Options):
    def __init__(self, switches="pq"):
        internals.Options.__init__(self)
        self.parse_switches(switches)
        self.quiet = 1




internals.Facet.polygons = property(internals.Facet.get_polygons)
internals.Facet.holes = property(internals.Facet.get_holes)
internals.Polygon.vertices = property(internals.Polygon.get_vertices)




def build(mesh_info, options=Options()):
    mesh = MeshInfo()
    internals.tetrahedralize(options, mesh_info, mesh)
    return mesh




def generate_surface_of_revolution(rz_points, radial_subdiv=16, point_offset=0):
    assert len(rz_points) > 0

    from math import sin, cos, pi

    def gen_point(r, phi, z):
        return (r*cos(phi), r*sin(phi), z)

    def gen_ring(r, z):
        if r == 0:
            p_indices = [p0+len(points)]
            points.append(gen_point(r, 0, z))
        else:
            p_indices = [p0+len(points)+i for i in range(radial_subdiv)]
            points.extend([gen_point(r, dphi*i, z) for i in range(radial_subdiv)])
        return p_indices

    def pair_with_successor(l):
        n = len(l)
        return [(l[i], l[(i+1)%n]) for i in range(n)]

    p0 = point_offset
    points = []
    polygons = []

    dphi = 2*pi/radial_subdiv

    last_r, last_z = rz_points[0]
    last_ring = gen_ring(last_r, last_z)

    for r, z in rz_points[1:]:
        ring = gen_ring(r, z)
        if last_r == 0:
            # make opening fan
            assert len(last_ring) == 1
            start_pt = last_ring[0]
            if r != 0:
                polygons.extend(
                        [(start_pt, succ, pt) for pt, succ in pair_with_successor(ring)]
                        )
        elif r == 0:
            # make closing fan
            assert len(ring) == 1
            end_pt = ring[0]
            polygons.extend(
                    [(pt, succ, end_pt) for pt, succ in pair_with_successor(last_ring)]
                    )
        else:
            # make quad strip
            last_pairs = pair_with_successor(last_ring)
            my_pairs = pair_with_successor(ring)
            polygons.extend(
                    [(a, b, c, d) for ((a,b), (d,c)) in zip(last_pairs, my_pairs)]
                    )

        last_ring = ring
        last_r = r
        last_z = z

    return points, polygons
            








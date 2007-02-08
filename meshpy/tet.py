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









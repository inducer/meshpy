from meshpy.common import MeshInfoBase, dump_array
import meshpy._tetgen as internals





class MeshInfo(internals.MeshInfo, MeshInfoBase):
    def set_facets(self, facets, markers=None):
        if markers:
            assert len(markers) == len(facets)

        self.facets.resize(len(facets))

        for i, vlist in enumerate(facets):
            facet = self.facets[i]
            polys = facet.polygons
            polys.resize(1)
            poly = facet.polygons[0]
            poly.vertices.resize(len(vlist))
            for j, pt_idx in enumerate(vlist):
                poly.vertices[j] = pt_idx

        if markers:
            self.facet_markers.setup()
            for i, mark in enumerate(markers):
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





def _PBCGroup_get_transmat(self):
    return PBCGroupTransmat(self)




class PBCGroupTransmat:
    def __init__(self, pbcgroup):
        self.pbcgroup = pbcgroup

    def __getitem__(self, (i,j)):
        return self.pcgroup.get_transmat_entry(i, j)

    def __setitem__(self, (i,j), v):
        return self.pcgroup.set_transmat_entry(i, j, v)




internals.Facet.polygons = property(internals.Facet.get_polygons)
internals.Facet.holes = property(internals.Facet.get_holes)
internals.Polygon.vertices = property(internals.Polygon.get_vertices)
internals.PBCGroup.point_pairs = property(internals.PBCGroup.get_point_pairs)
internals.PBCGroup.matrix = property(_PBCGroup_get_transmat)




def build(mesh_info, options=Options(), verbose=False, varvolume=False):
    mesh = MeshInfo()

    if not verbose:
        options.quiet = 1
    if varvolume:
        options.varvolume = 1

    internals.tetrahedralize(options, mesh_info, mesh)
    return mesh




EXT_OPEN = 0
EXT_CLOSE_IN_Z = 1
EXT_CLOSED_IN_RZ = 2




def generate_extrusion(rz_points, base_shape, closure=EXT_OPEN, point_idx_offset=0):
    assert len(rz_points) > 0

    def gen_ring(r, z):
        if r == 0:
            p_indices = [point_idx_offset+len(points)]
            points.append((0,0, z))
        else:
            first_idx = point_idx_offset+len(points)
            p_indices = range(first_idx, first_idx+len(base_shape))
            points.extend([(x*r, y*r, z) for (x,y) in base_shape])
        return p_indices

    def pair_with_successor(l):
        n = len(l)
        return [(l[i], l[(i+1)%n]) for i in range(n)]

    def connect_ring(r, ring, prev_r, prev_ring):
        if prev_r == 0:
            # make opening fan
            assert len(prev_ring) == 1
            start_pt = prev_ring[0]
            if r != 0:
                return [(start_pt, succ, pt) 
                        for pt, succ in pair_with_successor(ring)]
            else:
                return []
        elif r == 0:
            # make closing fan
            assert len(ring) == 1
            end_pt = ring[0]
            return [(pt, succ, end_pt) 
                    for pt, succ in pair_with_successor(prev_ring)]
        else:
            # make quad strip
            prev_pairs = pair_with_successor(prev_ring)
            my_pairs = pair_with_successor(ring)
            return [(a, b, c, d) for ((a,b), (d,c)) in zip(prev_pairs, my_pairs)]

    points = []
    polygons = []

    first_r, z = rz_points[0]
    first_ring = prev_ring = gen_ring(first_r, z)
    prev_r = first_r
    if closure == EXT_CLOSE_IN_Z:
        polygons.extend(first_ring)

    for r, z in rz_points[1:]:
        ring = gen_ring(r, z)
        polygons.extend(connect_ring(r, ring, prev_r, prev_ring))

        prev_ring = ring
        prev_r = r

    if closure == EXT_CLOSE_IN_Z:
        polygons.extend(prev_ring[::-1])
    if closure == EXT_CLOSED_IN_RZ:
        polygons.extend(connect_ring(first_r, first_ring, prev_r, prev_ring))

    return points, polygons




def generate_surface_of_revolution(rz_points, closure=EXT_OPEN, radial_subdiv=16, point_idx_offset=0):
    from math import sin, cos, pi

    dphi = 2*pi/radial_subdiv
    base_shape = [(cos(dphi*i), sin(dphi*i)) for i in range(radial_subdiv)]
    return generate_extrusion(rz_points, base_shape, closure=closure,
            point_idx_offset=point_idx_offset)
            

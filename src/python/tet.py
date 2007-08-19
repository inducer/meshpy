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

    @property
    def face_vertex_indices_to_face_marker(self):
        try:
            return self._fvi2fm
        except AttributeError:
            result = {}

            for i, face in enumerate(self.faces):
                result[frozenset(face)] = self.face_markers[i]

            self._fvi2fm = result
            return result

    def dump(self):
        for name in ["points"]:
            dump_array(name, getattr(self, name))
        for ifacet, facet in enumerate(self.faces):
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
    import pylinear.array as num

    return num.array(
            [[self.get_transmat_entry(i,j) 
                for j in xrange(4)]
                for i in xrange(4)])




def _PBCGroup_set_transmat(self, matrix):
    import pylinear.array as num

    for i in xrange(4):
        for j in xrange(4):
            self.set_transmat_entry(i, j, matrix[i,j])




def _PBCGroup_set_transform(self, matrix=None, translation=None):
    for i in xrange(4):
        for j in xrange(4):
            self.set_transmat_entry(i, j, 0)

    self.set_transmat_entry(3, 3, 1)

    if matrix is not None:
        for i in xrange(3):
            for j in xrange(3):
                self.set_transmat_entry(i, j, matrix[i][j])
    else:
        for i in xrange(3):
            self.set_transmat_entry(i, i, 1)

    if translation is not None:
        for i in xrange(3):
            self.set_transmat_entry(i, 3, translation[i])


    

internals.PBCGroup.matrix = property(
        _PBCGroup_get_transmat,
        _PBCGroup_set_transmat)
internals.PBCGroup.set_transform = _PBCGroup_set_transform




def build(mesh_info, options=Options(), verbose=False, 
        attributes=False, volume_constraints=False, max_volume=None):
    mesh = MeshInfo()

    if not verbose:
        options.quiet = 1

    if attributes:
        options.regionattrib = 1
    if volume_constraints:
        options.varvolume = 1
    if max_volume:
        options.fixedvolume = 1
        options.maxvolume = max_volume

    internals.tetrahedralize(options, mesh_info, mesh)
    return mesh




EXT_OPEN = 0
EXT_CLOSE_IN_Z = 1
EXT_CLOSED_IN_RZ = 2




def generate_extrusion(rz_points, base_shape, closure=EXT_OPEN, 
        point_idx_offset=0, ring_tags=None, closure_tag=0):
    """Extrude a given connected `base_shape' (a list of (x,y) points)
    along the z axis. For each step in the extrusion, the base shape
    is multiplied by a radius and shifted in the z direction. Radius
    and z offset are given by `rz_points', which is a list of
    (r, z) tuples.

    Returns (points, facets), where points is a list of points
    and facets is a list of tuples of indices into that point list, 
    each tuple specifying a polygon. If point_idx_offset is not
    zero, these indices start at this number. There may be a third
    return value, see `facet_markers' below.

    The extrusion proceeds by generating quadrilaterals connecting each
    ring.  If any given radius in `rz_points' is 0, triangle fans are
    produced instead of quads to provide non-degenerate closure.

    If `closure' is EXT_OPEN, no efforts are made to put end caps on the
    extrusion. 

    Specifying `closure' as EXT_CLOSE_IN_Z is (almost)
    equivalent to adding points with zero radius at the beginning 
    at end of the rz_points list. The z coordinates are equal to 
    the existing first and last points in that list. (This case is
    handled more efficiently by just generating big flat facets.
    Since these facets are always flat, triangle fans are 
    unnecessary.)

    If `closure' is EXT_CLOSED_IN_RZ, then a torus-like structure
    is assumed and the last ring is just connected to the first.

    If `ring_tags' is not None, it is an list of tags added to each
    ring. There should be len(rz_points)-1 entries in this list.
    If rings are added because of closure options, they receive the
    tag `closure_tag'.  If `facet_markers' is given, this function 
    returns (points, facets, tags), where tags is is a list containing 
    a tag for each generated facet.
    """

    assert len(rz_points) > 0
    
    if ring_tags is not None:
        assert len(rz_points) == len(ring_tags)+1

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


    def add_polygons(new_polys, tag):
        polygons.extend(new_polys)

        if ring_tags is not None:
            tags.extend(len(new_polys)*[tag])

    points = []
    polygons = []
    tags = []

    first_r, z = rz_points[0]
    first_ring = prev_ring = gen_ring(first_r, z)
    prev_r = first_r
    if closure == EXT_CLOSE_IN_Z:
        add_polygons([tuple(first_ring)], closure_tag)

    for i, (r, z) in enumerate(rz_points[1:]):
        ring = gen_ring(r, z)

        if ring_tags is not None:
            ring_tag = ring_tags[i]
        else:
            ring_tag = None

        add_polygons(
                connect_ring(r, ring, prev_r, prev_ring),
                ring_tag)

        prev_ring = ring
        prev_r = r

    if closure == EXT_CLOSE_IN_Z:
        add_polygons([tuple(prev_ring[::-1])], closure_tag)
    if closure == EXT_CLOSED_IN_RZ:
        add_polygons(connect_ring(
            first_r, first_ring, prev_r, prev_ring),
            closure_tag)

    if ring_tags is not None:
        return points, polygons, tags
    else:
        return points, polygons




def generate_surface_of_revolution(rz_points, 
        closure=EXT_OPEN, radial_subdiv=16, 
        point_idx_offset=0, ring_tags=None,
        closure_tag=0):
    from math import sin, cos, pi

    dphi = 2*pi/radial_subdiv
    base_shape = [(cos(dphi*i), sin(dphi*i)) for i in range(radial_subdiv)]
    return generate_extrusion(rz_points, base_shape, closure=closure,
            point_idx_offset=point_idx_offset,
            ring_tags=ring_tags, closure_tag=closure_tag)

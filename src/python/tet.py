from meshpy.common import MeshInfoBase, dump_array
import meshpy._tetgen as internals





class MeshInfo(internals.MeshInfo, MeshInfoBase):
    def set_facets(self, facets, markers=None):
        """Set a list of simple, single-polygon factes. Unlike L{set_facets_ex},
        C{set_facets} does not allow hole and only lets you use a single
        polygon per facet.

        @param facets: a list of facets, where each facet is a single 
          polygons, represented by a list of point indices.
        @param markers: Either None or a list of integers of the same
          length as C{facets}. Each integer is the facet marker assigned
          to its corresponding facet.

        @note: When the above says "list", any repeatable iterable 
          also accepted instead.
        """

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

    def set_facets_ex(self, facets, facet_holestarts=None, markers=None):
        """Set a list of complicated factes. Unlike L{set_facets},
        C{set_facets_ex()} allows holes and multiple polygons per
        facet.

        @param facets: a list of facets, where each facet is a list
          of polygons, and each polygon is represented by a list
          of point indices.
        @param facet_holestarts: Either None or a list of hole starting points
          for each facet. Each facet may have several hole starting points.
          The mesh generator starts "eating" a hole into the facet at each 
          starting point and continues until it hits a polygon specified
          in this facet's record in C{facets}.
        @param markers: Either None or a list of integers of the same
          length as C{facets}. Each integer is the facet marker assigned
          to its corresponding facet.

        @note: When the above says "list", any repeatable iterable 
          also accepted instead.
        """

        if markers:
            assert len(markers) == len(facets)
        if facet_holestarts is not None:
            assert len(facet_holestarts) == len(facets)

        self.facets.resize(len(facets))
        for i_facet, poly_list in enumerate(facets):
            facet = self.facets[i_facet]
            polys = facet.polygons

            polys.resize(len(poly_list))
            for i_poly, vertex_list in enumerate(poly_list):
                poly = facet.polygons[i_poly]

                poly.vertices.resize(len(vertex_list))
                for i_point, point in enumerate(vertex_list):
                    poly.vertices[i_point] = point

            if facet_holestarts is not None:
                hole_list = facet_holestarts[i_facet]
                facet_holes = facet.holes
                facet_holes.resize(len(hole_list))
                for i_hole, hole_start in enumerate(hole_list):
                    for i_coordinate, co_value in enumerate(hole_start):
                        facet_holes[i_hole, i_coordinate] = co_value

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
    def __init__(self, switches="pq", **kwargs):
        internals.Options.__init__(self)
        self.parse_switches(switches)
        self.quiet = 1

        for k, v in kwargs.iteritems():
            try:
                getattr(self, k)
            except AttributeError:
                raise ValueError, "invalid option: %s" % k
            else:
                setattr(self, k, v)





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
        attributes=False, volume_constraints=False, max_volume=None,
        diagnose=False):
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
    if diagnose:
        options.diagnose = 1

    internals.tetrahedralize(options, mesh_info, mesh)
    return mesh




EXT_OPEN = 0
EXT_CLOSED_IN_RZ = 1




def _is_same_float(a, b, threshold=1e-10):
    if abs(a) > abs(b):
        a,b = b,a

    # now abs(a) <= abs(b) always
    return abs(b) < threshold or abs(a-b)<threshold*b



def generate_extrusion(rz_points, base_shape, closure=EXT_OPEN, 
        point_idx_offset=0, ring_point_indices=None,
        ring_markers=None, rz_closure_marker=0):
    """Extrude a given connected C{base_shape} (a list of (x,y) points)
    along the z axis. For each step in the extrusion, the base shape
    is multiplied by a radius and shifted in the z direction. Radius
    and z offset are given by C{rz_points}, which is a list of
    (r, z) tuples.

    Returns C{(points, facets, facet_holestarts, markers)}, where C{points} is a list
    of (3D) points and facets is a list of polygons. Each polygon is, in turn,
    represented by a tuple of indices into C{points}. If C{point_idx_offset} is
    not zero, these indices start at that number. C{markers} is a list equal in
    length to C{facets}, each specifying the facet marker of that facet.
    C{facet_holestarts} is also equal in length to C{facets}, each element is a list of
    hole starting points for the corresponding facet.

    Use L{MeshInfo.set_facets_ex} to add the extrusion to a L{MeshInfo}
    structure.

    The extrusion proceeds by generating quadrilaterals connecting each
    ring.  If any given radius in C{rz_points} is 0, triangle fans are
    produced instead of quads to provide non-degenerate closure.

    If C{closure} is L{EXT_OPEN}, no efforts are made to put end caps on the
    extrusion. 

    If C{closure} is L{EXT_CLOSED_IN_RZ}, then a torus-like structure
    is assumed and the last ring is just connected to the first.

    If C{ring_markers} is not None, it is an list of markers added to each
    ring. There should be len(rz_points)-1 entries in this list.
    If rings are added because of closure options, they receive the
    corresponding C{XXX_closure_marker}.  If C{facet_markers} is given, this function 
    returns (points, facets, markers), where markers is is a list containing 
    a marker for each generated facet. Unspecified markers generally
    default to 0.

    If C{ring_point_indices} is given, it must be a list of the same 
    length as C{rz_points}. Each entry in the list may either be None,
    or a list of point indices. This list must contain the same number
    of points as the C{base_shape}; it is taken as the indices of 
    pre-existing points that are to be used for the given ring, instead
    of generating new points.
    """

    assert len(rz_points) > 0
    
    if ring_markers is not None:
        assert len(rz_points) == len(ring_markers)+1

    def get_ring(ring_idx):
        try:
            return rings[ring_idx]
        except KeyError:
            # need to generate fresh ring, continue
            pass

        p_indices = None
        if ring_point_indices is not None:
            p_indices = ring_point_indices[ring_idx]

        first_idx = point_idx_offset+len(points)
        
        r, z = rz_points[ring_idx]

        if r == 0:
            p_indices = (first_idx,)
            points.append((0,0, z))
        else:
            p_indices = tuple(xrange(first_idx, first_idx+len(base_shape)))
            points.extend([(x*r, y*r, z) for (x,y) in base_shape])

        rings[ring_idx]  = p_indices
        return p_indices

    def pair_with_successor(l):
        n = len(l)
        return [(l[i], l[(i+1)%n]) for i in range(n)]

    def add_polygons(new_polys, marker):
        """Add several new facets, each polygon in new_polys corresponding
        to a new facet.
        """
        facets.extend([poly] for poly in new_polys)
        markers.extend(len(new_polys)*[marker])
        holelists.extend(len(new_polys)*[[]])

    def add_facet(facet_polygons, holestarts, marker):
        """Add a single facet, with each polygon in C{facet_polygons} 
        belonging to a single facet.
        """
        facets.append(facet_polygons)
        markers.append(marker)
        holelists.append(holestarts)

    def connect_ring(ring1_idx, ring2_idx, marker):
        r1, z1 = rz_points[ring1_idx]
        r2, z2 = rz_points[ring2_idx]

        if _is_same_float(z2, z1):
            assert not _is_same_float(r1, r2)
            # we're moving purely outward--this doesn't need fans, only plane
            # surfaces. Special casing this leads to more freedom for TetGen
            # and hence better meshes.

            if r1 == 0:
                # make opening surface
                if r2 != 0:
                    add_polygons([get_ring(ring2_idx)], marker=marker)
            elif r2 == 0:
                # make closing surface
                add_polygons([get_ring(ring1_idx)], marker=marker)
            else:
                # make single-surface interface with hole
                add_facet([
                    get_ring(ring1_idx), 
                    get_ring(ring2_idx), 
                    ], 
                    holestarts=[(0,0,z1)], marker=marker)
        else:
            ring1 = get_ring(ring1_idx)
            ring2 = get_ring(ring2_idx)
            if r1 == 0:
                # make opening fan
                assert len(ring1) == 1
                start_pt = ring1[0]

                if r2 != 0:
                    add_polygons(
                            [(start_pt, succ, pt) 
                            for pt, succ in pair_with_successor(ring2)],
                            marker=marker)
            elif r2 == 0:
                # make closing fan
                assert len(ring2) == 1
                end_pt = ring2[0]
                add_polygons(
                        [(pt, succ, end_pt) 
                        for pt, succ in pair_with_successor(ring1)],
                        marker=marker)
            else:
                # make quad strip
                pairs1 = pair_with_successor(ring1)
                pairs2 = pair_with_successor(ring2)
                add_polygons(
                        [(a, b, c, d) for ((a,b), (d,c)) in zip(pairs1, pairs2)],
                        marker=marker)

    points = []
    facets = []
    markers = []
    holelists = []

    rings = {}

    # pre-populate ring dict with ring_point_indices
    if ring_point_indices is not None:
        for i, ring_points in enumerate(ring_point_indices):
            if ring_points is not None:
                assert isinstance(ring_points, tuple)

                if rz_points[i][0] == 0:
                    assert len(ring_points) == 1
                else:
                    assert len(ring_points) == len(base_shape)

                rings[i] = ring_points

    for i in range(len(rz_points)-1):
        if ring_markers is not None:
            ring_marker = ring_markers[i]
        else:
            ring_marker = 0

        connect_ring(i, i+1, ring_marker)

    if closure == EXT_CLOSED_IN_RZ:
        connect_ring(len(rz_points)-1, 0, rz_closure_marker)

    return points, facets, holelists, markers




def generate_surface_of_revolution(rz_points, 
        closure=EXT_OPEN, radial_subdiv=16, 
        point_idx_offset=0, ring_point_indices=None,
        ring_markers=None, rz_closure_marker=0):
    from math import sin, cos, pi

    dphi = 2*pi/radial_subdiv
    base_shape = [(cos(dphi*i), sin(dphi*i)) for i in range(radial_subdiv)]
    return generate_extrusion(rz_points, base_shape, closure=closure,
            point_idx_offset=point_idx_offset, 
            ring_point_indices=ring_point_indices,
            ring_markers=ring_markers, rz_closure_marker=rz_closure_marker,
            )

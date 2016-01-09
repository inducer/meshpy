from __future__ import division, absolute_import

__doc__ = """

Geometry builder
----------------

.. autoclass:: GeometryBuilder

Geometries
----------

These functions are designed so that their output can be splat-passed to
:meth:`GeometryBuilder.add_geometry`::

    builder = GeometryBuilder()
    builder.add_geometry(*make_ball(10))

.. autoclass:: Marker
    :members:
    :undoc-members:

.. autofunction:: make_box
.. autofunction:: make_circle
.. autofunction:: make_ball
.. autofunction:: make_cylinder

Extrusions and surfaces of revolution
-------------------------------------

.. data:: EXT_OPEN
.. data:: EXT_CLOSED_IN_RZ

.. autofunction:: generate_extrusion
.. autofunction:: generate_surface_of_revolution
"""

import numpy as np
from six.moves import range
from six.moves import zip


# {{{ geometry building

def bounding_box(points):
    return (
            np.asarray(np.min(points, axis=0), dtype=np.float64),
            np.asarray(np.max(points, axis=0), dtype=np.float64))


def is_multi_polygon(facets):
    if not len(facets):
        return False

    try:
        facets[0][0][0]  # facet 0, poly 0, point 0
    except TypeError:
        # pure python raises this
        return False
    except IndexError:
        # numpy raises this
        return False
    else:
        return True


def offset_point_indices(facets, offset):
    if is_multi_polygon(facets):
        return [[tuple(p_i+offset for p_i in poly)
            for poly in facet]
            for facet in facets]
    else:
        return [tuple(p_i+offset for p_i in facet) for facet in facets]


class GeometryBuilder(object):
    """
    .. automethod:: add_geometry
    .. automethod:: set
    .. automethod:: wrap_in_box
    .. automethod:: bounding_box
    .. automethod:: center
    .. automethod:: apply_transform
    """
    def __init__(self):
        self.points = []
        self.facets = []
        self.facet_hole_starts = None
        self.facet_markers = None
        self.point_markers = None

    def add_geometry(self, points, facets, facet_hole_starts=None,
            facet_markers=None, point_markers=None):
        if isinstance(facet_markers, int):
            facet_markers = len(facets) * [facet_markers]

        if facet_hole_starts and not self.facet_hole_starts:
            self.facet_hole_starts = len(self.facets) * []
        if facet_markers and not self.facet_markers:
            self.facet_markers = len(self.facets) * [0]
        if point_markers and not self.point_markers:
            self.point_markers = len(self.points) * [0]

        if not facet_hole_starts and self.facet_hole_starts:
            facet_hole_starts = len(facets) * [[]]
        if not facet_markers and self.facet_markers:
            facet_markers = len(facets) * [0]
        if not point_markers and self.point_markers:
            point_markers = len(points) * [0]

        if is_multi_polygon(facets) and not is_multi_polygon(self.facets):
            self.facets = [[facet] for facet in self.facets]

        if not is_multi_polygon(facets) and is_multi_polygon(self.facets):
            facets = [[facet] for facet in facets]

        self.facets.extend(offset_point_indices(facets, len(self.points)))
        self.points.extend(points)

        if facet_markers:
            self.facet_markers.extend(facet_markers)
            assert len(facets) == len(facet_markers)
        if facet_hole_starts:
            self.facet_hole_starts.extend(facet_hole_starts)
            assert len(facets) == len(facet_hole_starts)
        if point_markers:
            self.point_markers.extend(point_markers)
            assert len(points) == len(point_markers)

    def add_cycle(self, points, facet_markers=None, point_markers=None):
        def make_facets():
            end = len(points)-1
            for i in range(end):
                yield i, i+1
            yield end, 0

        self.add_geometry(points, list(make_facets()),
                facet_markers=facet_markers,
                point_markers=point_markers)

    def dimensions(self):
        return len(self.points[0])

    def set(self, mesh_info):
        """Transfer the built geometry into a :class:`meshpy.triangle.MeshInfo`
        or a :class:`meshpy.tet.MeshInfo`.
        """

        mesh_info.set_points(self.points, self.point_markers)
        if self.facet_hole_starts or is_multi_polygon(self.facets):
            mesh_info.set_facets_ex(self.facets,
                    self.facet_hole_starts, self.facet_markers)
        else:
            mesh_info.set_facets(self.facets, self.facet_markers)

    def mesher_module(self):
        dim = self.dimensions()
        if dim == 2:
            import meshpy.triangle
            return meshpy.triangle
        elif dim == 3:
            import meshpy.tet
            return meshpy.tet
        else:
            raise ValueError("unsupported dimensionality %d" % dim)

    def bounding_box(self):
        return bounding_box(self.points)

    def center(self):
        a, b = bounding_box(self.points)
        return (a+b)/2

    def wrap_in_box(self, distance, subdivisions=None):
        """
        :param subdivisions: is a tuple of integers specifying
          the number of subdivisions along each axis.
        """

        a, b = bounding_box(self.points)
        points, facets, _, facet_markers = \
                make_box(a-distance, b+distance, subdivisions)

        self.add_geometry(points, facets, facet_markers=facet_markers)

    def apply_transform(self, f):
        self.points = [f(x) for x in self.points]

# }}}


# {{{ actual geometries

class Marker:
    MINUS_X = 1
    PLUS_X = 2
    MINUS_Y = 3
    PLUS_Y = 4
    MINUS_Z = 5
    PLUS_Z = 6
    SHELL = 100

    FIRST_USER_MARKER = 1000


def make_box(a, b, subdivisions=None):
    """
    :param subdivisions: is a tuple of integers specifying
      the number of subdivisions along each axis.
    """

    a = [float(ai) for ai in a]
    b = [float(bi) for bi in b]

    assert len(a) == len(b)

    dimensions = len(a)
    if dimensions == 2:
        # CAUTION: Do not change point or facet order here.
        # Other code depends on this staying the way it is.

        points = [
                (a[0], a[1]),
                (b[0], a[1]),
                (b[0], b[1]),
                (a[0], b[1]),
                ]

        facets = [(0, 1), (1, 2), (2, 3), (3, 0)]

        facet_markers = [
                Marker.MINUS_Y, Marker.PLUS_X,
                Marker.PLUS_Y, Marker.MINUS_X]

    elif dimensions == 3:
        #    7--------6
        #   /|       /|
        #  4--------5 |  z
        #  | |      | |  ^
        #  | 3------|-2  | y
        #  |/       |/   |/
        #  0--------1    +--->x

        points = [
                (a[0], a[1], a[2]),
                (b[0], a[1], a[2]),
                (b[0], b[1], a[2]),
                (a[0], b[1], a[2]),
                (a[0], a[1], b[2]),
                (b[0], a[1], b[2]),
                (b[0], b[1], b[2]),
                (a[0], b[1], b[2]),
                ]

        facets = [
                (0, 1, 2, 3),
                (0, 1, 5, 4),
                (1, 2, 6, 5),
                (7, 6, 2, 3),
                (7, 3, 0, 4),
                (4, 5, 6, 7)
                ]

        facet_markers = [Marker.MINUS_Z, Marker.MINUS_Y, Marker.PLUS_X,
                Marker.PLUS_Y, Marker.MINUS_X, Marker.PLUS_Z]
    else:
        raise ValueError("unsupported dimension count: %d" % len(a))

    if subdivisions is not None:
        if dimensions != 2:
            raise NotImplementedError(
                    "subdivision not implemented for any "
                    "dimension count other than 2")

        from meshpy.triangle import subdivide_facets
        points, facets, facet_markers = subdivide_facets(
                [subdivisions[0], subdivisions[1],
                    subdivisions[0], subdivisions[1]],
                points, facets, facet_markers)

    return points, facets, None, facet_markers


def make_circle(r, center=(0, 0), subdivisions=40, marker=Marker.SHELL):
    def round_trip_connect(seq):
        result = []
        for i in range(len(seq)):
            result.append((i, (i+1) % len(seq)))
        return result

    phi = np.linspace(0, 2*np.pi, num=subdivisions, endpoint=False)
    cx, cy = center
    x = r*np.cos(phi) + cx
    y = r*np.sin(phi) + cy

    return ([np.array(pt) for pt in zip(x, y)],
            round_trip_connect(list(range(subdivisions))),
            None,
            subdivisions*[marker])


def make_ball(r, subdivisions=10):
    from math import pi, cos, sin

    dphi = pi/subdivisions

    def truncate(my_r):
        if abs(my_r) < 1e-9*r:
            return 0
        else:
            return my_r

    rz = [(truncate(r*sin(i*dphi)), r*cos(i*dphi)) for i in range(subdivisions+1)]

    return generate_surface_of_revolution(
            rz, closure=EXT_OPEN, radial_subdiv=subdivisions)


def make_cylinder(radius, height, radial_subdivisions=10,
        height_subdivisions=1):
    dz = height/height_subdivisions
    rz = [(0, 0)] \
            + [(radius, i*dz) for i in range(height_subdivisions+1)] \
            + [(0, height)]
    ring_markers = [Marker.MINUS_Z] \
            + ((height_subdivisions)*[Marker.SHELL]) \
            + [Marker.PLUS_Z]

    return generate_surface_of_revolution(rz,
            closure=EXT_OPEN, radial_subdiv=radial_subdivisions,
            ring_markers=ring_markers)

# }}}


# {{{ extrusions

def _is_same_float(a, b, threshold=1e-10):
    if abs(a) > abs(b):
        a, b = b, a

    # now abs(a) <= abs(b) always
    return abs(b) < threshold or abs(a-b) < threshold*abs(b)


EXT_OPEN = 0
EXT_CLOSED_IN_RZ = 1


def generate_extrusion(rz_points, base_shape, closure=EXT_OPEN,
        point_idx_offset=0, ring_point_indices=None,
        ring_markers=None, rz_closure_marker=0):
    """Extrude a given connected *base_shape* (a list of (x,y) points)
    along the z axis. For each step in the extrusion, the base shape
    is multiplied by a radius and shifted in the z direction. Radius
    and z offset are given by *rz_points*, which is a list of
    (r, z) tuples.

    Returns ``(points, facets, facet_holestarts, markers)``, where *points* is
    a list of (3D) points and facets is a list of polygons. Each polygon is, in
    turn, represented by a tuple of indices into *points*. If
    *point_idx_offset* is not zero, these indices start at that number.
    *markers* is a list equal in length to *facets*, each specifying the facet
    marker of that facet.  *facet_holestarts* is also equal in length to
    *facets*, each element is a list of hole starting points for the
    corresponding facet.

    Use L{MeshInfo.set_facets_ex} to add the extrusion to a L{MeshInfo}
    structure.

    The extrusion proceeds by generating quadrilaterals connecting each
    ring.  If any given radius in *rz_points* is 0, triangle fans are
    produced instead of quads to provide non-degenerate closure.

    If *closure* is :data:`EXT_OPEN`, no efforts are made to put end caps on the
    extrusion.

    If *closure* is :data:`EXT_CLOSED_IN_RZ`, then a torus-like structure
    is assumed and the last ring is just connected to the first.

    If *ring_markers* is not None, it is an list of markers added to each
    ring. There should be len(rz_points)-1 entries in this list.
    If rings are added because of closure options, they receive the
    corresponding *XXX_closure_marker*.  If *facet_markers* is given, this function
    returns (points, facets, markers), where markers is is a list containing
    a marker for each generated facet. Unspecified markers generally
    default to 0.

    If *ring_point_indices* is given, it must be a list of the same
    length as *rz_points*. Each entry in the list may either be None,
    or a list of point indices. This list must contain the same number
    of points as the *base_shape*; it is taken as the indices of
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
            points.append((0, 0, z))
        else:
            p_indices = tuple(range(first_idx, first_idx+len(base_shape)))
            points.extend([(x*r, y*r, z) for (x, y) in base_shape])

        rings[ring_idx] = p_indices
        return p_indices

    def pair_with_successor(l):
        n = len(l)
        return [(l[i], l[(i+1) % n]) for i in range(n)]

    def add_polygons(new_polys, marker):
        """Add several new facets, each polygon in new_polys corresponding
        to a new facet.
        """
        facets.extend([poly] for poly in new_polys)
        markers.extend(len(new_polys)*[marker])
        holelists.extend(len(new_polys)*[[]])

    def add_facet(facet_polygons, holestarts, marker):
        """Add a single facet, with each polygon in *facet_polygons*
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
                    holestarts=[(0, 0, z1)], marker=marker)
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
                        [(a, b, c, d) for ((a, b), (d, c)) in zip(pairs1, pairs2)],
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
                    assert len(ring_points) == len(base_shape), \
                            ("Ring points length (%d) does not "
                                    "match base shape length (%d)"
                                    % (len(ring_points), len(base_shape)))

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
    return generate_extrusion(
            rz_points, base_shape, closure=closure,
            point_idx_offset=point_idx_offset,
            ring_point_indices=ring_point_indices,
            ring_markers=ring_markers, rz_closure_marker=rz_closure_marker,
            )

# }}}

# vim: foldmethod=marker

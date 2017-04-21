from __future__ import division
from __future__ import absolute_import
from meshpy.common import MeshInfoBase, dump_array
import meshpy._triangle as internals
from six.moves import range
from six.moves import zip


class MeshInfo(internals.MeshInfo, MeshInfoBase):
    _constituents = [
            "points", "point_attributes", "point_markers",
            "elements", "element_attributes", "element_volumes",
            "neighbors",
            "facets", "facet_markers",
            "holes",
            "regions",
            "faces", "face_markers",
            "normals",
            ]

    def __getstate__(self):
        return self.number_of_point_attributes, \
               self.number_of_element_attributes, \
               [(name, getattr(self, name)) for name in self._constituents]

    def __setstate__(self, xxx_todo_changeme):
        (p_attr_count, e_attr_count, state) = xxx_todo_changeme
        self.number_of_point_attributes = p_attr_count
        self.number_of_element_attributes = e_attr_count
        for name, array in state:
            if name not in self._constituents:
                raise RuntimeError("Unknown constituent during unpickling")

            dest_array = getattr(self, name)

            if array is None:
                dest_array.deallocate()
            else:
                if len(dest_array) != len(array):
                    dest_array.resize(len(array))
                if not dest_array.allocated and len(array) > 0:
                    dest_array.setup()

                for i, tup in enumerate(array):
                    for j, v in enumerate(tup):
                        dest_array[i, j] = v

    def set_facets(self, facets, facet_markers=None):
        self.facets.resize(len(facets))

        for i, facet in enumerate(facets):
            self.facets[i] = facet

        if facet_markers is not None:
            self.facet_markers.setup()
            for i, mark in enumerate(facet_markers):
                self.facet_markers[i] = mark

    def dump(self):
        for name in self._constituents:
            dump_array(name, getattr(self, name))


def subdivide_facets(subdivisions, points, facets, facet_markers=None):
    """Return a new facets array in which the original facets are
    each subdivided into C{subdivisions} subfacets.

    This routine is useful if you have to prohibit the insertion of Steiner
    points on the boundary  of your triangulation to allow the mesh to conform
    either to itself periodically or another given mesh. In this case, you may
    use this routine to create the necessary resolution along the boundary
    in a predefined way.

    @arg subdivisions: Either an C{int}, indicating a uniform number of subdivisions
      throughout, or a list of the same length as C{facets}, specifying a subdivision
      count for each individual facet.
    @arg points: A list of points referred to from the facets list.
    @arg facets: The list of old facets, in the form C{[(p1, p2), (p3,p4), ...]}.
    @arg facet_markers: Either C{None} or a list of facet markers of the same length
      as C{facets}.
    @return: The new tuple C{(new_points, new_facets)}.
      (Or C{(new_points, new_facets, new_facet_markers)} if C{facet_markers} is not
      C{None}.)
    """

    def intermediate_points(pa, pb, n):
        for i in range(1, n):
            tau = i/n
            yield [pai*(1-tau) + tau*pbi for pai, pbi in zip(pa, pb)]

    if isinstance(subdivisions, int):
        from itertools import repeat
        subdiv_it = repeat(subdivisions, len(facets))
    else:
        assert len(facets) == len(subdivisions)
        subdiv_it = subdivisions.__iter__()

    new_points = points[:]
    new_facets = []

    if facet_markers is not None:
        assert len(facets) == len(facet_markers)
        new_facet_markers = []

    for facet_idx, ((pidx_a, pidx_b), subdiv) in enumerate(zip(facets, subdiv_it)):
        facet_points = [pidx_a]
        for p in intermediate_points(points[pidx_a], points[pidx_b], subdiv):
            facet_points.append(len(new_points))
            new_points.append(p)
        facet_points.append(pidx_b)

        for i, p1 in enumerate(facet_points[:-1]):
            p2 = facet_points[i+1]
            new_facets.append((p1, p2))

            if facet_markers is not None:
                new_facet_markers.append(facet_markers[facet_idx])

    if facet_markers is not None:
        return new_points, new_facets, new_facet_markers
    else:
        return new_points, new_facets


def build(mesh_info, verbose=False, refinement_func=None, attributes=False,
        volume_constraints=False, max_volume=None, allow_boundary_steiner=True,
        allow_volume_steiner=True, quality_meshing=True,
        generate_edges=None, generate_faces=False, min_angle=None,
        mesh_order=None, generate_neighbor_lists=False):
    """Triangulate the domain given in `mesh_info'."""
    opts = "pzj"
    if quality_meshing:
        if min_angle is not None:
            opts += "q%f" % min_angle
        else:
            opts += "q"

    if mesh_order is not None:
        opts += "o%d" % mesh_order

    if verbose:
        opts += "VV"
    else:
        opts += "Q"

    if attributes:
        opts += "A"

    if volume_constraints:
        opts += "a"
    if max_volume:
        opts += "a%.20f" % max_volume

    if refinement_func is not None:
        opts += "u"

    if generate_edges is not None:
        from warnings import warn
        warn("generate_edges is deprecated--use generate_faces instead")
        generate_faces = generate_edges
    if generate_neighbor_lists is not None:
        opts += "n"

    if generate_faces:
        opts += "e"

    if not allow_volume_steiner:
        opts += "YY"
        if allow_boundary_steiner:
            raise ValueError("cannot allow boundary Steiner points when volume "
                    "Steiner points are forbidden")
    else:
        if not allow_boundary_steiner:
            opts += "Y"

    # restore "C" locale--otherwise triangle might mis-parse stuff like "a0.01"
    try:
        import locale
    except ImportError:
        have_locale = False
    else:
        have_locale = True
        prev_num_locale = locale.getlocale(locale.LC_NUMERIC)
        locale.setlocale(locale.LC_NUMERIC, "C")

    try:
        mesh = MeshInfo()
        internals.triangulate(opts, mesh_info, mesh, MeshInfo(), refinement_func)
    finally:
        # restore previous locale if we've changed it
        if have_locale:
            locale.setlocale(locale.LC_NUMERIC, prev_num_locale)

    return mesh


def refine(input_p, verbose=False, refinement_func=None,  quality_meshing=True,
        min_angle=None, generate_neighbor_lists=False):
    opts = "razj"

    if quality_meshing:
        if min_angle is not None:
            opts += "q%f" % min_angle
        else:
            opts += "q"

    if len(input_p.faces) != 0:
        opts += "p"
    if verbose:
        opts += "VV"
    else:
        opts += "Q"
    if refinement_func is not None:
        opts += "u"
    if generate_neighbor_lists is not None:
        opts += "n"

    output_p = MeshInfo()
    internals.triangulate(opts, input_p, output_p, MeshInfo(), refinement_func)
    return output_p


def write_gnuplot_mesh(filename, out_p, facets=False):
    gp_file = open(filename, "w")

    if facets:
        segments = out_p.facets
    else:
        segments = out_p.elements

    for points in segments:
        for pt in points:
            gp_file.write("%f %f\n" % tuple(out_p.points[pt]))
        gp_file.write("%f %f\n\n" % tuple(out_p.points[points[0]]))

import numpy as np
import numpy.linalg as la




class LocalToGlobalMap(object):
    def __init__(self, nodes, ldis):
        self.nodes = nodes
        self.ldis  = ldis

        node_src_indices = np.array(
                ldis.lexicographic_to_gmsh_index_map(),
                dtype=np.intp)

        nodes = np.array(nodes, dtype=np.float64)
        reordered_nodes = nodes[node_src_indices, :]

        self.modal_coeff = la.solve(
                ldis.equidistant_vandermonde(), reordered_nodes)
        # axis 0: node number, axis 1: xyz axis

        if False:
            for i, c in zip(ldis.generate_mode_identifiers(), self.modal_coeff):
                print i, c

    def __call__(self, r):
        """Given a point *r* on the reference element, return the
        corresponding point *x* in global coordinates.
        """
        mc = self.modal_coeff

        return np.array([sum([
            mc[i, axis] * mbf(r)
            for i, mbf in enumerate(self.ldis.basis_functions())])
            for axis in range(self.ldis.dimensions)])

    def is_affine(self):
        from pytools import any

        has_high_order_geometry = any(
                sum(mid) >= 2 and abs(mc) >= 1e-13
                for mc_along_axis in self.modal_coeff.T
                for mid, mc in zip(
                    self.ldis.generate_mode_identifiers(),
                    mc_along_axis)
                )

        return not has_high_order_geometry





class HedgeMeshReceiver:
    def __init__(self,
            force_dimension=None, periodicity=None,
            allow_internal_boundaries=False,
            tag_mapper=lambda tag: tag):
        raise NotImplementedError

        # maps (tag_number, dimension) -> tag_name
        self.tag_name_map = {}
        self.gmsh_vertex_nrs_to_element = {}

    def add_element(self):
        gmsh_vertex_nrs_to_element[frozenset(gmsh_vertex_nrs)] = el_info

    def build_mesh(self):
        # figure out dimensionalities
        node_dim = single_valued(len(node) for node in nodes)
        vol_dim = max(el.el_type.dimensions for key, el in
                gmsh_vertex_nrs_to_element.iteritems() )
        bdry_dim = vol_dim - 1

        vol_elements = [el for key, el in gmsh_vertex_nrs_to_element.iteritems()
                if el.el_type.dimensions == vol_dim]
        bdry_elements = [el for key, el in gmsh_vertex_nrs_to_element.iteritems()
                if el.el_type.dimensions == bdry_dim]

        # build hedge-compatible elements
        from hedge.mesh.element import TO_CURVED_CLASS

        hedge_vertices = []
        hedge_elements = []

        gmsh_node_nr_to_hedge_vertex_nr = {}
        hedge_el_to_gmsh_element = {}

        def get_vertex_nr(gmsh_node_nr):
            try:
                return gmsh_node_nr_to_hedge_vertex_nr[gmsh_node_nr]
            except KeyError:
                hedge_vertex_nr = len(hedge_vertices)
                hedge_vertices.append(nodes[gmsh_node_nr])
                gmsh_node_nr_to_hedge_vertex_nr[gmsh_node_nr] = hedge_vertex_nr
                return hedge_vertex_nr

        for el_nr, gmsh_el in enumerate(vol_elements):
            el_map = LocalToGlobalMap(
                    [nodes[ni] for ni in  gmsh_el.node_indices],
                    gmsh_el.el_type)
            is_affine = el_map.is_affine()

            el_class = gmsh_el.el_type.geometry
            if not is_affine:
                try:
                    el_class = TO_CURVED_CLASS[el_class]
                except KeyError:
                    raise GmshFileFormatError("unsupported curved element type %s" % el_class)

            vertex_indices = [get_vertex_nr(gmsh_node_nr)
                    for gmsh_node_nr in gmsh_el.gmsh_vertex_indices]

            if is_affine:
                hedge_el = el_class(el_nr, vertex_indices, hedge_vertices)
            else:
                hedge_el = el_class(el_nr, vertex_indices, el_map)

            hedge_elements.append(hedge_el)
            hedge_el_to_gmsh_element[hedge_el] = gmsh_el

        from pytools import reverse_dictionary
        hedge_vertex_nr_to_gmsh_node_nr = reverse_dictionary(
                gmsh_node_nr_to_hedge_vertex_nr)

        del vol_elements

        def volume_tagger(el, all_v):
            return [tag_name_map[tag_nr, el.dimensions]
                    for tag_nr in hedge_el_to_gmsh_element[el].tag_numbers
                    if (tag_nr, el.dimensions) in tag_name_map]

        def boundary_tagger(fvi, el, fn, all_v):
            gmsh_vertex_nrs = frozenset(
                    hedge_vertex_nr_to_gmsh_node_nr[face_vertex_index]
                    for face_vertex_index in fvi)

            try:
                gmsh_element = gmsh_vertex_nrs_to_element[gmsh_vertex_nrs]
            except KeyError:
                return []
            else:
                x = [tag_name_map[tag_nr, el.dimensions-1]
                        for tag_nr in gmsh_element.tag_numbers
                        if (tag_nr, el.dimensions-1) in tag_name_map]
                if len(x) > 1:
                    from pudb import set_trace; set_trace()
                return x

        vertex_array = np.array(hedge_vertices, dtype=np.float64)
        pt_dim = vertex_array.shape[-1]
        if pt_dim != vol_dim:
            from warnings import warn
            warn("Found %d-dimensional mesh embedded in %d-dimensional space. "
                    "Hedge only supports meshes of zero codimension (for now). "
                    "Maybe you want to set force_dimension=%d?"
                    % (vol_dim, pt_dim, vol_dim))

        from hedge.mesh import make_conformal_mesh_ext
        return make_conformal_mesh_ext(
                vertex_array,
                hedge_elements,
                boundary_tagger=boundary_tagger,
                volume_tagger=volume_tagger,
                periodicity=periodicity,
                allow_internal_boundaries=allow_internal_boundaries)

def main():
    mr = HedgeMeshReceiver()

    import sys
    from meshpy.gmsh_reader import read_gmsh
    read_gmsh(mr, sys.argv[1])


if __name__ == "__main__":
    main()

# vim: fdm=marker

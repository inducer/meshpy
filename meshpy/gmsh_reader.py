"""Reader for the GMSH file format."""

from __future__ import division

__copyright__ = "Copyright (C) 2009 Xueyu Zhu, Andreas Kloeckner"

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

import numpy as np
#import numpy.linalg as la
from pytools import memoize_method, Record
from meshpy.gmsh import LiteralSource, FileSource  # noqa


__doc__ = """
.. exception:: GmshFileFormatError

Element types
-------------

.. autoclass:: GmshElementBase
.. autoclass:: GmshPoint
.. autoclass:: GmshIntervalElement
.. autoclass:: GmshTriangularElement
.. autoclass:: GmshIncompleteTriangularElement
.. autoclass:: GmshTetrahedralElement

Receiver interface
------------------

.. autoclass:: GmshMeshReceiverBase

Receiver example implementation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: GmshMeshReceiverNumPy

Reader
------

.. autoclass:: LiteralSource
.. autoclass:: FileSource

.. autofunction:: read_gmsh
.. autofunction:: generate_gmsh

"""


# {{{ tools

def generate_triangle_vertex_tuples(order):
    yield (0, 0)
    yield (order, 0)
    yield (0, order)


def generate_triangle_edge_tuples(order):
    for i in range(1, order):
        yield (i, 0)
    for i in range(1, order):
        yield (order-i, i)
    for i in range(1, order):
        yield (0, order-i)


def generate_triangle_volume_tuples(order):
    for i in range(1, order):
        for j in range(1, order-i):
            yield (j, i)


class LineFeeder:
    def __init__(self, line_iterable):
        self.line_iterable = iter(line_iterable)
        self.next_line = None

    def has_next_line(self):
        if self.next_line is not None:
            return True

        try:
            self.next_line = self.line_iterable.next()
        except StopIteration:
            return False
        else:
            return True

    def get_next_line(self):
        if self.next_line is not None:
            nl = self.next_line
            self.next_line = None
            return nl.strip()

        try:
            nl = self.line_iterable.next()
        except StopIteration:
            raise GmshFileFormatError("unexpected end of file")
        else:
            return nl.strip()

# }}}


# {{{ element info

class GmshElementBase(object):
    """
    .. automethod:: vertex_count
    .. automethod:: node_count
    .. automethod:: get_lexicographic_gmsh_node_indices
    .. automethod:: equidistant_vandermonde
    .. method:: equidistant_unit_nodes

      (Implemented by subclasses)
    """

    def __init__(self, order):
        self.order = order

    def vertex_count(self):
        return self.dimensions + 1

    @memoize_method
    def node_count(self):
        """Return the number of interpolation nodes in this element."""
        d = self.dimensions
        o = self.order
        from operator import mul
        from pytools import factorial
        return int(reduce(mul, (o + 1 + i for i in range(d)), 1) / factorial(d))

    @memoize_method
    def lexicographic_node_tuples(self):
        """Generate tuples enumerating the node indices present
        in this element. Each tuple has a length equal to the dimension
        of the element. The tuples constituents are non-negative integers
        whose sum is less than or equal to the order of the element.
        """
        from pytools import \
                generate_nonnegative_integer_tuples_summing_to_at_most
        result = list(
                generate_nonnegative_integer_tuples_summing_to_at_most(
                    self.order, self.dimensions))

        assert len(result) == self.node_count()
        return result

    @memoize_method
    def get_lexicographic_gmsh_node_indices(self):
        gmsh_tup_to_index = dict(
                (tup, i)
                for i, tup in enumerate(self.gmsh_node_tuples()))

        return np.array([gmsh_tup_to_index[tup]
                for tup in self.lexicographic_node_tuples()],
                dtype=np.intp)

    def get_gmsh_indices(self, tuple_fun):
        """Utility function for reconstructing node indices for edges & faces
           from node indices for elements. Useful in specialized
           subclasses of GmshReceiverBase. Maps tuples enumerated by
           tuple_fun to element array indices via the mapping provided
           by get_lexicographic_gmsh_node indices.

        *Note:* This function provides machinery for calculating
           indices for lower-dimensional elements from the
           highest-available-dimensional element type in the mesh. If
           used over all elements, the resulting list will contain
           duplicate edges/faces (that is, an edge/face may be listed
           multiple times, possibly with different, but equivalent,
           representations, such as rotating an edge/face by
           self.order nodes), so that list should then be processed to
           remove duplicates in GmshReceiverBase (or one of its
           subclasses).

        """
        gmsh_tup_to_index = dict(
                (tup, i)
                for i, tup in enumerate(self.gmsh_node_tuples()))

        tuples = tuple_fun()
        num_tuples = len(tuples)
        indices = [None] * num_tuples
        for i in range(num_tuples):
            indices[i] = np.array([gmsh_tup_to_index[tup] for tup in tuples[i]])

        return indices

    @memoize_method
    def get_gmsh_edge_indices(self):
        """Specialization of get_gmsh_indices to get edge indices."""
        return self.get_gmsh_indices(self.gmsh_edge_tuples)

    @memoize_method
    def get_gmsh_face_indices(self):
        """Specialization of get_gmsh_indices to get face indices."""
        return self.get_gmsh_indices(self.gmsh_face_tuples)

    @memoize_method
    def equidistant_vandermonde(self):
        from hedge.polynomial import generic_vandermonde

        return generic_vandermonde(
                list(self.equidistant_unit_nodes()),
                list(self.basis_functions()))


class GmshPoint(GmshElementBase):
    dimensions = 0

    @memoize_method
    def gmsh_node_tuples(self):
        return [()]

    @memoize_method
    def gmsh_edge_tuples(self):
        # 0-d element has no edges, so return empty list
        # Empty list useful as degenerate case for iterators:
        # then
        # for i in []:
        #     """ Some code """
        # will do nothing.
        # Also note that the empty tuple is the "correct thing
        # to do" for gmsh_node_tuples because numpy_array[()]
        # returns all of the indices of the array.
        return []

    @memoize_method
    def gmsh_face_tuples(self):
        # 0-d element has no faces, so return empty list
        # Empty list useful as degenerate case for iterators
        return []


class GmshIntervalElement(GmshElementBase):
    dimensions = 1

    @memoize_method
    def gmsh_node_tuples(self):
        return [(0,), (self.order,), ] + [
                (i,) for i in range(1, self.order)]

    @memoize_method
    def gmsh_edge_tuples(self):
        # 1-d element, so edge is whole element; must return
        # iterable of iterables! Could also return [()] here;
        # see GmshPointElement for details.
        return [self.gmsh_node_tuples()]

    @memoize_method
    def gmsh_face_tuples(self):
        # 1-d element has no faces, so return empty list
        # Empty list useful as degenerate case for iterators
        return []


class GmshIncompleteTriangularElement(GmshElementBase):
    dimensions = 2

    def __init__(self, order):
        self.order = order

    @memoize_method
    def gmsh_node_tuples(self):
        result = []
        for tup in generate_triangle_vertex_tuples(self.order):
            result.append(tup)
        for tup in generate_triangle_edge_tuples(self.order):
            result.append(tup)
        return result

    @memoize_method
    def gmsh_edge_tuples(self):
        # 3 edges: x-axis, y-axis, x + y = order
        x_axis_edge = [(i, 0) for i in range(self.order + 1)]
        y_axis_edge = [(0, i) for i in range(self.order + 1)]
        x_plus_y_eq_order_edge = [(self.order - i, i)
                                  for i in range(self.order + 1)]
        return [x_axis_edge, y_axis_edge, x_plus_y_eq_order_edge]

    @memoize_method
    def gmsh_face_tuples(self):
        # 2-d element, so face is whole element; must return a
        # iterable of iterables! Could also return [()] here.
        return [self.gmsh_node_tuples()]


class GmshTriangularElement(GmshElementBase):
    dimensions = 2

    @memoize_method
    def gmsh_node_tuples(self):
        result = []
        for tup in generate_triangle_vertex_tuples(self.order):
            result.append(tup)
        for tup in generate_triangle_edge_tuples(self.order):
            result.append(tup)
        for tup in generate_triangle_volume_tuples(self.order):
            result.append(tup)
        return result

    @memoize_method
    def gmsh_edge_tuples(self):
        # 3 edges: x-axis, y-axis, x + y = order
        x_axis_edge = [(i, 0) for i in range(self.order + 1)]
        y_axis_edge = [(0, i) for i in range(self.order + 1)]
        x_plus_y_eq_order_edge = [(self.order - i, i)
                                  for i in range(self.order + 1)]
        return [x_axis_edge, y_axis_edge, x_plus_y_eq_order_edge]

    @memoize_method
    def gmsh_face_tuples(self):
        # 2-d element, so face is whole element; must return an iterable
        # of iterables! Could also return [()] here.
        return [self.gmsh_node_tuples()]


class GmshTetrahedralElement(GmshElementBase):
    dimensions = 3

    @memoize_method
    def gmsh_node_tuples(self):
        # gmsh's node ordering is on crack
        return {
                1: [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)],
                2: [
                    (0, 0, 0), (2, 0, 0), (0, 2, 0), (0, 0, 2), (1, 0, 0), (1, 1, 0),
                    (0, 1, 0), (0, 0, 1), (0, 1, 1), (1, 0, 1)],
                3: [
                    (0, 0, 0), (3, 0, 0), (0, 3, 0), (0, 0, 3), (1, 0, 0), (2, 0, 0),
                    (2, 1, 0), (1, 2, 0), (0, 2, 0), (0, 1, 0), (0, 0, 2), (0, 0, 1),
                    (0, 1, 2), (0, 2, 1), (1, 0, 2), (2, 0, 1), (1, 1, 0), (1, 0, 1),
                    (0, 1, 1), (1, 1, 1)],
                4: [
                    (0, 0, 0), (4, 0, 0), (0, 4, 0), (0, 0, 4), (1, 0, 0), (2, 0, 0),
                    (3, 0, 0), (3, 1, 0), (2, 2, 0), (1, 3, 0), (0, 3, 0), (0, 2, 0),
                    (0, 1, 0), (0, 0, 3), (0, 0, 2), (0, 0, 1), (0, 1, 3), (0, 2, 2),
                    (0, 3, 1), (1, 0, 3), (2, 0, 2), (3, 0, 1), (1, 1, 0), (1, 2, 0),
                    (2, 1, 0), (1, 0, 1), (2, 0, 1), (1, 0, 2), (0, 1, 1), (0, 1, 2),
                    (0, 2, 1), (1, 1, 2), (2, 1, 1), (1, 2, 1), (1, 1, 1)],
                5: [
                    (0, 0, 0), (5, 0, 0), (0, 5, 0), (0, 0, 5), (1, 0, 0), (2, 0, 0),
                    (3, 0, 0), (4, 0, 0), (4, 1, 0), (3, 2, 0), (2, 3, 0), (1, 4, 0),
                    (0, 4, 0), (0, 3, 0), (0, 2, 0), (0, 1, 0), (0, 0, 4), (0, 0, 3),
                    (0, 0, 2), (0, 0, 1), (0, 1, 4), (0, 2, 3), (0, 3, 2), (0, 4, 1),
                    (1, 0, 4), (2, 0, 3), (3, 0, 2), (4, 0, 1), (1, 1, 0), (1, 3, 0),
                    (3, 1, 0), (1, 2, 0), (2, 2, 0), (2, 1, 0), (1, 0, 1), (3, 0, 1),
                    (1, 0, 3), (2, 0, 1), (2, 0, 2), (1, 0, 2), (0, 1, 1), (0, 1, 3),
                    (0, 3, 1), (0, 1, 2), (0, 2, 2), (0, 2, 1), (1, 1, 3), (3, 1, 1),
                    (1, 3, 1), (2, 1, 2), (2, 2, 1), (1, 2, 2), (1, 1, 1), (2, 1, 1),
                    (1, 2, 1), (1, 1, 2)],
                }[self.order]

        @memoize_method
        def gmsh_edge_tuples(self):
            all_tuples = self.gmsh_node_tuples()
            # 6 edges: x-axis, y-axis, z-axis
            #          x + y = order, x + z = order, y + z = order
            x_axis_edge = [(i, 0, 0) for i in range(self.order + 1)]
            y_axis_edge = [(0, i, 0) for i in range(self.order + 1)]
            z_axis_edge = [(0, 0, i) for i in range(self.order + 1)]
            x_plus_y_eq_order_edge = [(self.order - i, i, 0)
                                      for i in range(self.order + 1)]
            x_plus_z_eq_order_edge = [(self.order - i, 0, i)
                                      for i in range(self.order + 1)]
            y_plus_z_eq_order_edge = [(0, self.order - i, i)
                                      for i in range(self.order + 1)]
            return [x_axis_edge,
                    y_axis_edge,
                    z_axis_edge,
                    x_plus_y_eq_order_edge,
                    x_plus_z_eq_order_edge,
                    y_plus_z_eq_order_edge]

        @memoize_method
        def gmsh_face_tuples(self):
            all_tuples = self.gmsh_node_tuples()
            # 4 faces: x = 0, y = 0, z = 0, x + y + z = order
            x_eq_0_face = [tup for tup in all_tuples if tup[0] == 0]
            y_eq_0_face = [tup for tup in all_tuples if tup[1] == 0]
            z_eq_0_face = [tup for tup in all_tuples if tup[2] == 0]
            sum_eq_order = [tup for tup in all_tuples
                            if tup[0] + tup[1] + tup[2] == self.order]
            return [x_eq_0_face,
                    y_eq_0_face,
                    z_eq_0_face,
                    sum_eq_order_face]


# }}}


# {{{ receiver interface

class GmshMeshReceiverBase(object):
    """
    .. attribute:: gmsh_element_type_to_info_map
    .. automethod:: set_up_nodes
    .. automethod:: add_node
    .. automethod:: finalize_nodes
    .. automethod:: set_up_elements
    .. automethod:: add_element
    .. automethod:: finalize_elements
    .. automethod:: add_tag
    .. automethod:: finalize_tags
    """

    gmsh_element_type_to_info_map = {
            1:  GmshIntervalElement(1),
            2:  GmshTriangularElement(1),
            4:  GmshTetrahedralElement(1),
            8:  GmshIntervalElement(2),
            9:  GmshTriangularElement(2),
            11: GmshTetrahedralElement(2),
            15: GmshPoint(0),
            20: GmshIncompleteTriangularElement(3),
            21: GmshTriangularElement(3),
            22: GmshIncompleteTriangularElement(4),
            23: GmshTriangularElement(4),
            24: GmshIncompleteTriangularElement(5),
            25: GmshTriangularElement(5),
            26: GmshIntervalElement(3),
            27: GmshIntervalElement(4),
            28: GmshIntervalElement(5),
            29: GmshTetrahedralElement(3),
            30: GmshTetrahedralElement(4),
            31: GmshTetrahedralElement(5)
            }

    def set_up_nodes(self, count):
        pass

    def add_node(self, node_nr, point):
        pass

    def finalize_nodes(self):
        pass

    def set_up_elements(self, count):
        pass

    def add_element(self, element_nr, element_type, vertex_nrs,
            lexicographic_nodes, tag_numbers):
        pass

    def finalize_elements(self):
        pass

    def add_tag(self, name, index, dimension):
        pass

    def finalize_tags(self):
        pass

# }}}


# {{{ receiver example

class GmshMeshReceiverNumPy(GmshMeshReceiverBase):
    """GmshReceiver that emulates the semantics of
    :class:`meshpy.triangle.MeshInfo` and :class:`meshpy.tet.MeshInfo` by using
    similar fields, but instead of loading data into ForeignArrays, load into
    NumPy arrays. Since this class is not wrapping any libraries in other
    languages -- the Gmsh data is obtained via parsing text -- use :mod:`numpy`
    arrays as the base array data structure for convenience.

    .. versionadded:: 2014.1
    """

    def __init__(self):
        # Use data fields similar to meshpy.triangle.MeshInfo and
        # meshpy.tet.MeshInfo
        self.points = None
        self.elements = None
        self.element_types = None
        self.element_markers = None
        self.tags = None

    # Gmsh has no explicit concept of facets or faces; certain faces are a type
    # of element.  Consequently, there are no face markers, but elements can be
    # grouped together in physical groups that serve as markers.

    def set_up_nodes(self, count):
        # Preallocate array of nodes within list; treat None as sentinel value.
        # Preallocation not done for performance, but to assign values at indices
        # in random order.
        self.points = [None] * count

    def add_node(self, node_nr, point):
        self.points[node_nr] = point

    def finalize_nodes(self):
        pass

    def set_up_elements(self, count):
        # Preallocation of arrays for assignment elements in random order.
        self.elements = [None] * count
        self.element_types = [None] * count
        self.element_markers = [None] * count
        self.tags = []

    def add_element(self, element_nr, element_type, vertex_nrs,
            lexicographic_nodes, tag_numbers):
        self.elements[element_nr] = vertex_nrs
        self.element_types[element_nr] = element_type
        self.element_markers[element_nr] = tag_numbers
        # TODO: Add lexicographic node information

    def finalize_elements(self):
        pass

    def add_tag(self, name, index, dimension):
        self.tags.append((name, index, dimension))

    def finalize_tags(self):
        pass

# }}}


# {{{ file reader

class GmshFileFormatError(RuntimeError):
    pass


def read_gmsh(receiver, filename, force_dimension=None):
    """Read a gmsh mesh file from *filename* and feed it to *receiver*.

    :param receiver: Implements the :class:`GmshMeshReceiverBase` interface.
    :param force_dimension: if not None, truncate point coordinates to
        this many dimensions.
    """
    mesh_file = open(filename, 'rt')
    try:
        result = parse_gmsh(receiver, mesh_file, force_dimension=force_dimension)
    finally:
        mesh_file.close()

    return result


def generate_gmsh(receiver, source, dimensions, order=None, other_options=[],
            extension="geo", gmsh_executable="gmsh", force_dimension=None):
    """Run gmsh and feed the output to *receiver*.

    :arg source: an instance of :class:`LiteralSource` or :class:`FileSource`
    :param receiver: Implements the :class:`GmshMeshReceiverBase` interface.
    """
    from meshpy.gmsh import GmshRunner
    runner = GmshRunner(source, dimensions, order=order,
            other_options=other_options, extension=extension,
            gmsh_executable=gmsh_executable)

    runner.__enter__()
    try:
        result = parse_gmsh(receiver, runner.output_file,
                force_dimension=force_dimension)
    finally:
        runner.__exit__(None, None, None)

    return result


def parse_gmsh(receiver, line_iterable, force_dimension=None):
    """
    :arg source: an instance of :class:`LiteralSource` or :class:`FileSource`
    :arg receiver: This object will be fed the entities encountered in reading the
        GMSH file. See :class:`GmshMeshReceiverBase` for the interface this
        object needs to conform to.
    :param force_dimension: if not None, truncate point coordinates to this many
        dimensions.
    """

    feeder = LineFeeder(line_iterable)

    # collect the mesh information

    class ElementInfo(Record):
        pass

    while feeder.has_next_line():
        next_line = feeder.get_next_line()
        if not next_line.startswith("$"):
            raise GmshFileFormatError(
                    "expected start of section, '%s' found instead" % next_line)

        section_name = next_line[1:]

        if section_name == "MeshFormat":
            line_count = 0
            while True:
                next_line = feeder.get_next_line()
                if next_line == "$End"+section_name:
                    break

                if line_count == 0:
                    version_number, file_type, data_size = next_line.split()

                if line_count > 0:
                    raise GmshFileFormatError(
                            "more than one line found in MeshFormat section")

                if version_number not in ["2.1", "2.2"]:
                    from warnings import warn
                    warn("unexpected mesh version number '%s' found"
                            % version_number)

                if file_type != "0":
                    raise GmshFileFormatError(
                            "only ASCII gmsh file type is supported")

                line_count += 1

        elif section_name == "Nodes":
            node_count = int(feeder.get_next_line())
            receiver.set_up_nodes(node_count)

            node_idx = 1

            while True:
                next_line = feeder.get_next_line()
                if next_line == "$End"+section_name:
                    break

                parts = next_line.split()
                if len(parts) != 4:
                    raise GmshFileFormatError(
                            "expected four-component line in $Nodes section")

                read_node_idx = int(parts[0])
                if read_node_idx != node_idx:
                    raise GmshFileFormatError("out-of-order node index found")

                if force_dimension is not None:
                    point = [float(x) for x in parts[1:force_dimension+1]]
                else:
                    point = [float(x) for x in parts[1:]]

                receiver.add_node(
                        node_idx-1,
                        np.array(point, dtype=np.float64))

                node_idx += 1

            if node_count+1 != node_idx:
                raise GmshFileFormatError("unexpected number of nodes found")

            receiver.finalize_nodes()

        elif section_name == "Elements":
            element_count = int(feeder.get_next_line())
            receiver.set_up_elements(element_count)

            element_idx = 1
            while True:
                next_line = feeder.get_next_line()
                if next_line == "$End"+section_name:
                    break

                parts = [int(x) for x in next_line.split()]

                if len(parts) < 4:
                    raise GmshFileFormatError("too few entries in element line")

                read_element_idx = parts[0]
                if read_element_idx != element_idx:
                    raise GmshFileFormatError("out-of-order node index found")

                el_type_num = parts[1]
                try:
                    element_type = \
                            receiver.gmsh_element_type_to_info_map[el_type_num]
                except KeyError:
                    raise GmshFileFormatError("unexpected element type %d"
                            % el_type_num)

                tag_count = parts[2]
                tags = parts[3:3+tag_count]

                # convert to zero-based
                node_indices = np.array(
                        [x-1 for x in parts[3+tag_count:]], dtype=np.intp)

                if element_type.node_count() != len(node_indices):
                    raise GmshFileFormatError(
                            "unexpected number of nodes in element")

                gmsh_vertex_nrs = node_indices[:element_type.vertex_count()]
                zero_based_idx = element_idx - 1

                tag_numbers = [tag for tag in tags[:1] if tag != 0]

                receiver.add_element(element_nr=zero_based_idx,
                        element_type=element_type, vertex_nrs=gmsh_vertex_nrs,
                        lexicographic_nodes=node_indices[
                            element_type.get_lexicographic_gmsh_node_indices()],
                        tag_numbers=tag_numbers)

                element_idx += 1

            if element_count+1 != element_idx:
                raise GmshFileFormatError("unexpected number of elements found")

            receiver.finalize_elements()

        elif section_name == "PhysicalNames":
            name_count = int(feeder.get_next_line())
            name_idx = 1

            while True:
                next_line = feeder.get_next_line()
                if next_line == "$End"+section_name:
                    break

                dimension, number, name = next_line.split(" ", 2)
                dimension = int(dimension)
                number = int(number)

                if not name[0] == '"' or not name[-1] == '"':
                    raise GmshFileFormatError("expected quotes around physical name")

                receiver.add_tag(name[1:-1], number, dimension)

                name_idx += 1

            if name_count+1 != name_idx:
                raise GmshFileFormatError(
                        "unexpected number of physical names found")

            receiver.finalize_tags()
        else:
            # unrecognized section, skip
            from warnings import warn
            warn("unrecognized section '%s' in gmsh file" % section_name)
            while True:
                next_line = feeder.get_next_line()
                if next_line == "$End"+section_name:
                    break

# }}}

# vim: fdm=marker

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
import numpy.linalg as la
from pytools import memoize_method, Record, single_valued


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

        The order in which these nodes are generated dictates the local
        node numbering.
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



class GmshIntervalElement(GmshElementBase):
    dimensions = 1

    @memoize_method
    def gmsh_node_tuples(self):
        return [(0,), (self.order,),] + [
                (i,) for i in range(1, self.order)]




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






# }}}

# {{{ receiver interface

class GmshMeshReceiverBase(object):
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

# {{{ file reader

class GmshFileFormatError(RuntimeError):
    pass




def read_gmsh(receiver, filename, force_dimension=None):
    """
    :param force_dimension: if not None, truncate point coordinates to this many dimensions.
    """
    mesh_file = open(filename, 'rt')
    try:
        result = parse_gmsh(receiver, mesh_file)
    finally:
        mesh_file.close()

    return result




def generate_gmsh(receiver, source, dimensions, order=None, other_options=[],
            extension="geo", gmsh_executable="gmsh", force_dimension=None):
    from meshpy.gmsh import GmshRunner
    runner = GmshRunner(source, dimensions, order=order,
            other_options=other_options, extension=extension,
            gmsh_executable=gmsh_executable)

    runner.__enter__()
    try:
        result = parse_gmsh(receiver, runner.output_file, force_dimension=force_dimension)
    finally:
        runner.__exit__(None, None, None)

    return result




def parse_gmsh(receiver, line_iterable, force_dimension=None):
    """
    :arg receiver: This object will be fed the entities encountered in reading the
        GMSH file. See :class:`GmshMeshReceiverBase` for the interface this object needs
        to conform to.
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
            raise GmshFileFormatError("expected start of section, '%s' found instead" % next_line)

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
                    raise GmshFileFormatError("more than one line found in MeshFormat section")

                if version_number not in ["2.1", "2.2"]:
                    from warnings import warn
                    warn("unexpected mesh version number '%s' found" % version_number)

                if file_type != "0":
                    raise GmshFileFormatError("only ASCII gmsh file type is supported")

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
                    raise GmshFileFormatError("expected four-component line in $Nodes section")

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
                    element_type = receiver.gmsh_element_type_to_info_map[el_type_num]
                except KeyError:
                    raise GmshFileFormatError("unexpected element type %d"
                            % el_type_num)

                tag_count = parts[2]
                tags = parts[3:3+tag_count]

                # convert to zero-based
                node_indices = np.array([x-1 for x in parts[3+tag_count:]], dtype=np.intp)

                if element_type.node_count()!= len(node_indices):
                    raise GmshFileFormatError("unexpected number of nodes in element")

                gmsh_vertex_nrs = node_indices[:element_type.vertex_count()]
                zero_based_idx = element_idx - 1

                tag_numbers = [tag for tag in tags[:1] if tag != 0]

                receiver.add_element(element_nr=zero_based_idx,
                        element_type=element_type, vertex_nrs=gmsh_vertex_nrs,
                        lexicographic_nodes=node_indices[
                            element_type.get_lexicographic_gmsh_node_indices()],
                        tag_numbers=tag_numbers)

                element_idx +=1

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
                raise GmshFileFormatError("unexpected number of physical names found")

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

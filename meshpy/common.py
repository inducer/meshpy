from __future__ import absolute_import
from __future__ import print_function
from six.moves import range
from six.moves import zip
class _Table:
    def __init__(self):
        self.Rows = []

    def add_row(self, row):
        self.Rows.append([str(i) for i in row])

    def __str__(self):
        columns = len(self.Rows[0])
        col_widths = [max(len(row[i]) for row in self.Rows)
                      for i in range(columns)]

        lines = [
            " ".join([cell.ljust(col_width)
                      for cell, col_width in zip(row, col_widths)])
            for row in self.Rows]
        return "\n".join(lines)




def _linebreak_list(list, per_line=10, pad=None):
    def format(s):
        if pad is None:
            return str(s)
        else:
            return str(s).rjust(pad)

    result = ""
    while len(list) > per_line:
        result += " ".join(format(l) for l in list[:per_line]) + "\n"
        list = list[per_line:]
    return result + " ".join(format(l) for l in list)



class MeshInfoBase:
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





    def set_points(self, points, point_markers=None):
        if point_markers is not None:
            assert len(point_markers) == len(point_markers)

        self.points.resize(len(points))

        for i, pt in enumerate(points):
            self.points[i] = pt

        if point_markers is not None:
            self.point_markers.setup()
            for i, mark in enumerate(point_markers):
                self.point_markers[i] = mark





    def set_holes(self, hole_starts):
        self.holes.resize(len(hole_starts))
        for i, hole in enumerate(hole_starts):
            self.holes[i] = hole




    def write_neu(self, outfile, bc={}, periodicity=None, description="MeshPy Output"):
        """Write the mesh out in (an approximation to) Gambit neutral mesh format.

        outfile is a file-like object opened for writing.

        bc is a dictionary mapping single face markers (or frozensets of them)
        to a tuple (bc_name, bc_code).

        periodicity is either a tuple (face_marker, (px,py,..)) giving the
        face marker of the periodic boundary and the period in each coordinate
        direction (0 if none) or the value None for no periodicity.
        """

        from meshpy import version
        from datetime import datetime

        # header --------------------------------------------------------------
        outfile.write("CONTROL INFO 2.1.2\n")
        outfile.write("** GAMBIT NEUTRAL FILE\n")
        outfile.write("%s\n" % description)
        outfile.write("PROGRAM: MeshPy VERSION: %s\n" % version)
        outfile.write("%s\n" % datetime.now().ctime())

        bc_markers = list(bc.keys())
        if periodicity:
            periodic_marker, periods = periodicity
            bc_markers.append(periodic_marker)

        assert len(self.points)

        dim = len(self.points[0])
        data = (
                ("NUMNP", len(self.points)),
                ("NELEM", len(self.elements)),
                ("NGRPS", 1),
                ("NBSETS", len(bc_markers)),
                ("NDFCD", dim),
                ("NDFVL", dim),
                )

        tbl = _Table()
        tbl.add_row(key for key, value in data)
        tbl.add_row(value for key, value in data)
        outfile.write(str(tbl))
        outfile.write("\n")
        outfile.write("ENDOFSECTION\n")

        # nodes ---------------------------------------------------------------
        outfile.write("NODAL COORDINATES 2.1.2\n")
        for i, pt in enumerate(self.points):
            outfile.write("%d %s\n" %
                    (i+1, " ".join(repr(c) for c in pt)))
        outfile.write("ENDOFSECTION\n")

        # elements ------------------------------------------------------------
        outfile.write("ELEMENTS/CELLS 2.1.2\n")
        if dim == 2:
            eltype = 3
        else:
            eltype = 6

        for i, el in enumerate(self.elements):
            outfile.write("%8d%3d%3d %s\n" %
                    (i+1, eltype, len(el),
                        "".join("%8d" % (p+1) for p in el)))
        outfile.write("ENDOFSECTION\n")

        # element groups ------------------------------------------------------
        outfile.write("ELEMENT GROUP 1.3.0\n")
        # FIXME
        i = 0
        grp_elements = list(range(len(self.elements)))
        material = 1
        flags = 0
        outfile.write("GROUP:%11d ELEMENTS:%11d MATERIAL:%11s NFLAGS: %11d\n"
                % (1, len(grp_elements), repr(material), flags))
        outfile.write(("epsilon: %s\n" % material).rjust(32)) # FIXME
        outfile.write("0\n")
        outfile.write(_linebreak_list([str(i+1) for i in grp_elements],
            pad=8)
                + "\n")
        outfile.write("ENDOFSECTION\n")

        # boundary conditions -------------------------------------------------
        # build mapping face -> (tet, neu_face_index)
        face2el = {}

        if dim == 2:
            for ti, el in enumerate(self.elements):
                # Sledge++ Users' Guide, figure 4
                faces = [
                        frozenset([el[0], el[1]]),
                        frozenset([el[1], el[2]]),
                        frozenset([el[2], el[0]]),
                        ]
                for fi, face in enumerate(faces):
                    face2el.setdefault(face, []).append((ti, fi+1))

        elif dim == 3:
            face2el = {}
            for ti, el in enumerate(self.elements):
                # Sledge++ Users' Guide, figure 5
                faces = [
                        frozenset([el[1], el[0], el[2]]),
                        frozenset([el[0], el[1], el[3]]),
                        frozenset([el[1], el[2], el[3]]),
                        frozenset([el[2], el[0], el[3]]),
                        ]
                for fi, face in enumerate(faces):
                    face2el.setdefault(face, []).append((ti, fi+1))

        else:
            raise ValueError("invalid number of dimensions (%d)" % dim)

        # actually output bc sections
        if not self.faces.allocated:
            from warnings import warn
            warn("no exterior faces in mesh data structure, not writing boundary conditions")
        else:
            # requires -f option in tetgen, -e in triangle

            for bc_marker in bc_markers:
                if isinstance(bc_marker, frozenset):
                    face_indices = [i
                            for i, face in enumerate(self.faces)
                            if self.face_markers[i] in bc_marker]
                else:
                    face_indices = [i
                            for i, face in enumerate(self.faces)
                            if bc_marker == self.face_markers[i]]

                if not face_indices:
                    continue

                outfile.write("BOUNDARY CONDITIONS 2.1.2\n")
                if bc_marker in bc:
                    # regular BC

                    bc_name, bc_code = bc[bc_marker]
                    outfile.write("%32s%8d%8d%8d%8d\n"
                            % (bc_name,
                                1, # face BC
                                len(face_indices),
                                0, # zero additional values per face,
                                bc_code,
                                )
                            )
                else:
                    # periodic BC

                    outfile.write("%s%s%8d%8d%8d\n"
                            % ("periodic", " ".join(repr(p) for p in periods),
                                len(face_indices),
                                0, # zero additional values per face,
                                0,
                                )
                            )

                for i, fi in enumerate(face_indices):
                    face_nodes = frozenset(self.faces[fi])
                    adj_el = face2el[face_nodes]
                    assert len(adj_el) == 1

                    el_index, el_face_number = adj_el[0]

                    outfile.write("%10d%5d%5d\n" %
                            (el_index+1, eltype, el_face_number))

                outfile.write("ENDOFSECTION\n")

            outfile.close()
            # FIXME curved boundaries?
            # FIXME proper element group support





def dump_array(name, array):
    print("array %s: %d elements, %d values per element" % (name, len(array), array.unit))

    if len(array) == 0 or array.unit == 0:
        return

    try:
        array[0]
    except RuntimeError:
        print("  not allocated")
        return

    for i, entry in enumerate(array):
        if isinstance(entry, list):
            print("  %d: %s" % (i, ",".join(str(sub) for sub in entry)))
        else:
            print("  %d: %s" % (i, entry))


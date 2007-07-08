from meshpy.common import MeshInfoBase, dump_array
import meshpy._triangle as internals




class MeshInfo(internals.MeshInfo, MeshInfoBase):
    _constituents = [ 
            "points", "point_attributes", "point_markers", 
            "elements", "element_attributes", "element_volumes", 
            "neighbors", 
            "faces", "face_markers", 
            "holes", 
            "regions", 
            "edges", "edge_markers", 
            "normals", 
            ]

    def __getstate__(self):
        def dump_array(array):
            try:
                return [
                    [array[i,j] for j in range(array.unit)]
                    for i in range(len(array))]
            except RuntimeError:
                # not allocated
                return None

        return self.number_of_point_attributes, \
               self.number_of_element_attributes, \
               [(name, dump_array(getattr(self, name))) for name in self._constituents]

    def __setstate__(self, (p_attr_count, e_attr_count, state)):
        self.number_of_point_attributes = p_attr_count
        self.number_of_element_attributes = e_attr_count
        for name, array in state:
            if name not in self._constituents:
                raise RuntimeError, "Unknown constituent during unpickling"

            dest_array = getattr(self, name)

            if array is None:
                dest_array.deallocate()
            else:
                if len(dest_array) != len(array):
                    dest_array.resize(len(array))
                if not dest_array.allocated and len(array)>0:
                    dest_array.setup()

                for i,tup in enumerate(array):
                    for j,v in enumerate(tup):
                        dest_array[i, j] = v

    def set_faces(self, faces, face_markers=None):
        self.faces.resize(len(faces))
        
        for i, face in enumerate(faces):
            self.faces[i] = face

        if face_markers is not None:
            self.face_markers.setup()
            for i, mark in enumerate(face_markers):
                self.face_markers[i] = mark

    def dump(self):
        for name in self._constituents:
            dump_array(name, getattr(self, name))







def build(mesh_info, verbose=False, refinement_func=None, attributes=False,
        volume_constraints=True, max_volume=None):
    """Triangulate the domain given in `mesh_info'."""
    opts = "pzqj"
    if verbose:
        opts += "VV"
    else:
        opts += "Q"

    if attributes:
        opts += "A"

    if volume_constraints:
        opts += "a"
        if max_volume:
            raise ValueError, "cannot specify both area_constraints and max_area"
    elif max_volume:
        opts += "a%s" % repr(max_area)

    if refinement_func is not None:
        opts += "u"

    mesh = MeshInfo()
    internals.triangulate(opts, mesh_info, mesh, MeshInfo(), refinement_func)
    return mesh




def refine(input_p, verbose=False, refinement_func=None):
    opts = "razj"
    if len(input_p.faces) != 0:
        opts += "p"
    if verbose:
        opts += "VV"
    else:
        opts += "Q"
    if refinement_func is not None:
        opts += "u"
    output_p = MeshInfo()
    internals.triangulate(opts, input_p, output_p, MeshInfo(), refinement_func)
    return output_p




def write_gnuplot_mesh(filename, out_p):
    gp_file = file(filename, "w")
    
    for points in out_p.elements:
        for pt in points:
            gp_file.write("%f %f 0\n" % tuple(out_p.points[pt]))
        gp_file.write("%f %f 0\n\n" % tuple(out_p.points[points[0]]))


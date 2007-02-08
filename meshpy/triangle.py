from meshpy.common import MeshInfoBase
import meshpy._triangle as internals




class MeshInfo(internals.MeshInfo, MeshInfoBase):
    _constituents = [ 
            "points", "point_attributes", "point_markers", 
            "elements", "element_attributes", "element_volumes", 
            "neighbors", 
            "segments", "segment_markers", 
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

                for i,tup in enumerate(array):
                    for j,v in enumerate(tup):
                        dest_array[i, j] = v

    def set_segments(self, segments, segment_markers=None):
        self.segments.resize(len(segments))
        
        for i, seg in enumerate(segments):
            self.segments[i] = seg

        if segment_markers is not None:
            assert len(segment_markers) == len(segments)
            for i, mark in enumerate(segment_markers):
                self.SegmentMarkers[i] = mark








def build(mesh_info, verbose=False, refinement_func=None):
    opts = "pzqj"
    if verbose:
        opts += "VV"
    else:
        opts += "Q"
    if refinement_func is not None:
        opts += "u"

    mesh = MeshInfo()
    internals.triangulate(opts, mesh_info, mesh, MeshInfo(), refinement_func)
    return mesh




def refine(input_p, verbose=False, refinement_func=None):
    opts = "razj"
    if input_p.Segments.size() != 0:
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




def dump_parameters(par):
    def dump_array(name, array):
        subs = array.unit()
        print "array %s: %d elements, %d values per element" % (name, array.size(), subs)
        if array.size() == 0 or array.unit() == 0:
            return
        try:
            array.get(0)
        except RuntimeError:
            print "  not allocated"
            return

        for i in range(array.size()):
            print "  %d:" % i,
            for j in range(subs):
                print array.get_sub(i,j),
            print

    for name, arr in par._constituents:
        dump_array(name, getattr(par, name))




def write_gnuplot_mesh(filename, out_p):
    gp_file = file(filename, "w")
    
    for points in out_p.elements:
        for pt in points:
            gp_file.write("%f %f 0\n" % tuple(out_p.points[pt]))
        gp_file.write("%f %f 0\n\n" % tuple(out_p.points[points[0]]))


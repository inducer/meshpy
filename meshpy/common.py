class MeshInfoBase:
    def set_points(self, points, point_markers=None):
        if point_markers is not None:
            assert len(point_markers) == len(point_markers)

        self.points.resize(len(points))

        for i, pt in enumerate(points):
            self.points[i] = pt
      
        if point_markers is not None:
            for i, mark in enumerate(point_markers):
                self.point_markers[i] = mark





    def set_holes(self, hole_starts):
        self.holes.resize(len(hole_starts))
        for i, hole in enumerate(hole_starts):
            self.holes[i] = hole




def dump_array(name, array):
    print "array %s: %d elements, %d values per element" % (name, len(array), array.unit)

    if len(array) == 0 or array.unit == 0:
        return

    try:
        array[0]
    except RuntimeError:
        print "  not allocated"
        return

    for i, entry in enumerate(array):
        if isinstance(entry, list):
            print "  %d: %s" % (i, ",".join(str(sub) for sub in entry))
        else:
            print "  %d: %s" % (i, entry)


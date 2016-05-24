from __future__ import absolute_import

import six
from six.moves import range


def uniform_refine_triangles(points, elements, factor=2):
    new_points = points[:]
    new_elements = []
    old_face_to_new_faces = {}
    face_point_dict = {}

    points_per_edge = factor+1

    def get_refined_face(a, b):
        if a > b:
            a, b = b, a
            flipped = True
        else:
            flipped = False

        try:
            face_points = face_point_dict[a, b]
        except KeyError:
            a_pt, b_pt = [points[idx] for idx in [a, b]]
            dx = (b_pt - a_pt)/factor

            # build subdivided facet
            face_points = [a]

            for i in range(1, points_per_edge-1):
                face_points.append(len(new_points))
                new_points.append(a_pt + dx*i)

            face_points.append(b)

            face_point_dict[a, b] = face_points

            # build old_face_to_new_faces
            old_face_to_new_faces[frozenset([a, b])] = [
                    (face_points[i], face_points[i+1])
                    for i in range(factor)]

        if flipped:
            return face_points[::-1]
        else:
            return face_points

    for a, b, c in elements:
        a_pt, b_pt, c_pt = [points[idx] for idx in [a, b, c]]
        dr = (b_pt - a_pt)/factor
        ds = (c_pt - a_pt)/factor

        ab_refined, bc_refined, ac_refined = [
                get_refined_face(*pt_indices)
                for pt_indices in [(a, b), (b, c), (a, c)]]

        el_point_dict = {}

        # fill out edges of el_point_dict
        for i in range(points_per_edge):
            el_point_dict[i, 0] = ab_refined[i]
            el_point_dict[0, i] = ac_refined[i]
            el_point_dict[points_per_edge-1-i, i] = bc_refined[i]

        # fill out interior of el_point_dict
        for i in range(1, points_per_edge-1):
            for j in range(1, points_per_edge-1-i):
                el_point_dict[i, j] = len(new_points)
                new_points.append(a_pt + dr*i + ds*j)

        # generate elements
        for i in range(0, points_per_edge-1):
            for j in range(0, points_per_edge-1-i):
                new_elements.append((
                    el_point_dict[i, j],
                    el_point_dict[i+1, j],
                    el_point_dict[i, j+1],
                    ))
                if i+1+j+1 <= factor:
                    new_elements.append((
                        el_point_dict[i+1, j+1],
                        el_point_dict[i+1, j],
                        el_point_dict[i, j+1],
                        ))

    from meshpy.triangle import MeshInfo
    mi = MeshInfo()
    mi.set_points(new_points)
    mi.elements.resize(len(new_elements))
    for i, el in enumerate(new_elements):
        mi.elements[i] = el
    from meshpy.triangle import write_gnuplot_mesh
    write_gnuplot_mesh("mesh.dat", mi)

    return new_points, new_elements, old_face_to_new_faces


def make_swizzle_matrix(spec):
    import numpy
    axes = ["x", "y", "z"]

    mapping = dict((axis, axis) for axis in axes)
    for one_spec in spec.split(","):
        import_axis, final_axis = one_spec.split(":")
        mapping[import_axis] = final_axis

    assert set(mapping.keys()) == set(axes), \
            "axis mapping not complete"
    assert set(axis.lstrip("-") for axis in six.itervalues(mapping)) == set(axes), \
            "Axis mapping not onto"

    n = len(axes)
    result = numpy.zeros((n, n), dtype=int)

    for imp_axis, final_axis in six.iteritems(mapping):
        imp_axis = axes.index(imp_axis)

        sign = 1
        while final_axis.startswith("-"):
            sign *= -1
            final_axis = final_axis[1:]
        final_axis = axes.index(final_axis)

        result[final_axis, imp_axis] = sign

    return result

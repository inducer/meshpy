Triangle/TetGen interface
=========================

.. module:: meshpy

Some common notions
-------------------

.. class:: ForeignArray

    Note that :class:`ForeignArray` instances are not usually created by users,
    and :class:`ForeignArray`  is not a class name available in MeshPy. It is
    just used to explain the interface provided.

    Almost all input and output data in MeshPy can be accessed using the
    :class:`ForeignArray` interface.  It is called "foreign" because it
    provides access to an area of memory accessible by a pointer managed by an
    outside piece of software, such as a mesh generator.

    Note that :class:`ForeignArray` has no *append* method. Instead, use
    :meth:`ForeignArray.resize` and then set the consecutive entries of the
    array.

    .. method:: __len__()

        Return the number of entries in the array. If the array is 2D (i.e. has
        non-1 :attr:`unit`), :meth:`ForeignArray.__len__` only returns the
        length of the leading dimension.  For example, for an array of points
        in *n*-dimensional space, :meth:`__len__` returns the number of points.

    .. attribute:: unit

        If this :class:`ForeignArray` represents a two-dimensional array, such
        as an array of point coordinates, :meth:`ForeignArray.unit` gives the
        size of the subordinate dimension.

        For example, for an array of points in 3-dimensional space,
        :meth:`ForeignArray.__len__` returns the number of dimensions (3).

    .. attribute:: allocated

        Return a :class:`bool` indicating whether storage has
        been allocated for this array. This is only meaningful if the size
        of this array is tied to that of another, see :meth:`ForeignArray.setup`.

    .. method:: resize(new_size)

        Change the length of the array as returned by :meth:`ForeignArray.__len__`.

    .. method:: setup()

        Set up (i.e. allocate) storage for the array. This only works on arrays
        whose size is tied to that of other arrays, such as an array of point
        markers, which necessarily has the same size as the associated array of
        points, if it is allocated.

    .. method:: deallocate()

        Release any storage associated with the array.

    .. method:: __getitem__(index)
                __setitem__(index, value)

        Get and set entries in the array. If this foreign array is 2D
        (see :attr:`ForeignArray.unit`), index may be a 2-tuple of integers, as in::

            points[2,1] = 17

:mod:`meshpy.triangle` -- Triangular Meshing
--------------------------------------------
.. module:: meshpy.triangle
    :synopsis: Generate triangular meshes
.. moduleauthor:: Andreas Klöckner <inform@tiker.net>


.. class:: ForeignArray

    See :class:`meshpy.ForeignArray` for shared documentation.

.. class:: MeshInfo

    :class:`MeshInfo` objects are picklable.

    .. attribute:: points

        A 2D :class:`ForeignArray` of :class:`float` with dimension *(N,2)*,
        providing a list of points that are referred to by index from other
        entries of this structure.

    .. attribute:: point_attributes

        If :attr:`MeshInfo.number_of_point_attributes` is non-zero, this is a
        :class:`ForeignArray` of :class:`float`\ s of point attributes.

        This element's size is tied to that of :attr:`MeshInfo.points`.

    .. attribute:: point_markers

        :class:`ForeignArray` of :class:`float`\ s of point attributes.

        This element's size is tied to that of :attr:`MeshInfo.points`.

    .. attribute:: elements

    .. attribute:: element_attributes

        This element's size is tied to that of :attr:`MeshInfo.elements`.

    .. attribute:: element_volumes

        This element's size is tied to that of :attr:`MeshInfo.elements`.

    .. attribute:: neighbors

    .. attribute:: facets

    .. attribute:: facet_markers

    .. attribute:: holes

    .. attribute:: regions

    .. attribute:: faces
    .. attribute:: face_markers

    .. attribute:: normals

    .. attribute:: number_of_point_attributes
    .. attribute:: number_of_element_vertices

        Defautls to 4 for linear tetrahedra. Change to 10 for second-order
        tetrahedra.

    .. attribute:: number_of_element_attributes

    Convenient setters:

    .. method:: set_points(points, point_markers=None)
    .. method:: set_holes(points, hole_starts)
    .. method:: set_facets(facets, facet_markers=None)

    Other functionality:

    .. method:: copy()

        Return a duplicate copy of this object.

.. function:: subdivide_facets(subdivisions, points, facets, facet_markers)

    Subdivide facets into *subdivisions* subfacets.

    This routine is useful if you have to prohibit the insertion of Steiner
    points on the boundary  of your triangulation to allow the mesh to conform
    either to itself periodically or another given mesh. In this case, you may
    use this routine to create the necessary resolution along the boundary
    in a predefined way.

    *subdivisions* is either an :class:`int`, indicating a uniform number of
    subdivisions throughout, or a list of the same length as *facets*,
    specifying a subdivision count for each individual facet.

    *points*
        a list of points referred to from the facets list.
    *facets*
        a list of old facets, in the form *[(p1, p2), (p3,p4), ...]*.
    *facet_markers*
        either *None* or a list of facet markers of the same length
        as *facets*.

    Returns a tuple *(new_points, new_facets)*,
    or *(new_points, new_facets, new_facet_markers)* if *facet_markers* is not
    *None*.

.. function:: build(mesh_info, verbose=False, refinement_func=None, attributes=False, volume_constraints=True, max_volume=None, allow_boundary_steiner=True, allow_volume_steiner=True, quality_meshing=True, generate_edges=None, generate_faces=False, min_angle=None)

.. function:: refine(input_p, verbose=False, refinement_func=None,  quality_meshing=True, min_angle=None)

.. function:: write_gnuplot_mesh(filename, out_p, facets=False)

:mod:`meshpy.tet` -- Tetrahedral Meshing
----------------------------------------

.. module:: meshpy.tet
   :synopsis: Generate triangular meshes
.. moduleauthor:: Andreas Klöckner <inform@tiker.net>

.. class:: ForeignArray

    See :class:`meshpy.ForeignArray` for shared documentation.

.. class:: Options(switches='pq', **kwargs)

    Run time switches for TetGen. See the TetGen documentation for the meaning of each
    switch.

    Using the *kwargs* constructor argument, all the attributes defined
    below can be set. This setting will occur after
    :meth:`Options.parse_switches` is called with the *switches* parameter.

    .. attribute:: plc
    .. attribute:: quality
    .. attribute:: refine
    .. attribute:: coarse
    .. attribute:: metric
    .. attribute:: varvolume
    .. attribute:: fixedvolume
    .. attribute:: insertaddpoints
    .. attribute:: regionattrib
    .. attribute:: conformdel
    .. attribute:: diagnose
    .. attribute:: zeroindex
    .. attribute:: optlevel
    .. attribute:: optpasses
    .. attribute:: order
    .. attribute:: facesout
    .. attribute:: edgesout
    .. attribute:: neighout
    .. attribute:: voroout
    .. attribute:: meditview
    .. attribute:: gidview
    .. attribute:: geomview
    .. attribute:: nobound
    .. attribute:: nonodewritten
    .. attribute:: noelewritten
    .. attribute:: nofacewritten
    .. attribute:: noiterationnum
    .. attribute:: nomerge
    .. attribute:: nobisect
    .. attribute:: noflip
    .. attribute:: nojettison
    .. attribute:: steiner
    .. attribute:: fliprepair
    .. attribute:: docheck
    .. attribute:: quiet
    .. attribute:: verbose
    .. attribute:: useshelles
    .. attribute:: minratio
    .. attribute:: goodratio
    .. attribute:: minangle
    .. attribute:: goodangle
    .. attribute:: maxvolume
    .. attribute:: maxdihedral
    .. attribute:: alpha1
    .. attribute:: alpha2
    .. attribute:: alpha3
    .. attribute:: epsilon
    .. attribute:: epsilon2

    .. method:: parse_switches(switches)

.. class:: Polygon

    .. attribute:: vertices

.. class:: Facet

    .. attribute:: polygons
    .. attribute:: holes

.. class:: PBCGroup

    .. attribute:: facet_marker_1
    .. attribute:: facet_marker_2
    .. attribute:: point_pairs
    .. attribute:: matrix


.. class:: MeshInfo

    .. attribute:: points
    .. attribute:: point_attributes
    .. attribute:: point_metric_tensors
    .. attribute:: point_markers
    .. attribute:: elements
    .. attribute:: element_attributes
    .. attribute:: element_volumes
    .. attribute:: neighbors
    .. attribute:: facets
    .. attribute:: facet_markers
    .. attribute:: holes
    .. attribute:: regions
    .. attribute:: facet_constraints
    .. attribute:: segment_constraints
    .. attribute:: pbc_groups
    .. attribute:: faces
    .. attribute:: adjacent_elements
    .. attribute:: face_markers
    .. attribute:: edges
    .. attribute:: edge_markers
    .. attribute:: edge_adjacent_elements

        .. versionadded:: 2016.1
    .. attribute:: number_of_point_attributes
    .. attribute:: number_of_element_attributes

    Convenient setters:

    .. method:: set_points(points, point_markers=None)
    .. method:: set_holes(points, hole_starts)
    .. method:: set_facets(facets, markers=None)

        Set a list of simple, single-polygon factes. Unlike
        :meth:`MeshInfo.set_facets_ex`, this method does not allow holes and
        only lets you use a single polygon per facet.

        *facets*
            a list of facets, where each facet is a single
            polygons, represented by a list of point indices.
        *markers*
            Either None or a list of integers of the same
            length as facets. Each integer is the facet marker assigned
            to its corresponding facet.

        .. note::

            When the above says "list", any repeatable iterable
            also accepted instead.

    .. method:: set_facets_ex(facets, facet_holestarts=None, markers=None)

        Set a list of complicated facets. Unlike :meth:`MeshInfo.set_facets`,
        this method allows holes and multiple polygons per facet.

        *facets*
            a list of facets, where each facet is a list
            of polygons, and each polygon is represented by a list
            of point indices.
        *facet_holestarts*
            Either None or a list of hole starting points
            for each facet. Each facet may have several hole starting points.
            The mesh generator starts "eating" a hole into the facet at each
            starting point and continues until it hits a polygon specified
            in this facet's record in *facets*.
        *markers*
            Either None or a list of integers of the same
            length as *facets*. Each integer is the facet marker assigned
            to its corresponding facet.

        .. note::

            When the above says "list", any repeatable iterable
            also accepted instead.

    Other functionality:

    .. attribute:: face_vertex_indices_to_face_marker

    .. method:: dump()
    .. method:: write_vtk(filename)

    TetGen-provided loading and saving:

    .. method:: save_nodes(filename)
    .. method:: save_elements(filename)
    .. method:: save_faces(filename)
    .. method:: save_edges(filename)
    .. method:: save_neighbors(filename)
    .. method:: save_poly(filename)
    .. method:: load_node(filename)
    .. method:: load_pbc(filename)
    .. method:: load_var(filename)
    .. method:: load_mtr(filename)
    .. method:: load_poly(filename)
    .. method:: load_ply(filename)
    .. method:: load_stl(filename)
    .. method:: load_medit(filename)
    .. method:: load_plc(filename)
    .. method:: load_tetmesh(filename)

.. function:: build(mesh_info, options=Options("pq"), verbose=False, attributes=False, volume_constraints=False, max_volume=None, diagnose=False, insert_points=None, mesh_order=None)

    :param insert_points: a :class:`MeshInfo` object specifying additional points to be inserted


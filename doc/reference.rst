Reference Documentation
=======================

Some common notions
-------------------

.. class:: ForeignArray
    
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


.. class:: MeshInfo

    :class:`MeshInfo` objects are picklable.
    
    .. attribute:: points

        A 2D :class:`ForeignArray` of :class:`float` with dimension *(N,2)*,
        providing a list of points that are referred to by index from other
        entries of this structure.

    .. attribute:: point_attributes

        If :attr:`MeshInfo.number_of_point_attributes` is non-zero, this is a
        :class:`ForeignArray` of :class:`floats` of point attributes.

        This element's size is tied to that of :attr:`MeshInfo.points`.

    .. attribute:: point_markers

        :class:`ForeignArray` of :class:`floats` of point attributes.

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

.. function:: build(mesh_info, verbose=False, refinement_func=None, attributes=False, volume_constraints=True, max_volume=None, allow_boundary_steiner=True, generate_edges=None, generate_faces=False, min_angle=None)

.. function:: refine(input_p, verbose=False, refinement_func=None)

.. function:: write_gnuplot_mesh(filename, out_p, facets=False)

:mod:`meshpy.tet` -- Tetrahedral Meshing
----------------------------------------

.. module:: meshpy.tet
   :synopsis: Generate triangular meshes
.. moduleauthor:: Andreas Klöckner <inform@tiker.net>

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
    .. attribute:: offcenter
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
    .. attribute:: offcenter
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

.. function:: build(mesh_info, options=Options("pq"), verbose=False, attributes=False, volume_constraints=False, max_volume=None, diagnose=False, insert_points=None)

    :param insert_points: a :class:`MeshInfo` object specifying additional points to be inserted

.. data:: EXT_OPEN
.. data:: EXT_CLOSED_IN_RZ

.. function:: generate_extrusion(rz_points, base_shape, closure=EXT_OPEN, point_idx_offset=0, ring_point_indices=None, ring_markers=None, rz_closure_marker=0)

    Extrude a given connected *base_shape* (a list of (x,y) points)
    along the z axis. For each step in the extrusion, the base shape
    is multiplied by a radius and shifted in the z direction. Radius
    and z offset are given by *rz_points*, which is a list of
    (r, z) tuples.

    Returns *(points, facets, facet_holestarts, markers)*, where *points* is a list
    of (3D) points and facets is a list of polygons. Each polygon is, in turn,
    represented by a tuple of indices into *points*. If *point_idx_offset* is
    not zero, these indices start at that number. *markers* is a list equal in
    length to *facets*, each specifying the facet marker of that facet.
    *facet_holestarts* is also equal in length to *facets*, each element is a list of
    hole starting points for the corresponding facet.

    Use :meth:`MeshInfo.set_facets_ex` to add the extrusion to a :class:`MeshInfo`
    structure.

    The extrusion proceeds by generating quadrilaterals connecting each
    ring.  If any given radius in *rz_points* is 0, triangle fans are
    produced instead of quads to provide non-degenerate closure.

    If *closure* is :data:`EXT_OPEN`, no efforts are made to put end caps on the
    extrusion. 

    If *closure* is :data:`EXT_CLOSED_IN_RZ`, then a torus-like structure
    is assumed and the last ring is just connected to the first.

    If *ring_markers* is not None, it is an list of markers added to each
    ring. There should be len(rz_points)-1 entries in this list.
    If rings are added because of closure options, they receive the
    corresponding *XXX_closure_marker*.  If *facet_markers* is given, this function 
    returns (points, facets, markers), where markers is is a list containing 
    a marker for each generated facet. Unspecified markers generally
    default to 0.

    If *ring_point_indices* is given, it must be a list of the same 
    length as *rz_points*. Each entry in the list may either be None,
    or a list of point indices. This list must contain the same number
    of points as the *base_shape*; it is taken as the indices of 
    pre-existing points that are to be used for the given ring, instead
    of generating new points.

.. function:: generate_surface_of_revolution(rz_points, closure=EXT_OPEN, radial_subdiv=16, point_idx_offset=0, ring_point_indices=None, ring_markers=None, rz_closure_marker=0)

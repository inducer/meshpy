Welcome to MeshPy's documentation!
==================================

MeshPy offers quality triangular and tetrahedral mesh generation for Python.
Meshes of this type are chiefly used in finite-element simulation codes, but
also have many other applications ranging from computer graphics to robotics.

In order to generate these 2D and 3D meshes, MeshPy provides Python interfaces
to a few well-regarded mesh generators: 

* `Triangle <http://www.cs.cmu.edu/~quake/triangle.html>`_ by J. Shewchuk.
* `TetGen <http://tetgen.berlios.de/>`_ by Hang Si.
* `Gmsh <http://geuz.org/gmsh/>`_ by Christophe Geuzaine and Jean-François Remacle.

Triangle and TetGen are included in the package in slightly modified versions. Gmsh
is called as a subprocess.

Show me! I need examples!
-------------------------
This simple code generates a mesh of a "brick"::

    from meshpy.tet import MeshInfo, build

    mesh_info = MeshInfo()
    mesh_info.set_points([
        (0,0,0), (2,0,0), (2,2,0), (0,2,0),
        (0,0,12), (2,0,12), (2,2,12), (0,2,12),
        ])
    mesh_info.set_facets([
        [0,1,2,3],
        [4,5,6,7],
        [0,4,5,1],
        [1,5,6,2],
        [2,6,7,3],
        [3,7,4,0],
        ])
    mesh = build(mesh_info)
    print "Mesh Points:"
    for i, p in enumerate(mesh.points):
        print i, p
    print "Point numbers in tetrahedra:"
    for i, t in enumerate(mesh.elements):
        print i, t
    mesh.write_vtk("test.vtk")

As a result of this, you will get::

    Mesh Points:
    0 [0.0, 0.0, 0.0]
    1 [2.0, 0.0, 0.0]
    2 [2.0, 2.0, 0.0]
    3 [0.0, 2.0, 0.0]
    4 [0.0, 0.0, 12.0]
    5 [2.0, 0.0, 12.0]
    6 [2.0, 2.0, 12.0]
    7 [0.0, 2.0, 12.0]
    8 [1.000116, 0.0, 0.0]
    9 [0.0, 0.99960499999999997, 0.0]
    10 [0.0, 0.99934199999999995, 12.0]
    11 [1.0006170000000001, 0.0, 12.0]
    ...
    Point numbers in tetrahedra:
    0 [21, 39, 38, 52]
    1 [9, 50, 2, 3]
    2 [12, 45, 15, 54]
    3 [39, 43, 20, 52]
    4 [41, 45, 24, 54]
    ...

and a file :file:`test.vtk` that you can view with `Paraview <http://paraview.org>`_ or
`Visit <http://www.llnl.gov/VisIt/>`_.

Contents
========

.. toctree::
    :maxdepth: 2

    installation
    tri-tet
    gmsh
    geometry
    faq

MeshPy has its own `web page <http://mathema.tician.de/software/meshpy>`_, where you
can find updated software, news, a forum, and documentation.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


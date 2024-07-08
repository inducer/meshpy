Welcome to MeshPy's documentation!
==================================

.. toctree::
    :maxdepth: 2
    :hidden:

    installation
    tri-tet
    gmsh
    geometry
    faq
    🚀 Github <https://github.com/inducer/meshpy>
    💾 Download Releases <https://pypi.org/project/meshpy>

MeshPy offers quality triangular and tetrahedral mesh generation for Python.
Meshes of this type are chiefly used in finite-element simulation codes, but
also have many other applications ranging from computer graphics to robotics.

In order to generate these 2D and 3D meshes, MeshPy provides Python interfaces
to a few well-regarded mesh generators:

* `Triangle <https://www.cs.cmu.edu/~quake/triangle.html>`__ by J. Shewchuk.
* `TetGen <https://wias-berlin.de/software/tetgen>`__ by Hang Si.

Triangle and TetGen are included in the package in slightly modified versions.
An interface for `Gmsh <https://gmsh.info/>`__ was also part of MeshPy, but is
now its own package `gmsh_interop <https://github.com/inducer/gmsh_interop>`__.

MeshPy has its own `web page <https://mathema.tician.de/software/meshpy>`_,
where you can find updated software, news, a forum, and documentation.

Show me! I need examples!
-------------------------

This file is included in the :mod:`meshpy` distribution as
:download:`examples/demo.py <../examples/demo.py>`.

.. literalinclude:: ../examples/demo.py

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

and a file :file:`test.vtk` that you can view with
`Paraview <https://www.paraview.org>`__ or
`Visit <https://visit-dav.github.io/visit-website/>`__.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


MeshPy: Simplicial Mesh Generation from Python
==============================================

.. image:: https://gitlab.tiker.net/inducer/meshpy/badges/master/pipeline.svg
   :target: https://gitlab.tiker.net/inducer/meshpy/commits/master
.. image:: https://badge.fury.io/py/meshpy.png
    :target: http://pypi.python.org/pypi/meshpy

MeshPy offers quality triangular and tetrahedral mesh generation for Python.
Meshes of this type are chiefly used in finite-element simulation codes, but
also have many other applications ranging from computer graphics to robotics.

In order to generate 2D and 3D meshes, MeshPy provides Python interfaces to
three well-regarded mesh generators, `Triangle
<http://www.cs.cmu.edu/~quake/triangle.html>`_ by J.  Shewchuk, `TetGen
<http://tetgen.berlios.de/>`_ by Hang Si
The former two are included in the package in slightly modified versions. A
generic mesh reader for the latter is included, as is an easy way to run `gmsh`
from a Python script.

For an interface to `gmsh
<http://www.geuz.org/gmsh/>`_ by Christophe Geuzaine and Jean-Francois Remacle,
see `gmsh_interop <https://github.com/inducer/gmsh_interop>`.

MeshPy has no dependencies other than a C++ compiler and a working Python installation.

As of Version 0.91.2, MeshPy also works with Python 3.

Online resources
================

* `Home page <https://mathema.tician.de/software/meshpy>`_
* `Documentation <http://documen.tician.de/meshpy>`_
* `Source <https://github.com/inducer/meshpy>`_
* `Package index <https://pypi.python.org/pypi/MeshPy>`_
* `Mailing list <http://lists.tiker.net/listinfo/meshpy>`_

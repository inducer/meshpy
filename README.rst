MeshPy: Simplicial Mesh Generation from Python
==============================================

.. image:: https://gitlab.tiker.net/inducer/meshpy/badges/main/pipeline.svg
    :alt: Gitlab Build Status
    :target: https://gitlab.tiker.net/inducer/meshpy/commits/main
.. image:: https://github.com/inducer/meshpy/workflows/CI/badge.svg?branch=main
    :alt: Github Build Status
    :target: https://github.com/inducer/meshpy/actions?query=branch%3Amain+workflow%3ACI
.. image:: https://badge.fury.io/py/MeshPy.svg
    :alt: Python Package Index Release Page
    :target: https://pypi.org/project/meshpy/
.. image:: https://zenodo.org/badge/2757253.svg
    :alt: Zenodo DOI for latest release
    :target: https://zenodo.org/badge/latestdoi/2757253

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

For an interface to `gmsh <http://www.geuz.org/gmsh/>`_ by Christophe Geuzaine
and Jean-Francois Remacle, see `gmsh_interop <https://github.com/inducer/gmsh_interop>`__.

MeshPy has no dependencies other than a C++ compiler,
`pybind11 <https://pybind11.readthedocs.io/en/stable/>`_,
and a working Python installation. Before installing meshpy,
you may install pybind11 using the command::

   pip install pybind11

Online resources
================

* `Home page <https://mathema.tician.de/software/meshpy>`_
* `Documentation <http://documen.tician.de/meshpy>`_
* `Source <https://github.com/inducer/meshpy>`_
* `Package index <https://pypi.org/project/MeshPy>`_
* `Discussions <https://github.com/inducer/meshpy/discussions>`_


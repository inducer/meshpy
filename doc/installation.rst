.. highlight:: sh

Installation
============

This tutorial will walk you through the process of building MeshPy. To follow,
you really only need three basic things:

* A UNIX-like machine with web access.
* A working `Python <http://www.python.org>`__ installation.
* A recent C++ compiler. We use `pybind11 <https://pybind11.readthedocs.io>`__
  to create the wrappers, so see their documentation for minimal required versions
  if in doubt.
* `meson-python <https://meson-python.readthedocs.io>`__ and
  `ninja <https://ninja-build.org/>`__, which are used to build the wrapper.
  See the `[buildsystem]` section in `pyproject.toml` for an up to date list.

Step 1: Download and unpack MeshPy
-----------------------------------

`Download MeshPy <http://pypi.org/project/MeshPy>`_ and unpack it::

    $ tar xfz MeshPy-VERSION.tar.gz

If you're downloading from ``git`` instead::

    $ git clone https://github.com/inducer/meshpy.git

Step 2: Build MeshPy
--------------------

MeshPy uses `meson-python <https://meson-python.readthedocs.io>`__ as its build
system. For additional compilation options (e.g. compiling in debug mode),
see their official documentation.

First, just type::

    $ cd MeshPy-VERSION # if you're not there already

If you want to just build a source distribution or a wheel for MeshPy, you can
run::

    $ python -m build --sdist .
    $ python -m build --wheel .

or with the trusty ``pip``::

    $ python -m pip wheel --no-deps .

If you want to install MeshPy in editable mode for development, use::

    $ python -m pip install --no-build-isolation --editable .

(the ``--no-build-isolation`` flag is very important!). At this point, you can
also pass additional configuration options to ``meson``. For example, to build
in debug mode, run::

    $ python -m pip install \
        --no-build-isolation -Csetup-args=-Dbuildtype=debug \
        --editable .

Once that works, congratulations! You've successfully built MeshPy.

Step 3: Test MeshPy
-------------------

Just type::

    $ python -m pytest -v -s test

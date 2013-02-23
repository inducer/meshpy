.. highlight:: sh

Installation
============

This tutorial will walk you through the process of building MeshPy. To follow,
you really only need three basic things:

* A UNIX-like machine with web access.
* A C++ compiler, preferably a Version 4.x gcc.
* A working `Python <http://www.python.org>`_ installation, Version 2.4 or newer.

Step 1: Download and unpack MeshPy
-----------------------------------

`Download MeshPy <http://pypi.python.org/pypi/MeshPy>`_ and unpack it::

    $ tar xfz MeshPy-VERSION.tar.gz

If you're downloading from git, say::

    $ git clone --recursive http://git.tiker.net/trees/meshpy.git

If your version of git doesn't support `--recursive`, then say::

    $ git clone http://git.tiker.net/trees/meshpy.git
    $ cd meshpy
    $ git submodule init
    $ git submodule update

The setup script will remind you about this if you forget.

Step 2: Build MeshPy
--------------------

Just type::

    $ cd MeshPy-VERSION # if you're not there already
    $ ./configure
    $ python setup.py install

Once that works, congratulations! You've successfully built MeshPy.

Step 3: Test MeshPy
-------------------

Just type::

    $ cd test
    $ py.test

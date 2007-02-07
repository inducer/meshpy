#!/usr/bin/env python

import os
from distutils.core import setup,Extension

home = os.getenv("HOME")
boost_path = "%s/work/boost" % home
include_dirs = [boost_path, "src"]
library_dirs = ["%s/pool/lib" % home]
libraries = ["boost_python"]

triangle_macros = [
  ( "EXTERNAL_TEST", 1 ),
  ( "ANSI_DECLARATORS", 1 ),
  ( "TRILIBRARY", 1 ) ,
  ]

tetgen_macros = [
  ("TETLIBRARY", 1),
  ]

setup(name="MeshPy",
      version="0.90",
      description="A wrapper around the TetGen and Triangle",
      author="Andreas Kloeckner",
      author_email="inform@tiker.net",
      license = "BSD for the wrapper/non-commercial MIT for the meshers",
      url="http://news.tiker.net/software/meshpy",
      packages = [ "meshpy" ],
      ext_modules = [
        Extension(
          "meshpy._triangle", 
          ["src/wrap_triangle.cpp","src/triangle.c"],
          include_dirs = include_dirs,
          library_dirs = library_dirs,
          libraries = libraries,
          define_macros=triangle_macros
          ),
        Extension(
          "meshpy._tetgen", 
          ["src/tetgen.cpp", "src/predicates.cpp", "src/wrap_tetgen.cpp"],
          include_dirs = include_dirs,
          library_dirs = library_dirs,
          libraries = libraries,
          define_macros=tetgen_macros
          ),
        ]
     )

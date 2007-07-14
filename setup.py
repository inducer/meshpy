#!/usr/bin/env python

import sys

try:
    execfile("siteconf.py")
except IOError:
    print "*** Please run configure first."
    sys.exit(1)

from distutils.core import setup,Extension

def non_matching_config():
    print "*** The version of your configuration template does not match"
    print "*** the version of the setup script. Please re-run configure."
    sys.exit(1)

try:
    MESHPY_CONF_TEMPLATE_VERSION
except NameError:
    non_matching_config()

if MESHPY_CONF_TEMPLATE_VERSION != 1:
    non_matching_config()

triangle_macros = [
  ( "EXTERNAL_TEST", 1 ),
  ( "ANSI_DECLARATORS", 1 ),
  ( "TRILIBRARY", 1 ) ,
  ]

tetgen_macros = [
  ("TETLIBRARY", 1),
  ( "SELF_CHECK", 1 ) ,
  ]

INCLUDE_DIRS = BOOST_INCLUDE_DIRS
LIBRARY_DIRS = BOOST_LIBRARY_DIRS
LIBRARIES = BPL_LIBRARIES

execfile("meshpy/__init__.py")
setup(name="MeshPy",
      version=version,
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
          include_dirs=INCLUDE_DIRS,
          library_dirs=LIBRARY_DIRS,
          libraries=LIBRARIES,
          define_macros=triangle_macros
          ),
        Extension(
          "meshpy._tetgen", 
          ["src/tetgen.cpp", "src/predicates.cpp", "src/wrap_tetgen.cpp"],
          include_dirs=INCLUDE_DIRS,
          library_dirs=LIBRARY_DIRS,
          libraries=LIBRARIES,
          define_macros=tetgen_macros
          ),
        ]
     )

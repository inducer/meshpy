#!/usr/bin/env python

def get_config_schema():
    from aksetup_helper import ConfigSchema, Option, \
            IncludeDir, LibraryDir, Libraries, \
            Switch, StringListOption

    return ConfigSchema([
        IncludeDir("BOOST", []),
        LibraryDir("BOOST", []),
        Libraries("BOOST_PYTHON", ["boost_python-gcc42-mt"]),

        StringListOption("CXXFLAGS", [], 
            help="Any extra C++ compiler options to include"),
        StringListOption("LDFLAGS", [], 
            help="Any extra linker options to include"),
        ])




def main():
    import glob
    from aksetup_helper import hack_distutils, \
            get_config, setup, Extension

    hack_distutils()
    conf = get_config(get_config_schema())

    triangle_macros = [
      ( "EXTERNAL_TEST", 1 ),
      ( "ANSI_DECLARATORS", 1 ),
      ( "TRILIBRARY", 1 ) ,
      ]

    tetgen_macros = [
      ("TETLIBRARY", 1),
      ("SELF_CHECK", 1) ,
      ]

    INCLUDE_DIRS = conf["BOOST_INC_DIR"] + ["src/cpp"]
    LIBRARY_DIRS = conf["BOOST_LIB_DIR"]
    LIBRARIES = conf["BOOST_PYTHON_LIBNAME"]

    execfile("src/python/__init__.py", conf)
    setup(name="MeshPy",
          version=conf["version"],
          description="Triangular and Tetrahedral Mesh Generator",
          long_description="""
          MeshPy offers quality triangular and tetrahedral mesh
          generation for Python. Meshes of this type are chiefly used
          in finite-element simulation codes, but also have many
          other applications ranging from computer graphics to
          robotics.

          In order to generate 2D and 3D meshes, MeshPy provides
          Python interfaces to two well-regarded mesh generators,
          `Triangle <http://www.cs.cmu.edu/~quake/triangle.html>`_ by
          J.  Shewchuk and `TetGen <http://tetgen.berlios.de/>`_ by
          Hang Si. Both are included in the package in slightly
          modified versions.

          MeshPy uses `Boost.Python <http://www.boost.org>`_. 

          Documentation
          =============

          See the `MeshPy Documentation <http://tiker.net/doc/meshpy>`_ page.
          """,
          author="Andreas Kloeckner",
          author_email="inform@tiker.net",
          license = "MIT for the wrapper/non-commercial MIT for the meshers",
          url="http://mathema.tician.de/software/meshpy",
          classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Intended Audience :: Other Audience',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: MIT License',
            'License :: Free for non-commercial use',
            'Natural Language :: English',
            'Programming Language :: C++',
            'Programming Language :: Python',
            'Topic :: Multimedia :: Graphics :: 3D Modeling',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Mathematics',
            'Topic :: Scientific/Engineering :: Physics',
            'Topic :: Scientific/Engineering :: Visualization',
            'Topic :: Software Development :: Libraries',
            ],

          packages = [ "meshpy" ],
          package_dir={"meshpy": "src/python"},
          ext_modules = [
            Extension(
              "meshpy._triangle", 
              ["src/cpp/wrap_triangle.cpp","src/cpp/triangle.c"],
              include_dirs=INCLUDE_DIRS,
              library_dirs=LIBRARY_DIRS,
              libraries=LIBRARIES,
              define_macros=triangle_macros,
              extra_compile_args=conf["CXXFLAGS"],
              extra_link_args=conf["LDFLAGS"],
              ),
            Extension(
              "meshpy._tetgen", 
              ["src/cpp/tetgen.cpp", "src/cpp/predicates.cpp", "src/cpp/wrap_tetgen.cpp"],
              include_dirs=INCLUDE_DIRS,
              library_dirs=LIBRARY_DIRS,
              libraries=LIBRARIES,
              define_macros=tetgen_macros,
              extra_compile_args=conf["CXXFLAGS"],
              extra_link_args=conf["LDFLAGS"],
              ),
            ]
         )




if __name__ == '__main__':
    main()

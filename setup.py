#!/usr/bin/env python

def get_config_schema():
    from aksetup_helper import (ConfigSchema,
            BoostLibraries, Switch, StringListOption, make_boost_base_options)

    return ConfigSchema(make_boost_base_options() + [
        BoostLibraries("python"),

        Switch("USE_SHIPPED_BOOST", True, "Use included Boost library"),

        StringListOption("CXXFLAGS", [], 
            help="Any extra C++ compiler options to include"),
        StringListOption("LDFLAGS", [], 
            help="Any extra linker options to include"),
        ])




def main():
    from aksetup_helper import (hack_distutils,
            get_config, setup, Extension, set_up_shipped_boost_if_requested,
            check_git_submodules)

    check_git_submodules()

    hack_distutils()
    conf = get_config(get_config_schema())

    TRI_EXTRA_OBJECTS, TRI_EXTRA_DEFINES = set_up_shipped_boost_if_requested("meshpy_tri_", conf)
    TET_EXTRA_OBJECTS, TET_EXTRA_DEFINES = set_up_shipped_boost_if_requested("meshpy_tet_", conf)

    triangle_macros = [
      ( "EXTERNAL_TEST", 1 ),
      ( "ANSI_DECLARATORS", 1 ),
      ( "TRILIBRARY", 1 ) ,
      ] + list(TRI_EXTRA_DEFINES.iteritems())

    tetgen_macros = [
      ("TETLIBRARY", 1),
      ("SELF_CHECK", 1) ,
      ] + list(TET_EXTRA_DEFINES.iteritems())

    INCLUDE_DIRS = conf["BOOST_INC_DIR"] + ["src/cpp"]
    LIBRARY_DIRS = conf["BOOST_LIB_DIR"]
    LIBRARIES = conf["BOOST_PYTHON_LIBNAME"]

    init_filename = "meshpy/__init__.py"
    exec(compile(open(init_filename, "r").read(), init_filename, "exec"), conf)

    try:
        from distutils.command.build_py import build_py_2to3 as build_py
    except ImportError:
        # 2.x
        from distutils.command.build_py import build_py

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

          As of Version 0.91.2, MeshPy also works with Python 3.

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
            'Programming Language :: Python :: 3',
            'Topic :: Multimedia :: Graphics :: 3D Modeling',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Mathematics',
            'Topic :: Scientific/Engineering :: Physics',
            'Topic :: Scientific/Engineering :: Visualization',
            'Topic :: Software Development :: Libraries',
            ],

          packages = [ "meshpy" ],
          ext_modules = [
            Extension(
              "meshpy._triangle", 
              ["src/cpp/wrap_triangle.cpp","src/cpp/triangle.c"]
              + TRI_EXTRA_OBJECTS,
              include_dirs=INCLUDE_DIRS,
              library_dirs=LIBRARY_DIRS,
              libraries=LIBRARIES,
              define_macros=triangle_macros,
              extra_compile_args=conf["CXXFLAGS"],
              extra_link_args=conf["LDFLAGS"],
              ),
            Extension(
              "meshpy._tetgen", 
              ["src/cpp/tetgen.cpp", "src/cpp/predicates.cpp", "src/cpp/wrap_tetgen.cpp"]
              + TET_EXTRA_OBJECTS,
              include_dirs=INCLUDE_DIRS,
              library_dirs=LIBRARY_DIRS,
              libraries=LIBRARIES,
              define_macros=tetgen_macros,
              extra_compile_args=conf["CXXFLAGS"],
              extra_link_args=conf["LDFLAGS"],
              ),
            ],

          # 2to3 invocation
          cmdclass={'build_py': build_py},
          )




if __name__ == '__main__':
    main()

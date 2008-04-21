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
        ])




def main():
    import glob
    from aksetup_helper import hack_distutils, \
            get_config, setup, Extension

    hack_distutils()
    conf = get_config()

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
          description="A wrapper around the TetGen and Triangle",
          author="Andreas Kloeckner",
          author_email="inform@tiker.net",
          license = "BSD for the wrapper/non-commercial MIT for the meshers",
          url="http://news.tiker.net/software/meshpy",
          packages = [ "meshpy" ],
          package_dir={"meshpy": "src/python"},
          ext_modules = [
            Extension(
              "meshpy._triangle", 
              ["src/cpp/wrap_triangle.cpp","src/cpp/triangle.c"],
              include_dirs=INCLUDE_DIRS,
              library_dirs=LIBRARY_DIRS,
              libraries=LIBRARIES,
              define_macros=triangle_macros
              ),
            Extension(
              "meshpy._tetgen", 
              ["src/cpp/tetgen.cpp", "src/cpp/predicates.cpp", "src/cpp/wrap_tetgen.cpp"],
              include_dirs=INCLUDE_DIRS,
              library_dirs=LIBRARY_DIRS,
              libraries=LIBRARIES,
              define_macros=tetgen_macros
              ),
            ]
         )




if __name__ == '__main__':
    main()

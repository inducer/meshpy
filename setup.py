#!/usr/bin/env python
import sys, os

def get_config_schema():
    from aksetup_helper import (ConfigSchema,
            BoostLibraries, Switch, StringListOption, make_boost_base_options)

    return ConfigSchema(make_boost_base_options() + [
        BoostLibraries("python"),

        Switch("USE_SHIPPED_BOOST", False, "Use included Boost library"),

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

    hack_distutils(what_opt=1)
    conf = get_config(get_config_schema())

    TRI_EXTRA_OBJECTS, TRI_EXTRA_DEFINES = \
            set_up_shipped_boost_if_requested("meshpy", conf)
    TET_EXTRA_OBJECTS, TET_EXTRA_DEFINES = TRI_EXTRA_OBJECTS, TRI_EXTRA_DEFINES

    triangle_macros = [
            ("EXTERNAL_TEST", 1),
            ("ANSI_DECLARATORS", 1),
            ("TRILIBRARY", 1),
            ] + list(TRI_EXTRA_DEFINES.items())

    tetgen_macros = [
            ("TETLIBRARY", 1),
            ("SELF_CHECK", 1),
            ] + list(TET_EXTRA_DEFINES.items())

    INCLUDE_DIRS = conf["BOOST_INC_DIR"] + ["src/cpp"]
    LIBRARY_DIRS = conf["BOOST_LIB_DIR"]
    LIBRARIES = conf["BOOST_PYTHON_LIBNAME"]

    ######## simple use CMAKE to find get the directories:

    boost_variables = ["VERSION", "INCLUDE_DIRS", "LIB_DIRS", "LIBRARIES"]
    boost_dict = {}
    if sys.version_info.major < 3:
      output = os.popen("cmake . -Dpy_version=2")
    else:
      output = os.popen("cmake .")

    for line in output:
      for var in boost_variables:
        if var in line:
          line = line.replace('-- ' + var, '').replace(': ', '').replace('\n', '')
          boost_dict[var] = line
    if not "VERSION" in boost_dict:
      print("CMake didn't find any boost library")
      print("default installation will be used instead.")
    else:
      print("use cmake to detect bost")
      lib_name = os.path.basename(boost_dict["LIBRARIES"])
      lib_name = lib_name.replace("lib", "").replace(".so", "").replace(".lib", "")
      INCLUDE_DIRS = [boost_dict["INCLUDE_DIRS"]] + ["src/cpp"]
      LIBRARY_DIRS = [boost_dict["LIB_DIRS"]]
      LIBRARIES = [lib_name]
    ########## end of CMAKE configuration

    print("using the following configuration:")
    print("INCLUDE_DIRS: ", INCLUDE_DIRS)
    print("LIBRARY_DIRS: ", LIBRARY_DIRS)
    print("LIBRARIES: ", LIBRARIES)

    init_filename = "meshpy/__init__.py"
    exec(compile(open(init_filename, "r").read(), init_filename, "exec"), conf)

    import codecs
    setup(name="MeshPy",
          version=conf["version"],
          description="Triangular and Tetrahedral Mesh Generator",
          long_description=codecs.open("README.rst", "r", "utf-8").read(),
          author="Andreas Kloeckner",
          author_email="inform@tiker.net",
          license="MIT for the wrapper/non-commercial for the Triangle/GNU Affero Public License for TetGen",
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
              'Programming Language :: Python :: 2.6',
              'Programming Language :: Python :: 2.7',
              'Programming Language :: Python :: 3',
              'Programming Language :: Python :: 3.2',
              'Programming Language :: Python :: 3.3',
              'Programming Language :: Python :: 3.4',
              'Topic :: Multimedia :: Graphics :: 3D Modeling',
              'Topic :: Scientific/Engineering',
              'Topic :: Scientific/Engineering :: Mathematics',
              'Topic :: Scientific/Engineering :: Physics',
              'Topic :: Scientific/Engineering :: Visualization',
              'Topic :: Software Development :: Libraries',
              ],

          packages=["meshpy"],
          install_requires=[
                  "pytools>=2011.2",
                  "pytest>=2",
                  "numpy",
                  "six",
                  ],
          ext_modules=[
              Extension(
                  "meshpy._triangle",
                  ["src/cpp/wrap_triangle.cpp", "src/cpp/triangle.c"]
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
                  [
                      "src/cpp/tetgen.cpp",
                      "src/cpp/predicates.cpp",
                      "src/cpp/wrap_tetgen.cpp"]
                  + TET_EXTRA_OBJECTS,
                  include_dirs=INCLUDE_DIRS,
                  library_dirs=LIBRARY_DIRS,
                  libraries=LIBRARIES,
                  define_macros=tetgen_macros,
                  extra_compile_args=conf["CXXFLAGS"],
                  extra_link_args=conf["LDFLAGS"],
                  ),
              ])


if __name__ == '__main__':
    main()

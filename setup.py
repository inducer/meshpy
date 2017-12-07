#!/usr/bin/env python
import sys
import os


# {{{ use cmake to find boost

def get_boost_defaults_from_cmake():
    boost_variables = ["VERSION", "INCLUDE_DIRS", "LIB_DIRS", "LIBRARIES"]
    boost_dict = {}

    cmake_cmd = ["cmake", "."]
    if sys.version_info < (3,):
        cmake_cmd.append("-Dpy_version=2")
    else:
        cmake_cmd.append("-Dpy_version=3")

    from subprocess import Popen, PIPE

    boost_conf = {}

    try:
        cmake = Popen(cmake_cmd, stdout=PIPE)
    except OSError:
        return boost_conf

    cmake_out, stderr_out = cmake.communicate()

    if cmake.returncode == 0:
        for line in cmake_out.decode("utf-8").split("\n"):
            for var in boost_variables:
                if var in line:
                    line = (line
                            .replace('-- ' + var, '')
                            .replace(': ', '')
                            .replace('\n', ''))
                    boost_dict[var] = line

    else:
        print("*** error return from cmake")

    if "VERSION" in boost_dict:
        print("used cmake to detect boost")
        bpl_lib_name = os.path.basename(boost_dict["LIBRARIES"])
        bpl_lib_name = (bpl_lib_name
                .replace(".lib", "")
                .replace("lib", "")
                .replace(".so", ""))

        boost_conf["BOOST_INC_DIR"] = [boost_dict["INCLUDE_DIRS"]]
        boost_conf["BOOST_LIB_DIR"] = [boost_dict["LIB_DIRS"]]
        boost_conf["BOOST_PYTHON_LIBNAME"] = bpl_lib_name

    return boost_conf

# }}}


def get_config_schema():
    from aksetup_helper import (ConfigSchema,
            BoostLibraries, Switch, StringListOption, IncludeDir, LibraryDir)

    cmake_boost_conf = get_boost_defaults_from_cmake()

    return ConfigSchema([
        IncludeDir("BOOST", cmake_boost_conf.get("BOOST_INC_DIR", [])),
        LibraryDir("BOOST", cmake_boost_conf.get("BOOST_LIB_DIR", [])),
        BoostLibraries("python",
            default_lib_name=cmake_boost_conf.get("BOOST_PYTHON_LIBNAME")),

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

    # }}}

    include_dirs = conf["BOOST_INC_DIR"] + ["src/cpp"]
    library_dirs = conf["BOOST_LIB_DIR"]
    libraries = conf["BOOST_PYTHON_LIBNAME"]

    init_filename = "meshpy/__init__.py"
    exec(compile(open(init_filename, "r").read(), init_filename, "exec"), conf)

    import codecs
    setup(name="MeshPy",
          version=conf["version"],
          description="Triangular and Tetrahedral Mesh Generator",
          long_description=codecs.open("README.rst", "r", "utf-8").read(),
          author="Andreas Kloeckner",
          author_email="inform@tiker.net",
          license=("MIT for the wrapper/non-commercial for "
              "the Triangle/GNU Affero Public License for TetGen"),
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
                  "gmsh_interop",
                  "six",
                  ],
          ext_modules=[
              Extension(
                  "meshpy._triangle",
                  ["src/cpp/wrap_triangle.cpp", "src/cpp/triangle.c"]
                  + TRI_EXTRA_OBJECTS,
                  include_dirs=include_dirs,
                  library_dirs=library_dirs,
                  libraries=libraries,
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
                  include_dirs=include_dirs,
                  library_dirs=library_dirs,
                  libraries=libraries,
                  define_macros=tetgen_macros,
                  extra_compile_args=conf["CXXFLAGS"],
                  extra_link_args=conf["LDFLAGS"],
                  ),
              ])


if __name__ == '__main__':
    main()

# vim: foldmethod=marker

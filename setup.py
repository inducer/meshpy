#!/usr/bin/env python


def get_config_schema():
    from aksetup_helper import (ConfigSchema, StringListOption)

    return ConfigSchema([
        StringListOption("CXXFLAGS", [],
            help="Any extra C++ compiler options to include"),
        StringListOption("LDFLAGS", [],
            help="Any extra linker options to include"),
        ])


def main():
    from aksetup_helper import (hack_distutils,
            check_pybind11, get_config, setup, check_git_submodules,
            Extension,
            get_pybind_include, PybindBuildExtCommand)

    check_pybind11()
    check_git_submodules()

    hack_distutils(what_opt=1)
    conf = get_config(
            get_config_schema(),
            warn_about_no_config=False)

    triangle_macros = [
            ("EXTERNAL_TEST", 1),
            ("ANSI_DECLARATORS", 1),
            ("TRILIBRARY", 1),
            ]

    tetgen_macros = [
            ("TETLIBRARY", 1),
            ("SELF_CHECK", 1),
            ]

    # }}}

    include_dirs = [
            get_pybind_include(),
            get_pybind_include(user=True)
            ] + ["src/cpp"]

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
          url="https://documen.tician.de/meshpy",
          classifiers=[
              "Development Status :: 4 - Beta",
              "Intended Audience :: Developers",
              "Intended Audience :: Other Audience",
              "Intended Audience :: Science/Research",
              "License :: OSI Approved :: MIT License",
              "License :: Free for non-commercial use",
              "Natural Language :: English",
              "Programming Language :: C++",
              "Programming Language :: Python",
              "Programming Language :: Python :: 3",
              "Topic :: Multimedia :: Graphics :: 3D Modeling",
              "Topic :: Scientific/Engineering",
              "Topic :: Scientific/Engineering :: Mathematics",
              "Topic :: Scientific/Engineering :: Physics",
              "Topic :: Scientific/Engineering :: Visualization",
              "Topic :: Software Development :: Libraries",
              ],

          packages=["meshpy"],
          setup_requires=["pybind11"],
          python_requires="~=3.6",
          install_requires=[
                  "pytools>=2011.2",
                  "pytest>=2",
                  "numpy",
                  "gmsh_interop",
                  ],
          ext_modules=[
              Extension(
                  "meshpy._internals",
                  [
                      "src/cpp/wrapper.cpp",

                      "src/cpp/wrap_triangle.cpp",
                      "src/cpp/triangle.cpp",

                      "src/cpp/wrap_tetgen.cpp",
                      "src/cpp/tetgen.cpp",
                      "src/cpp/predicates.cpp",
                      ],
                  include_dirs=include_dirs,
                  define_macros=triangle_macros + tetgen_macros,
                  extra_compile_args=conf["CXXFLAGS"],
                  extra_link_args=conf["LDFLAGS"],
                  ),
              ],
          cmdclass={"build_ext": PybindBuildExtCommand},
          zip_safe=False,
          )


if __name__ == "__main__":
    main()

# vim: foldmethod=marker

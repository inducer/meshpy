#!/usr/bin/env python

import sys
import setuptools
from setuptools import Extension
from setuptools.command.build_ext import build_ext


def get_config_schema():
    from aksetup_helper import (ConfigSchema, StringListOption)

    return ConfigSchema([
        StringListOption("CXXFLAGS", [],
            help="Any extra C++ compiler options to include"),
        StringListOption("LDFLAGS", [],
            help="Any extra linker options to include"),
        ])


# {{{ pybind11 gunk

class get_pybind_include(object):  # noqa
    """Helper class to determine the pybind11 include path

    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked. """

    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)


ext_modules = [
    Extension(
        'python_example',
        ['src/main.cpp'],
        include_dirs=[
            # Path to pybind11 headers
            get_pybind_include(),
            get_pybind_include(user=True)
        ],
        language='c++'
    ),
]


# As of Python 3.6, CCompiler has a `has_flag` method.
# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        try:
            compiler.compile([f.name], extra_postargs=[flagname])
        except setuptools.distutils.errors.CompileError:
            return False
    return True


def cpp_flag(compiler):
    """Return the -std=c++[11/14] compiler flag.

    The c++14 is prefered over c++11 (when it is available).
    """
    if has_flag(compiler, '-std=c++14'):
        return '-std=c++14'
    elif has_flag(compiler, '-std=c++11'):
        return '-std=c++11'
    else:
        raise RuntimeError('Unsupported compiler -- at least C++11 support '
                           'is needed!')


class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""
    c_opts = {
        'msvc': ['/EHsc'],
        'unix': [],
    }

    if sys.platform == 'darwin':
        c_opts['unix'] += ['-stdlib=libc++', '-mmacosx-version-min=10.7']

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        if ct == 'unix':
            opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, '-fvisibility=hidden'):
                opts.append('-fvisibility=hidden')
        elif ct == 'msvc':
            opts.append('/DVERSION_INFO=\\"%s\\"' % self.distribution.get_version())
        for ext in self.extensions:
            ext.extra_compile_args = opts
        build_ext.build_extensions(self)

# }}}


def main():
    from aksetup_helper import (hack_distutils,
            get_config, setup, check_git_submodules)

    check_git_submodules()

    hack_distutils(what_opt=1)
    conf = get_config(get_config_schema())

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
          setup_requires=["pybind11"],
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
                  ["src/cpp/wrap_triangle.cpp", "src/cpp/triangle.c"],
                  include_dirs=include_dirs,
                  define_macros=triangle_macros,
                  extra_compile_args=conf["CXXFLAGS"],
                  extra_link_args=conf["LDFLAGS"],
                  ),
              Extension(
                  "meshpy._tetgen",
                  [
                      "src/cpp/tetgen.cpp",
                      "src/cpp/predicates.cpp",
                      "src/cpp/wrap_tetgen.cpp"],
                  include_dirs=include_dirs,
                  define_macros=tetgen_macros,
                  extra_compile_args=conf["CXXFLAGS"],
                  extra_link_args=conf["LDFLAGS"],
                  ),
              ],
          cmdclass={'build_ext': BuildExt},
          zip_safe=False,
          )


if __name__ == '__main__':
    main()

# vim: foldmethod=marker

project('meshpy', 'cpp',
  license: 'MIT',
  meson_version: '>=1.0.0',
  default_options : ['warning_level=2', 'cpp_std=c++14'],
)

# {{{ gather includes

py_mod = import('python')
py = py_mod.find_installation(pure: false)
pybind11_dep = dependency('pybind11')

# }}}

# {{{ extension

wrapper_src = [
  'src/cpp/foreign_array.hpp',
  'src/cpp/foreign_array_wrap.hpp',
  'src/cpp/wrapper.cpp',

  'src/cpp/wrap_triangle.cpp',
  'src/cpp/triangle.h',
  'src/cpp/triangle.cpp',

  'src/cpp/wrap_tetgen.cpp',
  'src/cpp/tetgen.h',
  'src/cpp/tetgen.cpp',
  'src/cpp/predicates.cpp',
]

wrapper_defines = [
  '-DEXTERNAL_TEST',
  '-DANSI_DECLARATORS',
  '-DTRILIBRARY',

  '-DTETLIBRARY',
  '-DSELF_CHECK'
]

py.extension_module(
  '_internals',
  wrapper_src,
  dependencies : [pybind11_dep],
  c_args: wrapper_defines,
  cpp_args: wrapper_defines,
  subdir: 'meshpy',
  install: true,
)

py.install_sources([
    'meshpy/common.py',
    'meshpy/geometry.py',
    'meshpy/gmsh.py',
    'meshpy/gmsh_reader.py',
    'meshpy/__init__.py',
    'meshpy/naca.py',
    'meshpy/ply.py',
    'meshpy/tet.py',
    'meshpy/tools.py',
    'meshpy/triangle.py',
  ],
  subdir: 'meshpy'
)

# }}}

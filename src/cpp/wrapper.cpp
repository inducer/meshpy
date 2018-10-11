#include <pybind11/pybind11.h>
#include "foreign_array_wrap.hpp"

void expose_triangle(pybind11::module &m);
void expose_tetgen(pybind11::module &m);

PYBIND11_MODULE(_internals, m)
{
  exposePODForeignArray<double>(m, "RealArray");
  exposePODForeignArray<int>(m, "IntArray");

  expose_triangle(m);
  expose_tetgen(m);
}

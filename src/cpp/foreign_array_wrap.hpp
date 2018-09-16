#ifndef _HEADER_SEEN_FOREIGN_ARRAY_WRAP
#define _HEADER_SEEN_FOREIGN_ARRAY_WRAP




#include "foreign_array.hpp"
#include <pybind11/pybind11.h>




#define PYTHON_ERROR(TYPE, REASON) \
{ \
  PyErr_SetString(PyExc_##TYPE, REASON); \
  throw pybind11::error_already_set(); \
}


namespace {
  /* This wrap helper works as long as the value_type is a plain old data (POD)
   * type.
   *
   * In exchange for this, it nicely wraps the "unit" abstraction provided by
   * foreign arrays.
   */
  template <typename FA>
  struct tPODForeignArrayWrapHelper
  {
    typedef typename FA::value_type value_type;

    static pybind11::object getitem(FA &self, long idx)
    {
      if (idx < 0) idx += self.size();
      if (idx < 0 || idx >= (long) self.size())
        PYTHON_ERROR(IndexError, "index out of bounds");

      if (self.unit() > 1)
      {
        pybind11::list l;
        for (unsigned i = 0; i<self.unit();i++)
          l.append(self.getSub(idx, i));
        return l;
      }
      else
        return pybind11::cast(self.get(idx));
    }

    static pybind11::object getitem_tup(FA &self, pybind11::tuple idx)
    {
      if (len(idx) != 2)
        PYTHON_ERROR(IndexError, "expected index tuple of length 2");
      long i_main = pybind11::cast<int>(idx[0]);
      long i_sub = pybind11::cast<int>(idx[1]);

      if (i_main < 0 || i_main >= (long) self.size())
        PYTHON_ERROR(IndexError, "index out of bounds");
      if (i_sub < 0 || i_sub >= (long) self.unit())
        PYTHON_ERROR(IndexError, "subindex out of bounds");

      return pybind11::cast(self.getSub(i_main, i_sub));
    }

    static void setitem(FA &self, long idx, pybind11::object value)
    {
      if (idx < 0) idx += self.size();
      if (idx < 0 || idx >= (long) self.size())
        PYTHON_ERROR(IndexError, "index out of bounds");

      if (self.unit() > 1)
      {
        pybind11::sequence value_seq = pybind11::cast<pybind11::sequence>(value);

        if ((long) self.unit() != len(value))
          PYTHON_ERROR(ValueError, "value must be a sequence of length self.unit");

        for (size_t i = 0; i<len(value);i++)
          self.setSub(idx, i, pybind11::cast<value_type>(value_seq[i]));
      }
      else
        self.set(idx, pybind11::cast<value_type>(value));
    }

    static void setitem_tup(FA &self, pybind11::tuple idx, const value_type &v)
    {
      if (len(idx) != 2)
        PYTHON_ERROR(IndexError, "expected index tuple of length 2");
      long i_main = pybind11::cast<int>(idx[0]);
      long i_sub = pybind11::cast<int>(idx[1]);

      if (i_main < 0 || i_main >= (long) self.size())
        PYTHON_ERROR(IndexError, "index out of bounds");
      if (i_main < 0 || i_sub >= (long) self.unit())
        PYTHON_ERROR(IndexError, "subindex out of bounds");

      self.setSub(i_main, i_sub, v);
    }
  };




  /* This wrap helper works for more complicated data structures, for which we
   * just ship out internal references--boost::python takes care of life support
   * for us.
   *
   * In exchange for this, it does not allow setting entries or support the unit API.
   */
  template <typename FA>
  struct tStructureForeignArrayWrapHelper
  {
    typedef typename FA::value_type value_type;

    static value_type &getitem(FA &self, long idx)
    {
      if (idx < 0) idx += self.size();
      if (idx >= (long) self.size()) PYTHON_ERROR(IndexError, "index out of bounds");

      return self.get(idx);
    }
  };
}




template <typename T>
void exposePODForeignArray(pybind11::module &m,const std::string &name)
{
  typedef tForeignArray<T> cl;
  typedef tPODForeignArrayWrapHelper<cl> w_cl;

  pybind11::class_<cl>(m, name.c_str())
    .def("__len__", &cl::size)
    .def("resize", &cl::setSize)
    .def("setup", &cl::setup)
    .def_property_readonly("unit", &cl::unit)
    .def_property_readonly("allocated", &cl::is_allocated)
    .def("__getitem__", &w_cl::getitem)
    .def("__getitem__", &w_cl::getitem_tup)
    .def("__setitem__", &w_cl::setitem)
    .def("__setitem__", &w_cl::setitem_tup)
    .def("deallocate", &cl::deallocate)
    ;
}





template <typename T>
void exposeStructureForeignArray(pybind11::module &m, const std::string &name)
{
  typedef tForeignArray<T> cl;
  typedef tStructureForeignArrayWrapHelper<cl> w_cl;

  pybind11::class_<cl>(m, name.c_str())
    .def("__len__", &cl::size)
    .def("resize", &cl::setSize)
    .def("setup", &cl::setup)
    .def_property_readonly("unit", &cl::unit)
    .def_property_readonly("allocated", &cl::is_allocated)
    .def("__getitem__", &w_cl::getitem, pybind11::return_value_policy::reference_internal)
    .def("deallocate", &cl::deallocate)
    ;
}





#endif

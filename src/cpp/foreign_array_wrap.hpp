#ifndef _HEADER_SEEN_FOREIGN_ARRAY_WRAP
#define _HEADER_SEEN_FOREIGN_ARRAY_WRAP




#include "foreign_array.hpp"
#include <boost/python.hpp>




using namespace boost::python;




#define PYTHON_ERROR(TYPE, REASON) \
{ \
  PyErr_SetString(PyExc_##TYPE, REASON); \
  throw error_already_set(); \
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

    static object getitem(FA &self, long idx)
    {
      if (idx < 0) idx += self.size();
      if (idx < 0 || idx >= (long) self.size()) 
        PYTHON_ERROR(IndexError, "index out of bounds");
        
      if (self.unit() > 1)
      {
        list l;
        for (unsigned i = 0; i<self.unit();i++)
          l.append(self.getSub(idx, i));
        return l;
      }
      else 
        return object(self.get(idx));
    }

    static object getitem(FA &self, tuple idx)
    {
      if (len(idx) != 2)
        PYTHON_ERROR(IndexError, "expected index tuple of length 2");
      long i_main = extract<int>(idx[0]);
      long i_sub = extract<int>(idx[1]);

      if (i_main < 0) idx += self.size();
      if (i_main < 0 || i_main >= (long) self.size()) 
        PYTHON_ERROR(IndexError, "index out of bounds");
      if (i_sub < 0) idx += self.unit();
      if (i_sub < 0 || i_sub >= (long) self.unit()) 
        PYTHON_ERROR(IndexError, "subindex out of bounds");

      return object(self.getSub(i_main, i_sub));
    }

    static void setitem(FA &self, long idx, object value)
    {
      if (idx < 0) idx += self.size();
      if (idx < 0 || idx >= (long) self.size()) 
        PYTHON_ERROR(IndexError, "index out of bounds");

      if (self.unit() > 1)
      {
        if ((long) self.unit() != len(value)) 
          PYTHON_ERROR(ValueError, "value must be a sequence of length self.unit");
       
        for (long i = 0; i<len(value);i++)
          self.setSub(idx, i, extract<value_type>(value[i]));
      }
      else
        self.set(idx, extract<value_type>(value));
    }

    static void setitem(FA &self, tuple idx, const value_type &v)
    {
      if (len(idx) != 2)
        PYTHON_ERROR(IndexError, "expected index tuple of length 2");
      long i_main = extract<int>(idx[0]);
      long i_sub = extract<int>(idx[1]);

      if (i_main < 0) idx += self.size();
      if (i_main < 0 || i_main >= (long) self.size()) 
        PYTHON_ERROR(IndexError, "index out of bounds");
      if (i_sub < 0) idx += self.unit();
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
void exposePODForeignArray(const std::string &name)
{
  typedef tForeignArray<T> cl;
  typedef tPODForeignArrayWrapHelper<cl> w_cl;
  typedef typename cl::value_type value_type;

  boost::python::class_<cl, boost::noncopyable>(name.c_str(), no_init)
    .def("__len__", &cl::size)
    .def("resize", &cl::setSize)
    .def("setup", &cl::setup)
    .add_property("unit", &cl::unit)
    .add_property("allocated", &cl::is_allocated)
    .def("__getitem__", (object (*)(cl &, long)) &w_cl::getitem)
    .def("__getitem__", (object (*)(cl &, tuple)) &w_cl::getitem)
    .def("__setitem__", (void (*)(cl &, long, object)) &w_cl::setitem)
    .def("__setitem__", (void (*)(cl &, tuple, const value_type &)) &w_cl::setitem)
    .def("deallocate", &cl::deallocate)
    ;
}





template <typename T>
void exposeStructureForeignArray(const std::string &name)
{
  typedef tForeignArray<T> cl;
  typedef tStructureForeignArrayWrapHelper<cl> w_cl;
  typedef typename cl::value_type value_type;

  boost::python::class_<cl, boost::noncopyable>(name.c_str(), no_init)
    .def("__len__", &cl::size)
    .def("resize", &cl::setSize)
    .def("setup", &cl::setup)
    .add_property("unit", &cl::unit)
    .add_property("allocated", &cl::is_allocated)
    .def("__getitem__", &w_cl::getitem, return_internal_reference<>())
    .def("deallocate", &cl::deallocate)
    ;
}





#endif

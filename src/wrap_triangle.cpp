#include "triangle.h"
#include <boost/python.hpp>
#include <stdexcept>
#include <iostream>
#include "foreign_array.hpp"




using namespace boost::python;
using namespace std;




struct tMeshDescriptor : public triangulateio, public boost::noncopyable
{
  public:
    tForeignArray<REAL>		Points; // in/out
    tForeignArray<REAL>		PointAttributes; // in/out
    tForeignArray<int>		PointMarkers; // in/out

    tForeignArray<int>		Elements; // in/out
    tForeignArray<REAL>		ElementAttributes; // in/out
    tForeignArray<REAL>		ElementVolumes; // in only
    tForeignArray<int>		Neighbors; // out only

    tForeignArray<int>		Segments; // in/out
    tForeignArray<int>		SegmentMarkers; // in/out
    
    tForeignArray<REAL>		Holes; // in only

    tForeignArray<REAL>		Regions; // in only

    tForeignArray<int>		Edges; // out only
    tForeignArray<int>		EdgeMarkers; // out only
    tForeignArray<REAL>		Normals; // out only

  public:
    tMeshDescriptor()
      : Points("points", pointlist, numberofpoints, 2),
        PointAttributes("point_attributes", pointattributelist, numberofpoints, 0, &Points),
	PointMarkers("point_markers", pointmarkerlist, numberofpoints, 1, &Points),

	Elements("elements", trianglelist, numberoftriangles, 3),
	ElementAttributes("element_attributes", triangleattributelist, 
            numberoftriangles, 0, &Elements),
	ElementVolumes("element_volumes", trianglearealist, 
            numberoftriangles, 1, &Elements),
	Neighbors("neighbors", neighborlist, 
            numberoftriangles, 3, &Elements),

	Segments("segments", segmentlist, numberofsegments, 2),
	SegmentMarkers("segment_markers", segmentmarkerlist, numberofsegments, 1, &Segments),

	Holes("holes", holelist, numberofholes, 2),

	Regions("regions", regionlist, numberofregions, 4),

	Edges("edges", edgelist, numberofedges, 2),
	EdgeMarkers("edge_markers", edgemarkerlist, numberofedges, 1, &Edges),
	Normals("normals", normlist, numberofedges, 2, &Edges)
    {
      numberofpointattributes = 0;
      numberofcorners = 3;
      numberoftriangleattributes = 0;
    }

    unsigned numberOfPointAttributes() const
    {
      return numberofpointattributes;
    }

    unsigned numberOfElementAttributes() const
    {
      return numberoftriangleattributes;
    }

    void setNumberOfPointAttributes(unsigned attrs)
    {
      PointAttributes.setUnit(attrs);
      numberofpointattributes = attrs;
    }

    void setNumberOfElementAttributes(unsigned attrs)
    {
      ElementAttributes.setUnit(attrs);
      numberoftriangleattributes = attrs;
    }

    tMeshDescriptor &operator=(const tMeshDescriptor &src)
    {
      numberofpointattributes = src.numberofpointattributes ;
      numberofcorners = src.numberofcorners;
      numberoftriangleattributes = src.numberoftriangleattributes;

      Points = src.Points;
      PointAttributes = src.PointAttributes;
      PointMarkers = src.PointMarkers;

      Elements = src.Elements;
      ElementAttributes = src.ElementAttributes;
      ElementVolumes = src.ElementVolumes;
      Neighbors = src.Neighbors;

      Segments = src.Segments;
      SegmentMarkers = src.SegmentMarkers;

      Holes = src.Holes;

      Regions = src.Regions;

      Edges = src.Edges;
      EdgeMarkers = src.EdgeMarkers;
      Normals = src.Normals;

      return *this;
    }
};




tMeshDescriptor *copyMesh(const tMeshDescriptor &src)
{
  auto_ptr<tMeshDescriptor> copy(new tMeshDescriptor);
  *copy = src;
  return copy.release();
}




object RefinementFunction;




class tVertex : public boost::noncopyable
{
  public:
    REAL	*Data;

  public:
    tVertex(REAL *data)
    : Data(data)
    {
    }

    REAL x() { return Data[0]; }
    REAL y() { return Data[1]; }
};




int triunsuitable(vertex triorg, vertex tridest, vertex triapex, REAL area)
{
  // return 1 if triangle is too large, 0 otherwise
  try
  {
    tVertex org(triorg);
    tVertex dest(tridest);
    tVertex apex(triapex);
    return extract<bool>(RefinementFunction(
	  boost::ref(org), boost::ref(dest), boost::ref(apex), area));
  }
  catch (exception &ex)
  {
    cerr 
      << "*** Oops. Your Python refinement function raised an exception." << endl
      << "*** " << ex.what() << endl
      << "*** Sorry, we can't continue." << endl;
    abort();
  }
  catch (...)
  {
    cerr 
      << "*** Oops. Your Python refinement function raised an exception." << endl
      << "*** Sorry, we can't continue." << endl;
    abort();
  }
}




void triangulateWrapper(char *options, tMeshDescriptor &in, 
    tMeshDescriptor &out,
    tMeshDescriptor &voronoi,
    object refinement_func)
{
  RefinementFunction = refinement_func;
  triangulate(options, &in, &out, &voronoi);
  RefinementFunction = object(); // i.e. None

  out.holelist = NULL;
  out.numberofholes = 0;

  out.regionlist = NULL;
  out.numberofregions = 0;
}




template <typename T>
void exposeForeignArray(T, const string &name)
{
  typedef tForeignArray<T> cl;

  class_<cl, boost::noncopyable>
    (name.c_str(), no_init)
    .def("__len__", &cl::size)
    .def("size", &cl::size)
    .def("set_size", &cl::setSize)
    .def("setup", &cl::setup)
    .def("unit", &cl::unit)
    .def("set", &cl::set)
    .def("set_sub", &cl::setSub)
    .def("get", &cl::get)
    .def("get_sub", &cl::getSub)
    .def("deallocate", &cl::deallocate)
    ;
}





BOOST_PYTHON_MODULE(internals)
{
  def("triangulate", triangulateWrapper);

  {
    typedef tMeshDescriptor cl;
    class_<cl, boost::noncopyable>
      ("MeshDescriptor", init<>())
      .def_readonly("points", &cl::Points)
      .def_readonly("point_attributes", &cl::PointAttributes)
      .def_readonly("point_markers", &cl::PointMarkers)

      .def_readonly("elements", &cl::Elements)
      .def_readonly("element_attributes", &cl::ElementAttributes)
      .def_readonly("element_volumes", &cl::ElementVolumes)
      .def_readonly("neighbors", &cl::Neighbors)

      .def_readonly("Segments", &cl::Segments)
      .def_readonly("SegmentMarkers", &cl::SegmentMarkers)

      .def_readonly("Holes", &cl::Holes)

      .def_readonly("Regions", &cl::Regions)

      .def_readonly("Edges", &cl::Edges)
      .def_readonly("EdgeMarkers", &cl::EdgeMarkers)

      .def_readonly("Normals", &cl::Normals)

      .add_property("number_of_point_attributes", 
          &cl::numberOfPointAttributes,
          &cl::setNumberOfPointAttributes)
      .add_property("number_of_element_attributes", 
          &cl::numberOfElementAttributes,
          &cl::setNumberOfElementAttributes)

      .def("copy", &copyMesh, return_value_policy<manage_new_object>())
      .enable_pickling()
      ;
  }
  
  exposeForeignArray(REAL(), "RealArray");
  exposeForeignArray(int(), "IntArray");

  class_<tVertex, bases<>, tVertex, boost::noncopyable>("Vertex", no_init)
    .add_property("x", &tVertex::x)
    .add_property("y", &tVertex::y)
    ;
}

#include "triangle.h"
#include <boost/python.hpp>
#include <stdexcept>
#include <iostream>
#include "foreign_array_wrap.hpp"




using namespace boost::python;
using namespace std;




struct tMeshInfo : public triangulateio, public boost::noncopyable
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
    tMeshInfo()
      : Points("points", pointlist, numberofpoints, 2, NULL, true),
        PointAttributes("point_attributes", pointattributelist, numberofpoints, 0, &Points, true),
	PointMarkers("point_markers", pointmarkerlist, numberofpoints, 1, &Points, true),

	Elements("elements", trianglelist, numberoftriangles, 3, NULL, true),
	ElementAttributes("element_attributes", triangleattributelist, 
            numberoftriangles, 0, &Elements, true),
	ElementVolumes("element_volumes", trianglearealist, 
            numberoftriangles, 1, &Elements, true),
	Neighbors("neighbors", neighborlist, 
            numberoftriangles, 3, &Elements, true),

	Segments("segments", segmentlist, numberofsegments, 2, NULL, true),
	SegmentMarkers("segment_markers", segmentmarkerlist, numberofsegments, 1, &Segments, true),

	Holes("holes", holelist, numberofholes, 2, NULL, true),

	Regions("regions", regionlist, numberofregions, 4, NULL, true),

	Edges("edges", edgelist, numberofedges, 2, NULL, true),
	EdgeMarkers("edge_markers", edgemarkerlist, numberofedges, 1, &Edges, true),
	Normals("normals", normlist, numberofedges, 2, &Edges, true)
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

    tMeshInfo &operator=(const tMeshInfo &src)
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




tMeshInfo *copyMesh(const tMeshInfo &src)
{
  auto_ptr<tMeshInfo> copy(new tMeshInfo);
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




void triangulateWrapper(char *options, tMeshInfo &in, 
    tMeshInfo &out,
    tMeshInfo &voronoi,
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




BOOST_PYTHON_MODULE(_triangle)
{
  def("triangulate", triangulateWrapper);

  {
    typedef tMeshInfo cl;
    class_<cl, boost::noncopyable>
      ("MeshInfo", init<>())
      .def_readonly("points", &cl::Points)
      .def_readonly("point_attributes", &cl::PointAttributes)
      .def_readonly("point_markers", &cl::PointMarkers)

      .def_readonly("elements", &cl::Elements)
      .def_readonly("element_attributes", &cl::ElementAttributes)
      .def_readonly("element_volumes", &cl::ElementVolumes)
      .def_readonly("neighbors", &cl::Neighbors)

      .def_readonly("segments", &cl::Segments)
      .def_readonly("segment_markers", &cl::SegmentMarkers)

      .def_readonly("holes", &cl::Holes)

      .def_readonly("regions", &cl::Regions)

      .def_readonly("edges", &cl::Edges)
      .def_readonly("edge_markers", &cl::EdgeMarkers)

      .def_readonly("normals", &cl::Normals)

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
  
  exposePODForeignArray<REAL>("RealArray");
  exposePODForeignArray<int>("IntArray");

  class_<tVertex, bases<>, tVertex, boost::noncopyable>("Vertex", no_init)
    .add_property("x", &tVertex::x)
    .add_property("y", &tVertex::y)
    ;
}

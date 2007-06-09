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

    tForeignArray<int>		Faces; // in/out
    tForeignArray<int>		FaceMarkers; // in/out
    
    tForeignArray<REAL>		Holes; // in only

    tForeignArray<REAL>		Regions; // in only

    tForeignArray<int>		Edges; // out only
    tForeignArray<int>		EdgeMarkers; // out only
    tForeignArray<REAL>		Normals; // out only

  public:
    tMeshInfo()
      : Points(pointlist, numberofpoints, 2, NULL, true),
        PointAttributes(pointattributelist, numberofpoints, 0, &Points, true),
	PointMarkers(pointmarkerlist, numberofpoints, 1, &Points, true),

	Elements(trianglelist, numberoftriangles, 3, NULL, true),
	ElementAttributes(triangleattributelist, 
            numberoftriangles, 0, &Elements, true),
	ElementVolumes(trianglearealist, 
            numberoftriangles, 1, &Elements, true),
	Neighbors(neighborlist, 
            numberoftriangles, 3, &Elements, true),

	Faces(segmentlist, numberofsegments, 2, NULL, true),
	FaceMarkers(segmentmarkerlist, numberofsegments, 1, &Faces, true),

	Holes(holelist, numberofholes, 2, NULL, true),

	Regions(regionlist, numberofregions, 4, NULL, true),

	Edges(edgelist, numberofedges, 2, NULL, true),
	EdgeMarkers(edgemarkerlist, numberofedges, 1, &Edges, true),
	Normals(normlist, numberofedges, 2, &Edges, true)
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

      Faces = src.Faces;
      FaceMarkers = src.FaceMarkers;

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




PyObject *RefinementFunction;




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
  tVertex org(triorg);
  tVertex dest(tridest);
  tVertex apex(triapex);
  return call<bool>(RefinementFunction,
      boost::ref(org), boost::ref(dest), boost::ref(apex), area);
}




void triangulateWrapper(char *options, tMeshInfo &in, 
    tMeshInfo &out,
    tMeshInfo &voronoi,
    PyObject *refinement_func)
{
  RefinementFunction = refinement_func;
  triangulate(options, &in, &out, &voronoi);

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

      .def_readonly("faces", &cl::Faces)
      .def_readonly("face_markers", &cl::FaceMarkers)

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

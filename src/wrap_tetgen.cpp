#include "tetgen.h"
#include <boost/python.hpp>
#include <vector>
#include <stdexcept>
#include <iostream>
#include "foreign_array.hpp"




using namespace boost::python;
using namespace std;




struct tMeshDescriptor : public tetgenio, public boost::noncopyable
{
  public:
    tForeignArray<REAL>		Points; // in/out
    tForeignArray<REAL>		PointAttributes; // in/out
    tForeignArray<REAL>		AdditionalPoints; // out
    tForeignArray<REAL>		AdditionalPointAttributs; // out
    tForeignArray<int>		PointMarkers; // in/out

    tForeignArray<int>		Elements; // in/out
    tForeignArray<REAL>		ElementAttributes; // in/out
    tForeignArray<REAL>		ElementVolumes; // out
    tForeignArray<int>		Neighbors; // out

    tForeignArray<tetgenio::facet>		Facets;

  public:
    tMeshDescriptor()
      : Points("Points", pointlist, numberofpoints, 3),
        PointAttributes("PointAttributes", pointattributelist, numberofpoints, 0, &Points),
        AdditionalPoints("AdditionalPoints", addpointlist, numberofaddpoints, 3),
        PointAttributes("AdditionalPointAttributes", addpointattributelist, numberofaddpoints, 0, &AdditionalPoints),
	PointMarkers("PointMarkers", pointmarkerlist, numberofpoints, 1, &Points),

	Elements("Elements", tetrahedronlist, numberoftetrahedra, 4),
	ElementAttributes("ElementAttributes", tetrahedronattributelist, 
            numberoftetrahedra, 0, &Elements),
	ElementVolumes("ElementVolumes", tetrahedronvolumelist, 
            numberoftetrahedra, 1, &Elements),
	Neighbors("Neighbors", neighborlist, 
            numberoftetrahedra, 4, &Elements),

        Facets("Facets", facetlist, numberoffacets)

        /*
	Segments("Segments", segmentlist, numberofsegments, 2),
	SegmentMarkers("SegmentMarkers", segmentmarkerlist, numberofsegments, 1, &Segments),

	Holes("Holes", holelist, numberofholes, 3),

	Regions("Regions", regionlist, numberofregions, 4),

	Edges("Edges", edgelist, numberofedges, 2),
	EdgeMarkers("EdgeMarkers", edgemarkerlist, numberofedges, 1, &Edges),
	Normals("Normals", normlist, numberofedges, 2, &Edges)
        */
    {
      numberofpointattributes = 0;
      numberofcorners = 3;
      numberoftetrahedronattributes = 0; 
    } 
    
    unsigned numberOfPointAttributes() const
    {
      return numberofpointattributes;
    }

    unsigned numberOfElementAttributes() const
    {
      return numberoftetrahedronattributes;
    }

    void setNumberOfPointAttributes(unsigned attrs)
    {
      PointAttributes.setUnit(attrs);
      numberofpointattributes = attrs;
    }

    void setNumberOfElementAttributes(unsigned attrs)
    {
      ElementAttributes.setUnit(attrs);
      numberoftetrahedronattributes = attrs;
    }

    /*
    tTriangulationParameters &operator=(const tTriangulationParameters &src)
    {
      numberofpointattributes = src.numberofpointattributes ;
      numberofcorners = src.numberofcorners;
      numberoftriangleattributes = src.numberoftriangleattributes;

      Points = src.Points;
      PointAttributes = src.PointAttributes;
      PointMarkers = src.PointMarkers;

      Triangles = src.Triangles;
      TriangleAttributes = src.TriangleAttributes;
      TriangleAreas = src.TriangleAreas;
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
    */
};




/*
tTriangulationParameters *copyTriangulationParameters(const tTriangulationParameters &src)
{
  auto_ptr<tTriangulationParameters> copy(new tTriangulationParameters);
  *copy = src;
  return copy.release();
}
*/




void tetrahedralizeWrapper(tetgenbehavior &bhv, tMeshDescriptor &in, tMeshDescriptor &out)
{
  tetrahedralize(&bhv, &in, &out);
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
  def("tetrahedralize", tetrahedralizeWrapper);

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

      /*
      .def_readonly("Segments", &cl::Segments)
      .def_readonly("SegmentMarkers", &cl::SegmentMarkers)

      .def_readonly("Holes", &cl::Holes)

      .def_readonly("Regions", &cl::Regions)

      .def_readonly("Edges", &cl::Edges)
      .def_readonly("EdgeMarkers", &cl::EdgeMarkers)

      .def_readonly("Normals", &cl::Normals)
      */

      .add_property("number_of_point_attributes", 
          &cl::numberOfPointAttributes,
          &cl::setNumberOfPointAttributes)
      .add_property("number_of_element_attributes", 
          &cl::numberOfElementAttributes,
          &cl::setNumberOfElementAttributes)

      /*
         .def("copy", &copyTriangulationParameters,
         return_value_policy<manage_new_object>())
         */
      //.enable_pickling()
      ;
  }

  exposeForeignArray(REAL(), "RealArray");
  exposeForeignArray(int(), "IntArray");
}

#include "tetgen.h"
#include <pybind11/pybind11.h>
#include <vector>
#include <stdexcept>
#include <iostream>
#include "foreign_array_wrap.hpp"




namespace py = pybind11;
using namespace std;


namespace
{
  struct tMeshInfo : public tetgenio, public noncopyable
  {
    private:
      typedef tetgenio super;

    public:
      tForeignArray<REAL>                       Points; // in/out
      tForeignArray<REAL>                       PointAttributes; // in/out
      tForeignArray<REAL>                       PointMetricTensors; // in/out
      tForeignArray<int>                        PointMarkers; // in/out

      tForeignArray<int>                        Elements; // in/out
      tForeignArray<REAL>                       ElementAttributes; // in/out
      tForeignArray<REAL>                       ElementVolumes; // out
      tForeignArray<int>                        Neighbors; // out

      tForeignArray<tetgenio::facet>      Facets;
      tForeignArray<int>                  FacetMarkers;

      tForeignArray<REAL>                 Holes;
      tForeignArray<REAL>                 Regions;

      tForeignArray<REAL>                 FacetConstraints;
      tForeignArray<REAL>                 SegmentConstraints;

      tForeignArray<int>                  Faces;
      tForeignArray<int>                  AdjacentElements;
      tForeignArray<int>                  FaceMarkers;

      tForeignArray<int>                  Edges;
      tForeignArray<int>                  EdgeMarkers;
      tForeignArray<int>                  EdgeAdjTetList;

    public:
      tMeshInfo()
        : Points(pointlist, numberofpoints, 3),
          PointAttributes(pointattributelist, numberofpoints, 0, &Points),
          PointMetricTensors(pointmtrlist, numberofpoints, 0, &Points),
          PointMarkers(pointmarkerlist, numberofpoints, 1, &Points),

          Elements(tetrahedronlist, numberoftetrahedra, 0),
          ElementAttributes(tetrahedronattributelist,
              numberoftetrahedra, 0, &Elements),
          ElementVolumes(tetrahedronvolumelist, numberoftetrahedra, 1, &Elements),
          Neighbors(neighborlist, numberoftetrahedra, 4, &Elements),

          Facets(facetlist, numberoffacets),
          FacetMarkers(facetmarkerlist, numberoffacets, 1, &Facets),

          Holes(holelist, numberofholes, 3),

          Regions(regionlist, numberofregions, 5),

          FacetConstraints(facetconstraintlist, numberoffacetconstraints, 2),
          SegmentConstraints(segmentconstraintlist, numberofsegmentconstraints, 3),

          Faces(trifacelist, numberoftrifaces, 3),
          AdjacentElements(adjtetlist, numberoftrifaces, 2, &Faces),
          FaceMarkers(trifacemarkerlist, numberoftrifaces, 1, &Faces),

          Edges(edgelist, numberofedges, 2),
          EdgeMarkers(edgemarkerlist, numberofedges, 1, &Edges),
          EdgeAdjTetList(edgeadjtetlist, numberofedges, 1, &Edges)
      {
        Elements.fixUnit(numberofcorners);
      }

      unsigned numberOfPointAttributes() const
      {
        return numberofpointattributes;
      }

      unsigned numberOfPointMetricTensors() const
      {
        return numberofpointmtrs;
      }

      unsigned numberOfElementVertices() const
      {
        return numberofcorners;
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

      void setNumberOfPointMetricTensors(unsigned mtrs)
      {
        PointMetricTensors.setUnit(mtrs);
        numberofpointmtrs = mtrs;
      }

      void setNumberOfElementVertices(unsigned verts)
      {
        Elements.setUnit(verts);
        numberofcorners = verts;
      }

      void setNumberOfElementAttributes(unsigned attrs)
      {
        ElementAttributes.setUnit(attrs);
        numberoftetrahedronattributes = attrs;
      }

#define OVERRIDE_LOAD_WITH_ERROR_CHECK(WHAT, POSTPROC) \
      void load_##WHAT(char* filename) \
      { \
        if (!super::load_##WHAT(filename)) \
          throw std::runtime_error("load_" #WHAT " failed"); \
        POSTPROC; \
      }

      OVERRIDE_LOAD_WITH_ERROR_CHECK(node,);
      OVERRIDE_LOAD_WITH_ERROR_CHECK(var,);
      OVERRIDE_LOAD_WITH_ERROR_CHECK(mtr,);
      OVERRIDE_LOAD_WITH_ERROR_CHECK(poly,);
      OVERRIDE_LOAD_WITH_ERROR_CHECK(off,);
      OVERRIDE_LOAD_WITH_ERROR_CHECK(ply,);
      OVERRIDE_LOAD_WITH_ERROR_CHECK(stl,);
      OVERRIDE_LOAD_WITH_ERROR_CHECK(vtk,);

      void load_plc(char* filename, int object)
      {
        if (!super::load_plc(filename, object))
          throw std::runtime_error("load_plc failed");
      }

      void load_medit(char* filename, int object)
      {
        if (!super::load_medit(filename, object))
          throw std::runtime_error("load_tetmesh failed");
      }

      void load_tetmesh(char* filename, int object)
      {
        if (!super::load_tetmesh(filename, object))
          throw std::runtime_error("load_tetmesh failed");
        Elements.fixUnit(numberofcorners);
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




  void tetrahedralizeWrapper(tetgenbehavior &bhv, tMeshInfo &in, tMeshInfo &out,
      tMeshInfo *addin)
  {
    try
    {
      tetrahedralize(&bhv, &in, &out, addin);
    }
    catch (int &i)
    {
      throw runtime_error("TetGen runtime error code "+std::to_string(i));
    }

    out.Elements.fixUnit(out.numberofcorners);
    out.PointAttributes.fixUnit(out.numberofpointattributes);
    out.PointMetricTensors.fixUnit(out.numberofpointmtrs);
    out.ElementAttributes.fixUnit(out.numberoftetrahedronattributes);
  }




  tForeignArray<tetgenio::polygon> *facet_get_polygons(tetgenio::facet &self)
  {
    return new tForeignArray<tetgenio::polygon>(
        self.polygonlist, self.numberofpolygons);
  }




  tForeignArray<REAL> *facet_get_holes(tetgenio::facet &self)
  {
    return new tForeignArray<REAL>(self.holelist, self.numberofholes, 3);
  }





  tForeignArray<int> *polygon_get_vertices(tetgenio::polygon &self)
  {
    return new tForeignArray<int>(self.vertexlist, self.numberofvertices);
  }
}





#define DEF_RW_MEMBER(NAME) \
    def_readwrite(#NAME, &cl::NAME)
#define DEF_METHOD(NAME) \
    def(#NAME, &cl::NAME)

void expose_tetgen(pybind11::module &m)
{
  m.def("tetrahedralize", tetrahedralizeWrapper,
      py::arg("behavior"), py::arg("in"), py::arg("out"),
      py::arg("addin").none(true)=py::none());

  {
    typedef tMeshInfo cl;
    py::class_<cl>(m, "TetMeshInfo")
      .def(py::init<>())
      .def_readonly("points", &cl::Points)
      .def_readonly("point_attributes", &cl::PointAttributes)
      .def_readonly("point_metric_tensors", &cl::PointMetricTensors)
      .def_readonly("point_markers", &cl::PointMarkers)

      .def_readonly("elements", &cl::Elements)
      .def_readonly("element_attributes", &cl::ElementAttributes)
      .def_readonly("element_volumes", &cl::ElementVolumes)
      .def_readonly("neighbors", &cl::Neighbors)


      .def_readonly("facets", &cl::Facets)
      .def_readonly("facet_markers", &cl::FacetMarkers)

      .def_readonly("holes", &cl::Holes)

      .def_readonly("regions", &cl::Regions)

      .def_readonly("facet_constraints", &cl::FacetConstraints)
      .def_readonly("segment_constraints", &cl::SegmentConstraints)

      .def_readonly("faces", &cl::Faces)
      .def_readonly("adjacent_elements", &cl::AdjacentElements)
      .def_readonly("face_markers", &cl::FaceMarkers)

      .def_readonly("edges", &cl::Edges)
      .def_readonly("edge_markers", &cl::EdgeMarkers)
      .def_readonly("edge_adjacent_elements", &cl::EdgeAdjTetList)

      .def_property("number_of_point_attributes",
          &cl::numberOfPointAttributes,
          &cl::setNumberOfPointAttributes)
      .def_property("number_of_element_vertices",
          &cl::numberOfElementVertices,
          &cl::setNumberOfElementVertices)
      .def_property("number_of_element_attributes",
          &cl::numberOfElementAttributes,
          &cl::setNumberOfElementAttributes)

      .DEF_METHOD(save_nodes)
      .DEF_METHOD(save_elements)
      .DEF_METHOD(save_faces)
      .DEF_METHOD(save_edges)
      .DEF_METHOD(save_neighbors)
      .DEF_METHOD(save_poly)

      .DEF_METHOD(load_node)
      .DEF_METHOD(load_var)
      .DEF_METHOD(load_mtr)
      .DEF_METHOD(load_poly)
      .DEF_METHOD(load_off)
      .DEF_METHOD(load_ply)
      .DEF_METHOD(load_stl)
      .DEF_METHOD(load_medit)
      .DEF_METHOD(load_plc)
      .DEF_METHOD(load_tetmesh)

      /*
         .def("copy", &copyTriangulationParameters,
         return_value_policy<manage_new_object>())
         */
      //.enable_pickling()
      ;
  }

  {
    typedef tetgenio::facet cl;
    py::class_<cl>(m, "Facet")
      .def_property_readonly("polygons",
          facet_get_polygons, py::return_value_policy::reference_internal)
      .def_property_readonly("holes",
          facet_get_holes, py::return_value_policy::reference_internal)
      ;
  }

  {
    typedef tetgenio::polygon cl;
    py::class_<cl>(m, "Polygon")
      .def_property_readonly("vertices",
          polygon_get_vertices, py::return_value_policy::reference_internal)
      ;
  }

  {
    typedef tetgenbehavior cl;
    py::class_<cl>(m, "Options")
      .def(py::init<>())
      .DEF_RW_MEMBER(plc)
      .DEF_RW_MEMBER(psc)
      .DEF_RW_MEMBER(refine)
      .DEF_RW_MEMBER(quality)
      .DEF_RW_MEMBER(nobisect)
      .DEF_RW_MEMBER(coarsen)
      .DEF_RW_MEMBER(weighted)
      .DEF_RW_MEMBER(brio_hilbert)
      .DEF_RW_MEMBER(incrflip)
      .DEF_RW_MEMBER(flipinsert)
      .DEF_RW_MEMBER(metric)
      .DEF_RW_MEMBER(varvolume)
      .DEF_RW_MEMBER(fixedvolume)
      .DEF_RW_MEMBER(regionattrib)
      .DEF_RW_MEMBER(conforming)
      .DEF_RW_MEMBER(insertaddpoints)
      .DEF_RW_MEMBER(diagnose)
      .DEF_RW_MEMBER(convex)
      .DEF_RW_MEMBER(nomergefacet)
      .DEF_RW_MEMBER(nomergevertex)
      .DEF_RW_MEMBER(noexact)
      .DEF_RW_MEMBER(nostaticfilter)
      .DEF_RW_MEMBER(zeroindex)
      .DEF_RW_MEMBER(facesout)
      .DEF_RW_MEMBER(edgesout)
      .DEF_RW_MEMBER(neighout)
      .DEF_RW_MEMBER(voroout)
      .DEF_RW_MEMBER(meditview)
      .DEF_RW_MEMBER(vtkview)
      .DEF_RW_MEMBER(nobound)
      .DEF_RW_MEMBER(nonodewritten)
      .DEF_RW_MEMBER(noelewritten)
      .DEF_RW_MEMBER(nofacewritten)
      .DEF_RW_MEMBER(noiterationnum)
      .DEF_RW_MEMBER(nojettison)
      .DEF_RW_MEMBER(reversetetori)
      .DEF_RW_MEMBER(docheck)
      .DEF_RW_MEMBER(quiet)
      .DEF_RW_MEMBER(verbose)

      .DEF_RW_MEMBER(vertexperblock)
      .DEF_RW_MEMBER(tetrahedraperblock)
      .DEF_RW_MEMBER(shellfaceperblock)
      .DEF_RW_MEMBER(nobisect_param)
      .DEF_RW_MEMBER(addsteiner_algo)
      .DEF_RW_MEMBER(coarsen_param)
      .DEF_RW_MEMBER(weighted_param)
      .DEF_RW_MEMBER(fliplinklevel)
      .DEF_RW_MEMBER(flipstarsize)
      .DEF_RW_MEMBER(fliplinklevelinc)
      .DEF_RW_MEMBER(reflevel)
      .DEF_RW_MEMBER(optlevel)
      .DEF_RW_MEMBER(optscheme)
      .DEF_RW_MEMBER(delmaxfliplevel)
      .DEF_RW_MEMBER(order)
      .DEF_RW_MEMBER(steinerleft)
      .DEF_RW_MEMBER(no_sort)
      .DEF_RW_MEMBER(hilbert_order)
      .DEF_RW_MEMBER(hilbert_limit)
      .DEF_RW_MEMBER(brio_threshold)
      .DEF_RW_MEMBER(brio_ratio)
      .DEF_RW_MEMBER(facet_ang_tol)
      .DEF_RW_MEMBER(maxvolume)
      .DEF_RW_MEMBER(minratio)
      .DEF_RW_MEMBER(mindihedral)
      .DEF_RW_MEMBER(optmaxdihedral)
      .DEF_RW_MEMBER(optminsmtdihed)
      .DEF_RW_MEMBER(optminslidihed)
      .DEF_RW_MEMBER(epsilon)
      .DEF_RW_MEMBER(minedgelength)
      .DEF_RW_MEMBER(coarsen_percent)

      .def("parse_switches", (bool (tetgenbehavior::*)(char *)) &cl::parse_commandline)
      ;
  }

  exposeStructureForeignArray<tetgenio::facet>(m, "FacetArray");
  exposeStructureForeignArray<tetgenio::polygon>(m, "PolygonArray");
}

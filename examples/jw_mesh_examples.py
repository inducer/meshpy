# -*- coding: utf-8 -*-
"""
Short Gallery of examples
for meshpy

written by Juergen Weizenecker

"""

import numpy as np
import jw_meshtools as mt
import meshpy.triangle as triangle
import numpy.linalg as la


length=0.3




# Simple mesh rectangle
p,v=mt.RectangleSegments([-1,-1],[2.5,3],edge_length=length)
mt.DoTriMesh(p,v,edge_length=length)




# simple mesh circle
p,v=mt.CircleSegments([1,2],2,edge_length=length)
mt.DoTriMesh(p,v,edge_length=length)



#
# simple mesh triangle
#
p1,v1=mt.LineSegments([2,2],[-1,-3],edge_length=length)
p2,v2=mt.LineSegments([-1,-3],[3,-1],num_points=10)
p,v=mt.AddSegments(p1,p2,closed=True)
mt.DoTriMesh(p,v,edge_length=length)


# 
# two semicircles
#
p1,v1=mt.CircleSegments([1.,0],1,a_min=-np.pi/2,a_max=np.pi/2,num_points=20)
p2,v2=mt.CircleSegments([1,0],3,a_min=np.pi/2.,a_max=3.*np.pi/2,num_points=20)
p,v=mt.AddSegments(p1,p2,closed=True)
# plot mesh 
mt.DoTriMesh(p,v,edge_length=length)


#
# rectangle and inner circle
#
p1,v1=mt.RectangleSegments([-2,-2],[2.5,3],edge_length=length)
p2,v2=mt.CircleSegments([1,1],1,edge_length=length/5)
p,v=mt.AddCurves(p1,v1,p2,v2)
mt.DoTriMesh(p,v,edge_length=length)


#
# rectangle and inner line
#
p1,v1=mt.RectangleSegments([-2,-2],[2.5,3],edge_length=length)
p2,v2=mt.LineSegments([0,0],[1,1],edge_length=length/5)
p,v=mt.AddCurves(p1,v1,p2,v2)
p3,v3=mt.LineSegments([-1,1],[0,-1],edge_length=length/5)
p,v=mt.AddCurves(p,v,p3,v3)
mt.DoTriMesh(p,v,edge_length=length)



#
# rectangle with holes
p1,v1=mt.LineSegments([-2,-3],[2,-3],num_points=12)
p2,v2=mt.LineSegments([2,3],[-2,3],num_points=12)
p,v=mt.AddSegments(p1,p2,closed=True)
p3,v3=mt.CircleSegments([-0.5,0.5],0.5,edge_length=length)
p,v=mt.AddCurves(p,v,p3,v3)
p4,v4=mt.CircleSegments([1,-1],0.5,edge_length=length)
p,v=mt.AddCurves(p,v,p4,v4)
mt.DoTriMesh(p,v,edge_length=length,holes=[(-0.4,0.4),(0.95,-0.8)])




#
# 2D curve
#
t=np.linspace(0,2*np.pi,120)
r=3+np.sin(8*t)
x=r*np.cos(t)
y=r*np.sin(t)
p=[(x[j],y[j]) for j in range(len(t))]
p1,v1=mt.PointSegments(p)
mt.DoTriMesh(p1,v1,edge_length=length)



#
# rectangle and local refinement 
#
p1,v1=mt.RectangleSegments([0,0],[1,1],num_points=100)
p2,v2=mt.RectangleSegments([0.05,0.05],[0.95,0.95],num_points=40)
p,v=mt.AddCurves(p1,v1,p2,v2)
p3,v3=mt.RectangleSegments([0.1,0.1],[0.9,0.9],num_points=20)
p,v=mt.AddCurves(p,v,p3,v3)
mt.DoTriMesh(p,v,edge_length=length)




#
# 2D curve with local mesh refinement I
#
# 
t=np.linspace(0,2*np.pi,120)
r=3+np.sin(8*t)
x=r*np.cos(t)
y=r*np.sin(t)
p=[(x[j],y[j]) for j in range(len(t))]
p1,v1=mt.PointSegments(p)
# function for refinement
def myrefine1(tri_points, area):
  center_tri = np.sum(np.array(tri_points), axis=0)/3.
  x=center_tri[0]
  y=center_tri[1]
  if x>0:
    max_area=0.05*(1+3*x)
  else:
    max_area=0.05
  return bool(area>max_area);
mt.DoTriMesh(p1,v1,tri_refine=myrefine1)





#
# 2D curve with local refinement II
# !! 2 plots
#
# take p1 from above
p2,v2=mt.CircleSegments([0,0],1,edge_length=0.1)
p,v=mt.AddCurves(p1,v1,p2,v2)
# function for refinement
def myrefine2(tri_points, area):
  center_tri = np.sum(np.array(tri_points), axis=0)/3.
  r=np.sqrt(center_tri[0]**2+center_tri[1]**2) 
  max_area=0.3+(0.01-0.3)/(1+0.5*(r-1)**2)
  return bool(area>max_area);
mt.DoTriMesh(p1,v1,tri_refine=myrefine2)  
mt.DoTriMesh(p,v,tri_refine=myrefine2)




#
# 2D curve with local refinement III
# 
#
# take p1 from above
nodes=range(len(p1))
# define tree to speed up node search
from scipy.spatial import cKDTree
p1tree=cKDTree(np.array(p1))
# function for refinement
def myrefine3(tri_points, area):
  center_tri = np.sum(np.array(tri_points), axis=0)/3.
  p0=[(center_tri[0],center_tri[1])]
  node,r=mt.FindClosestNode(nodes,[],p0,tree=p1tree)
  r=r[0]
  max_area=0.3+(0.01-0.3)/(1+r**2) 
  return bool(area>max_area);
mt.DoTriMesh(p1,v1,tri_refine=myrefine3) 



#
# Example for using directly triangle
#

def round_trip_connect(start, end):
  return [(i, i+1) for i in range(start, end)] + [(end, start)]

points = [(1,0),(1,1),(-1,1),(-1,-1),(1,-1),(1,0)]
facets = round_trip_connect(0, len(points)-1)

circ_start = len(points)
points.extend(
        (3 * np.cos(angle), 3 * np.sin(angle))
        for angle in np.linspace(0, 2*np.pi, 29, endpoint=False))

facets.extend(round_trip_connect(circ_start, len(points)-1))

def needs_refinement(vertices, area):
    bary = np.sum(np.array(vertices), axis=0)/3
    max_area = 0.01 + abs((la.norm(bary, np.inf)-1))*0.1
    return bool(area > max_area)

info = triangle.MeshInfo()
info.set_points(points)
info.set_holes([(0,0)])
info.set_facets(facets)

mesh = triangle.build(info, refinement_func=needs_refinement)
#mesh = triangle.build(info) 

mesh_points = np.array(mesh.points)
mesh_tris = np.array(mesh.elements)

import matplotlib.pyplot as pt
print(mesh_points)
print(mesh_tris)
pt.triplot(mesh_points[:, 0], mesh_points[:, 1], mesh_tris)
pt.show()


  

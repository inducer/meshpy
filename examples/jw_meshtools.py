# -*- coding: utf-8 -*-
"""
Toolbox for generating a mesh

"""
import numpy as np
import scipy as sp
from scipy.spatial import cKDTree
import matplotlib.pyplot as plt
import meshpy.triangle as triangle
from mpl_toolkits.mplot3d import Axes3D
from collections import Counter

# import mayavi.mlab as mal


def RefineMeshElements(poi, tri, uu, n=1):

    t_new = []
    if n == 1:
        for t in tri:
            t_new += [[t[0], t[3], t[5]]]
            t_new += [[t[3], t[1], t[4]]]
            t_new += [[t[3], t[4], t[5]]]
            t_new += [[t[4], t[2], t[5]]]
            return poi, np.array(t_new), uu
    else:
        p_new = list(poi)
        u_new = list(uu)
        NN = len(poi)
        for t in tri:
            n1 = t[0]
            n2 = t[1]
            n3 = t[2]
            n4 = t[3]
            n5 = t[4]
            n6 = t[5]
            p1 = poi[n1]
            p2 = poi[n2]
            p3 = poi[n3]
            p4 = poi[n4]
            p5 = poi[n5]
            p6 = poi[n6]
            # define new points
            q1 = (p1 + p4 + p6) / 3.0
            q2 = (p4 + p2 + p5) / 3.0
            q3 = (p3 + p6 + p5) / 3.0
            q4 = (p4 + p5 + p6) / 3.0

            # compute values at new points
            b1 = poi[n2, 1] - poi[n3, 1]
            b2 = poi[n3, 1] - poi[n1, 1]
            b3 = poi[n1, 1] - poi[n2, 1]

            c1 = poi[n3, 0] - poi[n2, 0]
            c2 = poi[n1, 0] - poi[n3, 0]
            c3 = poi[n2, 0] - poi[n1, 0]

            a1 = poi[n2, 0] * poi[n3, 1] - poi[n3, 0] * poi[n2, 1]
            a2 = poi[n3, 0] * poi[n1, 1] - poi[n1, 0] * poi[n3, 1]
            a3 = poi[n1, 0] * poi[n2, 1] - poi[n2, 0] * poi[n1, 1]

            twodelta = b1 * c2 - c1 * b2

            PHI = uu[t]

            phi_inner = []
            for Q in [q1, q2, q3, q4]:
                N1 = 1.0 / twodelta * (a1 + b1 * Q[0] + c1 * Q[1])
                N2 = 1.0 / twodelta * (a2 + b2 * Q[0] + c2 * Q[1])
                N3 = 1.0 / twodelta * (a3 + b3 * Q[0] + c3 * Q[1])
                Basefunc = [
                    (2 * N1 - 1) * N1,
                    (2 * N2 - 1) * N2,
                    (2 * N3 - 1) * N3,
                    4 * N1 * N2,
                    4 * N2 * N3,
                    4 * N1 * N3,
                ]
                phi_inner += [sum(Basefunc * PHI)]

            p_new += [q1, q2, q3, q4]
            u_new += phi_inner
            t_new += [[n1, NN, n6], [n1, n4, NN], [n4, n6, NN]]
            t_new += [[n4, NN + 1, n5], [n4, n2, NN + 1], [n2, n5, NN + 1]]
            t_new += [[n5, NN + 2, n6], [n5, n3, NN + 2], [n3, n6, NN + 2]]
            t_new += [[n5, NN + 3, n4], [n5, n6, NN + 3], [n6, n4, NN + 3]]
            NN += 4

        print(t_new)
        p_new = np.array(p_new)
        t_new = np.array(t_new)
        u_new = np.array(u_new)

        return p_new, t_new, u_new


def PlotMeshNumbers(p, t, edges=[], pltshow=True):
    """
    PlotMeshNumbers(p,t,edges=[],pltshow=True)
    ---------------
    p   :  points of the triangular mesh
    t   :  elements of the mesh (first order 3 numbers, second order 6 numbers)
    """

    plt.triplot(p[:, 0], p[:, 1], t[:, 0:3])
    # annotate nodes
    for i in range(len(p)):
        buf = "%i" % (i)
        x = p[i, 0]
        y = p[i, 1]
        plt.plot(x, y, "ok", markersize=5)
        plt.text(x, y, buf, color="r", fontsize=13)

    # annotate elements
    for n in range(len(t)):
        buf = "%i" % (n)
        ps = (p[t[n, 0], :] + p[t[n, 1], :] + p[t[n, 2], :]) / 3.0
        plt.text(ps[0], ps[1], buf, color="b", fontsize=9)

    if edges != []:
        for n in range(len(edges)):
            buf = "%i" % (n)
            ps = (p[edges[n][0], :] + p[edges[n][1], :]) / 2.0
            plt.text(ps[0], ps[1], buf, color="g", fontsize=11)

    if pltshow == True:
        plt.show()


# only for a small number of triangles fast enough
def PlotSurfaceMesh(p, t, color="b"):
    ae, b, be = FindEdges(t)
    fig = plt.figure()
    ax = Axes3D(fig)
    for x in ae:
        P1 = p[x[0]]
        P2 = p[x[1]]
        X = np.array([P1[0], P2[0]])
        Y = np.array([P1[1], P2[1]])
        Z = np.array([P1[2], P2[2]])
        ax.plot(X, Y, Z, color)
    plt.show()
    return


# btype can be 'Nodes' or 'Segments'
#
def PlotBoundary(p, boundary, btype):
    """
    PlotBoundary(p,boundary,btype)
    ------------------------------
    plot a segment curve, a node curve, or a line graph
    boundary :  list of edges or nodes to be plotted
    btype    :  string of curve type ('Segments', 'Nodes', 'Curve')
    """

    bound = np.array(boundary)
    if btype == "Nodes":
        X = p[bound, 0]
        Y = p[bound, 1]
        plt.plot(X, Y, "bo")
    elif btype == "Lines":
        X = p[bound, 0]
        Y = p[bound, 1]
        plt.plot(X, Y, "-og")
    else:
        for b in bound:
            P1 = p[b[0], :]
            P2 = p[b[1], :]
            if btype == "Segments":
                farbe = "r"

                plt.plot([P1[0], P2[0]], [P1[1], P2[1]], farbe, lw=1)
                # arrows at segments
                dX = P2 - P1
                ls = np.sqrt(np.sum(dX**2))
                v1 = [-dX[0] - dX[1], dX[0] - dX[1]]
                av1 = np.sqrt(v1[0] ** 2 + v1[1] ** 2)
                v1 = v1 / av1 * ls / 2
                v2 = [dX[1] - dX[0], -dX[0] - dX[1]]
                av2 = np.sqrt(v2[0] ** 2 + v2[1] ** 2)
                v2 = v2 / av2 * ls / 2
                pm = (P1 + P2) / 2.0
                xx = [pm[0] + v1[0], pm[0], pm[0] + v2[0]]
                yy = [pm[1] + v1[1], pm[1], pm[1] + v2[1]]
                plt.plot(xx, yy, "y")
            else:
                farbe = "g"
                plt.plot([P1[0], P2[0]], [P1[1], P2[1]], farbe)

    # plt.show()


def MakeSurfaceMesh(xstr, ystr, zstr, u0, u1, v0, v1, n1, n2):

    eps = 1e-13

    all_u = np.linspace(u0, u1, n1)
    all_v = np.linspace(v0, v1, n2)

    # make u-v boundary for desired mesh
    uv_bound = [[all_u[i], all_v[0]] for i in range(n1)]
    uv_bound += [[all_u[-1], all_v[i]] for i in range(1, n2 - 1)]
    uv_bound += [[all_u[i], all_v[-1]] for i in range(n1)[-1::-1]]
    uv_bound += [[all_u[0], all_v[i]] for i in range(1, n2 - 1)[-1::-1]]

    max_len = max([np.max(np.diff(all_u)), np.max(np.diff(all_v))])

    # make mesh
    uv_points = np.array([x for x in uv_bound + [uv_bound[0]]])
    p1, v1 = PointSegments(uv_points)
    p_uv, elements, bou, li_bou = DoTriMesh(p1, v1, edge_length=max_len, show=False)

    # PlotMeshNumbers(p_uv,elements)

    # sort boundary points
    UVs = [[u0, v0], [u0, v0]]
    bseg = RetrieveSegments(p_uv, bou, li_bou, UVs, ["Nodes"])[0]
    bseg = np.sort(bseg)
    N = len(bseg)

    if N != len(uv_bound):
        print(
            "WARNING: Additional boundary points inserted by triangle.c (du too different from dv)"
        )

    # calculate boundary points of 3D surface mesh
    bound_p = np.zeros((N, 3))
    for i in bseg:
        u = p_uv[i, 0]
        v = p_uv[i, 1]
        p = np.array([eval(xstr), eval(ystr), eval(zstr)])
        bound_p[i, :] = p

    # check for identical points on boundary
    NN = len(p_uv)
    identical_nodes = []
    table_nodes = np.arange(NN)
    for i in range(N):
        id = ()
        for j in range(i + 1, N):
            # check if points are the same
            if (
                bseg[j] >= 0
                and bseg[i] >= 0
                and np.sum((bound_p[i, :] - bound_p[j, :]) ** 2) < eps
            ):
                id += (bseg[j],)
                # mark already identified nodes
                table_nodes[bseg[j]] = -1
                bseg[j] = -1

        if len(id) != 0:
            id += (bseg[i],)
            identical_nodes += [id[-1::-1]]

    # delete all identical nodes
    table_nodes = table_nodes[table_nodes >= 0]

    # calculate 3D points from uv points
    all_p = np.zeros((NN, 3))
    for i in range(NN):
        u = p_uv[i, 0]
        v = p_uv[i, 1]
        p = np.array([eval(xstr), eval(ystr), eval(zstr)])
        all_p[i, :] = p

    # final correspondace table
    final_table = np.arange(NN)
    # rename the nodes
    table_nodes = list(table_nodes)
    for j in table_nodes:
        final_table[j] = table_nodes.index(j)

    # rename identical nodes
    del_nodes = []
    for x in identical_nodes:
        for j in x[1::]:
            final_table[j] = final_table[x[0]]
            del_nodes += [j]

    # delete identical nodes
    del_nodes = np.sort(del_nodes)[-1::-1]
    for j in del_nodes:
        all_p = np.delete(all_p, j, axis=0)

    # rename nodes in elements
    elements = np.array(elements).flatten()
    elements = final_table[elements].reshape(-1, 3)

    elements = np.array([list(x) for x in elements if len(set(x)) == 3])

    # mal.triangular_mesh(all_p[:,0],all_p[:,1],all_p[:,2],elements)
    # mal.show()
    return all_p, elements
    # PlotSurfaceMesh(all_p,elements,color='b')
    # plt.show()


def MakeSphere(P0, R, mesh_len, epsilon=1e-8, type="cart"):

    if type == "cart":

        # make part of the sphere
        xstr = "%g*np.cos(u)*np.sin(v)" % (R)
        ystr = "%g*np.sin(u)*np.sin(v)" % (R)
        zstr = "%g*np.cos(v)" % (R)
        Nu = int(2 * np.pi * R / mesh_len)
        pp, tt = MakeSurfaceMesh(
            xstr, ystr, zstr, 0, 2 * np.pi, np.pi / 4.0, np.pi / 2.0, Nu, int(Nu / 3.0)
        )
        edges, bou, bel = FindEdges(tt)

        # add upper part
        ubou = []
        # count number of points on upper circle
        for x in bou:
            if pp[x[0], 2] > R / 10.0:
                ubou += [x]
        # use upper segments for new 2D circle
        ubou, bl = SortSegments(ubou)
        p2 = []
        v2 = []
        for j, x in enumerate(ubou):
            p2 += [(pp[x[0], 0], pp[x[0], 1])]
            if j == (len(ubou) - 1):
                j2 = 0
            else:
                j2 = j + 1
            v2 += [(j, j2)]

        # make circle mesh and lift up the z values
        ppp, ttt, bouu, li = DoTriMesh(p2, v2, edge_length=mesh_len, show=False)

        ppp = np.append(ppp, np.ones((len(ppp), 1)) * -1, axis=1)
        for i in range(len(ppp)):
            ppp[i, 2] = np.sqrt(R**2 - ppp[i, 0] ** 2 - ppp[i, 1] ** 2)

        # connect upper sphere and lower sphere
        bou = [[x[0], x[1]] for x in bou]
        p, t, b, bl, idn = ConnectMesh(pp, tt, bou, ppp, ttt, bouu, epsilon=1e-8)
        pp = p * 1
        for i in range(len(pp)):
            pp[i, 2] *= -1

        # connect lower half circle
        tt = [[x[1], x[0], x[2]] for x in t]
        bb = np.copy(b)
        pn, tn, bn, bln, idn = ConnectMesh(pp, tt, bb, p, t, b, epsilon=1e-8)

    else:
        # make part of the sphere
        xstr = "%g*np.cos(u)*np.sin(v)" % (R)
        ystr = "%g*np.sin(u)*np.sin(v)" % (R)
        zstr = "%g*np.cos(v)" % (R)
        Nu = int(2.0 * np.pi * R / mesh_len)
        pn, tn = MakeSurfaceMesh(
            xstr, ystr, zstr, 0, 2.0 * np.pi, 0, np.pi, Nu, int(Nu / 3.0)
        )
        edges, bou, bel = FindEdges(tn)

    Ps = np.array(P0)
    pn = np.array([X - Ps for X in pn])
    bou = []
    return pn, tn, bou


# Connect two different meshes at their overlapping boundary
def ConnectMesh(p1, t1, b1, p2, t2, b2, epsilon=1e-8):

    # find identical nodes on boundary
    # find correspondence between boundary nodes on boundary 1 and 2
    bb2 = [x[0] for x in b2]
    eps = epsilon**2
    id_nodes = []
    for seg in b1:
        X = p1[seg[0], :]
        for i, node2 in enumerate(bb2):
            Y = p2[node2, :]
            delta = np.sum((X - Y) ** 2)
            if delta < eps:
                id_nodes += [(seg[0], node2)]
                # print(X,Y)
                bb2.pop(i)

    # make list with all mesh 2 nodes for renumbering
    node2_table = np.arange(len(p2))
    tab = node2_table * 0 - 1
    id_b2 = [x[1] for x in id_nodes]
    node2_table = np.delete(node2_table, id_b2)
    for i, x in enumerate(node2_table):
        tab[x] = i + len(p1)
    # replace boundary nodes
    for x in id_nodes:
        tab[x[1]] = x[0]

    # delete identical nodes in p2
    idn2 = [x[1] for x in id_nodes]
    p2 = np.delete(p2, idn2, axis=0)

    # renumber in element list
    ptot = np.append(p1, p2, axis=0)
    for i in range(len(t2)):
        t2[i, :] = [tab[t2[i, 0]], tab[t2[i, 1]], tab[t2[i, 2]]]
    ttot = np.append(t1, t2, axis=0)

    # find new boundary
    idn1 = [x[0] for x in id_nodes]
    boundary1 = [x for x in b1 if not (idn1.count(x[0]) == 1 and idn1.count(x[1]) == 1)]
    boundary2 = [
        [tab[x[0]], tab[x[1]]]
        for x in b2
        if not (idn2.count(x[0]) == 1 and idn2.count(x[1]) == 1)
    ]

    boundary = np.append(boundary1, boundary2).reshape(-1, 2)

    boundary = [tuple(x) for x in boundary]
    btot, blist = SortSegments(boundary)
    blist += [len(btot)]
    # boundary=mt.CheckSegmentSense(ttot,bound,blist)

    print("identical nodes found", len(id_nodes))
    return ptot, ttot, btot, blist, id_nodes


# NoSe is a list containing the type of boundary 'Nodes' or 'Segments'
# points : mesh points
#
def RetrieveSegments(points, segments, curve_list, Ps, NoSe):
    """
    all = RetrieveSegments(points,segments,curve_list,Ps,NoSe)
    ------------------
    points     : all points of the mesh
    segments   : All edges used for search
    curve_list : List associated with segments
    Ps         : List of points.
                 Consecutive Points form start and endpoint of path lying in segments.
                 If there is no connection in segments the path is skipped
    NoSe       : List of strings defining type of path found ('Nodes' or 'Segments')
    """

    # extract first and second row from segment list
    row1 = list(np.array(segments)[:, 0])
    row2 = list(np.array(segments)[:, 1])
    # for second order
    if len(segments[0]) == 3:
        row3 = list(np.array(segments)[:, 2])
    else:
        row3 = []

    # find node indices for desired points
    bnodes = list(set(row1 + row2))
    nn, dd = FindClosestNode(bnodes, points, Ps)

    # print("Ps = ",Ps)
    # print("Nodes: ",nn)
    # print("error ",dd)

    # make different segments
    ret = []
    this_type = 0

    for k in range(len(Ps) - 1):
        Orient = False
        try:
            first = row1.index(nn[k])
            last = row2.index(nn[k + 1])
        except:
            try:
                first = row1.index(nn[k + 1])
                last = row2.index(nn[k])
                Orient = True
            except:
                # only possible if: last_bnr!=first_bnr
                try:
                    first = row1.index(nn[k + 1])
                    last = row1.index(nn[k])
                except:
                    first = row2.index(nn[k + 1])
                    last = row2.index(nn[k])

        # look for the number of boundary
        for j in range(len(curve_list) - 1):
            if curve_list[j] <= first < curve_list[j + 1]:
                first_bnr = j
            if curve_list[j] <= last < curve_list[j + 1]:
                last_bnr = j

        # both points are on the same boundary
        if last_bnr == first_bnr:
            # nodes
            # print("1. node  , 2. node ",nn[k],nn[k+1])
            # print("boundaries ",last_bnr,first_bnr)
            # print("this_type = ",this_type)
            if this_type >= len(NoSe):
                print(
                    "Error (this_type=%g , len(NoSe)=%g):  Increase  Nodes/Segments List"
                    % (this_type, len(NoSe))
                )
            if NoSe[this_type] == "Nodes":

                if first < last:
                    add = row1[first : last + 1]
                    add += row3[first : last + 1]
                else:
                    add = (
                        row1[first : curve_list[first_bnr + 1] :]
                        + row1[curve_list[first_bnr] : last + 1]
                    )
                    add += (
                        row3[first : curve_list[first_bnr + 1] :]
                        + row3[curve_list[first_bnr] : last + 1]
                    )
                # line not closed
                if nn[k] != nn[k + 1]:
                    add += [row2[last]]
            # segments
            else:

                if first < last:
                    add = segments[first : last + 1]
                else:
                    add = (
                        segments[first : curve_list[first_bnr + 1] :]
                        + segments[curve_list[first_bnr] : last + 1]
                    )

                if Orient == True:
                    add = [x[-1::-1] for x in add[-1::-1]]

            ret += [add]
            this_type += 1

    return ret


# find all points of the triangulation which are element of
# curve, given by a function call
def FindCurveSegments(points, t, func, inner_p=[]):

    ret = []
    for i, X in enumerate(points):
        yn = func(X)
        if yn == True:
            ret += [i]

    if ret == []:
        print("WARNING: No nodes found on given Curve func", func)
        return [], []
    else:
        print(len(ret), " Nodes found on inner curve")

    # construct edges
    t_all = np.array([t[:, 0], t[:, 1], t[:, 1], t[:, 2], t[:, 2], t[:, 0]]).T
    tt = t_all.reshape(3 * len(t), 2)
    all_edges = [tuple(x) for x in tt]
    # all unique edges
    all_edges = list(set(all_edges))

    nodes = ret[:]
    seg = []
    # find the segments to the node list
    for k in range(len(ret)):
        for y in all_edges:
            if (y[0] == ret[k] and y[1] in ret) or (y[1] == ret[k] and y[0] in ret):
                z = tuple(sorted(y))
                seg += [z]

    # make list unique
    seg = list(set(seg))

    # each node should be connected to other nodes not more than twice
    occ = [x[0] for x in seg] + [x[1] for x in seg]
    occ = Counter(occ)
    for x in occ:
        if occ[x] > 2:
            multiple = [y for y in seg if x in y]
            for z in multiple:
                pm = (points[z[0], :] + points[z[1], :]) / 2.0
                if not func(pm):
                    seg.remove(z)
                    occ[z[0]] -= 1
                    occ[z[1]] -= 1

    # sort list
    sseg, ls = SortSegments(seg)
    ls += [len(sseg)]
    if len(ls) > 2:
        print(len(ls) - 1, "different curves found")

    seg = [list(y) for y in sseg]

    # give segments a direction in 2D if desired,
    if len(points[0]) == 2 and inner_p != []:
        for n in range(len(ls) - 1):
            i1 = ls[n]
            i2 = ls[n + 1]
            # look for closest segment to inner point
            this_seg = seg[i1:i2]
            first_nodes = np.array(this_seg)[:, 0]
            # check first forclosest node
            tot_dist = []
            indices = []
            for pp in inner_p:
                i_p = np.array(pp)
                square_dist = np.sum((points[first_nodes, :] - i_p) ** 2, axis=1)
                jj = np.argsort(square_dist)[0]
                tot_dist += [square_dist[jj]]
                indices += [jj]
            nn = np.argsort(np.array(tot_dist))[0]
            jj = indices[nn]
            i_p = inner_p[nn]
            # closest segment at position jj
            n1 = this_seg[jj][0]
            n2 = this_seg[jj][1]
            dX = points[n2, :] - points[n1, :]
            dY = i_p - points[n1, :]
            # check orientation
            if np.cross(dX, dY) < 0:
                this_seg = [[x[1], x[0]] for x in this_seg[-1::-1]]
                seg[i1:i2] = this_seg
                print("change direction around", i_p)

    return nodes, seg, ls


# find the nodes or segements between two points P1, P2
# btype is Nodes or Segments
##########################################
# --> ZU LANGSAM RETRIEVEBOUNDARY nutzen
##########################################
def FindBoundary(p, t, P1, P2, btype):

    # find boundary
    kanten, rand_seg, rand_elemente = FindEdges(t)
    # connect boundary according to P1
    rand_seg, rand_list, P1_boundary = ConnectBoundary(
        rand_seg, p, pstart=[(P1[0], P1[1])]
    )
    # search for node at position P2
    index_start = rand_list[P1_boundary]
    if P1_boundary == len(rand_list) - 1:
        index_end = rand_seg.shape[0]
    else:
        index_end = rand_list[P1_boundary + 1]

    # print("index_start",index_start)
    # print("index_end",index_end)

    rand_seg = rand_seg[index_start:index_end]

    # print("rand_seg",rand_seg)

    NR = rand_seg.shape[0]
    vec = np.array(P2) - p[rand_seg[0, 1], :]
    this_min = np.dot(vec, vec)
    last_seg = 0
    for k in range(1, NR, 1):
        Pt = p[rand_seg[k, 1]]
        vec = Pt - P2
        this_prod = np.dot(vec, vec)
        if this_prod < this_min:
            this_min = this_prod
            last_seg = k

    # make boundary segments between P1 and P2
    result = np.array([rand_seg[0]])
    for k in range(1, last_seg + 1):
        result = np.insert(result, result.shape[0], rand_seg[k], axis=0)

    # define nodes if necessary
    if btype == "Nodes":
        last_node = result[result.shape[0] - 1, 1]
        result = result[:, 0]
        # not a closed boundary
        if result[0] != last_node:
            result = np.append(result, last_node)

    # print("Erster Punkt:",p[result[0],:])
    return result


# sort a list of edges (with elemental number) along a path
# [[40, (4, 8)], [90, (12, 17)], [40, (2, 4)], [8, (4, 8)], [90, (8, 12)], [8, (8, 12)]]
# -->
# [[90, (12, 17)], [90, (8, 12)], [8, (8, 12)], [8, (4, 8)], [40, (4, 8)], [40, (2, 4)]]
# not connected pathes are possible
def SortEdgeList(folly):

    fol = [[x[0], tuple(sorted(x[1]))] for x in folly]

    index = -1
    new_fol = []
    isolist = []
    while index < 0:
        # find start element (boundary element or first element of list)
        isolist.append(len(new_fol))
        index = 0
        edges = [x[1] for x in fol]
        for k, x in enumerate(edges):
            if edges.count(x) == 1:
                index = k
                break

        # start sorting
        new_fol.append(fol[index])
        del fol[index]
        while len(fol) > 0:
            # find index of next list element
            index = -1
            for k, y in enumerate(fol):
                if (new_fol[-1][0] == y[0]) | (new_fol[-1][1] == y[1]):
                    index = k
                    break
            if index < 0:
                break

            # add to new list and delete old list element
            new_fol.append(fol[index])
            del fol[index]

    return new_fol, isolist


def ContourSurface(p, t, u, iso_in, infig):

    # make iso values
    if isinstance(iso_in, int) == True:
        isolines = np.linspace(min(u), max(u), iso_in)
        print("isolines", isolines)
    else:
        isolines = iso_in

    # make all edges
    NE = len(t)
    all_edges = np.array([[x[0], x[1], x[1], x[2], x[2], x[0]] for x in t])
    all_edges = np.resize(all_edges, (3 * NE, 2))
    for iso in isolines:
        # find the edges and elements with an isoline with value iso
        iso_edges = [
            [i // 3, tuple(x)]
            for i, x in enumerate(all_edges)
            if min(u[x]) <= iso <= max(u[x])
        ]

        if len(iso_edges) > 1:
            iso_edges, nis = SortEdgeList(iso_edges)
            # add end of list for slicing
            nis.append(len(iso_edges))
            # run through all the non-connected isolines
            for k in range(len(nis) - 1):
                hhelp = iso_edges[nis[k] : nis[k + 1]]
                # take only each second point
                unique_ie = [hhelp[0]] + hhelp[1:-1:2] + [hhelp[-1]]

                # Compute polygon for this iso curve
                X = Y = Z = []
                for x in unique_ie:
                    i1 = x[1][0]
                    i2 = x[1][1]
                    t = (iso - u[i1]) / (u[i2] - u[i1])
                    P = p[i1] + t * (p[i2] - p[i1])
                    X = np.append(X, P[0])
                    Y = np.append(Y, P[1])
                    Z = np.append(Z, P[2])

                mal.plot3d(
                    X,
                    Y,
                    Z,
                    tube_radius=None,
                    figure=infig,
                    color=(0.2, 0.2, 0.2),
                    line_width=5,
                )

    return


#
#
#
#
def ComputeGradient(p, t, u, poi=[], num=10):
    """
    Compute the Gradient of a triangular mesh

    Input:   p    array([[x1,y1],[x2,y2],...])          node points
             t    array([[n1,n2,n3],[n4,n5,n6],...])    elements
             u    array([u1,u2,u3,.....])               function at node values
             poi  array([[X1,Y1],[X2,Y2],...])          points for gradient evaluation
             num  N                                     generate NxN points array poi

    Output:  x     x-component of point
             y     y-component of point
             g_x   gradient, x-component at (x,y)
             g_y   gradient, y-component at (x,y)
    """

    if poi == []:
        eps = 1e-6
        h1 = np.linspace(min(p[:, 0]) + eps, max(p[:, 0]) - eps, num)
        h2 = np.linspace(min(p[:, 1]) + eps, max(p[:, 1]) - eps, num)
        h1, h2 = np.meshgrid(h1, h2)
        h1.resize(num * num, 1)
        h2.resize(num * num, 1)
        points = np.append(h1, h2, axis=1)
    else:
        points = poi

    # Compute all a,b,c
    a1 = p[t[:, 1], 0] * p[t[:, 2], 1] - p[t[:, 1], 1] * p[t[:, 2], 0]
    a2 = p[t[:, 2], 0] * p[t[:, 0], 1] - p[t[:, 2], 1] * p[t[:, 0], 0]
    b1 = p[t[:, 1], 1] - p[t[:, 2], 1]
    b2 = p[t[:, 2], 1] - p[t[:, 0], 1]
    c1 = p[t[:, 2], 0] - p[t[:, 1], 0]
    c2 = p[t[:, 0], 0] - p[t[:, 2], 0]

    delta = 0.5 * (b1 * c2 - b2 * c1)

    XYUV = np.array([])
    for x in points:
        x = np.array(x)
        ksi = 0.5 / delta * (a1 + b1 * x[0] + c1 * x[1])
        eta = 0.5 / delta * (a2 + b2 * x[0] + c2 * x[1])

        element = np.where((ksi >= 0) & (eta >= 0) & (eta + ksi - 1 <= 0))[0]

        if len(element) > 0:
            element = element[0]

            bb1 = b1[element]
            bb2 = b2[element]
            bb3 = p[t[element, 0], 1] - p[t[element, 1], 1]

            cc1 = c1[element]
            cc2 = c2[element]
            cc3 = p[t[element, 1], 0] - p[t[element, 0], 0]

            dd = delta[element]

            u1 = u[t[element, 0]]
            u2 = u[t[element, 1]]
            u3 = u[t[element, 2]]

            gx = 0.5 / dd * (bb1 * u1 + bb2 * u2 + bb3 * u3)
            gy = 0.5 / dd * (cc1 * u1 + cc2 * u2 + cc3 * u3)

            help = np.append(x, np.array([gx, gy]))
            XYUV = np.append(XYUV, help)

    XYUV.resize(len(XYUV) // 4, 4)
    return XYUV[:, 0], XYUV[:, 1], XYUV[:, 2], XYUV[:, 3]


# For a given boundary segment Seg the corresponding boundary element is found. A list of
# all boundary elements must be provided
def FindBoundaryElement(t, Seg, BoundE):
    for i in range(len(BoundE)):
        # check main nodes
        if len(set(t[BoundE[i], 0:3]).intersection(Seg[0:2])) == 2:
            # print("Boundary Segment ",Seg,"  Boundary Element ",t[BoundE[i]])
            # sort in a way that the first two indices are boundary indices
            # main indices first
            ThirdIndex = list(set(t[BoundE[i], 0:3]) - set(Seg[0:2]))[0]
            dbllist = list(t[BoundE[i], 0:3]) * 2
            kk = 1 + dbllist.index(ThirdIndex)
            MainIndices = dbllist[kk : kk + 3]
            # middle indices next
            if len(Seg) == 3:
                dbllist = list(t[BoundE[i], 3:]) * 2
                kk = dbllist.index(Seg[2])
                RestIndices = dbllist[kk : kk + 3]
            else:
                RestIndices = []
            # print("Segment: ",Seg,"  Element: ---> ",MainIndices+RestIndices)
            return MainIndices + RestIndices


# Compute the normal derivative along the segments in boundary
#
def NormalDerivative(boundary, p, tt, u, inner=None, BouE=[]):
    """
    Compute the normal derivative on a given boundary

    Input:   boundary   [[n1,n2],[n3,n4],...]          boundary segments
             p    array([[x1,y1],[x2,y2],...])         node points
             t    array([[n1,n2,n3],[n4,n5,n6],...])   elements
             u    array([u1,u2,u3,.....])              function at node values
             right                                     direction of inner node/element

    Output:  nor       normal derivative at the segments
             rl        running length
             line_int  line integral over boundary of the normal derivative
    """

    # second order

    if len(boundary[0]) == 3:

        if BouE == []:
            edges, segments, BouE = FindEdges(tt)

        nor = []
        rl = []
        line_int = 0
        for seg in boundary:
            # find boundary element, third index is the volume index
            b_elem = FindBoundaryElement(tt, seg, BouE)

            xM, yM = p[b_elem[3]]

            X1 = p[b_elem[0]]
            X2 = p[b_elem[1]]
            X3 = p[b_elem[2]]
            ls = np.sqrt(np.sum((X2 - X1) ** 2))

            b_1 = X2[1] - X3[1]
            b_2 = X3[1] - X1[1]
            b_3 = X1[1] - X2[1]
            c_1 = X3[0] - X2[0]
            c_2 = X1[0] - X3[0]
            c_3 = X2[0] - X1[0]

            a_1 = X2[0] * X3[1] - X3[0] * X2[1]
            a_2 = X3[0] * X1[1] - X1[0] * X3[1]
            a_3 = X1[0] * X2[1] - X2[0] * X1[1]

            delta = 0.5 * (b_1 * c_2 - c_1 * b_2)
            delsq = delta**2

            Phi_1, Phi_2, Phi_3, Phi_4, Phi_5, Phi_6 = u[b_elem]

            b12 = b_1 * b_2
            b13 = b_1 * b_3
            b23 = b_2 * b_3
            b11 = b_1**2
            b22 = b_2**2
            b33 = b_3**2
            c12 = c_1 * c_2
            c13 = c_1 * c_3
            c23 = c_2 * c_3
            c11 = c_1**2
            c22 = c_2**2
            c33 = c_3**2

            Qseq = [0, 0, 0, 0, 0, 0]
            Qseq[0] = (b13 + c13) * (0.5 * delta - a_1 - b_1 * xM - c_1 * yM) / delsq
            Qseq[1] = (b23 + c23) * (0.5 * delta - a_2 - b_2 * xM - c_2 * yM) / delsq
            Qseq[2] = (b33 + c33) * (0.5 * delta - a_3 - b_3 * xM - c_3 * yM) / delsq
            Qseq[3] = (
                -(
                    a_1 * b23
                    + a_1 * c23
                    + a_2 * b13
                    + a_2 * c13
                    + 2 * b12 * b_3 * xM
                    + b13 * c_2 * yM
                    + b_1 * c23 * xM
                    + b23 * c_1 * yM
                    + b_2 * c13 * xM
                    + 2 * c12 * c_3 * yM
                )
                / delsq
            )
            Qseq[4] = (
                -(
                    a_2 * b33
                    + a_2 * c33
                    + a_3 * b23
                    + a_3 * c23
                    + 2 * b_2 * b33 * xM
                    + b23 * c_3 * yM
                    + b_2 * c33 * xM
                    + b33 * c_2 * yM
                    + b_3 * c23 * xM
                    + 2 * c_2 * c33 * yM
                )
                / delsq
            )
            Qseq[5] = (
                -(
                    a_1 * b33
                    + a_1 * c33
                    + a_3 * b13
                    + a_3 * c13
                    + 2 * b_1 * b33 * xM
                    + b13 * c_3 * yM
                    + b_1 * c33 * xM
                    + b33 * c_1 * yM
                    + b_3 * c13 * xM
                    + 2 * c_1 * c33 * yM
                )
                / delsq
            )

            density = (
                Qseq[0] * Phi_1
                + Qseq[1] * Phi_2
                + Qseq[2] * Phi_3
                + Qseq[3] * Phi_4
                + Qseq[4] * Phi_5
                + Qseq[5] * Phi_6
            )
            line_int += density

            nor += [density / ls]
            rl += [ls]

        # add all segment length
        for i in range(1, len(rl)):
            rl[i] += rl[i - 1]
        rl = np.array(rl) - rl[0]

        return np.array(nor), np.array(rl), line_int
    elif len(boundary[0]) == 2 and inner == None:

        if BouE == []:
            edges, segments, BouE = FindEdges(tt)

        nor = []
        rl = []
        line_int = 0
        for seg in boundary:
            # find boundary element, third index is the volume index
            b_elem = FindBoundaryElement(tt, seg, BouE)

            X1 = p[b_elem[0]]
            X2 = p[b_elem[1]]
            X3 = p[b_elem[2]]
            ls = np.sqrt(np.sum((X2 - X1) ** 2))

            b_1 = X2[1] - X3[1]
            b_2 = X3[1] - X1[1]
            b_3 = X1[1] - X2[1]
            c_1 = X3[0] - X2[0]
            c_2 = X1[0] - X3[0]
            c_3 = X2[0] - X1[0]

            delta = 0.5 * (b_1 * c_2 - c_1 * b_2)

            Phi_1, Phi_2, Phi_3 = u[b_elem]

            bb = 0.5 / delta * (b_1 * Phi_1 + b_2 * Phi_2 + b_3 * Phi_3)
            cc = 0.5 / delta * (c_1 * Phi_1 + c_2 * Phi_2 + c_3 * Phi_3)

            density = -bb * b_3 - cc * c_3
            line_int += density

            nor += [density / ls]
            rl += [ls]

        # add all segment length
        for i in range(1, len(rl)):
            rl[i] += rl[i - 1]
        rl = np.array(rl) - rl[0]

        return np.array(nor), np.array(rl), line_int

    # first order, older code --> needs update

    # step through all segments
    nor = []
    rl = [0]
    line_int = 0

    # make list of edges
    edges = []
    index_3 = []
    for lt in tt:
        edges += [set([lt[0], lt[1]])]
        index_3 += [lt[2]]
        edges += [set([lt[1], lt[2]])]
        index_3 += [lt[0]]
        edges += [set([lt[0], lt[2]])]
        index_3 += [lt[1]]

    for s in boundary:

        # seg=np.array(s)
        # no_el=[(np.setxor1d(tt[j],seg)[0],j) for j in range(len(tt)) if len(np.setxor1d(tt[j],seg))==1]

        # search for element containing segment s, save third index and element number
        so_seg = set(s)
        no_el = []
        for j in range(len(edges)):
            if so_seg == edges[j]:
                no_el += [(index_3[j], j // 3)]
                if len(no_el) == 2:
                    break

        # for inner curves the element has to be determined. Inner='right'
        # means that the element is on the right side of the oriented curve
        # print("s,node",seg,no_el,tt[no_el[0][1]],tt[no_el[1][1]])
        v1 = p[s[1], :] - p[s[0], :]
        normal_x = v1[1]
        normal_y = -v1[0]

        if len(no_el) == 2:
            v2 = p[no_el[0][0], :] - p[s[0], :]
            he = v1[0] * v2[1] - v1[1] * v2[0]
            if (he < 0 and inner == "right") or (he > 0 and inner == "left"):
                n = tt[no_el[0][1], :]
            else:
                n = tt[no_el[1][1], :]

            if inner == "right":
                normal_x *= -1
                normal_y *= -1
            # plt.plot([(p[n[0],0]+p[n[1],0]+p[n[2],0])/3],[(p[n[0],1]+p[n[1],1]+p[n[2],1])/3],'x')
        else:
            n = [no_el[0][0], s[0], s[1]]

        # local node 1 is always in the volume
        # print("normal",normal_x,normal_y)
        Ls = np.sqrt(normal_x**2 + normal_y**2)

        b1 = p[n[1], 1] - p[n[2], 1]
        b2 = p[n[2], 1] - p[n[0], 1]
        b3 = p[n[0], 1] - p[n[1], 1]

        c1 = p[n[2], 0] - p[n[1], 0]
        c2 = p[n[0], 0] - p[n[2], 0]
        c3 = p[n[1], 0] - p[n[0], 0]

        delta = 0.5 * (b1 * c2 - c1 * b2)

        u1 = u[n[0]]
        u2 = u[n[1]]
        u3 = u[n[2]]

        phi_x = b1 * u1 + b2 * u2 + b3 * u3
        phi_y = c1 * u1 + c2 * u2 + c3 * u3

        # print("Gradient",phi_x,phi_y)

        dudn = 0.5 / Ls / delta
        dudn *= phi_x * normal_x + phi_y * normal_y
        # print("dudn",dudn)

        line_int += Ls * dudn

        rl = np.append(rl, rl[-1] + Ls)
        nor = np.append(nor, dudn)

    # PlotBoundary(p,boundary,'Segments')
    # plt.triplot(p[:,0],p[:,1],tt)
    # plt.show()
    # remove last length as rl starts with 0
    rl = np.delete(rl, len(rl) - 1)

    return nor, rl, line_int


def GetPosition(allnodes, node):
    """
    Find the position of the nodes in array node in the array allnodes

    Input:   allnodes   array([n1,n2,n3,...])        array of nodes
             node       array([nn1,nn2,....])        array of nodes

    Output:  pos       array([pos_of_nn1,pos_of_nn2,...])
    """
    pos = np.array([np.where(allnodes == x)[0][0] for x in node])
    return pos


#
# Check orientation
#
def TriOrientation(p, t):
    """
    Check Orientation of a triangulation, flip if necessary
    """
    for m in range(len(t)):
        p1 = np.array(p[t[m, 0]])
        p2 = np.array(
            [
                t[m, 0],
            ]
        )
        p3 = np.array(
            p[
                t[m, 0],
            ]
        )
        if np.cross(p2 - p1, p3 - p1) < 0:
            t[m] = [t[m, 0], t[m, 2], t[m, 1]]
            print("flip ", m, " element")
    return p, t


# Extract the edges
# ouput, edges and boundary edges and boundary_elements
def FindEdges(t):
    """
    Find all edges of a given triangulation

    Input:   t    array([[n1,n2,n3],[n4,n5,n6],...])   elements

    Output:  all_edges
             boundary_edges
             boundary_elements
    """
    # pdb.set_trace();
    NE = t.shape[0]
    # generate an array of all edges
    tall = np.array([t[:, 0], t[:, 1], t[:, 1], t[:, 2], t[:, 2], t[:, 0]]).T
    tt = tall.reshape(3 * NE, 2)
    ttt = np.sort(tt, 1)

    # find all boundary edges
    all_edges = [tuple(x) for x in ttt]
    boundary_edges = []
    boundary_elements = []
    for i, x in enumerate(all_edges):
        if all_edges.count(x) == 1:
            row = i // 3
            col = 2 * (i % 3)
            boundary_edges.append(tuple(tall[row, col : col + 2]))
            boundary_elements.append(row)

    # find all unique edges
    all_edges = list(set(all_edges))
    boundary_elements = np.array(boundary_elements)
    return all_edges, boundary_edges, boundary_elements


##################
#
#  Boundary Tools
#
##################

# check the sense of the numbering in the segments
def CheckSegmentSense(t, boundary, indices):

    new_bound = []
    for k, pos in enumerate(indices):
        first = set(boundary[pos])
        boundary_element = [x for x in t if first.issubset(set(x))]
        x = boundary_element[0]
        if first == set([x[0], x[2]]):
            first = [x[2], x[0], x[1]]
        elif first == set([x[1], x[2]]):
            first = [x[1], x[2], x[0]]
        else:
            first = x
        # change sense

        if k == len(indices) - 1:
            end = len(boundary)
        else:
            end = indices[k + 1]
        this_bound = [list(x) for x in boundary[pos:end]]
        if first[0] != boundary[pos][0]:
            this_bound = [[x[1], x[0]] for x in this_bound[-1::-1]]
            # this_bound=[this_bound[-1]]+this_bound[:-1]

        new_bound += this_bound

    return new_bound


# given one segment
# e.g.  (X,2) find segment (2,Y) and delete (2,Y) from list
def FindNextSegment(all_segments, node):
    """
    Find a segment in a list of segments

    e.g.  node=(X,2) find segment (2,Y) and delete (2,Y) from list all_segments

    Output:  all_segments
             flag for indicating the start of a new boundary
    """
    # find next connecting segment

    help = [x for x in all_segments if x[0] == node or x[1] == node]

    new_bound = False
    if len(help) == 0:  # if connecting segment does not exist (=>new boundary)

        # new code, allow for open segment trajectories
        rest_nodes = [x for t in all_segments for x in t]
        one_occ = [
            [i // 2, x] for i, x in enumerate(rest_nodes) if rest_nodes.count(x) == 1
        ]
        # only closed segments are present
        if one_occ == []:
            ret = all_segments[0]
            del all_segments[all_segments.index(ret)]
        # open lines are present
        else:
            ret = all_segments[one_occ[0][0]]
            del all_segments[all_segments.index(ret)]
            if one_occ[0][1] == ret[1]:
                # print("Change direction of segment",ret)
                ret = ret[-1::-1]

        # old code
        # ret=all_segments[0]
        # del all_segments[all_segments.index(ret)]
        new_bound = True
    else:
        ret = help[0]
        del all_segments[all_segments.index(ret)]
        if ret[0] != node:
            ret = ret[-1::-1]
            # print("Change direction of segment",help[0])

    return ret, new_bound


# sort segments:  (3,6),(6,1),(1,12),(12,5),...
# on output: sorted segments and indices of the different boundaries
def SortSegments(all_segments):
    """
    Sort a list of Segements accordinly [(3,6),(6,1),(1,12),(12,5),...]

    Input:   unsorted list

    Output:  sorted list
             list containing the indices of a new boundary

    see also FindNextSegment
    """
    count = len(all_segments)

    node = -1
    sorted_segments = []
    boundaries = []
    for j in range(len(all_segments)):
        seg, new_bound = FindNextSegment(all_segments, node)
        node = seg[1]
        sorted_segments.append(seg)
        if new_bound == True:
            boundaries.append(j)

    if len(sorted_segments) != count:
        print("Something is wrong, number of segments not the same")
    return sorted_segments, boundaries


# connect segments in a defined way
# (see SortSegments), but start sorting with a defined point p
# multiple p'2 for different closed boundaries are possible
def ConnectBoundary(boundary_segments, Pall, pstart=[]):
    """
    Sort the boundary segments in a defined order

    Input:  boundary_segments   [[n1,n2],[n3,n4],...]           boundary segments
            pstart              array([[x1,y1],[x2,y2],...)     start number of boundary 1 with (x1,y1) ,...
            Pall                array([[X1,X1],[X2,X2],...)     node coordinates

    Output: sorted boundary segments
            start position of boundary segment for new curves
            this_boundary number of boundary for the last point in the list pstart

    see also SortSegments
    """

    # sort the boundary segments
    allseg = boundary_segments[:]
    allseg, boundaries = SortSegments(allseg)
    if pstart == []:
        return allseg, boundaries

    max_boundaries = len(boundaries)

    # find all nodes on the given boundary
    nodes = [x[0] for x in allseg]
    # find closest nodes to desired point list p
    indices, distances = FindClosestNode(nodes, Pall, pstart)
    # print("indices,dist=",indices,distances)
    # print("boundaries",boundaries)
    # print("all_seg",allseg)

    # change order within each closed boundary
    flag_sorted = []
    for j in range(len(boundaries)):
        flag_sorted.append(False)

    for j in range(len(indices)):
        # find position of node in the boundary list
        # indj gives the position of the segment in allseg
        indj = nodes.index(indices[j])
        # find the number of boundary the node belongs to
        this_boundary = (np.where((np.array(boundaries) <= indj))[0])[-1]

        if flag_sorted[this_boundary] == False:
            # define the indices for slicing
            ind_1 = boundaries[this_boundary]
            if this_boundary + 1 == max_boundaries:
                ind_2 = len(allseg)
            else:
                ind_2 = boundaries[this_boundary + 1]

            # rearange the segments in the corresponding boundary
            allseg = (
                allseg[:ind_1]
                + allseg[indj:ind_2]
                + allseg[ind_1:indj]
                + allseg[ind_2:]
            )
            # resort only once
            flag_sorted[this_boundary] = True

    allseg = [[x[0], x[1]] for x in allseg]
    allseg = np.array(allseg)
    # print("Ræckgabe: ",allseg,boundaries)
    return allseg, boundaries, this_boundary


# p0:   points to be mapped
# Pall: all points present in the mesh
# nodes: only these nodes are used for search
# constraint defines constraints on distance
# tree: take a special tree for the search
def FindClosestNode(nodes, Pall, p0, constraint=-1, tree=None):
    """
    nodes,dist = FindClosestNode(nodes,Pall,p0,constraint=-1,tree=None)
    -------
    0:   points to be mapped
    Pall: all points present in the mesh
    nodes: only these nodes are used for search
    constraint defines constraints on distance
    tree: take a special tree for the search
    """
    # take those points of the node list

    # print("len(nodes) ",len(nodes))
    # print("len(Pall) ",len(Pall))
    if tree == None:
        p_nodes = np.array(Pall)
        p_nodes = p_nodes[nodes]
        # look for minimum distance, define dist function
        mytree = cKDTree(p_nodes)
    else:
        mytree = tree

    dist, index = mytree.query(np.array(p0))

    node_closest = [nodes[j] for j in index]

    # check constraints
    num_p = len(p0)
    if constraint < 0:
        return node_closest, dist
    elif np.isscalar(constraint) == True:
        constraint = constraint * np.ones(num_p)
    elif len(p0) != len(constraint):
        print("Error in constraint definition")
        return [], []

    # check constraint for each node
    flags = [((dist[j] <= constraint[j]) | (constraint[j] < 0)) for j in range(num_p)]
    for j in range(num_p):
        if flags[j] == False:
            node_closest[j] = -1
    return node_closest, dist


# check relative position of two points
def SamePoint(p1, p2, delta):
    dp = np.array(p1) - np.array(p2)
    d = np.sqrt(dp[0] ** 2 + dp[1] ** 2)
    ret = False
    if d < delta:
        ret = True
    return ret


#####################
#
# Make simple curves
#
#####################
#
#
#
# make a circle or part of it
#
def CircleSegments(
    middle, radius, num_points=10, a_min=0.0, a_max=2.0 * np.pi, edge_length=-1
):
    """
    CircleSegments(middle,radius,num_points=10,a_min=0.,a_max=2.*np.pi,edge_length=-1)
    """
    # check for closed loop
    number_points = num_points
    if edge_length > 0:
        number_points = int(np.floor(abs(radius / edge_length * (a_max - a_min)))) + 1
        if number_points < 5:
            number_points = 5

    delta = (a_max - a_min) / number_points
    closed = False
    if abs(abs(a_max - a_min) - 2 * np.pi) < 0.1 * abs(delta):
        closed = True

    t = np.linspace(a_min, a_max, number_points, not closed)
    # define points
    points = [
        (middle[0] + radius * np.cos(angle), middle[1] + radius * np.sin(angle))
        for angle in t
    ]

    # define vertices
    vertices = [(j, j + 1) for j in range(0, len(points) - 1, 1)]
    if closed == True:
        vertices += [(len(points) - 1, 0)]
    return points, vertices


# Straight line
def LineSegments(P1, P2, num_points=10, edge_length=-1):
    """
    p,v = LineSegments(P1,P2,num_points=10,edge_length=-1)
    """
    number_points = num_points
    if edge_length > 0:
        p1 = np.array(P1)
        p2 = np.array(P2)
        number_points = int(np.floor(np.sqrt(np.sum((p2 - p1) ** 2)) / edge_length)) + 1
        if number_points <= 1:
            number_points = 5

    t = np.linspace(0, 1, number_points)
    points = [
        (P1[0] + param * (P2[0] - P1[0]), P1[1] + param * (P2[1] - P1[1]))
        for param in t
    ]
    vertices = [(j, j + 1) for j in range(0, len(points) - 1, 1)]
    return points, vertices


# Rectangle
def RectangleSegments(
    P1, P2, num_points=60, edge_length=-1, edge_lengthx=-1, edge_lengthy=-1
):
    """
    p,v = RectangleSegments(P1,P2,num_points=60,edge_length=-1,edge_lengthx=-1,edge_lengthy=-1)
    """
    P11 = [P2[0], P1[1]]
    P22 = [P1[0], P2[1]]
    npoints = int(np.floor(num_points / 4))

    lengx = edge_length
    lengy = edge_length
    if edge_lengthx > 0:
        lengx = edge_lengthx
    if edge_lengthy > 0:
        lengy = edge_lengthy

    p_1, v_1 = LineSegments(P1, P11, npoints, lengx)
    p_2, v_2 = LineSegments(P11, P2, npoints, lengy)
    p_3, v_3 = LineSegments(P2, P22, npoints, lengx)
    p_4, v_4 = LineSegments(P22, P1, npoints, lengy)
    p, v = AddSegments(p_1, p_2)
    p, v = AddSegments(p, p_3)
    p, v = AddSegments(p, p_4)
    return p, v


def ORecSegments(
    P1,
    P2,
    rho,
    num_points=60,
    num_pc=7,
    edge_length=-1,
    edge_lengthx=-1,
    edge_lengthy=-1,
):
    """
    p,v = ORecSegments(P1,P2,rho,num_points=60,num_pc=7,edge_length=-1,edge_lengthx=-1,edge_lengthy=-1)
    """
    x1L = P1[0]
    x2L = P2[0] - rho
    x1R = P1[0] + rho
    x2R = P2[0]

    y1L = P1[1] + rho
    y3L = P2[1]
    y1R = P1[1]
    y3R = P2[1] - rho

    Dxx = P2[0] - P1[0]
    Dyy = P2[1] - P1[1]
    if rho > Dxx / 3 or rho > Dyy / 3:
        print("Error, rho too large")

    lengx = edge_length
    lengy = edge_length
    if edge_lengthx > 0:
        lengx = edge_lengthx
    if edge_lengthy > 0:
        lengy = edge_lengthy

    npoints = int(np.floor(num_points / 4))
    p_1, v_1 = LineSegments([x1R, y1R], [x2L, y1R], npoints, lengx)
    p_2, v_2 = LineSegments([x2R, y1L], [x2R, y3R], npoints, lengy)
    p_3, v_3 = LineSegments([x2L, y3L], [x1R, y3L], npoints, lengx)
    p_4, v_4 = LineSegments([x1L, y3R], [x1L, y1L], npoints, lengy)
    p_5, v_5 = CircleSegments([x2L, y1L], rho, num_pc, -np.pi / 2.0, 0, edge_length)
    p_6, v_6 = CircleSegments([x2L, y3R], rho, num_pc, 0, np.pi / 2.0, edge_length)
    p_7, v_7 = CircleSegments([x1R, y3R], rho, num_pc, np.pi / 2.0, np.pi, edge_length)
    p_8, v_8 = CircleSegments(
        [x1R, y1L], rho, num_pc, np.pi, 3 * np.pi / 2, edge_length
    )
    p, v = AddSegments(p_1, p_5)
    p, v = AddSegments(p, p_2)
    p, v = AddSegments(p, p_6)
    p, v = AddSegments(p, p_3)
    p, v = AddSegments(p, p_7)
    p, v = AddSegments(p, p_4)
    p, v = AddSegments(p, p_8)
    return p, v


# List of points
def PointSegments(p, edge_length=-1):
    """
    p,v = PointSegments(p,edge_length=-1)
    """

    if edge_length != -1:
        pt = np.array(p)
        p1 = [pt[0]]
        for i in range(1, len(pt)):
            dp = pt[i] - pt[i - 1]
            N = (int)(np.sqrt(np.sum(dp**2)) / edge_length) + 1
            if N <= 2:
                N = 2
            tvals = np.linspace(0, 1, N)
            p1 += [list(pt[i - 1] + tt * dp) for tt in tvals[1:]]
        p1 = np.array(p1)
    else:
        p1 = np.array(p)

    delta = np.min(np.sqrt(np.sum((p1[1:] - p1[:-1]) ** 2, axis=1))) / 10.0
    Pall = [(x[0], x[1]) for x in p1]
    closed = False
    if SamePoint(p1[0], p1[-1], delta) == True:
        Pall = Pall[:-1]
        closed = True

    vertices = [(j, j + 1) for j in range(0, len(Pall) - 1, 1)]
    if closed == True:
        vertices += [(len(Pall) - 1, 0)]

    return Pall, vertices


def AddMultipleSegments(*args, **kwargs):
    """
    p,v = AddMultipleSegments(*args,**kwargs)
    """

    nn = len(args)
    p, v = AddSegments(args[0], args[1])
    for k in range(2, nn - 1):
        p, v = AddSegments(p, args[k])

    if kwargs:
        if kwargs["closed"] == True:
            p, v = AddSegments(p, args[nn - 1], closed=True)
        else:
            p, v = AddSegments(p, args[nn - 1])
    else:
        p, v = AddSegments(p, args[nn - 1])

    return p, v


def AddMultipleCurves(*allC):
    """
    p,v,ind = AddMultipleCurves(*allC)
    """

    N = len(allC)
    indi = N * [0]

    if N % 2 != 0:
        print("Number of Arguments not even")
        return False
    else:
        p, v = AddCurves(allC[0], allC[1], allC[2], allC[3])
        indi[0] = 0
        indi[1] = len(allC[2])
        j = 2
        for i in range(4, N, 2):
            p, v = AddCurves(p, v, allC[i], allC[i + 1])
            indi[j] = indi[j - 1] + len(allC[i])
            j += 1

    return p, v, indi


# Connect two different polygons
def AddSegments(P1, P2, closed=False):
    """
    p,v = AddSegments(P1,P2,closed=False)
    """
    p1 = np.array(P1)
    p2 = np.array(P2)
    # find smallest distance within points p1 and p2
    min1 = np.min(np.sqrt(np.sum((p1[1:] - p1[:-1]) ** 2, axis=1)))
    min2 = np.min(np.sqrt(np.sum((p2[1:] - p2[:-1]) ** 2, axis=1)))
    delta = np.min([min1, min2]) / 10.0

    # Add second curve to first curve
    del_first = SamePoint(p1[-1], p2[0], delta)
    Pall = P1[:]
    if del_first == True:
        Pall += P2[1:]
    else:
        Pall += P2

    # check if Pall is closed
    del_last = SamePoint(Pall[-1], p1[0], delta)
    if del_last == True:
        Pall = Pall[:-1]

    vertices = [(j, j + 1) for j in range(0, len(Pall) - 1, 1)]
    if (del_last == True) or (closed == True):
        vertices += [(len(Pall) - 1, 0)]

    return Pall, vertices


# Append Curves
def AddCurves(p1, v1, p2, v2, connect=False, connect_points=[], eps=1e-12):
    """
    p,v = AddCurves(p1,v1,p2,v2,connect=False,connect_points=[],eps=1e-12)
    """
    # make one list
    p = p1 + p2
    v2n = [(v2[j][0] + len(p1), v2[j][1] + len(p1)) for j in range(len(v2))]
    v = v1 + v2n

    # second segment array may contain
    # IDENTICAL points,
    # given in connect_points or indicated by the option connect
    con_pt = []
    if connect == True:
        con_pt = [x for x in p2]
    elif len(connect_points) != 0:
        con_pt = [x for x in connect_points]
    if len(con_pt) != 0:
        nodes1 = np.arange(0, len(p1))
        nodes2 = np.arange(0, len(p2))
        # node numbers of connect points in p1
        fn1, dn1 = FindClosestNode(nodes1, p1, con_pt)
        # node numbers of connect points in p2
        if connect != True:
            fn2, dn2 = FindClosestNode(nodes2, p2, con_pt)
        else:
            fn2 = np.arange(0, len(p2), dtype=int)
            dn = 0.0 * fn2

        # node numbers in p
        # sort node numbers for delete process
        sort_indices = np.argsort(fn2)
        dn1 = np.array(dn1)
        nodes2 += len(p1)
        replace_ind = []
        for ii in sort_indices[-1::-1]:
            # connect points are identical with points in p1
            if dn1[ii] < eps:
                print("replace point ", fn2[ii], " --> ", fn1[ii])
                replace_ind += [ii]
                del p[len(p1) + fn2[ii]]
                nodes2[fn2[ii] + 1 :] -= 1
        for ii in replace_ind:
            nodes2[fn2[ii]] = fn1[ii]

        v2n = [(int(nodes2[v2[j][0]]), int(nodes2[v2[j][1]])) for j in range(len(v2))]
        v = v1 + v2n

    return p, v


# Generate mesh
def DoTriMesh(
    points,
    vertices,
    edge_length=-1,
    holes=[],
    tri_refine=None,
    show=True,
    order=None,
    writeTo=None,
):
    """
    DoTriMesh(points,vertices,edge_length=-1,holes=[],tri_refine=None,show=True,order=None,writeTo=None)
    ---------
    output
    mesh_points , mesh_elements , bou_Edges , list_boundary_edges , mesh_boundary_elements , inner_curve_segments , list_inner_curve_segments
    """
    info = triangle.MeshInfo()
    info.set_points(points)
    if len(holes) > 0:
        info.set_holes(holes)
    info.set_facets(vertices)

    if tri_refine != None:
        mesh = triangle.build(info, refinement_func=tri_refine, mesh_order=order)
    elif edge_length <= 0:
        mesh = triangle.build(info, mesh_order=order)
    else:
        mesh = triangle.build(
            info,
            max_volume=0.5 * edge_length**2,
            mesh_order=order,
            generate_faces=True,
        )

    mesh_points = np.array(mesh.points, dtype=np.double)
    mesh_elements = np.array(mesh.elements, dtype=np.int64)
    mesh_facets = np.array(mesh.facets, dtype=np.int64)
    mesh_neighbors = np.array(mesh.neighbors, dtype=np.int64)
    # use generate_face=True in triangle.build for all edges
    # mesh_edges = np.array(mesh.faces,  dtype=np.int64)

    # generate boundary elements
    mesh_boundary_elements = []
    mesh_boundary_edges = []
    for i, x in enumerate(mesh_neighbors):
        # find boundary elements
        if x[0] == -1 or x[1] == -1 or x[2] == -1:
            # print("boundary element: ",x[0],x[1],x[2],"  element=",mesh_elements[i])
            mesh_boundary_elements += [i]
        # find boundary edges
        if x[0] == -1:
            mesh_boundary_edges += [[mesh_elements[i][1], mesh_elements[i][2]]]
        if x[1] == -1:
            mesh_boundary_edges += [[mesh_elements[i][0], mesh_elements[i][2]]]
        if x[2] == -1:
            mesh_boundary_edges += [[mesh_elements[i][0], mesh_elements[i][1]]]

    # make edge --> element map
    edge_element_map = {}
    for i, tt in enumerate(mesh_elements):
        e = [0, 0, 0]
        e[0] = tuple(np.sort([tt[0], tt[1]]))
        e[1] = tuple(np.sort([tt[0], tt[2]]))
        e[2] = tuple(np.sort([tt[1], tt[2]]))
        for j in [0, 1, 2]:
            try:
                edge_element_map[e[j]] += [i]
            except:
                edge_element_map[e[j]] = [i]

    # print("--> map",edge_element_map)
    # print("--> Randelemente: ",mesh_boundary_edges)
    # print("--> Kurven ",mesh_facets)

    # make boundary edges
    edges = [tuple(x) for x in mesh_boundary_edges]
    bou_Edges, list_bE = SortSegments(edges)
    bou_Edges = CheckSegmentSense(mesh_elements, bou_Edges, list_bE)
    list_bE += [len(bou_Edges)]

    # make edges of inner curves
    edges = [
        tuple(x) for x in mesh_facets if len(edge_element_map[tuple(np.sort(x))]) == 2
    ]
    Curves, list_Cu = SortSegments(edges)
    Curves = CheckSegmentSense(mesh_elements, Curves, list_Cu)
    list_Cu += [len(Curves)]

    if show == True:
        plt.gca().set_aspect(1)
        plt.triplot(mesh_points[:, 0], mesh_points[:, 1], mesh_elements[:, 0:3])
        plt.show()

    # second order boundary nodes
    if order == 2:

        # resort indices 4,5,6
        for i in range(len(mesh_elements)):
            secp = list(mesh_elements[i, 3:]) * 2
            mesh_elements[i, 3:] = secp[2:5]

        MiddleIndices = []
        for i in mesh_boundary_elements:
            MiddleIndices += list(mesh_elements[i, 3:])

        ps = [0.5 * (mesh_points[x[0], :] + mesh_points[x[1], :]) for x in bou_Edges]
        third_node = FindClosestNode(
            MiddleIndices, mesh_points, ps, constraint=-1, tree=None
        )
        bou_Edges = [[x[0], x[1], third_node[0][i]] for i, x in enumerate(bou_Edges)]

        err = CheckElementList(mesh_points, mesh_elements)
        if err > 0:
            print(
                "ERROR: Number of wrong sorted mesh_elements ",
                err,
                "# mesh_elements ",
                len(mesh_elements),
            )
            return False

    if writeTo != None:
        np.savez(
            writeTo,
            mesh_points,
            mesh_elements,
            bou_Edges,
            list_bE,
            mesh_boundary_elements,
            Curves,
            list_Cu,
        )

    return (
        mesh_points,
        mesh_elements,
        bou_Edges,
        list_bE,
        mesh_boundary_elements,
        Curves,
        list_Cu,
    )
    # return mesh_points,mesh_elements;


def LoadTriMesh(filename, show=True):
    """
    LoadTriMesh(filename,show=True)
    ------------------
    output
    mesh_points , mesh_elements , bou_Edges , list_boundary_edges , mesh_boundary_elements , inner_curve_segments , list_inner_curve_segments
    """

    erg = np.load(filename)

    poi = erg["arr_0"]
    tri = erg["arr_1"]
    BouE = erg["arr_2"].tolist()
    li_BE = erg["arr_3"].tolist()
    bou_elem = erg["arr_4"].tolist()
    CuE = erg["arr_5"].tolist()
    li_CE = erg["arr_6"].tolist()
    erg.close()

    if show == True:
        plt.triplot(poi[:, 0], poi[:, 1], tri[:, 0:3])
        plt.show()

    return poi, tri, BouE, li_BE, bou_elem, CuE, li_CE


#
#  Write xml file useful for fenics
#
def WriteXmlMesh(filename, p, t, do=None):
    """
    WriteXmlMesh(filename,p,t,do=None)
    """

    import xml.etree.ElementTree as ET

    # pretty print method
    def indent(elem, level=0):
        i = "\n" + level * "  "
        j = "\n" + (level - 1) * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for subelem in elem:
                indent(subelem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = j
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = j
        return elem

    # root element
    dolf = ET.Element(
        "dolfin",
        {
            "xmlns:dolfin": "https://fenicsproject.org converted from meshpy and meshtools"
        },
    )

    # full mesh
    mesh = ET.SubElement(dolf, "mesh", {"celltype": "triangle", "dim": "2"})

    # coordinates
    vert = ET.SubElement(mesh, "vertices", {"size": str(len(p))})

    for i, pp in enumerate(p):
        line = ET.SubElement(
            vert, "vertex", {"index": str(i), "x": str(pp[0]), "y": str(pp[1])}
        )

    # elements
    cells = ET.SubElement(mesh, "cells", {"size": str(len(t))})
    for i, tt in enumerate(t):
        line = ET.SubElement(
            cells,
            "triangle",
            {"index": str(i), "v0": str(tt[0]), "v1": str(tt[1]), "v2": str(tt[2])},
        )

    # data
    line = ET.SubElement(mesh, "data")

    # domains
    dom = ET.SubElement(mesh, "domains")
    if do == None:
        do = len(t) * [0]
    msh_vc = ET.SubElement(
        dom,
        "mesh_value_collection",
        {"name": "m", "type": "uint", "dim": "2", "size": "686"},
    )
    for i, dd in enumerate(do):
        line = ET.SubElement(
            msh_vc,
            "value",
            {"cell_index": str(i), "local_entity": "0", "value": str(dd)},
        )

    # write to file
    tree = ET.ElementTree(indent(dolf))
    tree.write(filename, xml_declaration=True, encoding="utf-8")


def CheckElementList(p, t):

    if len(t[0]) == 3:
        return 0
    else:
        j = 0
        for i in range(len(t)):
            diff1 = np.sum(((p[t[i, 0]] + p[t[i, 1]]) / 2.0 - p[t[i, 3]]) ** 2)
            diff2 = np.sum(((p[t[i, 1]] + p[t[i, 2]]) / 2.0 - p[t[i, 4]]) ** 2)
            diff3 = np.sum(((p[t[i, 2]] + p[t[i, 0]]) / 2.0 - p[t[i, 5]]) ** 2)
            if diff1 > 1e-10 or diff2 > 1e-10 or diff3 > 1e-10:
                # print("Error in element list (wrong order), ",i,t[i],diff1,diff2,diff3)
                j += 1
        return j


def MakeSecondOrderMesh(p, t, bou):
    edges, b_ed, b_el = FindEdges(t)

    new_p = []
    all_ed = []
    for X in edges:
        new_p += [0.5 * (p[X[0], :] + p[X[1], :])]
        all_ed += [set(X)]

    print("all edges=", all_ed)
    new_t = []
    for X in t:
        print(X)
        e1 = set([X[0], X[1]])
        e2 = set([X[1], X[2]])
        e3 = set([X[2], X[0]])
        i4 = all_ed.index(e1) + len(p)
        i5 = all_ed.index(e2) + len(p)
        i6 = all_ed.index(e3) + len(p)
        new_t += [[X[0], X[1], X[2], i4, i5, i6]]

    new_bou = []
    for X in bou:
        e1 = set([X[0], X[1]])
        i3 = all_ed.index(e1) + len(p)
        new_bou += [[X[0], X[1], i3]]

    p_new = np.array(list(p) + new_p)
    return p_new, np.array(new_t), np.array(new_bou)


############### BEM #################
#  points are the vertices of the segments (or elements)
#  nodes are the middle position in the segments for zero order


# flags[i]=0  potential of segment i is known
#          1  normal derivative of segment i is known
#
# return   middle-points in segment
#          half Diff-Vector
#          known PHI-segments
#          known DERIVATIVE-segments
def MakeBEMBoundary(p, v, func=False, curves=[]):

    # zero order base function, define nodes on middle position of element
    Ns = len(v)
    p = np.array(p)
    v = np.array(v)
    # compute middle points and elemental vectors
    mid_points = 0.5 * (p[v[:, 1], :] + p[v[:, 0], :])
    diff_points = 0.5 * (p[v[:, 1], :] - p[v[:, 0], :])

    mid_points = np.array(mid_points)

    # set all nodes as dirichlet nodes
    flags = Ns * [0]

    # type of boundary condition
    # if a function is provided dirichlet and neumann nodes are selected
    if func != False:
        flags = func(mid_points)
    else:
        if curves == []:
            print("Provide properties of Nodes according to:")
            print("0:  Value known")
            print("1:  Derivative known")
            return
        else:
            flags = curves

    # Vec1 dirichlet nodes, Vc2 Neumann nodes
    Vec1 = []
    Vec2 = []
    for i in range(Ns):
        # the potential is known for these nodes
        if flags[i] == 0:
            Vec1 += [i]
        # the derivative is known
        else:
            Vec2 += [i]

    return np.array(mid_points), np.array(diff_points), Vec1, Vec2


def ChangeCurveDirection(v):
    N = len(v)
    out = []
    for i in range(N):
        out += [(v[N - i - 1][1], v[N - i - 1][0])]
    return out


#
#  AllBound  [[p,v],[p,v],[p,v],[],...]
#  Dom       [[3,4,2],alpha]
#
def DoBemBoundary(AllBound, show=True, show_numbers=False):

    D_seg = [0]
    N_seg = [0]
    I_seg = [0]
    NofC = len(AllBound)
    Curves = NofC * [0]
    # count number of segemens for each type
    for i in range(NofC):
        seg = len(AllBound[i][1])
        if AllBound[i][2] == 0:
            a = D_seg[-1]
            D_seg += [a + seg]
        elif AllBound[i][2] == 1:
            a = N_seg[-1]
            N_seg += [a + seg]
        else:
            a = I_seg[-1]
            I_seg += [a + seg]

        Curves[i] = {"first": a, "last": a + seg - 1, "type": AllBound[i][2]}

    D_nodes = D_seg[-1]
    N_nodes = N_seg[-1]
    I_nodes = I_seg[-1]

    N_seg = [x + D_nodes for x in N_seg]
    I_seg = [x + D_nodes + N_nodes for x in I_seg]

    NofNodes = D_nodes + N_nodes + I_nodes
    VecB = np.zeros((NofNodes, 2))
    VecXm = np.zeros((NofNodes, 2))

    for i in range(NofC):

        # run through all boundaries
        p = np.array(AllBound[i][0])
        v = AllBound[i][1]
        NodeType = AllBound[i][2]

        # correct positions in Curves array
        if NodeType == 1:
            Curves[i]["first"] += D_nodes
            Curves[i]["last"] += D_nodes
        elif NodeType < 0:
            Curves[i]["first"] += D_nodes + N_nodes
            Curves[i]["last"] += D_nodes + N_nodes

        # Compute middle point and direction vector
        count = 0
        for s in v:
            VecB[Curves[i]["first"] + count] = np.array(
                [0.5 * (p[s[1], :] - p[s[0], :])]
            )
            VecXm[Curves[i]["first"] + count] = np.array(
                [0.5 * (p[s[1], :] + p[s[0], :])]
            )
            count += 1

        if show == True:
            PlotBoundary(p, v, "Segments")

    if show == True:
        plt.title("Dirichlet (blue),    Neumann (green),    Inner Curves (red)")
        for Z in Curves:
            x = VecXm[Z["first"] : Z["last"] + 1][:, 0]
            y = VecXm[Z["first"] : Z["last"] + 1][:, 1]
            if Z["type"] == 0:
                plt.plot(x, y, "ob", markersize=8)
            elif Z["type"] == 1:
                plt.plot(x, y, "sg", markersize=8)
            else:
                plt.plot(x, y, "vr", markersize=6)

            if show_numbers == True:
                for i in range(len(x)):
                    buf = " %i" % (Z["first"] + i)
                    plt.text(x[i], y[i], buf, color="k", fontsize=13)
        plt.show()

    return VecXm, VecB, Curves, D_nodes, N_nodes, I_nodes


#
# Make a curve list with all properties
#
def DoBemDomain(AllDom, CC):

    Curves = len(CC) * [0]
    for i in range(len(CC)):
        Curves[i] = {
            "first": CC[i]["first"],
            "last": CC[i]["last"],
            "type": CC[i]["type"],
        }

    for DomNumb, GG in enumerate(AllDom):
        for thisC in GG[0]:
            i = abs(thisC)
            # Add domain number and their alphas to curves list
            if "dom" in Curves[i]:
                if DomNumb > Curves[i]["dom"]:
                    Curves[i]["dom"] = (Curves[i]["dom"], DomNumb)
                    Curves[i]["alpha"] = (Curves[i]["alpha"], GG[1])
                else:
                    Curves[i]["dom"] = (DomNumb, Curves[i]["dom"])
                    Curves[i]["alpha"] = (GG[1], Curves[i]["alpha"])
            else:
                Curves[i]["dom"] = DomNumb
                Curves[i]["alpha"] = GG[1]

    return Curves


# G=[[CurveIndex1,CurveIndex2,..],alpha]
# negative Curveindex changes direction of curve --> newB on return
# Curves is changed on return
#
def MakeDomain(DomNumb, G, CC, VecB):

    D_nodes = []
    N_nodes = []
    I_nodes = []
    newB = np.copy(VecB)
    for thisC in G[0]:
        i = abs(thisC)
        start = CC[i]["first"]
        stop = CC[i]["last"] + 1
        nodes = range(start, stop)

        # change curve direction
        if thisC < 0:
            newB[nodes] *= -1.0

        if CC[i]["type"] == 0:
            D_nodes += nodes
        elif CC[i]["type"] == 1:
            N_nodes += nodes
        else:
            I_nodes += nodes

    all_nodes = D_nodes + N_nodes + I_nodes
    lND = len(D_nodes)
    lNN = len(N_nodes)
    lNI = len(I_nodes)

    return all_nodes, newB, lND, lNN, lNI

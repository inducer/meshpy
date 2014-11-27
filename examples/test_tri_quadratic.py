# Quadratic element demo, by Aravind Alwan

from numpy import *
from matplotlib.pyplot import *
from meshpy.triangle import MeshInfo, build

# Utility function to create lists of the form [(1,2), (2,3), (3,4),
#(4,1)], given two numbers 1 and 4
from itertools import islice, cycle
from six.moves import range
from six.moves import zip
loop = lambda a, b: list(zip(list(range(a, b)), islice(cycle(list(range(a, b))), 1, None)))

info = MeshInfo()
info.set_points([(0,0), (1,0), (1,1), (0,1), (2,0), (3,0), (3,1), (2,1)])
info.set_facets(loop(0,4) + loop(4,8), list(range(1,9))) # Create 8 facets and apply markers 1-8 on them
info.regions.resize(2)
info.regions[0] = [0.5, 0.5, 1, 0.1] # Fourth item specifies maximum area of triangles as a region attribute
info.regions[1] = [2.5, 0.5, 2, 0.1] # Replace 0.1 by a smaller value to produce a finer mesh

mesh = build(info, volume_constraints=True, attributes=True,
generate_faces=True, min_angle=33, mesh_order=2)

pts = vstack(mesh.points) # (npoints, 2)-array of points
elements = vstack(mesh.elements) # (ntriangles, 6)-array specifying element connectivity

# Matplotlib's Triangulation module uses only linear elements, so use only first 3 columns when plotting
triplot(pts[:,0], pts[:,1], elements[:,:3])

plot(pts[:,0], pts[:,1], 'ko') # Manually plot all points including the ones at the midpoints of triangle faces

# Plot a filled contour plot of the function (x - 1.5)^2 + y^2 over
# the mesh. Note tricontourf interpolation uses only linear elements
tricontourf(pts[:,0], pts[:,1], elements[:,:3], (pts[:,0]-1.5)**2 +
        pts[:,1]**2, 100)

axis([-0.1, 3.1, -0.8, 1.8])
show()

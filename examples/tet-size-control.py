from meshpy.tet import MeshInfo, build

mesh_info = MeshInfo()

# construct a two-box extrusion of this base
base = [(-2,-2,0), (2,-2,0), (2,2,0), (-2,2,0)]

# first, the nodes
mesh_info.set_points(
        base
        +[(x,y,z+5) for x,y,z in base]
        +[(x,y,z+10) for x,y,z in base]
        )

# next, the facets

# vertex indices for a box missing the -z face
box_without_minus_z = [ 
    [4,5,6,7],
    [0,4,5,1],
    [1,5,6,2],
    [2,6,7,3],
    [3,7,4,0],
    ]

def add_to_all_vertex_indices(facets, increment):
    return [[pt+increment for pt in facet] for facet in facets]

mesh_info.set_facets(
    [[0,1,2,3]] # base
    +box_without_minus_z # first box
    +add_to_all_vertex_indices(box_without_minus_z, 4) # second box
    )

# set the volume properties -- this is where the tet size constraints are
mesh_info.regions.resize(2)
mesh_info.regions[0] = [0,0,2, # point in volume -> first box
        0, # region tag (user-defined number)
        1e-1, # max tet volume in region
        ]
mesh_info.regions[1] = [0,0,7, # point in volume -> second box
        0, # region tag (user-defined number, arbitrary)
        1e-2, # max tet volume in region
        ]

mesh = build(mesh_info, area_constraints=True)

# this is a no-op, but it shows how to access the output data
for point in mesh.points:
    [x,y,z] = point

for element in mesh.elements:
    [pt_1, pt_2, pt_3, pt_4] = element

# this writes the mesh as a vtk file, requires pyvtk
mesh.write_vtk("test.vtk")

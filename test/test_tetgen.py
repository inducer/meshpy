from meshpy.tet import MeshInfo, build




def main():
    mesh_info = MeshInfo()
    mesh_info.set_points([
        (0,0,0),
        (2,0,0),
        (2,2,0),
        (0,2,0),
        (0,0,12),
        (2,0,12),
        (2,2,12),
        (0,2,12),
        ])
    mesh_info.set_facets([
        [0,1,2,3],
        [4,5,6,7],
        [0,4,5,1],
        [1,5,6,2],
        [2,6,7,3],
        [3,7,4,0],
        ],
        [-1,-2,0,0,0,0])
    #mesh_info.dump()
    #mesh_info.save_nodes("test")
    #mesh_info.save_poly("test")
    build(mesh_info)



if __name__ == "__main__":
    main()

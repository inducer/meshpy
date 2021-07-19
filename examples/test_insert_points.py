import logging
import numpy as np

from meshpy.tet import MeshInfo, Options, build

if __name__ == '__main__':
    logger = logging.getLogger('test_insert_points.py')

    points = [(0, 0, 0),
              (0, 0, 1),
              (1, 0, 0),
              (1, 0, 1),
              (1, 1, 0),
              (1, 1, 1),
              (0, 1, 0),
              (0, 1, 1)]

    facets = [(0, 1, 3, 2),
              (2, 3, 5, 4),
              (4, 5, 7, 6),
              (6, 7, 1, 0),
              (0, 2, 4, 6),
              (1, 3, 5, 7)]

    mesh_info = MeshInfo()
    mesh_info.set_points(points)
    mesh_info.set_facets(facets)

    options = Options(switches='', plc=True, verbose=True, quiet=False)

    # Insert an interior point of the cube as a constrained point
    interior_point = (0.33, 0.7, 0.91)

    insert_points_mesh_info = MeshInfo()
    insert_points_mesh_info.set_points([interior_point])

    mesh = build(mesh_info, options, max_volume=0.1,
                 insert_points=insert_points_mesh_info)

    mesh_points = np.array(mesh.points)
    min_dist = np.sqrt(np.sum((interior_point - mesh_points), axis=1)**2).min()

    if min_dist > 0:
        logger.error('tetrahedron mesh does not contain contrained point')

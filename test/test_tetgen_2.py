from meshpy.tet import MeshInfo, build




def parse_superfish_format(filename):
    import re
    
    lines = [line.strip() for line in file(filename, "r").readlines() 
            if line.strip().startswith("&po")]

    # parse the file
    line_re = re.compile(r"^\&po\s+(.*)\s*\&$")
    key_val_re = re.compile(r"^\s*([0-9a-zA-Z]+)\s*\=\s*(.*)\s*$")
    proplines = []
    for line in lines:
        line_match = line_re.match(line)
        assert line_match
        data = line_match.group(1).split(",")

        properties = {}
        for datum in data:
            datum_match = key_val_re.match(datum.strip())
            assert datum_match
            properties[datum_match.group(1)] = float(datum_match.group(2))
        proplines.append(properties)

    # concoct x-y-points
    from math import atan2, sin, cos, pi, ceil
    import pylinear.array as num
    import pylinear.computation as comp

    def add_point(pt):
        points.append((pt[1], pt[0]))

    points = []
    for i, p in enumerate(proplines):
        if "nt" in p:
            # draw arc
            last_point = points[-1]
            center = num.array((p["x0"], p["y0"]))
            r = p["r"]
            theta = pi/180.*p["theta"]

            tangent = num.array((cos(theta), sin(theta)))
            upward_normal = num.array((-sin(theta), cos(theta)))

            #print 180*theta/pi, last_point, center, tangent, upward_normal, last_point-center
            if (last_point - center)*upward_normal < 0:
                # draw ccw (positive) arc / upward
                phi_start = 3*pi/2 + theta
                phi_end = phi_start + pi/2
            else:
                # draw cw (negative) arc / downward
                phi_start = pi/2 + theta
                phi_end = phi_start - pi/2
            steps = 10
            dphi = (phi_end-phi_start) / steps
            phi = phi_start+dphi

            for i in range(steps):
                points.append(center + r*num.array((cos(phi), sin(phi))))
                phi += dphi
        else:
            points.append(num.array((p["x"], p["y"])))

    #outf = file("gun-lines.dat", "w")
    #for p in points:
        #outf.write("%f\t%f\n" % (p[0], p[1]))
    #outf.close()

    # turn (x,y) into (r,z)
    return [(p[1], p[0]) for p in points]


            





def generate_surface_of_revolution(rz_points, radial_subdiv=16, point_offset=0):
    assert len(rz_points) > 0

    from math import sin, cos, pi

    def gen_point(r, phi, z):
        return (r*cos(phi), r*sin(phi), z)

    def gen_ring(r, z):
        if r == 0:
            p_indices = [p0+len(points)]
            points.append(gen_point(r, 0, z))
        else:
            p_indices = [p0+len(points)+i for i in range(radial_subdiv)]
            points.extend([gen_point(r, dphi*i, z) for i in range(radial_subdiv)])
        return p_indices

    def pair_with_successor(l):
        n = len(l)
        return [(l[i], l[(i+1)%n]) for i in range(n)]

    p0 = point_offset
    points = []
    polygons = []

    dphi = 2*pi/radial_subdiv

    last_r, last_z = rz_points[0]
    last_ring = gen_ring(last_r, last_z)

    for r, z in rz_points[1:]:
        ring = gen_ring(r, z)
        if last_r == 0:
            # make opening fan
            assert len(last_ring) == 1
            start_pt = last_ring[0]
            if r != 0:
                polygons.extend(
                        [(start_pt, succ, pt) for pt, succ in pair_with_successor(ring)]
                        )
        elif r == 0:
            # make closing fan
            assert len(ring) == 1
            end_pt = ring[0]
            polygons.extend(
                    [(pt, succ, end_pt) for pt, succ in pair_with_successor(last_ring)]
                    )
        else:
            # make quad strip
            last_pairs = pair_with_successor(last_ring)
            my_pairs = pair_with_successor(ring)
            polygons.extend(
                    [(a, b, c, d) for ((a,b), (d,c)) in zip(last_pairs, my_pairs)]
                    )

        last_ring = ring
        last_r = r
        last_z = z

    return points, polygons
            






def main():
    simple_rz = [
        (0,0),
        (1,1),
        (1,2),
        (0,3),
        ]
    mesh_info = MeshInfo()
    rz_points = parse_superfish_format("gun.am")
    points, facets = generate_surface_of_revolution(rz_points)

    mesh_info.set_points(points)
    mesh_info.set_facets(facets, [0 for i in range(len(facets))])
    #mesh_info.save_nodes("test")
    #mesh_info.save_poly("test")
    #mesh_info.load_poly("test")
    mesh = build(mesh_info)
    mesh.write_vtk("my_mesh.vtk")
    #mesh.save_elements("gun")
    #mesh.save_nodes("gun")




if __name__ == "__main__":
    main()

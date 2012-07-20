class GmshMeshReceiver:
    def __init__(self):
        pass

    def add_node(self, node_nr, point):
        pass

    def finalize_nodes(self):
        pass

    def add_element(self, element_nr, element_type, vertex_nrs,
            lexicographic_nodes, tag_numbers):
        pass

    def finalize_elements(self):
        pass

    def add_tag(self, name, index, dimension):
        pass

    def finalize_tags(self):
        pass


def main():
    mr = GmshMeshReceiver()

    import sys
    from meshpy.gmsh_reader import read_gmsh
    read_gmsh(mr, sys.argv[1])


if __name__ == "__main__":
    main()

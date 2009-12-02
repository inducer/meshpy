# tools -----------------------------------------------------------------------
def _erase_dir(dir):
    from os import listdir, unlink, rmdir
    from os.path import join
    for name in listdir(dir):
        unlink(join(dir, name))
    rmdir(dir)



class _TempDirManager(object):
    def __init__(self):
        from tempfile import mkdtemp
        self.path = mkdtemp()

    def sub(self, n):
        from os.path import join
        return join(self.path, n)

    def clean_up(self):
        _erase_dir(self.path)

    def error_clean_up(self):
        _erase_dir(self.path)




class GmshRunner(object):
    def __init__(self, source, dimensions, order=None, other_options=[],
            extension="geo", gmsh_executable="gmsh"):
        self.source = source
        self.dimensions = dimensions
        self.order = order
        self.other_options = other_options
        self.extension = extension
        self.gmsh_executable = gmsh_executable

        if dimensions not in [1, 2, 3]:
            raise RuntimeError("dimensions must be one of 1,2,3")

    def __enter__(self):
        self.temp_dir_mgr = None
        temp_dir_mgr = _TempDirManager()
        try:
            working_dir = temp_dir_mgr.path
            from os.path import join
            source_file_name = join(working_dir, "temp."+self.extension)
            source_file = open(source_file_name, "w")
            try:
                source_file.write(self.source)
            finally:
                source_file.close()

            output_file_name = join(working_dir, "output.msh")
            cmdline = [
                    self.gmsh_executable,
                    "-%d" % self.dimensions,
                    "-o", output_file_name,
                    "-nopopup"]

            if self.order is not None:
                cmdline.extend(["-order", str(self.order)])

            cmdline.extend(self.other_options)
            cmdline.append(source_file_name)

            from pytools.prefork import call_capture_stdout
            call_capture_stdout(cmdline, working_dir)

            self.output_file = open(output_file_name, "r")

            self.temp_dir_mgr = temp_dir_mgr
            return self.output_file
        except:
            temp_dir_mgr.clean_up()
            raise

    def __exit__(self, type, value, traceback):
        self.output_file.close()
        if self.temp_dir_mgr is not None:
            self.temp_dir_mgr.clean_up()

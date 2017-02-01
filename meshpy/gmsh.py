import logging
logger = logging.getLogger(__name__)


__doc__ = """

.. exception:: GmshError
.. autoclass:: ScriptSource
.. autoclass:: FileSource
.. autoclass:: ScriptWithFilesSource

.. autoclass:: GmshRunner
"""


class GmshError(RuntimeError):
    pass


# {{{ tools

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


class ScriptSource(object):
    """
    .. versionadded:: 2016.1
    """
    def __init__(self, source, extension):
        self.source = source
        self.extension = extension


class LiteralSource(ScriptSource):
    """
    .. versionadded:: 2014.1
    """
    def __init__(self, source, extension):
        super(LiteralSource, self).__init__(source, extension)

        from warnings import warn
        warn("LiteralSource is deprecated, use ScriptSource instead",
                DeprecationWarning, stacklevel=2)


class FileSource(object):
    """
    .. versionadded:: 2014.1
    """
    def __init__(self, filename):
        self.filename = filename


class ScriptWithFilesSource(object):
    """
    .. versionadded:: 2016.1

    .. attribute:: source

        The script code to be fed to gmsh.

    .. attribute:: filenames

        The names of files to be copied to the temporary directory where
        gmsh is run.
    """
    def __init__(self, source, filenames, source_name="temp.geo"):
        self.source = source
        self.source_name = source_name
        self.filenames = filenames


class GmshRunner(object):
    def __init__(self, source, dimensions=None, order=None,
            incomplete_elements=None, other_options=[],
            extension="geo", gmsh_executable="gmsh",
            output_file_name="output.msh"):
        if isinstance(source, str):
            from warnings import warn
            warn("passing a string as 'source' is deprecated--use "
                    "one of the *Source classes",
                    DeprecationWarning)

            source = ScriptSource(source, extension)

        self.source = source
        self.dimensions = dimensions
        self.order = order
        self.incomplete_elements = incomplete_elements
        self.other_options = other_options
        self.gmsh_executable = gmsh_executable
        self.output_file_name = output_file_name

        if dimensions not in [1, 2, 3, None]:
            raise RuntimeError("dimensions must be one of 1,2,3 or None")

    def __enter__(self):
        self.temp_dir_mgr = None
        temp_dir_mgr = _TempDirManager()
        try:
            working_dir = temp_dir_mgr.path
            from os.path import join, abspath, exists

            if isinstance(self.source, ScriptSource):
                source_file_name = join(
                        working_dir, "temp."+self.source.extension)
                with open(source_file_name, "w") as source_file:
                    source_file.write(self.source.source)

            elif isinstance(self.source, FileSource):
                source_file_name = abspath(self.source.filename)
                if not exists(source_file_name):
                    raise IOError("'%s' does not exist" % source_file_name)

            elif isinstance(self.source, ScriptWithFilesSource):
                source_file_name = join(
                        working_dir, self.source.source_name)
                with open(source_file_name, "w") as source_file:
                    source_file.write(self.source.source)

                from os.path import basename
                from shutil import copyfile
                for f in self.source.filenames:
                    copyfile(f, join(working_dir, basename(f)))

            else:
                raise RuntimeError("'source' type unrecognized")

            output_file_name = join(working_dir, self.output_file_name)
            cmdline = [
                    self.gmsh_executable,
                    "-o", self.output_file_name,
                    "-nopopup"]

            if self.dimensions is not None:
                cmdline.append("-%d" % self.dimensions)

            if self.order is not None:
                cmdline.extend(["-order", str(self.order)])

            if self.incomplete_elements is not None:
                cmdline.extend(["-string",
                    "Mesh.SecondOrderIncomplete = %d;"
                    % int(self.incomplete_elements)])

            cmdline.extend(self.other_options)
            cmdline.append(source_file_name)

            if self.dimensions is None:
                cmdline.append("-")

            logger.info("invoking gmsh: '%s'" % " ".join(cmdline))
            from pytools.prefork import call_capture_output
            retcode, stdout, stderr = call_capture_output(
                    cmdline, working_dir)
            logger.info("return from gmsh")

            stdout = stdout.decode("utf-8")
            stderr = stderr.decode("utf-8")

            if stderr and "error" in stderr.lower():
                msg = "gmsh execution failed with message:\n\n"
                if stdout:
                    msg += stdout+"\n"
                msg += stderr+"\n"
                raise GmshError(msg)

            if stderr:
                from warnings import warn

                msg = "gmsh issued the following messages:\n\n"
                if stdout:
                    msg += stdout+"\n"
                msg += stderr+"\n"
                warn(msg)

            self.output_file = open(output_file_name, "r")

            self.temp_dir_mgr = temp_dir_mgr
            return self
        except:
            temp_dir_mgr.clean_up()
            raise

    def __exit__(self, type, value, traceback):
        self.output_file.close()
        if self.temp_dir_mgr is not None:
            self.temp_dir_mgr.clean_up()

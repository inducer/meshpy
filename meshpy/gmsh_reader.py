from warnings import warn

from gmsh_interop.reader import *  # noqa: F403


warn("meshpy.gmsh_reader is deprecated. Use gmsh_interop.reader instead.",
     DeprecationWarning, stacklevel=2)

from warnings import warn

from gmsh_interop.runner import *  # noqa: F403


warn("meshpy.gmsh is deprecated. Use gmsh_interop.runner instead.",
     DeprecationWarning, stacklevel=2)

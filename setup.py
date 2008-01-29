#!/usr/bin/env python

import sys

def main():
    try:
        conf = {}
        execfile("siteconf.py", conf)
    except IOError:
        print "*** Please run configure first."
        sys.exit(1)

    from distutils.core import setup,Extension

    def non_matching_config():
        print "*** The version of your configuration template does not match"
        print "*** the version of the setup script. Please re-run configure."
        sys.exit(1)

    if "MESHPY_CONF_TEMPLATE_VERSION" not in conf:
        non_matching_config()

    if conf["MESHPY_CONF_TEMPLATE_VERSION"] != 1:
        non_matching_config()

    triangle_macros = [
      ( "EXTERNAL_TEST", 1 ),
      ( "ANSI_DECLARATORS", 1 ),
      ( "TRILIBRARY", 1 ) ,
      ]

    tetgen_macros = [
      ("TETLIBRARY", 1),
      ("SELF_CHECK", 1) ,
      ]

    INCLUDE_DIRS = conf["BOOST_INCLUDE_DIRS"]
    LIBRARY_DIRS = conf["BOOST_LIBRARY_DIRS"]
    LIBRARIES = conf["BPL_LIBRARIES"]

    execfile("src/python/__init__.py", conf)
    setup(name="MeshPy",
          version=conf["version"],
          description="A wrapper around the TetGen and Triangle",
          author="Andreas Kloeckner",
          author_email="inform@tiker.net",
          license = "BSD for the wrapper/non-commercial MIT for the meshers",
          url="http://news.tiker.net/software/meshpy",
          packages = [ "meshpy" ],
          package_dir={"meshpy": "src/python"},
          ext_modules = [
            Extension(
              "meshpy._triangle", 
              ["src/cpp/wrap_triangle.cpp","src/cpp/triangle.c"],
              include_dirs=INCLUDE_DIRS,
              library_dirs=LIBRARY_DIRS,
              libraries=LIBRARIES,
              define_macros=triangle_macros
              ),
            Extension(
              "meshpy._tetgen", 
              ["src/cpp/tetgen.cpp", "src/cpp/predicates.cpp", "src/cpp/wrap_tetgen.cpp"],
              include_dirs=INCLUDE_DIRS,
              library_dirs=LIBRARY_DIRS,
              libraries=LIBRARIES,
              define_macros=tetgen_macros
              ),
            ]
         )




if __name__ == '__main__':
    # hack distutils.sysconfig to eliminate debug flags
    # stolen from mpi4py
    import sys
    if not sys.platform.lower().startswith("win"):
        from distutils import sysconfig

        cvars = sysconfig.get_config_vars()
        cflags = cvars.get('OPT')
        if cflags:
            cflags = cflags.split()
            for bad_prefix in ('-g', '-O', '-Wstrict-prototypes'):
                for i, flag in enumerate(cflags):
                    if flag.startswith(bad_prefix):
                        cflags.pop(i)
                        break
                if flag in cflags:
                    cflags.remove(flag)
            cflags.append("-O3")
            cvars['OPT'] = str.join(' ', cflags)
            cvars["CFLAGS"] = cvars["BASECFLAGS"] + " " + cvars["OPT"]
    # and now call main
    main()

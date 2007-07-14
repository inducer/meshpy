vars = [
    ("BOOST_INC_DIR", None,
        "The include directory for all of Boost C++"),
    ("BOOST_LIB_DIR", None,
        "The library directory for all of Boost C++"),
    ("BOOST_PYTHON_LIBNAME", "boost_python-gcc41-mt",
        "The name of the Boost Python library binary (without lib and .so)"),
    ("CXXFLAGS", None,
        "Any extra C++ compiler options to include"),
    ]

subst_files = ["Makefile", "siteconf.py"]

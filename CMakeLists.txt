cmake_minimum_required(VERSION 3.5)
# by default use python3
# for python2 use -Dpy_version=2

if (NOT py_version LESS 3)
    find_package( Boost COMPONENTS "python3")
else()
    find_package( Boost COMPONENTS "python")
endif()

if(Boost_FOUND)
    include_directories(${Boost_INCLUDE_DIRS})
    MESSAGE(STATUS "VERSION: " ${Boost_LIB_VERSION})
    MESSAGE(STATUS "INCLUDE_DIRS: " ${Boost_INCLUDE_DIRS})
    MESSAGE(STATUS "LIB_DIRS: " ${Boost_LIBRARY_DIRS})
    MESSAGE(STATUS "LIBRARIES: " ${Boost_LIBRARIES})
endif()

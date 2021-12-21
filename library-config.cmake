include(FindPackageHandleStandardArgs)

file( GLOB {{libraryName}}_SRCS 
${ARDUINO_LIBRARY_PATH}/src/*.cpp
${ARDUINO_LIBRARY_PATH}/src/*.cxx
${ARDUINO_LIBRARY_PATH}/src/*.c
)

file( GLOB {{libraryName}}_HDRS
${ARDUINO_LIBRARY_PATH}/src/*.hpp
${ARDUINO_LIBRARY_PATH}/src/*.hxx
${ARDUINO_LIBRARY_PATH}/src/*.h
)

FIND_PACKAGE_HANDLE_STANDARD_ARGS({{libraryName}} {{libraryName}}_SRCS {{libraryName}}_HDRS)
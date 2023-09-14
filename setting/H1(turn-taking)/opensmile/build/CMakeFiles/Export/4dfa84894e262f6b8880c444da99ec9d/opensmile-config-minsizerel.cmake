#----------------------------------------------------------------
# Generated CMake target import file for configuration "MinSizeRel".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "opensmile" for configuration "MinSizeRel"
set_property(TARGET opensmile APPEND PROPERTY IMPORTED_CONFIGURATIONS MINSIZEREL)
set_target_properties(opensmile PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_MINSIZEREL "C;CXX"
  IMPORTED_LOCATION_MINSIZEREL "${_IMPORT_PREFIX}/lib/opensmile.lib"
  )

list(APPEND _cmake_import_check_targets opensmile )
list(APPEND _cmake_import_check_files_for_opensmile "${_IMPORT_PREFIX}/lib/opensmile.lib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)

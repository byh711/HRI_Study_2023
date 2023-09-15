#----------------------------------------------------------------
# Generated CMake target import file for configuration "MinSizeRel".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "SMILEapi" for configuration "MinSizeRel"
set_property(TARGET SMILEapi APPEND PROPERTY IMPORTED_CONFIGURATIONS MINSIZEREL)
set_target_properties(SMILEapi PROPERTIES
  IMPORTED_IMPLIB_MINSIZEREL "${_IMPORT_PREFIX}/lib/SMILEapi.lib"
  IMPORTED_LOCATION_MINSIZEREL "${_IMPORT_PREFIX}/bin/SMILEapi.dll"
  )

list(APPEND _cmake_import_check_targets SMILEapi )
list(APPEND _cmake_import_check_files_for_SMILEapi "${_IMPORT_PREFIX}/lib/SMILEapi.lib" "${_IMPORT_PREFIX}/bin/SMILEapi.dll" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)

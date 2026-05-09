vcpkg_from_git(
    OUT_SOURCE_PATH SOURCE_PATH
    URL https://github.com/BuildWithCollab/collab-core.git
    REF 95d12ef5766233661f1192bdbf1cf9bf4b392ae2
)

vcpkg_cmake_configure(
    SOURCE_PATH ${SOURCE_PATH}
)

vcpkg_cmake_install()

file(MAKE_DIRECTORY "${CURRENT_PACKAGES_DIR}/share/${PORT}")
file(INSTALL "${SOURCE_PATH}/LICENSE" DESTINATION "${CURRENT_PACKAGES_DIR}/share/${PORT}" RENAME copyright)

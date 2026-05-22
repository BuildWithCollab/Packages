package("collab-hpp")
    set_homepage("https://github.com/BuildWithCollab/collab.hpp")
    set_description("📜 Core library for Collab projects")
    add_urls("https://github.com/BuildWithCollab/collab.hpp/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("v1.0.0", "783e328aaf44931d3cb6846506910009c78df9cddb843cc18993cf46c1ae00c4")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
    add_deps("fmt")
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package)
-- [[ /GENERATED:install ]]
    end)

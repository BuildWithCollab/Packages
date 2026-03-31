package("collab-core")
    set_homepage("https://github.com/BuildWithCollab/collab-core")
    set_description("Collab Core ⚓")
    set_license("0BSD")
    add_urls("https://github.com/BuildWithCollab/collab-core/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("v0.1.0", "3e7d90bf9472d9fa122d6103349c1fa970d30e30d6a909dc7d73dbc959a110b4")
    add_versions("v0.2.0", "cafae39c8af142a4d58de78950a8cdc8b657580a7712c3f52b88702cb889e170")
    add_versions("v0.3.0", "ecb3541431a1612bc634842261d5619d61899f1156ea67aef9306c88a40755cf")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
    add_deps("fmt")
    add_deps("spdlog")
    add_deps("platformfolders")
-- [[ /GENERATED:deps ]]
-- [[ GENERATED:install ]]
    on_install(function (package)
        import("package.tools.xmake").install(package, { build_tests = false })
    end)
-- [[ /GENERATED:install ]]

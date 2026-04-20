package("def_type")
    set_homepage("https://github.com/BuildWithCollab/def_type")
    set_description("C++23 runtime type definitions with reflection")
    set_license("0BSD")
    add_urls("https://github.com/BuildWithCollab/def_type/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("1.0.0", "9310b4c3102cc28afc392c561847e6141f03487277e2403402516e8cb75f0b22")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
    add_deps("pfr_non_boost")
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package)
-- [[ /GENERATED:install ]]
    end)

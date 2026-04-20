package("def_type")
    set_homepage("https://github.com/BuildWithCollab/def_type")
    set_description("C++23 runtime type definitions with reflection")
    set_license("0BSD")
    add_urls("https://github.com/BuildWithCollab/def_type/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("1.0.0", "9310b4c3102cc28afc392c561847e6141f03487277e2403402516e8cb75f0b22")
    add_versions("1.0.1", "e8c70901818b3e28a1bb9c4f0a65f251a25780a41cf977452a3d1d6eb754fd3a")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
    add_deps("pfr_non_boost")
    add_deps("fmt")
    add_deps("unordered_dense")
    add_deps("magic_enum")
    add_deps("nameof")
    add_deps("nlohmann_json")
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package, { build_tests = false, enable_pfr = true })
-- [[ /GENERATED:install ]]
    end)

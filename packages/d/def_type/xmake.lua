package("def_type")
    set_homepage("https://github.com/BuildWithCollab/def_type")
    set_description("C++23 runtime type definitions with reflection")
    set_license("0BSD")
    add_urls("https://github.com/BuildWithCollab/def_type/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("1.0.0", "9310b4c3102cc28afc392c561847e6141f03487277e2403402516e8cb75f0b22")
    add_versions("1.0.1", "e8c70901818b3e28a1bb9c4f0a65f251a25780a41cf977452a3d1d6eb754fd3a")
    add_versions("1.1.0", "5431a88f7048aef800e93a4a217edc394d3a772005de4f32959f66ce8c27fb08")
    add_versions("1.2.0", "cacc549de2889438e8df6b89561c22b6a157dc7a68330e331de21b72c448b431")
    add_versions("1.3.0", "44c0a9b312fcb2386b2b003627c4baef4f0593946c8ce71266c03de01dce1a4d")
    add_versions("1.3.1", "140227054353d26ff1fd44bb1c7839f87d2c712901459405a5693db812b956dd")
    add_versions("1.3.2", "3f7fe90f77f71370f21dab086111ed1b7c9ec14ee0fdaba5610eb433f3ce494c")
    add_versions("1.4.0", "86fce60022bdc37ac6144343b0ca2a222908391f6cbec22b8cbda9318a10ae01")
    add_versions("1.5.0", "29ae3225d363302b67d39977e19933a96a51410097cc04bac1439db83113edc7")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
    add_deps("pfr_non_boost")
    add_deps("fmt")
    add_deps("unordered_dense")
    add_deps("magic_enum")
    add_deps("nameof")
    add_deps("nlohmann_json")
-- [[ /GENERATED:deps ]]

    add_configs("enable_pfr", { description = "Enable PFR backend", default = true, type = "boolean" })
    add_configs("nlohmann_json_pkg", { description = "Package to use for for nlohmann_jso", type = "string", default = "nlohmann_json" })
    
    on_load(function (package)
        package:add("deps", package:config("nlohmann_json_pkg"))
    end)
    
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package, { build_tests = false, enable_pfr = true })
-- [[ /GENERATED:install ]]
        if package:config("enable_pfr") then
            package:add("defines", "DEF_TYPE_HAS_PFR")
        end
    end)

package("nlohmann_json-module-support")
    set_homepage("https://github.com/BuildWithCollab/collab-json-fork")
    set_description("🍴 (Fork) JSON for Modern C++")
    set_license("MIT")
    add_urls("https://github.com/BuildWithCollab/collab-json-fork/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("fixes-4529", "c4b53b6e9832ed81e63fed599f06eb83e8e2b8c0707891ef55e8c964c473cf90")
    add_versions("v0.0.1", "f171b2a5ba74fdf288e40c8a1f6bd2259378af0afa2166c3438d15c56b4c4a6c")
    add_versions("v0.0.2", "fbbe4021b659033d362aa7b9acd2ee7256e4e117d52652b411a9b35cd3e11e43")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package)
-- [[ /GENERATED:install ]]
    end)

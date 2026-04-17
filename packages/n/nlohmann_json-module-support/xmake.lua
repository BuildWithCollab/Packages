package("nlohmann_json-module-support")
    set_homepage("https://github.com/BuildWithCollab/collab-json-fork")
    set_description("🍴 (Fork) JSON for Modern C++")
    set_license("MIT")
    add_urls("https://github.com/BuildWithCollab/collab-json-fork/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("fixes-4529", "c4b53b6e9832ed81e63fed599f06eb83e8e2b8c0707891ef55e8c964c473cf90")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package)
-- [[ /GENERATED:install ]]
    end)

package("dotenv")
    set_homepage("https://github.com/BuildWithCollab/dotenv")
    set_description(".env library and CLI 🔧")
    set_license("0BSD")
    add_urls("https://github.com/BuildWithCollab/dotenv/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("v1.0.2", "760a09c4b114436153e93677edeffe75d06af71f9c2e1f08469c30d3718fba8e")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
    add_deps("collab-core")
    add_deps("collab-process")
    add_deps("nlohmann_json")
    add_deps("yaml-cpp")
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package, { build_tests = false, build_executable = false })
-- [[ /GENERATED:install ]]
    end)

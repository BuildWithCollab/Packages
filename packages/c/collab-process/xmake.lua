package("collab-process")
    set_homepage("https://github.com/BuildWithCollab/collab-process")
    set_description("Collab Process 🔀")
    set_license("0BSD")
    add_urls("https://github.com/BuildWithCollab/collab-process/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("v0.1.0", "6dcf3892cfa577fe8c0a8b1cc6cce18c9826806de849bc16c294ff120c0623bc")
    add_versions("v0.2.0", "86d8acea2984f165575d2c9ec9c9fc62be7002da02a5f0e189f292e3d14300cc")
    add_versions("v0.3.0", "f40d07a5e0c382e689cb87849745a4ad6fa5c015e270aca2ae5331a80ff4e91f")
    add_versions("v1.0.0", "c94dcff16e4fd445616e19292b2b2e052bf5e2d3a46e55ecb9220dbda5159ee8")
    add_versions("v1.1.0", "b1c714f05614b75e25ba6a2162fffe1751155f3a0baaf88f2540fba95a5e090d")
    add_versions("v1.1.1", "2d59ab6ffd49668a0005514e2c57da60205f4c8adce32ff9013230717e683427")
    add_versions("v1.2.0", "cf44fd698cab6abb61bf2a5365660812646573bf045e8b40a6da8de972a20d60")
    add_versions("v1.2.1", "f60f5a37caee31167ed96300f16210b50d34e6285e8faa94b0a054dec08b4395")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
    add_deps("collab-core")
    add_deps("dotenv")
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package, { build_tests = false })
-- [[ /GENERATED:install ]]
    end)

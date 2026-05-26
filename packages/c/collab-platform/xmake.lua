package("collab-platform")
    set_homepage("https://github.com/BuildWithCollab/collab-platform")
    set_description("🖥️ Misc platform-specific fun times 🖥️")
    set_license("0BSD")
    add_urls("https://github.com/BuildWithCollab/collab-platform/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("v0.1.0", "927de311b7fcbf2ffb5a9e06bf92a2c8f674d4856d74aa77e4db2242ef1fd3e8")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
    add_deps("collab-core")
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package)
-- [[ /GENERATED:install ]]
    end)

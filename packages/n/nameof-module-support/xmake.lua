package("nameof-module-support")
    set_homepage("https://github.com/BuildWithCollab/collab-nameof-fork")
    set_description("🍴 (Fork) Nameof operator for modern C++, simply obtain the name of a variable, type, function, macro, and enum")
    set_license("MIT")
    add_urls("https://github.com/BuildWithCollab/collab-nameof-fork/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("v0.0.1", "8734b8ab157a342dc3f27caac31d1042238eea1b1f0f1ab6a35169f5b9439710")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package)
-- [[ /GENERATED:install ]]
    end)

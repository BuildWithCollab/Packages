package("stduuid")
    set_homepage("https://github.com/BuildWithCollab/collab-stduuid-fork")
    set_description("🍴 (Fork) A C++17 cross-platform implementation for UUIDs")
    set_license("MIT")
    add_urls("https://github.com/BuildWithCollab/collab-stduuid-fork/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("v1.2.3", "3fc6023246b35bcb2a9c295014f769afa4f0016eeb9ec2351a67dfd1d53c6f3b")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package)
-- [[ /GENERATED:install ]]
    end)

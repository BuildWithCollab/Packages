package("pfr_non_boost")
    set_homepage("https://github.com/BuildWithCollab/collab-pfr_non_boost-fork")
    set_description("🍴 (Fork) Boost.PFR without the boost namespaces")
    set_license("BSL-1.0")
    add_urls("https://github.com/BuildWithCollab/collab-pfr_non_boost-fork/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("2.3.2", "5d6a05bd657d2c3cda119d8a6ff8195be962e2679fe66b2e999838e54ccf2508")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package)
-- [[ /GENERATED:install ]]
    end)

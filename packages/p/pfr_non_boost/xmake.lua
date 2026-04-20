package("pfr_non_boost")
    set_homepage("https://github.com/BuildWithCollab/collab-pfr_non_boost-fork")
    set_description("🍴 (Fork) Boost.PFR without the boost namespaces")
    set_license("BSL-1.0")
    add_urls("https://github.com/BuildWithCollab/collab-pfr_non_boost-fork/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("2.3.2", "6a091e1cab3b7b8c51a0b5c046f1f99372f4d348452ed82d20b2cf0ab08718f6")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package)
-- [[ /GENERATED:install ]]
    end)

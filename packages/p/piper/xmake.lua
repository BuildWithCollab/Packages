package("piper")
    set_homepage("https://github.com/BuildWithCollab/collab-piper-fork")
    set_description("🍴 (Fork) A fast, local neural text to speech system")
    set_license("MIT")
    add_urls("https://github.com/BuildWithCollab/collab-piper-fork/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
    add_deps("piper-phonemize")
    add_deps("spdlog")
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package, { build_executable = false })
-- [[ /GENERATED:install ]]
    end)

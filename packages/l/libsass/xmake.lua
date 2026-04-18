package("libsass")
    set_homepage("https://github.com/BuildWithCollab/collab-libsass-fork")
    set_description("🍴 (Fork) A C/C++ implementation of a Sass compiler")
    set_license("NOASSERTION")
    add_urls("https://github.com/BuildWithCollab/collab-libsass-fork/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("3.6.6", "55994d7ae4eb23287dc6e951ae52d1b71678d3eaac7b9adefdf77bce2c990800")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package)
-- [[ /GENERATED:install ]]
    end)

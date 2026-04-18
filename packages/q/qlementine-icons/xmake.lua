package("qlementine-icons")
    set_homepage("https://github.com/BuildWithCollab/collab-qlementine-icons-fork")
    set_description("🍴 (Fork) 🍊 Modern icon set for desktop Qt applications.")
    set_license("MIT")
    add_urls("https://github.com/BuildWithCollab/collab-qlementine-icons-fork/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("v1.14.0", "c26a868694a1ffe1e9db5f12e9491e45115462bb35ea710be6295769b364cca1")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package)
-- [[ /GENERATED:install ]]
    end)

package("rnnoise")
    set_homepage("https://github.com/BuildWithCollab/collab-rnnoise-fork")
    set_description("🍴 (Fork) Recurrent neural network for audio noise reduction")
    set_license("BSD-3-Clause")
    add_urls("https://github.com/BuildWithCollab/collab-rnnoise-fork/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("v0.2.0", "e2540e2fc08ac7bb428a0bdb3e4b7fdc40008d749cf9784233035e99f407f4f9")
    add_versions("v0.2.1", "28ea8cfc6ea55d475c918463a402e94cd949c798a0b5167b20317ab278d15df5")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package)
-- [[ /GENERATED:install ]]
    end)

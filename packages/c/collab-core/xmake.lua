package("collab-core")
    set_homepage("https://github.com/BuildWithCollab/collab-core")
    set_description("Collab Core ⚓")
    set_license("0BSD")
    add_urls("https://github.com/BuildWithCollab/collab-core/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("v0.1.0", "3e7d90bf9472d9fa122d6103349c1fa970d30e30d6a909dc7d73dbc959a110b4")
    add_versions("v0.2.0", "cafae39c8af142a4d58de78950a8cdc8b657580a7712c3f52b88702cb889e170")
    add_versions("v0.3.0", "ecb3541431a1612bc634842261d5619d61899f1156ea67aef9306c88a40755cf")
    add_versions("v0.5.0", "4078c137a5afcb62866c8ece70a9f36706b7b04e469f8ddd6aa34a2352ce783c")
    add_versions("v0.6.0", "ae24dce9b557e9bb208cf03af48c708222aa74e57337e123b43221950d77335d")
    add_versions("v0.7.0", "08f63649f4d77a5968dfe6eea6523ff4008190248e07f04583ccb8fff63d3d74")
    add_versions("v0.8.0", "2ca3f680d3d067093dca83f1d2f5c538e0022fa65ac9473e632780890c2bdd5e")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
    add_deps("fmt")
    add_deps("spdlog")
    add_deps("platformfolders")
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package, { build_tests = false })
-- [[ /GENERATED:install ]]
    end)

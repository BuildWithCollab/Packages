package("espeak-ng")
    set_homepage("https://github.com/BuildWithCollab/collab-espeak-ng-fork")
    set_description("🍴 (Fork) eSpeak NG is an open source speech synthesizer that supports more than hundred languages and accents.")
    set_license("GPL-3.0")
    add_urls("https://github.com/BuildWithCollab/collab-espeak-ng-fork/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("2026.03.30-test1", "e0f3b1af52d234610ae01c2715725d376ab5090e5cbf713f6ba4ea9c5891c97e")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package)
-- [[ /GENERATED:install ]]
    end)

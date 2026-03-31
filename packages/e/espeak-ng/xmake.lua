package("espeak-ng")
    set_homepage("https://github.com/BuildWithCollab/collab-espeak-ng-fork")
    set_description("🍴 (Fork) eSpeak NG is an open source speech synthesizer that supports more than hundred languages and accents.")
    set_license("GPL-3.0")
    add_urls("https://github.com/BuildWithCollab/collab-espeak-ng-fork/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("2026.03.30-test1", "05a526d6d554da4ee4f05e2efdaa91ea66ff64f6159c0da5c7bc819ea7dd176d")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package)
-- [[ /GENERATED:install ]]
    end)

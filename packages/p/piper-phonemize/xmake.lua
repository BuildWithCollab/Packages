package("piper-phonemize")
    set_homepage("https://github.com/BuildWithCollab/collab-piper-phonemize-fork")
    set_description("🍴 (Fork) C++ library for converting text to phonemes for Piper")
    set_license("MIT")
    add_urls("https://github.com/BuildWithCollab/collab-piper-phonemize-fork/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("2026.03.30-test1", "6e5e249ad748d2cd5ccc23c637ec60725469f5fea2f7e890e1e2d1b9e8fea16f")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
    add_deps("espeak-ng")
    add_deps("onnxruntime")
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package)
-- [[ /GENERATED:install ]]
    end)

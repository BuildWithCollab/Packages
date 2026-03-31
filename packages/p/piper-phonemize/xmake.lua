package("piper-phonemize")
    set_homepage("https://github.com/BuildWithCollab/collab-piper-phonemize-fork")
    set_description("🍴 (Fork) C++ library for converting text to phonemes for Piper")
    set_license("MIT")
    add_urls("https://github.com/BuildWithCollab/collab-piper-phonemize-fork/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("2026.03.30-test1", "e9eb938916d342995827b047e61da06a7a4e90463963093e3f884e0c81af0d6d")
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

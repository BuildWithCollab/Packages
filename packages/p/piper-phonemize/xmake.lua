package("piper-phonemize")
    set_homepage("https://github.com/BuildWithCollab/collab-piper-phonemize-fork")
    set_description("🍴 (Fork) C++ library for converting text to phonemes for Piper")
    set_license("MIT")
    add_urls("https://github.com/BuildWithCollab/collab-piper-phonemize-fork/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
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

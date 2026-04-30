package("safetensors-cpp")
    set_homepage("https://github.com/BuildWithCollab/collab-safetensors-cpp-fork")
    set_description("🍴 (Fork) Header-only safetensors loader and saver in C++")
    set_license("MIT")
    add_urls("https://github.com/BuildWithCollab/collab-safetensors-cpp-fork/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
    add_versions("1.0.0", "9cf37e4465a3f666b8b597c88aa54ae0f12dc2a87f0d57cbaa1b0737326a41bb")
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package)
-- [[ /GENERATED:install ]]
    end)

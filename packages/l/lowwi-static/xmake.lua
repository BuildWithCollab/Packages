package("lowwi-static")
    set_homepage("https://github.com/BuildWithCollab/collab-lowwi-fork")
    set_description("🍴 (Fork) Lightweight OpenWakeWord Implementation written in C++. ")
    set_license("Apache-2.0")
    add_urls("https://github.com/BuildWithCollab/collab-lowwi-fork/archive/refs/tags/$(version).tar.gz")
-- [[ GENERATED:versions ]]
-- [[ /GENERATED:versions ]]
-- [[ GENERATED:deps ]]
    add_deps("onnxruntime-static")
-- [[ /GENERATED:deps ]]
    on_install(function (package)
-- [[ GENERATED:install ]]
        import("package.tools.xmake").install(package)
-- [[ /GENERATED:install ]]
    end)

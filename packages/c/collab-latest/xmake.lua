package("collab-latest")
    set_homepage("https://github.com/BuildWithCollab/collab.cpp")
    set_description("Papyrus script compiler for Skyrim modding")
    set_license("MIT")

    add_urls("https://github.com/BuildWithCollab/collab.cpp.git")
    add_versions("main", "main")

    add_deps("collab-hpp")
    add_deps("fmt")
    add_deps("spdlog")
    add_deps("rang")

    on_install(function(package)
        import("package.tools.xmake").install(package, { build_tests = false })
    end)
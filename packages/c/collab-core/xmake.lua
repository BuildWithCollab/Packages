package("collab-core")
    set_homepage("https://github.com/BuildWithCollab/collab-core")
    set_description("Shared foundation for BuildWithCollab C++ libraries")
    set_license("0BSD")

    add_urls("https://github.com/BuildWithCollab/collab-core/archive/refs/tags/$(version).tar.gz",
             "https://github.com/BuildWithCollab/collab-core.git")
    add_versions("v0.1.0", "0019dfc4b32d63c1392aa264aed2253c1e0c2fb09216f8e2cc269bbfb8bb49b5")

    add_deps("fmt")
    add_deps("spdlog")
    add_deps("platformfolders")

    on_install(function(package)
        import("package.tools.xmake").install(package, {
            build_tests = false
        })
    end)

    on_test(function(package)
        assert(package:check_cxxsnippets({test = [[
            void test() {
                constexpr collab::Version v{0, 1, 0};
                static_assert(v == collab::Version{0, 1, 0});
            }
        ]]}, {configs = {languages = "c++23"}, includes = "collab/version.hpp"}))
    end)

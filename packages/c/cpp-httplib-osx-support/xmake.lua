package("cpp-httplib-osx-support")
    set_kind("library", {headeronly = true})
    set_homepage("https://github.com/yhirose/cpp-httplib")
    set_description("cpp-httplib with macOS Security/CoreFoundation framework linking for SSL")
    set_license("MIT")

    set_urls("https://github.com/yhirose/cpp-httplib/archive/refs/tags/$(version).tar.gz",
             "https://github.com/yhirose/cpp-httplib.git")

    add_versions("v0.37.2", "909766cd7697153c9e588b0f96defe1868b7bb11d94b8d4f0c83bb4875bc9066")

    add_configs("ssl",  { description = "Requires OpenSSL", default = false, type = "boolean"})
    add_configs("zlib",  { description = "Requires Zlib", default = false, type = "boolean"})
    add_configs("brotli",  { description = "Requires Brotli", default = false, type = "boolean"})
    add_configs("exceptions", {description = "Enable the use of C++ exceptions", default = true, type = "boolean"})

    add_deps("cmake")

    if on_check then
        on_check(function (package)
            local pkg_ver = package:version()
            if package:is_plat("windows") then
                local winver = winos.version()
                local vs = package:toolchain("msvc"):config("vs")
                assert(winver and winver:gt("win8"), "package(httplib): Windows 8 or lower is neither supported nor tested.")
                if pkg_ver and pkg_ver:ge("0.19.0") then
                    assert(vs and tonumber(vs) > 2015, "package(httplib >= 0.19.0): VS 2015 or lower is neither supported nor tested.")
                elseif pkg_ver and pkg_ver:ge("0.11.0") then
                    assert(vs and tonumber(vs) > 2013, "package(httplib >= 0.11.0): VS 2013 or lower is neither supported nor tested.")
                end
            end
            if pkg_ver and pkg_ver:ge("0.15.0") and package:is_plat("msys", "mingw") then
                wprint("package(httplib): MSYS2 (including MinGW) is not officially supported or tested by httplib.")
            end
            if package:is_plat("android") then
                local ndk = package:toolchain("ndk")
                local ndk_sdkver = ndk:config("ndk_sdkver")
                assert(ndk_sdkver and tonumber(ndk_sdkver) >= 24, "package(httplib): need ndk api level >= 24 for android")
            end
            if pkg_ver and pkg_ver:ge("0.23.0") then
                if package:check_sizeof("void*") == "4" then
                    raise("package(cpp-httplib >=0.23.0) does not support 32-bit")
                end
            end
        end)
    end

    on_load(function (package)
        if package:config("ssl") then
            package:add("deps", "openssl" .. (package:version():ge("0.15.0") and "3" or ""))
            package:add("defines", "CPPHTTPLIB_OPENSSL_SUPPORT")
            if package:is_plat("macosx") then
                package:add("frameworks", "CoreFoundation", "Security")
            end
        end
        if package:config("zlib") then
            package:add("deps", "zlib")
            package:add("defines", "CPPHTTPLIB_ZLIB_SUPPORT")
        end
        if package:config("brotli") then
            package:add("deps", "brotli")
            package:add("defines", "CPPHTTPLIB_BROTLI_SUPPORT")
        end
    end)

    on_install("!cygwin", function (package)
        local configs = {"-DHTTPLIB_COMPILE=OFF"}
        table.insert(configs, "-DCMAKE_BUILD_TYPE=" .. (package:is_debug() and "Debug" or "Release"))
        table.insert(configs, "-DBUILD_SHARED_LIBS=" .. (package:config("shared") and "ON" or "OFF"))
        table.insert(configs, "-DHTTPLIB_REQUIRE_OPENSSL=" .. (package:config("ssl") and "ON" or "OFF"))
        table.insert(configs, "-DHTTPLIB_REQUIRE_ZLIB=" .. (package:config("zlib") and "ON" or "OFF"))
        table.insert(configs, "-DHTTPLIB_REQUIRE_BROTLI=" .. (package:config("brotli") and "ON" or "OFF"))
        table.insert(configs, "-DHTTPLIB_NO_EXCEPTIONS=" .. (package:config("exceptions") and "OFF" or "ON"))

        if package:config("ssl") then
            local openssl = package:dep("openssl" .. (package:version():ge("0.15.0") and "3" or ""))
            if not openssl:is_system() then
                table.insert(configs, "-DOPENSSL_ROOT_DIR=" .. openssl:installdir())
            end
        end
        import("package.tools.cmake").install(package, configs)
    end)

    on_test(function (package)
        assert(package:check_cxxsnippets({test = [[
            void test() {
                httplib::Client cli("http://cpp-httplib-server.yhirose.repl.co");
            }
        ]]}, {configs = {languages = "c++11"}, includes = "httplib.h"}))
    end)

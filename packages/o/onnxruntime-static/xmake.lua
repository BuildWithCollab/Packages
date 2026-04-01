package("onnxruntime-static")
    set_homepage("https://www.onnxruntime.ai")
    set_description("ONNX Runtime static library: cross-platform, high performance ML inferencing (CPU)")
    set_license("MIT")

    if is_plat("windows") and is_arch("x64") then
        set_urls("https://github.com/BuildWithCollab/Packages/releases/download/onnxruntime-static-v$(version)/onnxruntime-win-x64-static-$(version).tar.gz")
        add_versions("1.24.4", "2bfde0766375ab8a40c63120f7146b472d450a8ee2e72009483da1d559737b3d")
    elseif is_plat("macosx") and is_arch("arm64") then
        set_urls("https://github.com/BuildWithCollab/Packages/releases/download/onnxruntime-static-v$(version)/onnxruntime-osx-arm64-static-$(version).tar.gz")
        add_versions("1.24.4", "7487c0d29f20873902b82cc5a5492431d661caf041bafe6ef59b398f111771e3")
    elseif is_plat("linux") and is_arch("x86_64") then
        set_urls("https://github.com/BuildWithCollab/Packages/releases/download/onnxruntime-static-v$(version)/onnxruntime-linux-x64-static-$(version).tar.gz")
        add_versions("1.24.4", "ce49d8bd11c8607f6e8fd5863bcf45e0bc7eae19a22a130a2ba7e30f5b788fbb")
    end

    on_check(function (package)
        local supported = false
        if package:is_plat("windows") and package:is_arch("x64") then supported = true
        elseif package:is_plat("macosx") and package:is_arch("arm64") then supported = true
        elseif package:is_plat("linux") and package:is_arch("x86_64") then supported = true
        end
        if not supported then
            raise("onnxruntime-static: no static build for %s/%s. Use add_requires(\"onnxruntime\") with {configs = {gpu = true}} for dynamic GPU builds.", package:plat(), package:arch())
        end
    end)

    on_load(function (package)
        if package:is_plat("windows") then
            package:add("syslinks", "advapi32", "shell32", "ole32", "oleaut32", "user32", "ws2_32", "bcrypt", "dxcore")
        end
    end)

    on_install("windows|x64", "macosx|arm64", "linux|x86_64", function (package)
        os.cp("include/*", package:installdir("include"))
        os.cp("lib/*", package:installdir("lib"))
    end)

    on_test(function (package)
        assert(package:check_cxxsnippets({test = [[
            #include <array>
            #include <cstdint>
            void test() {
                std::array<float, 2> data = {0.0f, 0.0f};
                std::array<int64_t, 1> shape{2};
                Ort::Env env;
                auto memory_info = Ort::MemoryInfo::CreateCpu(OrtDeviceAllocator, OrtMemTypeCPU);
                auto tensor = Ort::Value::CreateTensor<float>(memory_info, data.data(), data.size(), shape.data(), shape.size());
            }
        ]]}, {configs = {languages = "c++17"}, includes = "onnxruntime_cxx_api.h"}))
    end)

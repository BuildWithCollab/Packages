-- 🌙 Moonshine Voice — on-device streaming speech-to-text, prebuilt C/C++ SDK.
--
-- Upstream publishes per-platform tarballs containing:
--   include/moonshine-c-api.h   C ABI (opaque int32 handles, error codes)
--   include/moonshine-cpp.h     header-only C++11 wrapper over the C ABI
--   lib/...                     macOS: fat static libmoonshine.a with ONNX
--                               Runtime compiled in. Linux: libmoonshine.so +
--                               libonnxruntime.so.1 ($ORIGIN rpath). Windows:
--                               moonshine.lib + helper .libs + onnxruntime.dll.
--
-- Consumers on Linux/Windows must ship the shared ONNX Runtime next to their
-- binary (see collab-stt providers/moonshine/xmake.lua for the copy pattern).
package("moonshine-voice")
    set_homepage("https://github.com/moonshine-ai/moonshine")
    set_description("Moonshine Voice: on-device streaming speech-to-text (prebuilt C/C++ SDK)")
    set_license("MIT")

    if is_plat("macosx") and is_arch("arm64") then
        set_urls("https://github.com/moonshine-ai/moonshine/releases/download/v$(version)/moonshine-voice-macos-arm64.tar.gz")
        add_versions("0.1.5", "51151f98eb1b20b8fc141bab361a1574dbfdbef8300b632ee6679e373112e0f6")
    elseif is_plat("linux") and is_arch("x86_64") then
        set_urls("https://github.com/moonshine-ai/moonshine/releases/download/v$(version)/moonshine-voice-linux-x86_64.tar.gz")
        add_versions("0.1.5", "9c3a87fea93ff2ad957938868f95a0a366dce9ff8ad86bde6cdcf5a4cadb51df")
    elseif is_plat("linux") and is_arch("arm64", "aarch64") then
        set_urls("https://github.com/moonshine-ai/moonshine/releases/download/v$(version)/moonshine-voice-linux-arm64.tar.gz")
        add_versions("0.1.5", "1600c80a0806b7a2582307c98e7a56f4072e4b060498b08a0b75eb20af42def2")
    elseif is_plat("windows") and is_arch("x64") then
        set_urls("https://github.com/moonshine-ai/moonshine/releases/download/v$(version)/moonshine-voice-windows-x86_64.tar.gz")
        add_versions("0.1.5", "97c1987e8e1cd77bb5fe3b12ce5aad5172637107e1dfda112ea9b21bac8f4b65")
    end

    on_check(function (package)
        local ok = (package:is_plat("macosx") and package:is_arch("arm64"))
                or (package:is_plat("linux") and package:is_arch("x86_64", "arm64", "aarch64"))
                or (package:is_plat("windows") and package:is_arch("x64"))
        if not ok then
            raise("moonshine-voice: no prebuilt SDK for %s/%s", package:plat(), package:arch())
        end
    end)

    on_load(function (package)
        if package:is_plat("macosx") then
            -- Static archive; ORT is inside it. Needs Apple frameworks.
            package:add("links", "moonshine")
            package:add("frameworks", "CoreFoundation", "Foundation")
        elseif package:is_plat("windows") then
            -- moonshine.lib is static and split into helper archives; ORT is a DLL + import lib.
            package:add("links", "moonshine", "moonshine-utils", "ort-utils", "bin-tokenizer", "onnxruntime")
        else
            -- Shared libmoonshine.so; it finds libonnxruntime.so.1 via its own $ORIGIN rpath.
            package:add("links", "moonshine")
        end
    end)

    on_install("macosx|arm64", "linux|x86_64", "linux|arm64", "linux|aarch64", "windows|x64", function (package)
        os.cp("include/*", package:installdir("include"))
        os.cp("lib/*", package:installdir("lib"))
        if package:is_plat("windows") then
            os.cp("lib/*.dll", package:installdir("bin"))
        end
    end)

    on_test(function (package)
        assert(package:has_cfuncs("moonshine_get_version", {includes = "moonshine-c-api.h"}))
    end)

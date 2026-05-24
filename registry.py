# Author: Mrowr Purr
# Description: A CLI tool to manage a registry.json file that defines
#              C++ packages for vcpkg and xmake registries.
#
# Usage:
# > python registry.py list
# > python registry.py list some-lib
# > python registry.py add some-lib mrowr/some-lib
# > python registry.py add some-lib mrowr/some-lib --branch my-branch --registries vcpkg
# > python registry.py add-version some-lib v1.0.0
# > python registry.py add-version some-lib --latest
# > python registry.py remove-version some-lib v1.0.0
# > python registry.py remove some-lib
# > python registry.py generate
#
# Implementation notes:
#
# > This script only uses the Python standard library
# > so that it is easy to share and run on any system
# > without requiring additional dependencies.
#
# > This script is intentionally stored in a single file
# > to make it easy to copy and paste into a project.

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

DEFAULT_REGISTRY_FILE = "registry.json"
VALID_REGISTRIES = ("vcpkg", "xmake")
VALID_BUILD_TOOLS = ("xmake", "cmake", "none")


# --- Registry data operations ---


def _migrate_pkg_in_place(pkg: dict) -> None:
    if "options" in pkg and "cmake-options" not in pkg:
        pkg["cmake-options"] = pkg.pop("options")


def _get_build_tool(pkg: dict) -> str:
    tool = pkg.get("build-tool")
    if tool:
        return tool
    return "none" if pkg.get("header-only") else "xmake"


def _default_cmake_option_name(feature_name: str) -> str:
    return feature_name.upper().replace("-", "_")


def _default_xmake_config_name(feature_name: str) -> str:
    return feature_name.replace("-", "_")


def load_registry(path: Path) -> dict:
    if not path.exists():
        return {"packages": {}}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for pkg in data.get("packages", {}).values():
        _migrate_pkg_in_place(pkg)
    return data


def save_registry(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def add_package(
    data: dict,
    name: str,
    repo: str,
    branch: str | None = None,
    registries: list[str] | None = None,
    header_only: bool = False,
    build_tool: str | None = None,
) -> dict:
    packages = data.setdefault("packages", {})
    if name in packages:
        print(f"Package '{name}' already exists.", file=sys.stderr)
        sys.exit(1)
    entry = {"repo": repo}
    if branch:
        entry["branch"] = branch
    if registries and set(registries) != set(VALID_REGISTRIES):
        entry["registries"] = registries
    if header_only:
        entry["header-only"] = True
    if build_tool:
        if build_tool not in VALID_BUILD_TOOLS:
            print(f"Invalid build-tool: '{build_tool}'. Valid options: {', '.join(VALID_BUILD_TOOLS)}", file=sys.stderr)
            sys.exit(1)
        entry["build-tool"] = build_tool
    packages[name] = entry
    return data


def remove_package(data: dict, name: str) -> dict:
    packages = data.get("packages", {})
    if name not in packages:
        print(f"Package '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    del packages[name]
    return data


def add_version(data: dict, name: str, version: str) -> dict:
    packages = data.get("packages", {})
    if name not in packages:
        print(f"Package '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    versions = packages[name].setdefault("versions", [])
    if version in versions:
        print(f"Version '{version}' already exists for '{name}'.", file=sys.stderr)
        sys.exit(1)
    versions.append(version)
    return data


def remove_version(data: dict, name: str, version: str) -> dict:
    packages = data.get("packages", {})
    if name not in packages:
        print(f"Package '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    versions = packages[name].get("versions", [])
    if version not in versions:
        print(f"Version '{version}' not found for '{name}'.", file=sys.stderr)
        sys.exit(1)
    versions.remove(version)
    if not versions:
        del packages[name]["versions"]
    return data


def list_packages(data: dict, name: str | None = None) -> None:
    packages = data.get("packages", {})
    if name:
        if name not in packages:
            print(f"Package '{name}' not found.", file=sys.stderr)
            sys.exit(1)
        pkg = packages[name]
        _migrate_pkg_in_place(pkg)
        print(f"{name} ({pkg['repo']})")
        if "branch" in pkg:
            print(f"  branch: {pkg['branch']}")
        registries = pkg.get("registries", list(VALID_REGISTRIES))
        print(f"  registries: {', '.join(registries)}")
        versions = pkg.get("versions", [])
        if versions:
            print(f"  versions:")
            for v in versions:
                print(f"    - {v}")
        else:
            print(f"  versions: (none)")
    else:
        if not packages:
            print("No packages.")
            return
        for pkg_name, pkg in packages.items():
            _migrate_pkg_in_place(pkg)
            registries = pkg.get("registries", list(VALID_REGISTRIES))
            version_count = len(pkg.get("versions", []))
            features = pkg.get("features", {})
            n_versions = f"{version_count} version" + ("s" if version_count != 1 else "")
            line = f"  {pkg_name} ({pkg['repo']}) [{', '.join(registries)}] ({n_versions}"
            if features:
                n_feat = len(features)
                line += f", {n_feat} feature" + ("s" if n_feat != 1 else "")
            line += ")"
            print(line)


def _format_dep_display(dep) -> str:
    if isinstance(dep, str):
        return dep
    name = dep["name"]
    parts = [name]
    if "version" in dep:
        parts[0] = f"{name} {dep['version']}"
    if "configs" in dep:
        configs = ", ".join(f"{k}={v}" for k, v in dep["configs"].items())
        parts.append(f"({configs})")
    return " ".join(parts)


def show_package(data: dict, name: str) -> None:
    packages = data.get("packages", {})
    if name not in packages:
        print(f"Package '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    pkg = packages[name]
    _migrate_pkg_in_place(pkg)

    print(f"{name}")
    print(f"  repo: {pkg['repo']}")
    if "branch" in pkg:
        print(f"  branch: {pkg['branch']}")
    print(f"  build-tool: {_get_build_tool(pkg)}")
    registries = pkg.get("registries", list(VALID_REGISTRIES))
    print(f"  registries: {', '.join(registries)}")
    if pkg.get("header-only"):
        print(f"  header-only: true")

    versions = pkg.get("versions", [])
    if versions:
        print(f"  versions:")
        for v in versions:
            print(f"    - {v}")

    for key, label in [("dependencies", "dependencies"), ("xmake-dependencies", "xmake-dependencies"), ("vcpkg-dependencies", "vcpkg-dependencies")]:
        deps = pkg.get(key, [])
        if deps:
            print(f"  {label}:")
            for d in deps:
                print(f"    - {_format_dep_display(d)}")

    if pkg.get("xmake-config"):
        print(f"  xmake-config:")
        for k, v in pkg["xmake-config"].items():
            print(f"    {k}: {v}")

    if pkg.get("cmake-options"):
        print(f"  cmake-options:")
        for o in pkg["cmake-options"]:
            print(f"    - {o}")

    features = pkg.get("features", {})
    if features:
        default_features = pkg.get("default-features", [])
        print(f"  features:")
        for fname, fdef in features.items():
            ftype = _feature_type(fdef)
            tag = " (default)" if ftype == "boolean" and fname in default_features else ""
            print(f"    {fname}{tag}:")
            if ftype != "boolean":
                print(f"      type: {ftype}")
            if fdef.get("description"):
                print(f"      description: {fdef['description']}")
            if "default" in fdef:
                print(f"      default: {fdef['default']}")
            if fdef.get("values"):
                print(f"      values: {', '.join(fdef['values'])}")
            if fdef.get("cmake-option"):
                print(f"      cmake-option: {fdef['cmake-option']}")
            if fdef.get("xmake-config"):
                print(f"      xmake-config: {fdef['xmake-config']}")
            if fdef.get("defines"):
                print(f"      defines:")
                for d in fdef["defines"]:
                    print(f"        - {d}")
            if fdef.get("dependencies"):
                print(f"      dependencies:")
                for d in fdef["dependencies"]:
                    print(f"        - {_format_dep_display(d)}")


def parse_kv_pair(s: str):
    if "=" not in s:
        return s, True
    key, val = s.split("=", 1)
    if val.lower() == "true":
        return key, True
    if val.lower() == "false":
        return key, False
    try:
        return key, int(val)
    except ValueError:
        pass
    try:
        return key, float(val)
    except ValueError:
        pass
    return key, val


def _deps_key(registry: str | None = None) -> str:
    if registry == "xmake":
        return "xmake-dependencies"
    if registry == "vcpkg":
        return "vcpkg-dependencies"
    return "dependencies"


def _get_feature_or_exit(pkg: dict, pkg_name: str, feature: str) -> dict:
    features = pkg.get("features", {})
    if feature not in features:
        print(f"Feature '{feature}' not found in '{pkg_name}'.", file=sys.stderr)
        sys.exit(1)
    return features[feature]


def _feature_type(fdef: dict) -> str:
    return fdef.get("type", "boolean")


def _require_boolean_feature(fdef: dict, feature: str, pkg_name: str, op_label: str) -> None:
    if _feature_type(fdef) != "boolean":
        print(
            f"Cannot {op_label} on non-boolean feature '{feature}' of '{pkg_name}' (string features can't have deps or defines).",
            file=sys.stderr,
        )
        sys.exit(1)


def add_dependency(
    data: dict,
    name: str,
    dep_name: str,
    configs: dict | None = None,
    registry: str | None = None,
    version: str | None = None,
    feature: str | None = None,
) -> dict:
    packages = data.get("packages", {})
    if name not in packages:
        print(f"Package '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    if feature:
        if registry:
            print("--feature cannot be combined with --xmake or --vcpkg.", file=sys.stderr)
            sys.exit(1)
        fdef = _get_feature_or_exit(packages[name], name, feature)
        _require_boolean_feature(fdef, feature, name, "add a dep")
        deps = fdef.setdefault("dependencies", [])
        scope_label = f"feature '{feature}' of '{name}'"
    else:
        key = _deps_key(registry)
        deps = packages[name].setdefault(key, [])
        scope_label = f"'{key}' for '{name}'"
    for d in deps:
        existing_name = d if isinstance(d, str) else d["name"]
        if existing_name == dep_name:
            print(f"Dependency '{dep_name}' already exists in {scope_label}.", file=sys.stderr)
            sys.exit(1)
    if configs or version:
        entry = {"name": dep_name}
        if version:
            entry["version"] = version
        if configs:
            entry["configs"] = configs
        deps.append(entry)
    else:
        deps.append(dep_name)
    return data


def remove_dependency(
    data: dict,
    name: str,
    dep_name: str,
    registry: str | None = None,
    feature: str | None = None,
) -> dict:
    packages = data.get("packages", {})
    if name not in packages:
        print(f"Package '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    if feature:
        if registry:
            print("--feature cannot be combined with --xmake or --vcpkg.", file=sys.stderr)
            sys.exit(1)
        fdef = _get_feature_or_exit(packages[name], name, feature)
        _require_boolean_feature(fdef, feature, name, "remove a dep")
        deps = fdef.get("dependencies", [])
        scope_label = f"feature '{feature}' of '{name}'"
        container = fdef
        key = "dependencies"
    else:
        key = _deps_key(registry)
        deps = packages[name].get(key, [])
        scope_label = f"'{key}' for '{name}'"
        container = packages[name]
    new_deps = []
    found = False
    for d in deps:
        existing_name = d if isinstance(d, str) else d["name"]
        if existing_name == dep_name:
            found = True
        else:
            new_deps.append(d)
    if not found:
        print(f"Dependency '{dep_name}' not found in {scope_label}.", file=sys.stderr)
        sys.exit(1)
    if new_deps:
        container[key] = new_deps
    else:
        if key in container:
            del container[key]
    return data


def set_config(data: dict, name: str, key: str, value) -> dict:
    packages = data.get("packages", {})
    if name not in packages:
        print(f"Package '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    config = packages[name].setdefault("xmake-config", {})
    config[key] = value
    return data


# --- Feature data operations ---


def add_feature(
    data: dict,
    name: str,
    feature: str,
    description: str = "",
    cmake_option: str | None = None,
    xmake_config: str | None = None,
    type_: str = "boolean",
    default: str | None = None,
    values: list[str] | None = None,
) -> dict:
    if type_ not in ("boolean", "string"):
        print(f"Invalid feature type: '{type_}'. Valid: 'boolean', 'string'.", file=sys.stderr)
        sys.exit(1)
    if type_ == "string" and default is None:
        print(f"String features require --default.", file=sys.stderr)
        sys.exit(1)
    if type_ == "boolean" and (default is not None or values):
        print(f"--default and --value are only valid for string features (--type string).", file=sys.stderr)
        sys.exit(1)
    packages = data.get("packages", {})
    if name not in packages:
        print(f"Package '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    features = packages[name].setdefault("features", {})
    if feature in features:
        print(f"Feature '{feature}' already exists for '{name}'.", file=sys.stderr)
        sys.exit(1)
    fdef: dict = {"description": description}
    if type_ != "boolean":
        fdef["type"] = type_
    if default is not None:
        fdef["default"] = default
    if values:
        fdef["values"] = list(values)
    if cmake_option:
        fdef["cmake-option"] = cmake_option
    if xmake_config:
        fdef["xmake-config"] = xmake_config
    features[feature] = fdef
    return data


def remove_feature(data: dict, name: str, feature: str) -> dict:
    packages = data.get("packages", {})
    if name not in packages:
        print(f"Package '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    features = packages[name].get("features", {})
    if feature not in features:
        print(f"Feature '{feature}' not found in '{name}'.", file=sys.stderr)
        sys.exit(1)
    del features[feature]
    if not features:
        del packages[name]["features"]
    default_features = packages[name].get("default-features", [])
    if feature in default_features:
        default_features.remove(feature)
        if not default_features:
            del packages[name]["default-features"]
    return data


def set_feature(
    data: dict,
    name: str,
    feature: str,
    description: str | None = None,
    cmake_option: str | None = None,
    xmake_config: str | None = None,
    default: str | None = None,
    values: list[str] | None = None,
) -> dict:
    packages = data.get("packages", {})
    if name not in packages:
        print(f"Package '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    fdef = _get_feature_or_exit(packages[name], name, feature)
    if description is not None:
        fdef["description"] = description
    if cmake_option is not None:
        fdef["cmake-option"] = cmake_option
    if xmake_config is not None:
        fdef["xmake-config"] = xmake_config
    if default is not None:
        if _feature_type(fdef) != "string":
            print(f"--default is only valid for string features.", file=sys.stderr)
            sys.exit(1)
        fdef["default"] = default
    if values:
        if _feature_type(fdef) != "string":
            print(f"--value is only valid for string features.", file=sys.stderr)
            sys.exit(1)
        fdef["values"] = list(values)
    return data


def add_define(data: dict, name: str, feature: str, macro: str) -> dict:
    packages = data.get("packages", {})
    if name not in packages:
        print(f"Package '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    fdef = _get_feature_or_exit(packages[name], name, feature)
    _require_boolean_feature(fdef, feature, name, "add a define")
    defines = fdef.setdefault("defines", [])
    if macro in defines:
        print(f"Define '{macro}' already exists in feature '{feature}' of '{name}'.", file=sys.stderr)
        sys.exit(1)
    defines.append(macro)
    return data


def remove_define(data: dict, name: str, feature: str, macro: str) -> dict:
    packages = data.get("packages", {})
    if name not in packages:
        print(f"Package '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    fdef = _get_feature_or_exit(packages[name], name, feature)
    _require_boolean_feature(fdef, feature, name, "remove a define")
    defines = fdef.get("defines", [])
    if macro not in defines:
        print(f"Define '{macro}' not found in feature '{feature}' of '{name}'.", file=sys.stderr)
        sys.exit(1)
    defines.remove(macro)
    if not defines and "defines" in fdef:
        del fdef["defines"]
    return data


def set_default_features(data: dict, name: str, features: list[str]) -> dict:
    packages = data.get("packages", {})
    if name not in packages:
        print(f"Package '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    declared = packages[name].get("features", {})
    for f in features:
        if f not in declared:
            print(f"Feature '{f}' not declared on '{name}'. Add it first with add-feature.", file=sys.stderr)
            sys.exit(1)
    if features:
        packages[name]["default-features"] = list(features)
    elif "default-features" in packages[name]:
        del packages[name]["default-features"]
    return data


def set_build_tool(data: dict, name: str, build_tool: str) -> dict:
    packages = data.get("packages", {})
    if name not in packages:
        print(f"Package '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    if build_tool not in VALID_BUILD_TOOLS:
        print(f"Invalid build-tool: '{build_tool}'. Valid options: {', '.join(VALID_BUILD_TOOLS)}", file=sys.stderr)
        sys.exit(1)
    packages[name]["build-tool"] = build_tool
    return data


def set_cmake_option(data: dict, name: str, key: str, value: str) -> dict:
    packages = data.get("packages", {})
    if name not in packages:
        print(f"Package '{name}' not found.", file=sys.stderr)
        sys.exit(1)
    options = packages[name].setdefault("cmake-options", [])
    new_entry = f"{key}={value}"
    for i, opt in enumerate(options):
        if opt.split("=", 1)[0] == key:
            options[i] = new_entry
            return data
    options.append(new_entry)
    return data


def get_package_registries(pkg: dict) -> list[str]:
    return pkg.get("registries", list(VALID_REGISTRIES))


# --- GitHub API ---


def _github_request(url: str) -> Request:
    req = Request(url)
    token = os.environ.get("GH_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    return req


def _github_fetch_json(url: str, context: str = "") -> dict | list:
    try:
        with urlopen(_github_request(url)) as response:
            return json.load(response)
    except HTTPError as e:
        if e.code == 404:
            print(f"Repository not found: {context or url}", file=sys.stderr)
            print("Is the repository private? This tool requires public repositories (or set GH_TOKEN for private repos).", file=sys.stderr)
        elif e.code == 403:
            print(f"Access denied: {context or url}", file=sys.stderr)
            print("You may be rate-limited. Set GH_TOKEN to authenticate requests.", file=sys.stderr)
        else:
            print(f"GitHub API error ({e.code}): {context or url}", file=sys.stderr)
        sys.exit(1)


def get_latest_tag(repo: str) -> str:
    tags = _github_fetch_json(
        f"https://api.github.com/repos/{repo}/tags", context=repo
    )
    if not tags:
        print(f"No tags found for '{repo}'.", file=sys.stderr)
        sys.exit(1)
    return tags[0]["name"]


def get_repo_info(repo: str) -> dict:
    data = _github_fetch_json(
        f"https://api.github.com/repos/{repo}", context=repo
    )
    return {
        "description": data.get("description") or "",
        "license": (data.get("license") or {}).get("spdx_id") or "",
    }


def get_commit_info_for_ref(repo: str, ref: str) -> dict:
    data = _github_fetch_json(
        f"https://api.github.com/repos/{repo}/commits/{ref}", context=f"{repo}@{ref}"
    )
    return {
        "sha": data["sha"],
        "date": data["commit"]["committer"]["date"][:10],
    }


def fetch_tarball_sha256(repo: str, version: str) -> str:
    url = f"https://github.com/{repo}/archive/refs/tags/{version}.tar.gz"
    try:
        with urlopen(_github_request(url)) as response:
            data = response.read()
    except HTTPError as e:
        if e.code == 404:
            print(f"Tarball not found: {repo}@{version}", file=sys.stderr)
            print("Does this tag exist?", file=sys.stderr)
        else:
            print(f"Failed to download tarball ({e.code}): {repo}@{version}", file=sys.stderr)
        sys.exit(1)
    return hashlib.sha256(data).hexdigest()


# --- Git operations ---


def git_exec(args: list[str], working_dir: str | None = None) -> str:
    result = subprocess.run(
        ["git"] + [str(a) for a in args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=working_dir,
    )
    if result.returncode != 0:
        text_args = " ".join(str(a) for a in args)
        print(f"git {text_args} failed: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def git_tree_sha_for_path(path: str, working_dir: str | None = None) -> str:
    return git_exec(["rev-parse", f"HEAD:{path}"], working_dir)


# --- xmake generation ---


def xmake_package_dir(root: Path, name: str) -> Path:
    return root / "packages" / name[0].lower() / name


def _lua_value(val) -> str:
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, str):
        return f'"{val}"'
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, dict):
        pairs = ", ".join(f"{k} = {_lua_value(v)}" for k, v in val.items())
        return "{ " + pairs + " }"
    return str(val)


def _format_xmake_dep(dep) -> str:
    if isinstance(dep, str):
        return f'    add_deps("{dep}")'
    name = dep["name"]
    version = dep.get("version", "")
    configs = dep.get("configs", {})
    name_str = f"{name} {version}" if version else name
    if configs:
        return f'    add_deps("{name_str}", {{ configs = {_lua_value(configs)} }})'
    return f'    add_deps("{name_str}")'


MARKER_START = "-- [[ GENERATED:{section} ]]"
MARKER_END = "-- [[ /GENERATED:{section} ]]"


def _marker_start(section: str) -> str:
    return MARKER_START.format(section=section)


def _marker_end(section: str) -> str:
    return MARKER_END.format(section=section)


def _generate_xmake_versions_block(versions: list[str], version_hashes: dict[str, str]) -> list[str]:
    lines = []
    for version in versions:
        sha = version_hashes.get(version, "")
        lines.append(f'    add_versions("{version}", "{sha}")')
    return lines


def _generate_xmake_deps_block(dependencies: list) -> list[str]:
    lines = []
    for dep in dependencies:
        lines.append(_format_xmake_dep(dep))
    return lines


def _generate_xmake_configs_block(features: dict, default_features: list[str]) -> list[str]:
    lines = []
    default_features = default_features or []
    for fname, fdef in features.items():
        desc = (fdef.get("description") or "").replace('"', '\\"')
        if _feature_type(fdef) == "string":
            default_val = (fdef.get("default") or "").replace('"', '\\"')
            attrs = [
                f'description = "{desc}"',
                f'default = "{default_val}"',
                'type = "string"',
            ]
            if fdef.get("values"):
                vals = ", ".join(f'"{str(v).replace(chr(34), chr(92) + chr(34))}"' for v in fdef["values"])
                attrs.append(f'values = {{ {vals} }}')
            lines.append(f'    add_configs("{fname}", {{ {", ".join(attrs)} }})')
        else:
            is_default = "true" if fname in default_features else "false"
            lines.append(
                f'    add_configs("{fname}", {{ description = "{desc}", default = {is_default}, type = "boolean" }})'
            )
    return lines


def _generate_xmake_deps_and_defines_block(features: dict) -> list[str]:
    lines = []
    for fname, fdef in features.items():
        if _feature_type(fdef) != "boolean":
            continue
        deps = fdef.get("dependencies", []) or []
        defines = fdef.get("defines", []) or []
        if not deps and not defines:
            continue
        lines.append(f'        if package:config("{fname}") then')
        for dep in deps:
            if isinstance(dep, str):
                lines.append(f'            package:add("deps", "{dep}")')
            else:
                dname = dep["name"]
                version = dep.get("version", "")
                name_str = f"{dname} {version}" if version else dname
                configs = dep.get("configs", {})
                if configs:
                    lines.append(
                        f'            package:add("deps", "{name_str}", {{ configs = {_lua_value(configs)} }})'
                    )
                else:
                    lines.append(f'            package:add("deps", "{name_str}")')
        for define in defines:
            lines.append(f'            package:add("defines", "{define}")')
        lines.append("        end")
    return lines


def _generate_xmake_install_block(
    build_tool: str,
    xmake_config: dict | None,
    cmake_options: list[str] | None,
    features: dict | None,
) -> list[str]:
    features = features or {}
    xmake_config = xmake_config or {}
    cmake_options = cmake_options or []

    if build_tool == "none":
        return ['        os.cp("include", package:installdir())']

    if build_tool == "cmake":
        static_keys = {opt.split("=", 1)[0] for opt in cmake_options}
        feature_lines = []
        for fname, fdef in features.items():
            opt_name = fdef.get("cmake-option") or _default_cmake_option_name(fname)
            if opt_name in static_keys:
                continue
            if _feature_type(fdef) == "string":
                feature_lines.append(
                    f'        table.insert(configs, "-D{opt_name}=" .. package:config("{fname}"))'
                )
            else:
                feature_lines.append(
                    f'        table.insert(configs, "-D{opt_name}=" .. (package:config("{fname}") and "ON" or "OFF"))'
                )
        if not cmake_options and not feature_lines:
            return ['        import("package.tools.cmake").install(package)']
        opts_str = ", ".join(f'"-D{o}"' for o in cmake_options)
        lines = [f'        local configs = {{ {opts_str} }}'] if cmake_options else ['        local configs = {}']
        lines.extend(feature_lines)
        lines.append('        import("package.tools.cmake").install(package, configs)')
        return lines

    # build_tool == "xmake"
    if not features:
        if xmake_config:
            config_str = _lua_value(xmake_config)
            return [f'        import("package.tools.xmake").install(package, {config_str})']
        return ['        import("package.tools.xmake").install(package)']
    if xmake_config:
        lines = [f'        local configs = {_lua_value(xmake_config)}']
    else:
        lines = ['        local configs = {}']
    for fname, fdef in features.items():
        xc = fdef.get("xmake-config") or _default_xmake_config_name(fname)
        if _feature_type(fdef) == "string":
            lines.append(
                f'        if configs.{xc} == nil then configs.{xc} = package:config("{fname}") end'
            )
        else:
            lines.append(
                f'        if package:config("{fname}") and configs.{xc} == nil then configs.{xc} = true end'
            )
    lines.append('        import("package.tools.xmake").install(package, configs)')
    return lines


def generate_xmake_lua(
    name: str,
    repo: str,
    description: str,
    versions: list[str],
    version_hashes: dict[str, str],
    dependencies: list | None = None,
    header_only: bool = False,
    license: str = "",
    xmake_config: dict | None = None,
    build_tool: str | None = None,
    cmake_options: list[str] | None = None,
    features: dict | None = None,
    default_features: list[str] | None = None,
) -> str:
    if build_tool is None:
        build_tool = "none" if header_only else "xmake"
    features = features or {}
    default_features = default_features or []

    lines = []
    lines.append(f'package("{name}")')
    if header_only:
        lines.append('    set_kind("library", {headeronly = true})')
    lines.append(f'    set_homepage("https://github.com/{repo}")')
    lines.append(f'    set_description("{description}")')
    if license:
        lines.append(f'    set_license("{license}")')
    lines.append(f'    add_urls("https://github.com/{repo}/archive/refs/tags/$(version).tar.gz")')

    lines.append(_marker_start("versions"))
    lines.extend(_generate_xmake_versions_block(versions, version_hashes))
    lines.append(_marker_end("versions"))

    if features:
        lines.append(_marker_start("configs"))
        lines.extend(_generate_xmake_configs_block(features, default_features))
        lines.append(_marker_end("configs"))

    lines.append(_marker_start("deps"))
    if dependencies:
        lines.extend(_generate_xmake_deps_block(dependencies))
    lines.append(_marker_end("deps"))

    if features:
        lines.append('    on_load(function (package)')
        lines.append(_marker_start("deps_and_defines"))
        lines.extend(_generate_xmake_deps_and_defines_block(features))
        lines.append(_marker_end("deps_and_defines"))
        lines.append('    end)')

    lines.append('    on_install(function (package)')
    lines.append(_marker_start("install"))
    lines.extend(_generate_xmake_install_block(build_tool, xmake_config, cmake_options, features))
    lines.append(_marker_end("install"))
    lines.append('    end)')

    return "\n".join(lines) + "\n"


def _insert_configs_marker(content: str) -> str:
    start = _marker_start("configs")
    if start in content:
        return content
    versions_end = _marker_end("versions")
    if versions_end not in content:
        return content
    idx = content.index(versions_end) + len(versions_end)
    insertion = f"\n{start}\n{_marker_end('configs')}"
    return content[:idx] + insertion + content[idx:]


def _insert_on_load_block(content: str) -> str:
    start = _marker_start("deps_and_defines")
    if start in content:
        return content
    # Find on_install line to insert on_load right before it
    needle = "    on_install(function"
    if needle not in content:
        return content
    idx = content.index(needle)
    block = (
        "    on_load(function (package)\n"
        f"{start}\n"
        f"{_marker_end('deps_and_defines')}\n"
        "    end)\n"
    )
    return content[:idx] + block + content[idx:]


def update_xmake_lua(
    existing_content: str,
    versions: list[str],
    version_hashes: dict[str, str],
    dependencies: list | None = None,
    header_only: bool = False,
    xmake_config: dict | None = None,
    build_tool: str | None = None,
    cmake_options: list[str] | None = None,
    features: dict | None = None,
    default_features: list[str] | None = None,
) -> str:
    if build_tool is None:
        build_tool = "none" if header_only else "xmake"
    features = features or {}
    default_features = default_features or []

    result = existing_content
    if features:
        result = _insert_configs_marker(result)
        result = _insert_on_load_block(result)

    sections = {
        "versions": "\n".join(_generate_xmake_versions_block(versions, version_hashes)),
        "configs": "\n".join(_generate_xmake_configs_block(features, default_features)),
        "deps": "\n".join(_generate_xmake_deps_block(dependencies or [])),
        "deps_and_defines": "\n".join(_generate_xmake_deps_and_defines_block(features)),
        "install": "\n".join(_generate_xmake_install_block(build_tool, xmake_config, cmake_options, features)),
    }

    for section, new_content in sections.items():
        start = _marker_start(section)
        end = _marker_end(section)
        if start in result and end in result:
            before = result[:result.index(start) + len(start)]
            after = result[result.index(end):]
            if new_content:
                result = before + "\n" + new_content + "\n" + after
            else:
                result = before + "\n" + after

    return result


# --- vcpkg generation ---


def vcpkg_port_name(name: str) -> str:
    name = name.replace("_", "-").lower()
    name = re.sub(r"[^a-z0-9-]", "", name)
    name = re.sub(r"-+", "-", name)
    name = name.strip("-")
    return name


def vcpkg_version_string(date: str, sha: str) -> str:
    return f"{date}-{sha[:7]}"


def vcpkg_port_dir(root: Path, name: str) -> Path:
    pname = vcpkg_port_name(name)
    return root / "ports" / pname


def vcpkg_version_dir(root: Path, name: str) -> Path:
    pname = vcpkg_port_name(name)
    return root / "versions" / f"{pname[0]}-"


def vcpkg_version_file(root: Path, name: str) -> Path:
    pname = vcpkg_port_name(name)
    return vcpkg_version_dir(root, name) / f"{pname}.json"


def vcpkg_baseline_file(root: Path) -> Path:
    return root / "versions" / "baseline.json"


def generate_portfile_cmake(
    repo: str,
    ref: str,
    header_only: bool = False,
    options: list[str] | None = None,
    features: dict | None = None,
) -> str:
    features = features or {}

    feature_check_block = ""
    if features:
        mappings = []
        for fname, fdef in features.items():
            opt = fdef.get("cmake-option") or _default_cmake_option_name(fname)
            mappings.append(f"        {fname} {opt}")
        feature_check_block = (
            "\nvcpkg_check_features(OUT_FEATURE_OPTIONS FEATURE_OPTIONS\n"
            "    FEATURES\n"
            + "\n".join(mappings)
            + "\n)\n"
        )

    if features:
        options_lines = ["        ${FEATURE_OPTIONS}"]
        if options:
            options_lines.extend(f"        -D{opt}" for opt in options)
        options_text = "\n    OPTIONS\n" + "\n".join(options_lines)
    elif options:
        options_text = "\n    OPTIONS " + " ".join(f"-D{opt}" for opt in options)
    else:
        options_text = ""

    cleanup = ""
    if header_only:
        cleanup = """
file(REMOVE_RECURSE
    "${CURRENT_PACKAGES_DIR}/debug"
    "${CURRENT_PACKAGES_DIR}/lib"
)"""

    return f"""vcpkg_from_git(
    OUT_SOURCE_PATH SOURCE_PATH
    URL https://github.com/{repo}.git
    REF {ref}
){feature_check_block}
vcpkg_cmake_configure(
    SOURCE_PATH ${{SOURCE_PATH}}{options_text}
)

vcpkg_cmake_install(){cleanup}

file(MAKE_DIRECTORY "${{CURRENT_PACKAGES_DIR}}/share/${{PORT}}")
file(INSTALL "${{SOURCE_PATH}}/LICENSE" DESTINATION "${{CURRENT_PACKAGES_DIR}}/share/${{PORT}}" RENAME copyright)
"""


def _translate_dep_for_vcpkg(dep, owner_name: str):
    if isinstance(dep, str):
        return vcpkg_port_name(dep)
    dep_name = dep["name"]
    configs = dep.get("configs", {}) or {}
    bool_features = [k for k, v in configs.items() if v is True]
    non_bool = {k: v for k, v in configs.items() if not isinstance(v, bool)}
    if non_bool:
        print(
            f"Warning: non-boolean configs on dep '{dep_name}' of '{owner_name}' cannot translate to vcpkg features and will be dropped: {non_bool}",
            file=sys.stderr,
        )
    if bool_features:
        return {"name": vcpkg_port_name(dep_name), "features": bool_features}
    return vcpkg_port_name(dep_name)


def generate_vcpkg_json(
    name: str,
    description: str,
    version_string: str,
    dependencies: list | None = None,
    features: dict | None = None,
    default_features: list[str] | None = None,
) -> dict:
    pname = vcpkg_port_name(name)
    vcpkg_json: dict = {
        "name": pname,
        "version-string": version_string,
        "description": description,
        "dependencies": [
            {"name": "vcpkg-cmake", "host": True},
            {"name": "vcpkg-cmake-config", "host": True},
        ],
    }
    for dep in (dependencies or []):
        vcpkg_json["dependencies"].append(_translate_dep_for_vcpkg(dep, name))

    features = features or {}
    if features:
        feat_block: dict = {}
        for fname, fdef in features.items():
            entry: dict = {"description": fdef.get("description", "")}
            fdeps = fdef.get("dependencies", []) or []
            if fdeps:
                entry["dependencies"] = [_translate_dep_for_vcpkg(d, name) for d in fdeps]
            feat_block[fname] = entry
        vcpkg_json["features"] = feat_block
        if default_features:
            vcpkg_json["default-features"] = list(default_features)

    return vcpkg_json


def generate_vcpkg_versions_json(versions: list[dict]) -> dict:
    return {"versions": versions}


def generate_vcpkg_baseline(packages: dict[str, str]) -> dict:
    default = {}
    for name, version_string in packages.items():
        default[name] = {"baseline": version_string, "port-version": 0}
    return {"default": default}


# --- generate orchestrator ---


SHA256_CACHE_FILE = ".sha256-cache.json"


def _load_sha256_cache(root: Path) -> dict:
    cache_path = root / SHA256_CACHE_FILE
    if cache_path.exists():
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_sha256_cache(root: Path, cache: dict) -> None:
    cache_path = root / SHA256_CACHE_FILE
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)
        f.write("\n")


def _cached_fetch(fetch_fn, cache: dict):
    def wrapper(kind, **kwargs):
        if kind == "tarball_sha256":
            key = f"{kwargs['repo']}@{kwargs['version']}"
            if key in cache:
                wrapper._cache_hit = True
                return cache[key]
            wrapper._cache_hit = False
            result = fetch_fn(kind, **kwargs)
            cache[key] = result
            return result
        return fetch_fn(kind, **kwargs)
    wrapper._cache_hit = False
    return wrapper


def generate(data: dict, root: Path, fetch_fn=None, commit: bool = True, overwrite: bool = False, only_package: str | None = None) -> None:
    if fetch_fn is None:
        fetch_fn = _default_fetch

    packages = data.get("packages", {})
    if not packages:
        print("No packages to generate.")
        return

    sha256_cache = _load_sha256_cache(root)
    fetch_fn = _cached_fetch(fetch_fn, sha256_cache)

    working_dir = str(root)
    baseline_entries = {}

    # Load existing baseline if present
    baseline_path = vcpkg_baseline_file(root)
    if baseline_path.exists():
        with open(baseline_path, "r", encoding="utf-8") as f:
            existing_baseline = json.load(f)
        baseline_entries = existing_baseline.get("default", {})

    for name, pkg in packages.items():
        if only_package and name != only_package:
            continue
        _migrate_pkg_in_place(pkg)
        registries = get_package_registries(pkg)
        repo = pkg["repo"]
        versions = pkg.get("versions", [])
        common_deps = pkg.get("dependencies", [])
        xmake_deps = common_deps + pkg.get("xmake-dependencies", [])
        vcpkg_deps = common_deps + pkg.get("vcpkg-dependencies", [])
        header_only = pkg.get("header-only", False)
        cmake_options = pkg.get("cmake-options", [])
        build_tool = _get_build_tool(pkg)
        features = pkg.get("features", {})
        default_features = pkg.get("default-features", [])

        print(f"--- {name} ---")

        repo_info = fetch_fn("repo_info", repo=repo)
        description = repo_info["description"]
        license_id = repo_info["license"]

        xmake_config = pkg.get("xmake-config", {})

        if "xmake" in registries:
            _generate_xmake(
                root, name, repo, description, versions, xmake_deps,
                header_only, fetch_fn, license_id, xmake_config, overwrite,
                build_tool=build_tool, cmake_options=cmake_options,
                features=features, default_features=default_features,
            )

        if "vcpkg" in registries:
            _generate_vcpkg(
                root, name, repo, description, versions, vcpkg_deps,
                header_only, cmake_options, fetch_fn, commit, working_dir, baseline_entries,
                features=features, default_features=default_features,
            )

    # Write baseline (all vcpkg packages)
    if baseline_entries:
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        with open(baseline_path, "w", encoding="utf-8") as f:
            json.dump({"default": baseline_entries}, f, indent=2)
        if commit:
            git_exec(["add", str(baseline_path)], working_dir)

    _save_sha256_cache(root, sha256_cache)


def _generate_xmake(
    root, name, repo, description, versions, dependencies, header_only,
    fetch_fn, license_id="", xmake_config=None, overwrite=False,
    build_tool=None, cmake_options=None, features=None, default_features=None,
):
    version_hashes = {}
    for version in versions:
        sha256 = fetch_fn("tarball_sha256", repo=repo, version=version)
        if hasattr(fetch_fn, '_cache_hit') and fetch_fn._cache_hit:
            print(f"  xmake: {version} (cached)")
        else:
            print(f"  xmake: fetched SHA256 for {version}")
        version_hashes[version] = sha256

    pkg_dir = xmake_package_dir(root, name)
    pkg_dir.mkdir(parents=True, exist_ok=True)
    xmake_path = pkg_dir / "xmake.lua"

    if xmake_path.exists() and not overwrite:
        existing = xmake_path.read_text(encoding="utf-8")
        updated = update_xmake_lua(
            existing, versions, version_hashes,
            dependencies=dependencies, header_only=header_only,
            xmake_config=xmake_config,
            build_tool=build_tool, cmake_options=cmake_options,
            features=features, default_features=default_features,
        )
        xmake_path.write_text(updated, encoding="utf-8")
        print(f"  xmake: updated {xmake_path}")
    else:
        xmake_lua = generate_xmake_lua(
            name, repo, description, versions, version_hashes,
            dependencies=dependencies, header_only=header_only,
            license=license_id, xmake_config=xmake_config,
            build_tool=build_tool, cmake_options=cmake_options,
            features=features, default_features=default_features,
        )
        xmake_path.write_text(xmake_lua, encoding="utf-8")
        print(f"  xmake: wrote {xmake_path}")


def _generate_vcpkg(
    root, name, repo, description, versions, dependencies,
    header_only, options, fetch_fn, commit, working_dir, baseline_entries,
    features=None, default_features=None,
):
    if features:
        boolean_features = {}
        for fname, fdef in features.items():
            if _feature_type(fdef) == "boolean":
                boolean_features[fname] = fdef
            else:
                print(f"  vcpkg: skipping non-boolean feature '{fname}' (vcpkg features are strictly boolean)")
        features = boolean_features
        if default_features:
            default_features = [f for f in default_features if f in features]
    if not versions:
        print(f"  vcpkg: no versions for '{name}', skipping")
        return

    # Load existing version entries to avoid re-generating
    version_file = vcpkg_version_file(root, name)
    existing_versions = {}
    if version_file.exists():
        with open(version_file, "r", encoding="utf-8") as f:
            vdata = json.load(f)
        for entry in vdata.get("versions", []):
            existing_versions[entry["version-string"]] = entry["git-tree"]

    # Resolve all version-strings and find which need new git-trees
    version_infos = []
    for version in versions:
        commit_info = fetch_fn("commit_info", repo=repo, ref=version)
        vs = vcpkg_version_string(commit_info["date"], commit_info["sha"])
        version_infos.append({"version": version, "vs": vs, "sha": commit_info["sha"]})

    # Reuse existing git-trees for already-tracked versions
    version_entries = []
    needs_commit = False
    latest_info = version_infos[-1]

    for info in version_infos:
        vs = info["vs"]
        if vs in existing_versions:
            print(f"  vcpkg: {vs} (tracked)")
            version_entries.append({"version-string": vs, "git-tree": existing_versions[vs]})
        else:
            # New version — we'll generate port files for it below
            print(f"  vcpkg: {vs} (new)")
            version_entries.append({"version-string": vs, "git-tree": None})
            needs_commit = True

    # Always generate port files for the latest version (deps/description may have changed)
    port_dir = vcpkg_port_dir(root, name)
    port_dir.mkdir(parents=True, exist_ok=True)
    portfile_path = port_dir / "portfile.cmake"
    vcpkg_json_path = port_dir / "vcpkg.json"

    new_portfile = generate_portfile_cmake(
        repo, latest_info["sha"], header_only=header_only, options=options,
        features=features,
    )
    new_vcpkg_json = json.dumps(
        generate_vcpkg_json(
            name, description, latest_info["vs"], dependencies,
            features=features, default_features=default_features,
        ),
        indent=2,
    )

    old_portfile = portfile_path.read_text(encoding="utf-8") if portfile_path.exists() else ""
    old_vcpkg_json = vcpkg_json_path.read_text(encoding="utf-8") if vcpkg_json_path.exists() else ""
    if (new_portfile != old_portfile) or (new_vcpkg_json != old_vcpkg_json):
        needs_commit = True

    if not needs_commit:
        print(f"  vcpkg: no changes")
        # Still need to populate version_entries for baseline
        baseline_entries[vcpkg_port_name(name)] = {"baseline": latest_info["vs"], "port-version": 0}
        return

    portfile_path.write_text(new_portfile, encoding="utf-8")
    vcpkg_json_path.write_text(new_vcpkg_json, encoding="utf-8")

    # Single commit for port files, then get git-tree for any new versions
    pname = vcpkg_port_name(name)
    if commit:
        git_exec(["add", f"ports/{pname}"], working_dir)
        git_exec(["commit", "-m", f"Update {pname}"], working_dir)
        tree_sha = git_tree_sha_for_path(f"ports/{pname}", working_dir)
        print(f"  vcpkg: git-tree {tree_sha}")
    else:
        tree_sha = "no-commit-mode"

    # Fill in git-tree for any new versions (they all get the current tree)
    for entry in version_entries:
        if entry["git-tree"] is None:
            entry["git-tree"] = tree_sha

    # Write versions file
    latest_vs = version_entries[-1]["version-string"]
    version_dir = vcpkg_version_dir(root, name)
    version_dir.mkdir(parents=True, exist_ok=True)
    with open(version_file, "w", encoding="utf-8") as f:
        json.dump(generate_vcpkg_versions_json(version_entries), f, indent=2)

    if commit:
        git_exec(["add", str(version_file)], working_dir)

    baseline_entries[vcpkg_port_name(name)] = {"baseline": latest_vs, "port-version": 0}
    print(f"  vcpkg: baseline -> {latest_vs}")


def _default_fetch(kind: str, **kwargs) -> str | dict:
    if kind == "repo_info":
        return get_repo_info(kwargs["repo"])
    elif kind == "tarball_sha256":
        return fetch_tarball_sha256(kwargs["repo"], kwargs["version"])
    elif kind == "commit_info":
        return get_commit_info_for_ref(kwargs["repo"], kwargs["ref"])
    raise ValueError(f"Unknown fetch kind: {kind}")


SELF_UPDATE_REPO = "BuildWithCollab/cpp-package-registry-util"
SELF_UPDATE_PATH = "registry.py"


def self_update() -> None:
    url = f"https://api.github.com/repos/{SELF_UPDATE_REPO}/contents/{SELF_UPDATE_PATH}?ref=main"
    try:
        data = _github_fetch_json(url, context="self-update")
    except SystemExit:
        print("Failed to check for updates.", file=sys.stderr)
        return
    import base64
    new_content = base64.b64decode(data["content"])

    script_path = Path(__file__).resolve()
    old_content = script_path.read_bytes()

    if new_content == old_content:
        print("Already up to date.")
        return

    script_path.write_bytes(new_content)
    print(f"Updated {script_path}")


# --- README generation ---


def _get_git_remote_url(working_dir: str | None = None) -> str:
    result = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        cwd=working_dir,
    )
    if result.returncode != 0:
        return ""
    url = result.stdout.strip()
    # Normalize git@ to https
    if url.startswith("git@github.com:"):
        url = "https://github.com/" + url[len("git@github.com:"):]
    if url.endswith(".git"):
        url = url[:-4]
    return url


def _get_git_head_sha(working_dir: str | None = None) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        cwd=working_dir,
    )
    if result.returncode != 0:
        return "<commit-hash>"
    return result.stdout.strip()


def _github_url_to_parts(url: str) -> tuple[str, str]:
    parts = url.rstrip("/").split("/")
    if len(parts) >= 2:
        return parts[-2], parts[-1]
    return "", ""


README_MARKER_START = "<!-- REGISTRY:content -->"
README_MARKER_END = "<!-- /REGISTRY:content -->"


def update_readme(readme_path: Path, content: str) -> bool:
    if not readme_path.exists():
        print(f"{readme_path} not found.", file=sys.stderr)
        print(f'Create a README.md and add these markers where you want the registry content:\n\n{README_MARKER_START}\n{README_MARKER_END}', file=sys.stderr)
        return False

    existing = readme_path.read_text(encoding="utf-8")
    if README_MARKER_START not in existing or README_MARKER_END not in existing:
        print(f"Markers not found in {readme_path}.", file=sys.stderr)
        print(f"\nAdd these markers to your README.md where you want the registry content to appear:\n\n{README_MARKER_START}\n{README_MARKER_END}", file=sys.stderr)
        return False

    before = existing[:existing.index(README_MARKER_START) + len(README_MARKER_START)]
    after = existing[existing.index(README_MARKER_END):]
    updated = before + "\n" + content + "\n" + after
    readme_path.write_text(updated, encoding="utf-8")
    print(f"Updated {readme_path}")
    return True


def generate_readme(data: dict, working_dir: str | None = None) -> str:
    repo_url = _get_git_remote_url(working_dir)
    head_sha = _get_git_head_sha(working_dir)
    org, repo_name = _github_url_to_parts(repo_url)

    packages = data.get("packages", {})
    pkg_names = list(packages.keys())

    xmake_pkgs = []
    vcpkg_pkgs = []
    for name, pkg in packages.items():
        registries = get_package_registries(pkg)
        repo = pkg.get("repo", "")
        link = f"https://github.com/{repo}" if repo else ""
        if "xmake" in registries:
            xmake_pkgs.append((name, link))
        if "vcpkg" in registries:
            vcpkg_pkgs.append((vcpkg_port_name(name), link))

    vcpkg_names = [name for name, _ in vcpkg_pkgs]

    xmake_registry_name = org or "my-registry"
    git_url = f"{repo_url}.git" if repo_url else "https://github.com/your-user/your-registry.git"
    commits_url = f"{repo_url}/commits/main/" if repo_url else "https://github.com/your-user/your-registry/commits/main/"

    example_pkg = pkg_names[0] if pkg_names else "some-package"
    example_vcpkg = vcpkg_names[0] if vcpkg_names else "some-package"

    xmake_pkg_list = "\n".join(f"- [`{name}`]({link})" for name, link in xmake_pkgs) if xmake_pkgs else ""
    vcpkg_pkg_list = "\n".join(f"- [`{name}`]({link})" for name, link in vcpkg_pkgs) if vcpkg_pkgs else ""

    def _json_list(items, indent_spaces):
        if not items:
            return '["some-package"]'
        if len(items) == 1:
            return json.dumps(items)
        prefix = " " * indent_spaces
        inner = ",\n".join(f'{prefix}    "{item}"' for item in items)
        return f"[\n{inner}\n{prefix}]"

    vcpkg_packages_json = _json_list(vcpkg_names, 12)
    vcpkg_deps_json = _json_list(vcpkg_names, 8)

    return f"""## Packages <!-- omit in toc -->

This is a [`vcpkg`](https://vcpkg.io/) and [`xmake`](https://xmake.io/) C++ package registry.

---

- [Build Tool Configuration](#build-tool-configuration)
  - [`xmake`](#xmake)
  - [`vcpkg`](#vcpkg)
    - [`vcpkg-configuration.json`](#vcpkg-configurationjson)
      - [Updating Baselines](#updating-baselines)
    - [`vcpkg.json`](#vcpkg-json)

---

## Build Tool Configuration

### `xmake`

{xmake_pkg_list}

Configuring `xmake` to use this package registry couldn't be easier:

```lua
add_repositories("{xmake_registry_name} {git_url}")

add_requires("{example_pkg}")

target("my-project")
    set_kind("binary")
    add_files("src/*.cpp")
    add_packages("{example_pkg}")
```

### `vcpkg`

{vcpkg_pkg_list}

Custom registries for `vcpkg` are a bit more involved, but still easy to set up.

There are two configuration files you need:

- `vcpkg-configuration.json`
- `vcpkg.json`

#### `vcpkg-configuration.json`

This tells `vcpkg` where to find packages. Create this file in your project root:

```json
{{
    "default-registry": {{
        "kind": "git",
        "repository": "https://github.com/microsoft/vcpkg.git",
        "baseline": "<latest-vcpkg-commit-hash>"
    }},
    "registries": [
        {{
            "kind": "git",
            "repository": "{git_url}",
            "baseline": "{head_sha}",
            "packages": {vcpkg_packages_json}
        }}
    ]
}}
```

> Update the `packages` list with the names of the packages you want to use from this registry.

##### Updating Baselines

A `baseline` is a git commit hash. `vcpkg` uses it to determine which package versions are available.

**When this registry is updated**, you need to update the baseline to see new packages or versions.

To get the latest baseline for this registry:

```
git ls-remote {git_url} HEAD
```

Or visit: {commits_url}

To get the latest baseline for the main `vcpkg` registry:

```
git ls-remote https://github.com/microsoft/vcpkg.git HEAD
```

#### `vcpkg.json`

This is your project manifest. Add the packages you want:

```json
{{
    "name": "my-project",
    "version-string": "0.0.1",
    "dependencies": {vcpkg_deps_json}
}}
```

> The `name` and `version-string` fields just need to be valid — they can be anything.
> `name` must be all lowercase letters, numbers, and hyphens.

You can mix packages from different registries. For example, `spdlog` from the main `vcpkg` registry and `{example_vcpkg}` from this one:

```json
{{
    "name": "my-project",
    "version-string": "0.0.1",
    "dependencies": [
        "spdlog",
        "{example_vcpkg}"
    ]
}}
```
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage a registry.json file for vcpkg and xmake C++ package registries."
    )
    parser.add_argument(
        "-f", "--file",
        default=DEFAULT_REGISTRY_FILE,
        help=f"Path to the registry JSON file (default: {DEFAULT_REGISTRY_FILE})",
    )

    subparsers = parser.add_subparsers(dest="command")

    # add
    add_parser = subparsers.add_parser("add", help="Add a package to the registry.")
    add_parser.add_argument("name", help="Package name (e.g. some-lib)")
    add_parser.add_argument("repo", help="GitHub repository (e.g. user/repo)")
    add_parser.add_argument("--branch", help="Git branch to track (default: repo default)")
    add_parser.add_argument(
        "--registries",
        default="vcpkg,xmake",
        help="Comma-separated list of registries (default: vcpkg,xmake)",
    )
    add_parser.add_argument("--header-only", action="store_true", help="Mark the package as header-only")
    add_parser.add_argument(
        "--build-tool",
        choices=list(VALID_BUILD_TOOLS),
        help="Upstream build tool (default: 'none' if --header-only, else 'xmake')",
    )

    # remove
    rm_parser = subparsers.add_parser("remove", help="Remove a package from the registry.")
    rm_parser.add_argument("name", help="Package name to remove")

    # add-version
    av_parser = subparsers.add_parser("add-version", help="Add a version to a package.")
    av_parser.add_argument("name", help="Package name")
    av_parser.add_argument("version", nargs="?", help="Version string (e.g. v1.0.0)")
    av_parser.add_argument("--latest", action="store_true", help="Fetch the latest tag from GitHub")

    # remove-version
    rv_parser = subparsers.add_parser("remove-version", help="Remove a version from a package.")
    rv_parser.add_argument("name", help="Package name")
    rv_parser.add_argument("version", help="Version string to remove")

    # list
    ls_parser = subparsers.add_parser("list", help="List packages or versions.")
    ls_parser.add_argument("name", nargs="?", help="Package name (omit to list all)")

    # show
    show_parser = subparsers.add_parser("show", help="Show full details for a package.")
    show_parser.add_argument("name", help="Package name")

    # add-dep
    ad_parser = subparsers.add_parser("add-dep", help="Add a dependency to a package.")
    ad_parser.add_argument("name", help="Package name")
    ad_parser.add_argument("dep", help="Dependency name")
    ad_parser.add_argument("configs", nargs="*", help="Config key=value pairs (e.g. filesystem=true)")
    ad_parser.add_argument("-v", "--version", dest="dep_version", help="Version constraint (e.g. 1.x, >=2.0)")
    ad_parser.add_argument("--feature", help="Scope this dep to a feature instead of top-level")
    ad_group = ad_parser.add_mutually_exclusive_group()
    ad_group.add_argument("--xmake", action="store_true", help="Add as xmake-only dependency")
    ad_group.add_argument("--vcpkg", action="store_true", help="Add as vcpkg-only dependency")

    # remove-dep
    rd_parser = subparsers.add_parser("remove-dep", help="Remove a dependency from a package.")
    rd_parser.add_argument("name", help="Package name")
    rd_parser.add_argument("dep", help="Dependency name to remove")
    rd_parser.add_argument("--feature", help="Remove from a feature's deps instead of top-level")
    rd_group = rd_parser.add_mutually_exclusive_group()
    rd_group.add_argument("--xmake", action="store_true", help="Remove from xmake-only dependencies")
    rd_group.add_argument("--vcpkg", action="store_true", help="Remove from vcpkg-only dependencies")

    # set-config
    sc_parser = subparsers.add_parser("set-config", help="Set xmake-config values for a package.")
    sc_parser.add_argument("name", help="Package name")
    sc_parser.add_argument("values", nargs="+", help="Config key=value pairs (e.g. build_tests=false)")

    # add-feature
    af_parser = subparsers.add_parser("add-feature", help="Declare a feature on a package.")
    af_parser.add_argument("name", help="Package name")
    af_parser.add_argument("feature", help="Feature name (e.g. ssl)")
    af_parser.add_argument("--description", default="", help="Feature description")
    af_parser.add_argument(
        "--type", dest="ftype", default="boolean", choices=["boolean", "string"],
        help="Feature type (default: boolean). String features are xmake-only.",
    )
    af_parser.add_argument(
        "--default", dest="default_value",
        help="Default value (required for --type string)",
    )
    af_parser.add_argument(
        "--value", dest="values", action="append", default=[],
        help="Allowed value (repeatable, --type string only). Omit to allow any string.",
    )
    af_parser.add_argument("--cmake-option", help="Upstream CMake option name (default: UPPER_CASE feature name)")
    af_parser.add_argument("--xmake-config", help="Upstream xmake config name (default: feature name with hyphens -> underscores)")

    # remove-feature
    rf_parser = subparsers.add_parser("remove-feature", help="Remove a feature (and its scoped deps + defines).")
    rf_parser.add_argument("name", help="Package name")
    rf_parser.add_argument("feature", help="Feature name to remove")

    # set-feature
    sf_parser = subparsers.add_parser("set-feature", help="Update a feature's metadata.")
    sf_parser.add_argument("name", help="Package name")
    sf_parser.add_argument("feature", help="Feature name")
    sf_parser.add_argument("--description", help="Feature description")
    sf_parser.add_argument("--cmake-option", help="Upstream CMake option name")
    sf_parser.add_argument("--xmake-config", help="Upstream xmake config name")
    sf_parser.add_argument("--default", dest="default_value", help="Default value (string features only)")
    sf_parser.add_argument(
        "--value", dest="values", action="append", default=[],
        help="Replace the allowed-values list (string features only, repeatable)",
    )

    # add-define
    adef_parser = subparsers.add_parser("add-define", help="Add a consumer-side preprocessor define to a feature.")
    adef_parser.add_argument("name", help="Package name")
    adef_parser.add_argument("feature", help="Feature name")
    adef_parser.add_argument("macro", help="Macro name (e.g. MYLIB_SSL_SUPPORT)")

    # remove-define
    rdef_parser = subparsers.add_parser("remove-define", help="Remove a define from a feature.")
    rdef_parser.add_argument("name", help="Package name")
    rdef_parser.add_argument("feature", help="Feature name")
    rdef_parser.add_argument("macro", help="Macro name to remove")

    # set-default-features
    sdf_parser = subparsers.add_parser("set-default-features", help="Replace the list of default-on features.")
    sdf_parser.add_argument("name", help="Package name")
    sdf_parser.add_argument(
        "-f", "--feature", dest="features", action="append", default=[],
        help="Feature name (repeatable). Omit all to clear the list.",
    )

    # set-build-tool
    sbt_parser = subparsers.add_parser("set-build-tool", help="Set the upstream build tool for a package.")
    sbt_parser.add_argument("name", help="Package name")
    sbt_parser.add_argument("build_tool", choices=list(VALID_BUILD_TOOLS), help="Build tool")

    # set-cmake-option
    sco_parser = subparsers.add_parser("set-cmake-option", help="Set an always-on CMake -D flag.")
    sco_parser.add_argument("name", help="Package name")
    sco_parser.add_argument("value", help="KEY=VALUE (e.g. BUILD_TESTS=OFF)")

    # readme
    readme_parser = subparsers.add_parser("readme", help="Generate a README snippet for consumers of this registry.")
    readme_parser.add_argument(
        "--update", action="store_true",
        help="Update README.md in place between <!-- REGISTRY:content --> markers",
    )

    # self-update
    subparsers.add_parser("self-update", help="Update registry.py to the latest version from GitHub.")

    # generate
    gen_parser = subparsers.add_parser("generate", help="Generate vcpkg and xmake registry files.")
    gen_parser.add_argument("name", nargs="?", help="Generate only this package (default: all)")
    gen_parser.add_argument(
        "--no-commit", action="store_true",
        help="Generate files without git commits (useful for testing)",
    )
    gen_parser.add_argument(
        "--overwrite", action="store_true",
        help="Overwrite existing files instead of updating marked sections",
    )

    return parser


def main(argv: list[str] | None = None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    registry_path = Path(args.file)

    if args.command == "readme":
        data = load_registry(registry_path)
        root = str(registry_path.parent) if registry_path.parent != Path() else None
        content = generate_readme(data, working_dir=root)
        if args.update:
            readme_path = registry_path.parent / "README.md"
            update_readme(readme_path, content)
        else:
            print(content)
        return

    if args.command == "self-update":
        self_update()
        return

    if args.command == "list":
        data = load_registry(registry_path)
        list_packages(data, args.name)
        return

    if args.command == "show":
        data = load_registry(registry_path)
        show_package(data, args.name)
        return

    if args.command == "generate":
        data = load_registry(registry_path)
        root = registry_path.parent
        generate(data, root, commit=not args.no_commit, overwrite=args.overwrite, only_package=args.name)
        print("Done.")
        return

    # All other commands modify the registry file
    data = load_registry(registry_path)

    if args.command == "add":
        registries = [r.strip() for r in args.registries.split(",")]
        for r in registries:
            if r not in VALID_REGISTRIES:
                print(f"Invalid registry: '{r}'. Valid options: {', '.join(VALID_REGISTRIES)}", file=sys.stderr)
                sys.exit(1)
        add_package(
            data, args.name, args.repo, branch=args.branch, registries=registries,
            header_only=args.header_only, build_tool=args.build_tool,
        )

    elif args.command == "remove":
        remove_package(data, args.name)

    elif args.command == "add-version":
        if args.latest:
            packages = data.get("packages", {})
            if args.name not in packages:
                print(f"Package '{args.name}' not found.", file=sys.stderr)
                sys.exit(1)
            repo = packages[args.name]["repo"]
            version = get_latest_tag(repo)
            print(f"Latest tag for '{repo}': {version}")
        elif args.version:
            version = args.version
        else:
            print("Provide a version string or use --latest.", file=sys.stderr)
            sys.exit(1)
        add_version(data, args.name, version)

    elif args.command == "remove-version":
        remove_version(data, args.name, args.version)

    elif args.command == "add-dep":
        configs = {}
        for pair in (args.configs or []):
            k, v = parse_kv_pair(pair)
            configs[k] = v
        reg = "xmake" if args.xmake else ("vcpkg" if args.vcpkg else None)
        add_dependency(
            data, args.name, args.dep, configs=configs or None, registry=reg,
            version=args.dep_version, feature=args.feature,
        )

    elif args.command == "remove-dep":
        reg = "xmake" if args.xmake else ("vcpkg" if args.vcpkg else None)
        remove_dependency(data, args.name, args.dep, registry=reg, feature=args.feature)

    elif args.command == "set-config":
        for pair in args.values:
            k, v = parse_kv_pair(pair)
            set_config(data, args.name, k, v)

    elif args.command == "add-feature":
        add_feature(
            data, args.name, args.feature,
            description=args.description,
            cmake_option=args.cmake_option,
            xmake_config=args.xmake_config,
            type_=args.ftype,
            default=args.default_value,
            values=args.values or None,
        )

    elif args.command == "remove-feature":
        remove_feature(data, args.name, args.feature)

    elif args.command == "set-feature":
        set_feature(
            data, args.name, args.feature,
            description=args.description,
            cmake_option=args.cmake_option,
            xmake_config=args.xmake_config,
            default=args.default_value,
            values=args.values or None,
        )

    elif args.command == "add-define":
        add_define(data, args.name, args.feature, args.macro)

    elif args.command == "remove-define":
        remove_define(data, args.name, args.feature, args.macro)

    elif args.command == "set-default-features":
        set_default_features(data, args.name, args.features)

    elif args.command == "set-build-tool":
        set_build_tool(data, args.name, args.build_tool)

    elif args.command == "set-cmake-option":
        if "=" not in args.value:
            print("set-cmake-option requires KEY=VALUE.", file=sys.stderr)
            sys.exit(1)
        key, val = args.value.split("=", 1)
        set_cmake_option(data, args.name, key, val)

    save_registry(registry_path, data)


if __name__ == "__main__":
    main()

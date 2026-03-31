# BuildWithCollab Packages

📦 xmake + vcpkg 📦

<!-- REGISTRY:content -->
## Packages <!-- omit in toc -->

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

- [`collab-core`](https://github.com/BuildWithCollab/collab-core)
- [`collab-process`](https://github.com/BuildWithCollab/collab-process)

Configuring `xmake` to use this package registry couldn't be easier:

```lua
add_repositories("BuildWithCollab https://github.com/BuildWithCollab/Packages.git")

add_requires("collab-core")

target("my-project")
    set_kind("binary")
    add_files("src/*.cpp")
    add_packages("collab-core")
```

### `vcpkg`

- [`collab-core`](https://github.com/BuildWithCollab/collab-core)
- [`collab-process`](https://github.com/BuildWithCollab/collab-process)

Custom registries for `vcpkg` are a bit more involved, but still easy to set up.

There are two configuration files you need:

- `vcpkg-configuration.json`
- `vcpkg.json`

#### `vcpkg-configuration.json`

This tells `vcpkg` where to find packages. Create this file in your project root:

```json
{
    "default-registry": {
        "kind": "git",
        "repository": "https://github.com/microsoft/vcpkg.git",
        "baseline": "<latest-vcpkg-commit-hash>"
    },
    "registries": [
        {
            "kind": "git",
            "repository": "https://github.com/BuildWithCollab/Packages.git",
            "baseline": "18b93a0d0de5e22b45564b015ae4d6b160e66cc0",
            "packages": [
                "collab-core",
                "collab-process"
            ]
        }
    ]
}
```

> Update the `packages` list with the names of the packages you want to use from this registry.

##### Updating Baselines

A `baseline` is a git commit hash. `vcpkg` uses it to determine which package versions are available.

**When this registry is updated**, you need to update the baseline to see new packages or versions.

To get the latest baseline for this registry:

```
git ls-remote https://github.com/BuildWithCollab/Packages.git HEAD
```

Or visit: https://github.com/BuildWithCollab/Packages/commits/main/

To get the latest baseline for the main `vcpkg` registry:

```
git ls-remote https://github.com/microsoft/vcpkg.git HEAD
```

#### `vcpkg.json`

This is your project manifest. Add the packages you want:

```json
{
    "name": "my-project",
    "version-string": "0.0.1",
    "dependencies": [
            "collab-core",
            "collab-process"
        ]
}
```

> The `name` and `version-string` fields just need to be valid — they can be anything.
> `name` must be all lowercase letters, numbers, and hyphens.

You can mix packages from different registries. For example, `spdlog` from the main `vcpkg` registry and `collab-core` from this one:

```json
{
    "name": "my-project",
    "version-string": "0.0.1",
    "dependencies": [
        "spdlog",
        "collab-core"
    ]
}
```

<!-- /REGISTRY:content -->

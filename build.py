#!/usr/bin/env python3
"""Build script for ReflectOnMee addon.

Usage:
  python build.py all     # clean -> build -> package
  python build.py clean   # remove build artifacts
  python build.py build   # copy addon files to build/
  python build.py package # create .ankiaddon zip
"""
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path


def get_version():
    try:
        import tomllib
        with open("pyproject.toml", "rb") as f:
            pyproject_version = tomllib.load(f)["project"]["version"]
    except Exception:
        pyproject_version = "0.0.4"

    init_path = Path("__init__.py")
    init_version = None
    for line in init_path.read_text().splitlines():
        if line.startswith("version"):
            init_version = line.split("=")[1].strip().strip('"').strip("'")
            break

    if init_version and init_version != pyproject_version:
        print(
            f"ERROR: Version mismatch! "
            f"pyproject.toml: {pyproject_version}, "
            f"__init__.py: {init_version}"
        )
        sys.exit(1)

    return pyproject_version


def clean():
    print("Cleaning build artifacts...")
    patterns = ["build", "*.egg-info", "__pycache__"]
    for p in patterns:
        prefix = p.split("*")[0]
        if not prefix:
            continue
        for found in Path(".").rglob(prefix):
            if found.is_dir():
                shutil.rmtree(found, ignore_errors=True)
    print("  Done")


def build_addon():
    version = get_version()
    print(f"Building ReflectOnMee v{version}...")

    build_dir = Path("build") / "reflect_on_mee_addon"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)

    for item in ["__init__.py", "reflectOnMee.py"]:
        src = Path(item)
        if not src.exists():
            print(f"ERROR: {item} not found")
            sys.exit(1)
        shutil.copy2(src, build_dir / item)
        print(f"  Copied {item}")

    manifest = {
        "package": "ReflectOnMee",
        "name": "Reflect On Mee - Helps Alleviate RGS",
        "version": version,
    }
    manifest_path = build_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  manifest.json written")

    print(f"  Built at {build_dir}")


def create_package():
    version = get_version()
    print("Creating .ankiaddon package...")

    addon_dir = Path("build") / "reflect_on_mee_addon"
    if not addon_dir.exists():
        print("ERROR: build/reflect_on_mee_addon not found. Run 'build' first.")
        sys.exit(1)

    build_dir = Path("build")
    package_name = f"reflect_on_mee_v{version}.ankiaddon"
    package_path = build_dir / package_name

    with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(addon_dir):
            for d in dirs:
                dir_path = Path(root) / d
                arc_path = dir_path.relative_to(addon_dir)
                zf.write(dir_path, str(arc_path) + "/")
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(addon_dir)
                zf.write(file_path, arc_path)

    print(f"  Package: {package_path}")
    print(f"  Size: {package_path.stat().st_size / 1024:.1f} KB")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]
    if cmd == "clean":
        clean()
    elif cmd == "build":
        build_addon()
    elif cmd == "package":
        build_addon()
        create_package()
    elif cmd == "all":
        clean()
        build_addon()
        create_package()
        print("\nBuild complete!")
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()

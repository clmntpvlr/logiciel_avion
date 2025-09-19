"""Helper script to package the application as a standalone executable."""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


def _discover_data_folders(root: Path) -> list[tuple[Path, str]]:
    """Return pairs ``(source, relative_target)`` for data folders to bundle."""
    candidates = ["assets", "ui"]
    data: list[tuple[Path, str]] = []
    for name in candidates:
        source = root / name
        if source.exists():
            data.append((source, name))
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a packaged executable using PyInstaller.",
        epilog=(
            "Requires PyInstaller to be installed in the current Python "
            "environment."
        ),
    )
    parser.add_argument(
        "--name",
        default="AircraftDesigner",
        help="Name of the generated executable (default: %(default)s)",
    )
    parser.add_argument(
        "--icon",
        default=None,
        help="Optional path to an icon to embed into the executable.",
    )
    parser.add_argument(
        "--onedir",
        action="store_true",
        help="Create an unpacked directory instead of a single executable.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove previous build/dist directories before packaging.",
    )
    args = parser.parse_args(argv)

    try:
        import PyInstaller.__main__ as pyinstaller
    except ModuleNotFoundError:  # pragma: no cover - executed when missing dependency
        print(
            "PyInstaller n'est pas installé. Exécutez 'pip install pyinstaller'"
            " puis relancez la commande.",
            file=sys.stderr,
        )
        return 1

    root = Path(__file__).resolve().parents[1]
    entry_point = root / "main.py"

    build_root = root / "build"
    work_dir = build_root / "pyinstaller"
    dist_dir = root / "dist"

    if args.clean:
        shutil.rmtree(work_dir, ignore_errors=True)
        shutil.rmtree(dist_dir, ignore_errors=True)

    build_root.mkdir(exist_ok=True)
    work_dir.mkdir(exist_ok=True)
    dist_dir.mkdir(exist_ok=True)

    cmd = [
        str(entry_point),
        "--name",
        args.name,
        "--noconfirm",
        "--distpath",
        str(dist_dir),
        "--workpath",
        str(work_dir),
        "--specpath",
        str(work_dir),
    ]

    if args.icon:
        cmd.extend(["--icon", args.icon])

    if args.onedir:
        cmd.append("--onedir")
    else:
        cmd.append("--onefile")

    for source, rel_target in _discover_data_folders(root):
        cmd.extend([
            "--add-data",
            f"{source}{os.pathsep}{rel_target}",
        ])

    print("Exécution de PyInstaller avec :", " ".join(cmd))
    pyinstaller.run(cmd)
    print(f"Exécutable disponible dans : {dist_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

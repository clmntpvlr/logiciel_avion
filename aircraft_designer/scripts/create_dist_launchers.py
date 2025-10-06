# aircraft_designer/scripts/create_dist_launchers.py
from __future__ import annotations
import os
import sys
import platform
from pathlib import Path
import subprocess
import argparse
from typing import Iterable, Tuple, Optional

APP_NAME_DEFAULT = "Aircraft Designer"

def _project_root() -> Path:
    # .../aircraft_designer/scripts -> parents[1] = .../aircraft_designer
    return Path(__file__).resolve().parents[1]

def _candidate_dist_dirs(project_root: Path, override: Optional[Path]) -> Iterable[Path]:
    """
    Ordre de recherche des dossiers dist:
      1) --dist (si fourni)
      2) aircraft_designer/dist
      3) repo_root/dist  (repo_root = parent de aircraft_designer)
    """
    seen = set()
    if override:
        yield override
        seen.add(override.resolve())
    d1 = project_root / "dist"
    if d1.resolve() not in seen:
        yield d1
        seen.add(d1.resolve())
    d2 = project_root.parent / "dist"
    if d2.resolve() not in seen:
        yield d2

def _find_main_binary(dist: Path) -> Tuple[Optional[Path], bool]:
    """
    Retourne (path, is_windows_exe) si trouvé, sinon (None, False).
    """
    if not dist.exists():
        return None, False
    candidates = ["main.exe", "AircraftDesigner.exe", "main", "AircraftDesigner"]
    for name in candidates:
        p = dist / name
        if p.exists() and p.is_file():
            return p, p.suffix.lower() == ".exe"
    # fallback : premier exécutable trouvable
    for p in dist.iterdir():
        if p.is_file() and os.access(p, os.X_OK):
            return p, p.suffix.lower() == ".exe"
    return None, False

def _write_text(path: Path, content: str):
    path.write_text(content, encoding="utf-8")
    if platform.system() != "Windows":
        mode = path.stat().st_mode
        path.chmod(mode | 0o111)

def create_windows_launchers(dist: Path, app_name: str, exe_path: Path, icon_ico: Path | None):
    # 1) .bat lanceur
    bat = dist / f"Run {app_name}.bat"
    bat_content = f"""@echo off
setlocal
cd /d "%~dp0"
start "" "{exe_path.name}"
"""
    _write_text(bat, bat_content)

    # 2) .lnk (optionnel)
    lnk = dist / f"{app_name}.lnk"
    icon_line = f'$S.IconLocation = "{icon_ico}";' if icon_ico and icon_ico.exists() else ""
    ps = f"""
$W = New-Object -ComObject WScript.Shell
$S = $W.CreateShortcut("{lnk.as_posix().replace('/', '\\\\')}")
$S.TargetPath = "{exe_path.as_posix().replace('/', '\\\\')}"
$S.WorkingDirectory = "{dist.as_posix().replace('/', '\\\\')}"
{icon_line}
$S.Save()
"""
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
            check=True
        )
    except Exception as e:
        print(f"[WARN] Impossible de créer le .lnk (le .bat suffit) : {e}")

def create_linux_launchers(dist: Path, app_name: str, exe_path: Path, icon_png: Path | None):
    desktop = dist / f"{app_name}.desktop"
    lines = [
        "[Desktop Entry]",
        "Type=Application",
        f"Name={app_name}",
        f"Exec={exe_path}",
        f"Path={dist}",
        "Terminal=false",
    ]
    if icon_png and icon_png.exists():
        lines.append(f"Icon={icon_png}")
    _write_text(desktop, "\n".join(lines) + "\n")

    sh = dist / f"run_{exe_path.stem}.sh"
    sh_content = f"""#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
"./{exe_path.name}" >/dev/null 2>&1 &
"""
    _write_text(sh, sh_content)

def create_macos_launchers(dist: Path, app_name: str, exe_path: Path, icon_png: Path | None):
    cmd = dist / f"{app_name}.command"
    cmd_content = f"""#!/bin/bash
cd "$(dirname "$0")"
"./{exe_path.name}" >/dev/null 2>&1 &
"""
    _write_text(cmd, cmd_content)

    app_path = dist / f"{app_name}.app"
    osa_script = f'do shell script "cd {dist.as_posix()} && ./{exe_path.name} >/dev/null 2>&1 &"'
    try:
        subprocess.run(["osacompile", "-o", str(app_path), "-e", osa_script], check=True)
    except Exception as e:
        print(f"[WARN] osacompile indisponible, .command suffira : {e}")

def main():
    parser = argparse.ArgumentParser(description="Crée des lanceurs double-cliquables dans un dossier dist.")
    parser.add_argument(
        "--dist",
        type=str,
        default=None,
        help="Dossier dist à utiliser (sinon auto-détection: aircraft_designer/dist puis <repo>/dist)"
    )
    parser.add_argument(
        "--name", type=str, default=APP_NAME_DEFAULT, help="Nom de l'application (pour les lanceurs)"
    )
    args = parser.parse_args()

    sys_name = platform.system()
    project_root = _project_root()
    override = Path(args.dist).resolve() if args.dist else None

    print("[INFO] Dossiers dist scannés (dans l'ordre) :")
    cand = list(_candidate_dist_dirs(project_root, override))
    for d in cand:
        print(f"  - {d}")

    exe_path = None
    chosen_dist = None
    is_win_exe = False
    for d in cand:
        p, is_win = _find_main_binary(d)
        if p is not None:
            exe_path = p
            chosen_dist = d
            is_win_exe = is_win
            break

    if exe_path is None or chosen_dist is None:
        print("[ERROR] Aucun binaire détecté dans les dossiers dist listés.")
        print("Astuce :")
        print("  - Place ton main.exe (ou binaire) dans aircraft_designer/dist/ ou dans <repo>/dist/")
        print("  - Ou passe un chemin explicite : --dist C:\\chemin\\vers\\dist")
        sys.exit(2)

    app_name = args.name
    assets = project_root / "assets"
    icon_ico = assets / "icon.ico"
    icon_png = assets / "icon.png"

    print(f"[INFO] Dist retenu : {chosen_dist}")
    print(f"[INFO] Binaire détecté : {exe_path.name}")
    print(f"[INFO] Création des lanceurs pour {sys_name} ...")

    if sys_name == "Windows":
        create_windows_launchers(chosen_dist, app_name, exe_path, icon_ico if icon_ico.exists() else None)
    elif sys_name == "Darwin":
        create_macos_launchers(chosen_dist, app_name, exe_path, icon_png if icon_png.exists() else None)
    else:
        create_linux_launchers(chosen_dist, app_name, exe_path, icon_png if icon_png.exists() else None)

    print("✅ Lanceurs créés dans :", chosen_dist)
    print("   - Double-clique dessus pour lancer l'app.")

if __name__ == "__main__":
    main()

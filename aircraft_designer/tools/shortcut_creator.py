"""Utilities to create a desktop shortcut for the application."""
from __future__ import annotations

import os
import platform
import shlex
import stat
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _find_packaged_executable(root: Path) -> Path | None:
    """Return the packaged executable in ``root / 'dist'`` if available."""
    dist = root / "dist"
    if not dist.is_dir():
        return None

    preferred = [
        dist / "main.exe",
        dist / "AircraftDesigner.exe",
        dist / "main",
        dist / "AircraftDesigner",
    ]
    for candidate in preferred:
        if candidate.is_file():
            return candidate

    exec_files = [p for p in dist.iterdir() if p.is_file() and os.access(p, os.X_OK)]
    if len(exec_files) == 1:
        return exec_files[0]
    return None


def _default_icon(root: Path, system: str) -> Path | None:
    assets = root / "assets"
    icon = assets / ("icon.ico" if system == "Windows" else "icon.png")
    return icon if icon.exists() else None


def _resolve_target_and_workdir(root: Path) -> tuple[Path, list[str], Path]:
    target = _find_packaged_executable(root)
    workdir = root
    if target:
        return target, [], workdir
    main_py = root / "main.py"
    return Path(sys.executable), [str(main_py)], workdir


def _desktop_dir(system: str) -> Path:
    home = Path.home()
    if system == "Linux":
        for name in ("Desktop", "Bureau"):
            candidate = home / name
            if candidate.exists():
                return candidate
        desk = home / "Desktop"
        desk.mkdir(parents=True, exist_ok=True)
        return desk
    return home / "Desktop"


def _windows_create_shortcut(
    shortcut: Path,
    target: Path,
    args: list[str],
    workdir: Path,
    icon: Path | None,
) -> None:
    def _ps_quote(s: str) -> str:
        return s.replace("'", "''")

    target_s = _ps_quote(str(target))
    args_s = _ps_quote(" ".join(shlex.quote(a) for a in args))
    workdir_s = _ps_quote(str(workdir))
    shortcut_s = _ps_quote(str(shortcut))
    parts = [
        f"$s=(New-Object -COM WScript.Shell).CreateShortcut('{shortcut_s}');",
        f"$s.TargetPath='{target_s}';",
        f"$s.WorkingDirectory='{workdir_s}';",
    ]
    if args:
        parts.append(f"$s.Arguments='{args_s}';")
    if icon:
        parts.append(f"$s.IconLocation='{_ps_quote(str(icon))}';")
    parts.append("$s.Save()")
    ps_script = "".join(parts)
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True)


def _linux_create_shortcut(
    shortcut: Path,
    app_name: str,
    command: str,
    workdir: Path,
    icon: Path | None,
) -> None:
    lines = [
        "[Desktop Entry]",
        "Type=Application",
        f"Name={app_name}",
        f"Exec={command}",
        f"Path={workdir}",
        "Terminal=false",
    ]
    if icon:
        lines.append(f"Icon={icon}")
    shortcut.write_text("\n".join(lines) + "\n")
    shortcut.chmod(shortcut.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def _macos_create_shortcut(
    desktop: Path,
    app_name: str,
    command: str,
    workdir: Path,
) -> Path:
    bundle = desktop / f"{app_name}.app"
    shell_cmd = f"cd {shlex.quote(str(workdir))} && {command} >/dev/null 2>&1 &"
    applescript = f'do shell script "{shell_cmd.replace('"', '\\"')}"'
    try:
        subprocess.run(["osacompile", "-o", str(bundle), "-e", applescript], check=True)
        return bundle
    except (FileNotFoundError, subprocess.CalledProcessError):
        cmd_path = desktop / f"{app_name}.command"
        content = (
            "#!/bin/bash\n"
            f"cd {shlex.quote(str(workdir))}\n"
            f"{command}\n"
        )
        cmd_path.write_text(content)
        cmd_path.chmod(cmd_path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
        return cmd_path


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_desktop_shortcut(app_name: str = "Aircraft Designer", icon_path: str | None = None) -> Path:
    """Create a desktop shortcut launching the application.

    Parameters
    ----------
    app_name:
        Name of the shortcut.
    icon_path:
        Optional path to an icon file.

    Returns
    -------
    Path
        The path to the created shortcut.
    """

    root = Path(__file__).resolve().parents[1]
    system = platform.system()
    target, args, workdir = _resolve_target_and_workdir(root)

    icon: Path | None
    if icon_path:
        p = Path(icon_path)
        icon = p if p.exists() else None
    else:
        icon = _default_icon(root, system)

    desktop = _desktop_dir(system)

    if system == "Windows":
        shortcut = desktop / f"{app_name}.lnk"
        _windows_create_shortcut(shortcut, target, args, workdir, icon)
    elif system == "Linux":
        shortcut = desktop / f"{app_name}.desktop"
        command = " ".join(shlex.quote(str(p)) for p in [target, *args])
        _linux_create_shortcut(shortcut, app_name, command, workdir, icon)
    elif system == "Darwin":
        command = " ".join(shlex.quote(str(p)) for p in [target, *args])
        shortcut = _macos_create_shortcut(desktop, app_name, command, workdir)
    else:
        raise RuntimeError(f"Unsupported platform: {system}")

    return shortcut.resolve()


# ---------------------------------------------------------------------------
# PyQt5 integration snippet (commented)
# ---------------------------------------------------------------------------
# Example usage inside a PyQt5 MainWindow:
#
# from PyQt5.QtWidgets import QAction, QMessageBox
#
# def setup_shortcut_action(self):
#     action = QAction("Créer un raccourci Bureau", self)
#     action.triggered.connect(self._on_create_shortcut)
#     self.menuBar().addAction(action)
#
# def _on_create_shortcut(self):
#     try:
#         path = create_desktop_shortcut()
#         QMessageBox.information(self, "Succès", f"Raccourci créé : {path}")
#     except Exception as exc:  # noqa: BLE001
#         QMessageBox.critical(self, "Erreur", str(exc))

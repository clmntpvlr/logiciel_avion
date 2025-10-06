"""Command line interface to create a desktop shortcut."""
from __future__ import annotations

import argparse

from aircraft_designer.tools.shortcut_creator import create_desktop_shortcut


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a desktop shortcut")
    parser.add_argument("--name", default="Aircraft Designer", help="Shortcut name")
    parser.add_argument("--icon", default=None, help="Optional path to an icon")
    args = parser.parse_args()
    try:
        path = create_desktop_shortcut(app_name=args.name, icon_path=args.icon)
    except Exception as exc:  # noqa: BLE001
        print(exc)
        return 1
    print(f"Raccourci créé : {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

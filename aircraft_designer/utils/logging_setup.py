"""Simple logging configuration."""
from __future__ import annotations

import logging
from pathlib import Path

from .paths import logs_dir


_loggers: dict[str, logging.Logger] = {}


def get_logger(name: str) -> logging.Logger:
    """Return a logger writing into shared log directory."""
    if name in _loggers:
        return _loggers[name]
    logs_dir()
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        file_handler = logging.FileHandler(Path(logs_dir()) / "database.log", encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    _loggers[name] = logger
    return logger

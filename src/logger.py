"""Configuração simples de logs locais para console e arquivo."""

from __future__ import annotations

import logging
from pathlib import Path


def configure_logging(level: str, directory: Path, application_name: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    root = logging.getLogger(application_name)
    root.setLevel(level)
    root.handlers.clear()
    root.propagate = False

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    file_handler = logging.FileHandler(
        directory / f"{application_name}.log", encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)


def get_logger(application_name: str, name: str) -> logging.Logger:
    return logging.getLogger(f"{application_name}.{name}")

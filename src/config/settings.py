"""Configurações tipadas carregadas de settings.ini."""

from __future__ import annotations

import sys
from configparser import ConfigParser
from configparser import Error as ConfigParserError
from dataclasses import dataclass
from pathlib import Path


def _resolve_default_settings_path() -> Path:
    """Resolve o caminho do settings.ini em modo dev ou executável (PyInstaller)."""
    if getattr(sys, "frozen", False):
        exe_dir_ini = Path(sys.executable).resolve().parent / "settings.ini"
        if exe_dir_ini.is_file():
            return exe_dir_ini
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            bundled_ini = Path(meipass) / "src" / "config" / "settings.ini"
            if bundled_ini.is_file():
                return bundled_ini
    return Path(__file__).with_name("settings.ini")


DEFAULT_SETTINGS_PATH = _resolve_default_settings_path()


@dataclass(frozen=True, slots=True)
class Settings:
    application_name: str
    environment: str
    dry_run: bool
    target_url: str
    timeout_seconds: int
    max_retries: int
    retry_delay_seconds: int
    log_level: str
    log_directory: Path

    @classmethod
    def load(cls, path: str | Path | None = None) -> Settings:
        settings_path = Path(path) if path else _resolve_default_settings_path()
        if not settings_path.is_file():
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {settings_path}")

        parser = ConfigParser()
        loaded = parser.read(settings_path, encoding="utf-8")
        if not loaded:
            raise ValueError(f"Não foi possível ler o arquivo: {settings_path}")

        try:
            timeout = parser.getint("automation", "timeout_seconds")
            dry_run = parser.getboolean("application", "dry_run")
            max_retries = parser.getint("automation", "max_retries", fallback=3)
            retry_delay = parser.getint("automation", "retry_delay_seconds", fallback=2)

            settings = cls(
                application_name=parser.get("application", "name"),
                environment=parser.get("application", "environment"),
                dry_run=dry_run,
                target_url=parser.get("automation", "target_url"),
                timeout_seconds=timeout,
                max_retries=max_retries,
                retry_delay_seconds=retry_delay,
                log_level=parser.get("logging", "level").upper(),
                log_directory=Path(parser.get("logging", "directory")),
            )
        except (ConfigParserError, KeyError, ValueError) as exc:
            raise ValueError(f"Configuração inválida em {settings_path}: {exc}") from exc

        settings._validate()
        return settings

    def _validate(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("automation.timeout_seconds deve ser maior que zero")
        if self.max_retries <= 0:
            raise ValueError("automation.max_retries deve ser maior que zero")
        if self.retry_delay_seconds < 0:
            raise ValueError("automation.retry_delay_seconds não pode ser negativo")
        if not self.application_name.strip():
            raise ValueError("application.name não pode estar vazio")

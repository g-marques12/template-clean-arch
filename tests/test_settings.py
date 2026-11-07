from pathlib import Path

import pytest

from src.config.settings import Settings


def test_load_settings_from_ini(tmp_path: Path) -> None:
    ini = tmp_path / "settings.ini"
    ini.write_text(
        """[application]
name = test-app
environment = test
dry_run = true

[automation]
target_url = https://example.com
timeout_seconds = 10

[logging]
level = debug
directory = test-logs
""",
        encoding="utf-8",
    )

    settings = Settings.load(ini)

    assert settings.application_name == "test-app"
    assert settings.dry_run is True
    assert settings.timeout_seconds == 10
    assert settings.log_level == "DEBUG"


def test_load_settings_fails_when_file_does_not_exist(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        Settings.load(tmp_path / "missing.ini")

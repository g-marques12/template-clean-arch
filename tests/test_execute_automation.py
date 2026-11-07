import logging
from pathlib import Path
from unittest.mock import Mock

import pytest

from src.config.settings import Settings
from src.use_cases.execute_automation import ExecuteAutomationUseCase


def _make_settings(target_url: str = "https://example.com") -> Settings:
    return Settings(
        application_name="test-app",
        environment="test",
        dry_run=True,
        target_url=target_url,
        timeout_seconds=10,
        log_level="INFO",
        log_directory=Path("logs"),
    )


def test_execute_automation_navigates_to_url() -> None:
    selenium_mock = Mock()
    logger_mock = logging.getLogger("test")
    settings = _make_settings("https://example.com")

    use_case = ExecuteAutomationUseCase(
        settings=settings,
        selenium_service=selenium_mock,
        logger=logger_mock,
    )

    result = use_case.execute()

    selenium_mock.acessar_url.assert_called_once_with("https://example.com")
    assert result == "Fluxo executado com sucesso."


def test_execute_automation_rejects_invalid_url() -> None:
    selenium_mock = Mock()
    logger_mock = logging.getLogger("test")
    settings = _make_settings("url-invalida.com")

    use_case = ExecuteAutomationUseCase(
        settings=settings,
        selenium_service=selenium_mock,
        logger=logger_mock,
    )

    with pytest.raises(ValueError, match="http"):
        use_case.execute()

    selenium_mock.acessar_url.assert_not_called()

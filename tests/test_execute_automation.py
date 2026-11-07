import logging
from pathlib import Path
from unittest.mock import Mock, call

import pytest

from src.config.settings import Settings
from src.use_cases.execute_automation import ExecuteAutomationUseCase


def _make_settings(
    target_url: str = "https://example.com", max_retries: int = 3, retry_delay: int = 0
) -> Settings:
    return Settings(
        application_name="test-app",
        environment="test",
        dry_run=True,
        target_url=target_url,
        timeout_seconds=10,
        max_retries=max_retries,
        retry_delay_seconds=retry_delay,
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


def test_execute_automation_retries_on_failure_and_succeeds() -> None:
    selenium_mock = Mock()
    # Falha na 1ª tentativa e tem sucesso na 2ª
    selenium_mock.acessar_url.side_effect = [RuntimeError("Timeout transitório"), None]
    logger_mock = logging.getLogger("test-retry")
    settings = _make_settings("https://example.com", max_retries=2, retry_delay=0)

    use_case = ExecuteAutomationUseCase(
        settings=settings,
        selenium_service=selenium_mock,
        logger=logger_mock,
    )

    result = use_case.execute()

    assert result == "Fluxo executado com sucesso."
    assert selenium_mock.acessar_url.call_count == 2
    selenium_mock.tirar_screenshot.assert_called_once()


def test_execute_automation_raises_when_max_retries_exceeded() -> None:
    selenium_mock = Mock()
    selenium_mock.acessar_url.side_effect = RuntimeError("Erro permanente")
    logger_mock = logging.getLogger("test-error")
    settings = _make_settings("https://example.com", max_retries=2, retry_delay=0)

    use_case = ExecuteAutomationUseCase(
        settings=settings,
        selenium_service=selenium_mock,
        logger=logger_mock,
    )

    with pytest.raises(RuntimeError, match="Erro permanente"):
        use_case.execute()

    assert selenium_mock.acessar_url.call_count == 2

"""Ponto de entrada principal da aplicação."""

from __future__ import annotations

from src.config.settings import Settings
from src.logger import configure_logging, get_logger
from src.services.selenium_service import SeleniumService
from src.use_cases.execute_automation import ExecuteAutomationUseCase


def main() -> None:
    settings = Settings.load()

    configure_logging(
        level=settings.log_level,
        directory=settings.log_directory,
        application_name=settings.application_name,
    )

    logger = get_logger(settings.application_name, "main")
    logger.info("Processo iniciado")

    # Inicia o serviço de automação web com Selenium
    selenium = SeleniumService(
        timeout_padrao=settings.timeout_seconds,
        headless=False,
    )

    try:
        # Instancia e executa o caso de uso orquestrador
        use_case = ExecuteAutomationUseCase(
            settings=settings,
            selenium_service=selenium,
            logger=logger,
        )
        message = use_case.execute()

    except Exception:
        logger.exception("Processo finalizado com erro")
        raise
    else:
        logger.info("Processo finalizado com sucesso | %s", message)
    finally:
        # Dica: descomente para fechar o navegador automaticamente no fim
        # selenium.fechar_navegador()
        pass


if __name__ == "__main__":
    main()

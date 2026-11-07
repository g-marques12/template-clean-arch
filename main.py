"""Ponto de entrada principal da aplicação."""

from __future__ import annotations

from src.config.settings import Settings
from src.logger import configure_logging, get_logger
from src.services.automation_service import AutomationService
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

    try:
        # 1. Instanciar Services (Integrações externas / Infraestrutura)
        automation_service = AutomationService(
            dry_run=settings.dry_run,
            timeout_seconds=settings.timeout_seconds,
            logger=get_logger(settings.application_name, "service"),
        )
        # api_service = ApiService(...)
        # file_service = FileService(...)

        # 2. Instanciar e executar Use Cases (Regras de negócio)
        use_case = ExecuteAutomationUseCase(
            settings=settings,
            automation_service=automation_service,
        )
        message = use_case.execute()

    except Exception:
        logger.exception("Processo finalizado com erro")
        raise
    else:
        logger.info("Processo finalizado com sucesso | %s", message)


if __name__ == "__main__":
    main()

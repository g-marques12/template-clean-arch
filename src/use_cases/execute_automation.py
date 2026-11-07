"""Caso de uso orquestrador da automação."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from src.config.settings import Settings

if TYPE_CHECKING:
    from src.services.selenium_service import SeleniumService


class ExecuteAutomationUseCase:
    def __init__(
        self,
        settings: Settings,
        selenium_service: SeleniumService,
        logger: logging.Logger,
    ) -> None:
        self.settings = settings
        self.bot = selenium_service
        self.logger = logger

    def execute(self) -> str:
        if not self.settings.target_url.startswith(("http://", "https://")):
            raise ValueError(
                f"A URL configurada deve iniciar com http:// ou https://: {self.settings.target_url}"
            )

        self.logger.info("Navegando até a URL: %s", self.settings.target_url)
        self.bot.acessar_url(self.settings.target_url)

        # -------------------------------------------------------------
        # Aqui você orquestra e chama seus Use Cases específicos:
        # Exemplo:
        #
        # login_use_case = LoginUseCase(selenium_service=self.bot)
        # login_use_case.execute()
        #
        # emitir_dados_use_case = EmitirDadosUseCase(selenium_service=self.bot)
        # emitir_dados_use_case.execute()
        # -------------------------------------------------------------

        return "Fluxo executado com sucesso."

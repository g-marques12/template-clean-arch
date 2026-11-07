"""Caso de uso orquestrador da automação com gestão de retentativas."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING
from src.config.settings import Settings

if TYPE_CHECKING:
    from src.services.selenium_service import SeleniumService


class ExecuteAutomationUseCase:
    """
    Orquestrador principal do processo.
    Responsável por gerenciar o ciclo de vida da execução, aplicar política
    de retentativas contra falhas transitórias e acionar os Use Cases do projeto.
    """

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
        """Executa a orquestração do processo com suporte a retentativas configuráveis."""
        if not self.settings.target_url.startswith(("http://", "https://")):
            raise ValueError(
                f"A URL configurada deve iniciar com http:// ou https://: {self.settings.target_url}"
            )

        tentativa = 1
        max_tentativas = self.settings.max_retries

        while tentativa <= max_tentativas:
            try:
                self.logger.info(
                    "Iniciando ciclo de orquestração [Tentativa %s de %s]",
                    tentativa,
                    max_tentativas,
                )
                self._executar_passos()
                self.logger.info("Ciclo de orquestração finalizado com sucesso!")
                return "Fluxo executado com sucesso."

            except Exception as exc:
                self.logger.warning(
                    "Falha durante a tentativa %s/%s: %s",
                    tentativa,
                    max_tentativas,
                    exc,
                )

                # Salva screenshot para diagnóstico da falha na pasta logs/
                screenshot_path = (
                    self.settings.log_directory
                    / f"erro_tentativa_{tentativa}.png"
                )
                try:
                    self.bot.tirar_screenshot(screenshot_path)
                    self.logger.info("Screenshot de auditoria gravado em: %s", screenshot_path)
                except Exception:
                    pass

                if tentativa >= max_tentativas:
                    self.logger.error("Limite máximo de retentativas atingido. Abortando execução.")
                    raise

                self.logger.info(
                    "Aguardando %s segundos antes da próxima tentativa...",
                    self.settings.retry_delay_seconds,
                )
                time.sleep(self.settings.retry_delay_seconds)
                self._recuperar_estado_para_retry()
                tentativa += 1

        return "Fluxo finalizado."

    def _executar_passos(self) -> None:
        """
        Executa a sequência ordenada dos Use Cases do seu projeto.
        
        Cada Use Case possui seu próprio try/except interno para tratar e
        formatar os erros específicos de seu domínio.
        """
        # 1. Navegação inicial
        self.logger.info("Acessando URL alvo: %s", self.settings.target_url)
        self.bot.acessar_url(self.settings.target_url)

        # ---------------------------------------------------------------------
        # 2. Instanciação e execução dos Use Cases específicos do projeto:
        #
        # login_use_case = RealizarLoginUseCase(
        #     selenium_service=self.bot,
        #     settings=self.settings,
        #     logger=self.logger,
        # )
        # login_use_case.execute()
        #
        # emitir_dados_use_case = EmitirDadosUseCase(
        #     selenium_service=self.bot,
        #     settings=self.settings,
        #     logger=self.logger,
        # )
        # emitir_dados_use_case.execute()
        # ---------------------------------------------------------------------

    def _recuperar_estado_para_retry(self) -> None:
        """Prepara o navegador antes de uma nova tentativa (atualiza página ou volta à raiz)."""
        try:
            self.logger.info("Restaurando estado do navegador para a próxima tentativa...")
            self.bot.voltar_conteudo_principal()
            self.bot.atualizar_pagina()
        except Exception as exc:
            self.logger.debug("Não foi possível atualizar a página para retry: %s", exc)

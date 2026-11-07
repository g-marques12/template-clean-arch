"""Implementação do serviço base de automação/integração."""

from __future__ import annotations

import logging
import webbrowser


class AutomationService:
    def __init__(
        self,
        dry_run: bool,
        timeout_seconds: int,
        logger: logging.Logger,
    ) -> None:
        self._dry_run = dry_run
        self._timeout_seconds = timeout_seconds
        self._logger = logger

    def open_url(self, url: str) -> None:
        if self._dry_run:
            self._logger.info(
                "DRY-RUN | abrir URL: %s (timeout=%ss)",
                url,
                self._timeout_seconds,
            )
            return

        self._logger.info("Abrindo URL: %s", url)
        webbrowser.open(url)

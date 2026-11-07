"""Caso de uso principal do projeto."""

from __future__ import annotations

from typing import Protocol

from src.config.settings import Settings


class AutomationGateway(Protocol):
    def open_url(self, url: str) -> None: ...


class ExecuteAutomationUseCase:
    def __init__(
        self,
        settings: Settings,
        automation_service: AutomationGateway,
    ) -> None:
        self.settings = settings
        self.automation_service = automation_service

    def execute(self) -> str:
        if not self.settings.target_url.startswith(("http://", "https://")):
            raise ValueError(
                f"A URL configurada deve iniciar com http:// ou https://: {self.settings.target_url}"
            )

        # Exemplo de passo do caso de uso (remova e implemente sua regra de negócio)
        self.automation_service.open_url(self.settings.target_url)

        return "Fluxo executado com sucesso."

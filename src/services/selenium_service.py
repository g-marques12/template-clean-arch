from __future__ import annotations

import base64
import os
import time
from pathlib import Path
from typing import Any
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
    NoSuchElementException,
)


class SeleniumService:
    """Serviço robusto para automações web com Selenium WebDriver no Google Chrome."""

    def __init__(
        self,
        timeout_padrao: int = 15,
        headless: bool = False,
        diretorio_download: str | Path | None = None,
    ) -> None:
        self.timeout_padrao = timeout_padrao
        self.driver = self._configurar_driver(headless, diretorio_download)
        self.wait = WebDriverWait(self.driver, self.timeout_padrao)

    def _configurar_driver(
        self, headless: bool, diretorio_download: str | Path | None
    ) -> webdriver.Chrome:
        """Configura as opções do Chrome para ambiente seguro e resiliente de automação."""
        options = Options()
        if headless:
            options.add_argument("--headless=new")

        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        if diretorio_download:
            download_str = str(Path(diretorio_download).resolve())
            Path(download_str).mkdir(parents=True, exist_ok=True)
            prefs = {
                "download.default_directory": download_str,
                "download.prompt_for_download": False,
                "directory_upgrade": True,
                "safebrowsing.enabled": True,
            }
            options.add_experimental_option("prefs", prefs)

        return webdriver.Chrome(options=options)

    # =========================================================================
    # NAVEGAÇÃO E CICLO DE VIDA DO NAVEGADOR
    # =========================================================================
    def acessar_url(self, url: str) -> None:
        """Navega para a URL informada."""
        self.driver.get(url)

    def atualizar_pagina(self) -> None:
        """Recarrega a página atual."""
        self.driver.refresh()

    def obter_url_atual(self) -> str:
        """Retorna a URL corrente do navegador."""
        return self.driver.current_url

    def obter_titulo_pagina(self) -> str:
        """Retorna o título (<title>) da página atual."""
        return self.driver.title

    def fechar_aba_atual(self) -> None:
        """Fecha a aba atualmente em foco."""
        self.driver.close()

    def fechar_navegador(self) -> None:
        """Fecha todas as abas e encerra a sessão do WebDriver."""
        if getattr(self, "driver", None):
            try:
                self.driver.quit()
            except Exception:
                pass

    # =========================================================================
    # ESPERAS EXPLÍCITAS E VERIFICAÇÕES
    # =========================================================================
    def esperar_elemento_visivel(
        self, by: str, seletor: str, timeout: int | None = None
    ) -> WebElement:
        """Aguarda até que o elemento esteja presente no DOM e visível na tela."""
        tempo = timeout or self.timeout_padrao
        try:
            return WebDriverWait(self.driver, tempo).until(
                EC.visibility_of_element_located((str(by), seletor))
            )
        except TimeoutException as exc:
            raise TimeoutException(
                f"Timeout: elemento '{seletor}' não ficou visível após {tempo}s."
            ) from exc

    def esperar_elemento_clicavel(
        self, by: str, seletor: str, timeout: int | None = None
    ) -> WebElement:
        """Aguarda até que o elemento esteja visível e habilitado para clique."""
        tempo = timeout or self.timeout_padrao
        try:
            return WebDriverWait(self.driver, tempo).until(
                EC.element_to_be_clickable((str(by), seletor))
            )
        except TimeoutException as exc:
            raise TimeoutException(
                f"Timeout: elemento '{seletor}' não ficou clicável após {tempo}s."
            ) from exc

    def esperar_elemento_desaparecer(
        self, by: str, seletor: str, timeout: int | None = None
    ) -> bool:
        """Aguarda até que um elemento (ex: spinner de loading) desapareça da tela."""
        tempo = timeout or self.timeout_padrao
        return WebDriverWait(self.driver, tempo).until(
            EC.invisibility_of_element_located((str(by), seletor))
        )

    def verificar_elemento_existe(
        self, by: str, seletor: str, timeout: int = 3
    ) -> bool:
        """Verifica rapidamente se um elemento existe no DOM, retornando True ou False."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((str(by), seletor))
            )
            return True
        except TimeoutException:
            return False

    def encontrar_elementos(self, by: str, seletor: str) -> list[WebElement]:
        """Retorna uma lista de elementos encontrados com o seletor."""
        return self.driver.find_elements(str(by), seletor)

    # =========================================================================
    # INTERAÇÕES: CLIQUES, DIGITAÇÃO E TECLADO
    # =========================================================================
    def clicar(self, by: str, seletor: str, retries: int = 3) -> None:
        """Clica no elemento, com scroll automático e retentativas em caso de interceptação."""
        for tentativa in range(1, retries + 1):
            try:
                elemento = self.esperar_elemento_visivel(by, seletor)
                self.scroll_ate_elemento(elemento)
                time.sleep(0.3)

                elemento_clicavel = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((str(by), seletor))
                )
                elemento_clicavel.click()
                return
            except (ElementClickInterceptedException, StaleElementReferenceException) as exc:
                if tentativa == retries:
                    self.tirar_screenshot(f"erro_click_{seletor.replace('/', '_')[:30]}.png")
                    raise Exception(
                        f"Falha ao clicar no elemento '{seletor}' após {retries} tentativas: {exc}"
                    ) from exc
                time.sleep(1)

    def clicar_via_javascript(self, elemento_ou_seletor: WebElement | tuple[str, str]) -> None:
        """Força o clique em um elemento via JavaScript (ignora bloqueios e interceptações visuais)."""
        if isinstance(elemento_ou_seletor, tuple):
            by, seletor = elemento_ou_seletor
            elemento = self.esperar_elemento_visivel(by, seletor)
        else:
            elemento = elemento_ou_seletor
        self.driver.execute_script("arguments[0].click();", elemento)

    def preencher_texto(
        self, by: str, seletor: str, texto: str, limpar_campo: bool = True
    ) -> None:
        """Preenche texto em campo de input."""
        elemento = self.esperar_elemento_visivel(by, seletor)
        if limpar_campo:
            elemento.clear()
        elemento.send_keys(texto)

    def enviar_tecla(self, by: str, seletor: str, tecla: str) -> None:
        """Envia tecla especial (ex: 'ENTER', 'TAB', 'ESCAPE') para um elemento."""
        elemento = self.esperar_elemento_visivel(by, seletor)
        tecla_obj = getattr(Keys, tecla.upper(), tecla)
        elemento.send_keys(tecla_obj)

    def extrair_texto(self, by: str, seletor: str) -> str:
        """Extrai o texto visível de um elemento."""
        elemento = self.esperar_elemento_visivel(by, seletor)
        return elemento.text.strip()

    def extrair_atributo(self, by: str, seletor: str, atributo: str) -> str | None:
        """Extrai o valor de um atributo HTML (ex: 'value', 'href', 'src')."""
        elemento = self.esperar_elemento_visivel(by, seletor)
        return elemento.get_attribute(atributo)

    # =========================================================================
    # SELEÇÃO (COMBOBOX / DROPDOWN <select>)
    # =========================================================================
    def selecionar_dropdown_por_texto(self, by: str, seletor: str, texto_visivel: str) -> None:
        """Seleciona uma opção de uma tag <select> pelo texto visível."""
        elemento = self.esperar_elemento_visivel(by, seletor)
        select = Select(elemento)
        select.select_by_visible_text(texto_visivel)

    def selecionar_dropdown_por_valor(self, by: str, seletor: str, valor: str) -> None:
        """Seleciona uma opção de uma tag <select> pelo atributo value."""
        elemento = self.esperar_elemento_visivel(by, seletor)
        select = Select(elemento)
        select.select_by_value(valor)

    # =========================================================================
    # AÇÕES AVANÇADAS DO MOUSE E SCROLL
    # =========================================================================
    def passar_mouse_por_cima(self, by: str, seletor: str) -> None:
        """Hover do mouse sobre um elemento (útil para menus flutuantes)."""
        elemento = self.esperar_elemento_visivel(by, seletor)
        ActionChains(self.driver).move_to_element(elemento).perform()

    def duplo_clique(self, by: str, seletor: str) -> None:
        """Executa um clique duplo sobre o elemento."""
        elemento = self.esperar_elemento_visivel(by, seletor)
        ActionChains(self.driver).double_click(elemento).perform()

    def scroll_ate_elemento(self, elemento_ou_seletor: WebElement | tuple[str, str]) -> None:
        """Faz a rolagem da página até deixar o elemento centralizado."""
        if isinstance(elemento_ou_seletor, tuple):
            by, seletor = elemento_ou_seletor
            elemento = self.esperar_elemento_visivel(by, seletor)
        else:
            elemento = elemento_ou_seletor
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)

    def scroll_para_o_fim(self) -> None:
        """Rola a página até o final."""
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # =========================================================================
    # ABAS, JANELAS E IFRAMES
    # =========================================================================
    def trocar_para_nova_aba(self, indice_aba: int = -1) -> None:
        """
        Alterna o foco para outra aba.
        Índice -1: última aba aberta (geralmente aberta por clique).
        Índice 0: aba principal original.
        """
        abas = self.driver.window_handles
        self.driver.switch_to.window(abas[indice_aba])

    def mudar_para_iframe(self, by: str, seletor: str) -> None:
        """Muda o contexto de execução para dentro de um <iframe>."""
        elemento_iframe = self.esperar_elemento_visivel(by, seletor)
        self.driver.switch_to.frame(elemento_iframe)

    def voltar_conteudo_principal(self) -> None:
        """Retorna o contexto para a página raiz (fora de iframes)."""
        self.driver.switch_to.default_content()

    # =========================================================================
    # ALERTAS DO NAVEGADOR (pop-ups JS alert/confirm)
    # =========================================================================
    def aceitar_alerta(self, timeout: int = 5) -> str:
        """Aguarda e clica em 'OK' no alerta do navegador, retornando seu texto."""
        alerta = WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        texto = alerta.text
        alerta.accept()
        return texto

    def cancelar_alerta(self, timeout: int = 5) -> str:
        """Aguarda e clica em 'Cancelar' no alerta do navegador, retornando seu texto."""
        alerta = WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        texto = alerta.text
        alerta.dismiss()
        return texto

    # =========================================================================
    # IMPRESSÃO EM PDF E AUDITORIA VISUAL (SCREENSHOT)
    # =========================================================================
    def salvar_pagina_como_pdf(self, caminho_arquivo: str | Path) -> Path:
        """
        Gera e salva o PDF da página atual silenciosamente via Chrome DevTools Protocol (CDP).
        Cria automaticamente as pastas necessárias no disco.
        """
        destino = Path(caminho_arquivo)
        destino.parent.mkdir(parents=True, exist_ok=True)

        resultado = self.driver.execute_cdp_cmd(
            "Page.printToPDF",
            {
                "printBackground": True,
                "landscape": False,
                "preferCSSPageSize": True,
            },
        )

        conteudo_pdf = base64.b64decode(resultado["data"])
        with open(destino, "wb") as f:
            f.write(conteudo_pdf)

        return destino

    def tirar_screenshot(self, nome_arquivo: str | Path) -> Path:
        """Captura screenshot da tela e salva garantindo criação das pastas."""
        destino = Path(nome_arquivo)
        if not destino.suffix:
            destino = destino.with_suffix(".png")
        destino.parent.mkdir(parents=True, exist_ok=True)

        self.driver.save_screenshot(str(destino))
        return destino

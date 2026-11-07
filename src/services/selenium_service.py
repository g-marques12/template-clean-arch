import os
import time
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    TimeoutException, 
    ElementClickInterceptedException, 
    StaleElementReferenceException
)

class SeleniumService:
    def __init__(self, timeout_padrao: int = 15, headless: bool = False, diretorio_download: str = None):
        self.timeout_padrao = timeout_padrao
        self.driver = self._configurar_driver(headless, diretorio_download)
        self.wait = WebDriverWait(self.driver, self.timeout_padrao)

    def _configurar_driver(self, headless: bool, diretorio_download: str) -> webdriver.Chrome:
        """Configura as opções do Chrome para um ambiente de automação."""
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        
        # Configuração de diretório de download dinâmico
        if diretorio_download:
            prefs = {
                "download.default_directory": diretorio_download,
                "download.prompt_for_download": False,
                "directory_upgrade": True
            }
            options.add_experimental_option("prefs", prefs)

        return webdriver.Chrome(options=options)

    # NAVEGAÇÃO E CONTROLE
    def acessar_url(self, url: str) -> None:
        """Acessa uma página web específica."""
        self.driver.get(url)

    def atualizar_pagina(self) -> None:
        self.driver.refresh()

    def fechar_navegador(self) -> None:
        """Encerra a sessão do WebDriver."""
        if self.driver:
            self.driver.quit()

    # ESPERAS E BUSCAS
    def esperar_elemento_visivel(self, by: By, seletor: str, timeout: int = None) -> WebElement:
        """Aguarda até que o elemento esteja visível na tela."""
        tempo_espera = timeout if timeout else self.timeout_padrao
        wait = WebDriverWait(self.driver, tempo_espera)
        try:
            return wait.until(EC.visibility_of_element_located((by, seletor)))
        except TimeoutException:
            raise Exception(f"Timeout: Elemento '{seletor}' não ficou visível após {tempo_espera}s.")

    def verificar_elemento_existe(self, by: By, seletor: str, timeout: int = 3) -> bool:
        """Verifica de forma rápida se um elemento existe na página, retornando True ou False."""
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, seletor)))
            return True
        except TimeoutException:
            return False

    # INTERAÇÕES (CLICK, TYPE)
    def clicar(self, by: By, seletor: str, retries: int = 3) -> None:
        """Clica em um elemento, lidando com interceptações ou referências obsoletas."""
        tentativa = 0
        while tentativa < retries:
            try:
                elemento = self.esperar_elemento_visivel(by, seletor)
                # Scroll até o elemento antes de clicar costuma evitar erros de interceptação
                self.driver.execute_script("arguments[0].scrollIntoView(true);", elemento)
                # Pequena pausa para a UI renderizar após o scroll
                time.sleep(0.5) 
                
                wait_clicavel = WebDriverWait(self.driver, 5)
                elemento_clicavel = wait_clicavel.until(EC.element_to_be_clickable((by, seletor)))
                elemento_clicavel.click()
                return
            except (ElementClickInterceptedException, StaleElementReferenceException) as e:
                tentativa += 1
                if tentativa == retries:
                    self.tirar_screenshot(f"erro_click_{seletor.replace('/', '_')}.png")
                    raise Exception(f"Falha ao clicar no elemento '{seletor}' após {retries} tentativas. Erro: {str(e)}")
                time.sleep(1)

    def preencher_texto(self, by: By, seletor: str, texto: str, limpar_campo: bool = True) -> None:
        """Preenche um campo de input. Opcionalmente limpa o campo antes."""
        elemento = self.esperar_elemento_visivel(by, seletor)
        if limpar_campo:
            elemento.clear()
        elemento.send_keys(texto)

    def extrair_texto(self, by: By, seletor: str) -> str:
        """Extrai o texto interno de um elemento."""
        elemento = self.esperar_elemento_visivel(by, seletor)
        return elemento.text.strip()

    # FRAMES E ABAS
    def mudar_para_iframe(self, by: By, seletor: str) -> None:
        """Alterna o contexto do navegador para dentro de um iframe específico."""
        elemento_iframe = self.esperar_elemento_visivel(by, seletor)
        self.driver.switch_to.frame(elemento_iframe)

    def voltar_conteudo_principal(self) -> None:
        """Retorna o contexto para a página principal (fora de todos os iframes)."""
        self.driver.switch_to.default_content()

    def trocar_para_nova_aba(self, indice_aba: int = -1) -> None:
        """
        Alterna para uma aba específica.
        Índice -1 altera para a última aba aberta (geralmente a aba que acabou de abrir).
        Índice 0 altera para a primeira (original).
        """
        abas = self.driver.window_handles
        self.driver.switch_to.window(abas[indice_aba])

    # AUDITORIA E DEBUG
    def tirar_screenshot(self, nome_arquivo: str) -> str:
        """Tira um print da tela inteira. Útil para log de erros em execuções unattended."""
        if not nome_arquivo.endswith(".png"):
            nome_arquivo += ".png"
        
        caminho_completo = os.path.join(os.getcwd(), nome_arquivo)
        self.driver.save_screenshot(caminho_completo)
        return caminho_completo

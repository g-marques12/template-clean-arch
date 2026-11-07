# Template Clean Architecture Simplificado para Python

Este repositório contém uma estrutura simplificada de **Clean Architecture** para o desenvolvimento de projetos pessoais, automações e ferramentas em Python, pronta para publicação no GitHub e empacotamento em executável (`.exe`).

A arquitetura foi desenhada para ser simples, modular e sem burocracias, facilitando a manutenção e a escalabilidade do projeto sem camadas desnecessárias.

---

## Estrutura do Projeto

```text
template-clean-arch/
├── build/
│   ├── README.md                   # Guia detalhado para geração do executável
│   ├── build.bat                   # Atalho de build para Windows (CMD / duplo clique)
│   ├── build.ps1                   # Script de build para PowerShell
│   └── build_exe.py                # Empacotador automatizado com PyInstaller
├── resources/
│   └── README.md                   # Recursos estáticos, ícones (.ico) e arquivos auxiliares
├── src/
│   ├── config/
│   │   ├── settings.example.ini    # Modelo de configuração versionado no Git
│   │   ├── settings.ini            # Configurações locais e segredos (ignorado pelo Git)
│   │   └── settings.py             # Leitor tipado das configurações do arquivo INI
│   ├── services/
│   │   ├── __init__.py             # Exportador de serviços
│   │   └── automation_service.py   # Implementação concreta de integrações externas
│   ├── use_cases/
│   │   ├── __init__.py             # Exportador de casos de uso
│   │   └── execute_automation.py   # Regra de negócio e fluxo do caso de uso
│   ├── __init__.py
│   └── logger.py                   # Configuração consolidada de logs locais (console e arquivo)
├── tests/
│   ├── test_execute_automation.py  # Testes dos Casos de Uso
│   └── test_settings.py            # Testes das configurações
├── main.py                         # Ponto de entrada e orquestrador principal da aplicação
├── pyproject.toml                  # Configuração de ferramentas (pytest e ruff)
└── requirements.txt                # Dependências de desenvolvimento, build e runtime
```

---

## Como as Partes se Relacionam

1. **`main.py`**: Ponto de entrada principal (Composition Root). Carrega as configurações tipadas, inicializa os logs locais, instancia os `Services` e `Use Cases`, e controla o ciclo de vida da execução (`try/except`).
2. **`src/logger.py`**: Responsável por configurar os logs no console e criar os arquivos de log físicos na pasta `logs/`.
3. **`src/config/settings.py`**: Carrega e valida as configurações do arquivo `settings.ini` (suportando tanto execução via código-fonte quanto execução via `.exe` compilado).
4. **`src/use_cases/`**: Contém as regras de negócio do projeto, desacopladas de implementações externas através de protocolos/contratos.
5. **`src/services/`**: Implementações concretas de infraestrutura e integrações externas (APIs, arquivos, navegador, banco de dados, GUI, etc.).
6. **`build/`**: Scripts que empacotam todo o projeto em um executável `.exe` pronto para distribuição na pasta `dist/`.

---

## Preparação do Ambiente

Requisito recomendado: Python 3.10 ou superior.

### 1. Instalação das Dependências

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configuração Local (`settings.ini`)

Por segurança, o arquivo `src/config/settings.ini` está no `.gitignore` para não subir credenciais ou configurações locais para o GitHub. Ao clonar o projeto em outra máquina, copie o arquivo de exemplo:

```powershell
Copy-Item src/config/settings.example.ini src/config/settings.ini
```

---

## Executando o Projeto

### Execução em Desenvolvimento

Para rodar diretamente via terminal (ou pressionando `F5` no VS Code):

```powershell
python main.py
```

### Gerando o Executável (`.exe`)

Quando finalizar o projeto e quiser gerar o executável na pasta `dist/`:

```powershell
python build/build_exe.py
```

*(Ou utilize `.\build\build.ps1` / `build\build.bat`. Veja mais opções como `--noconsole` e ícone customizado em `build/README.md`).*

---

## Testes e Qualidade

Para rodar os testes unitários:

```powershell
pytest
```

Para validar a formatação e qualidade do código com Ruff:

```powershell
ruff check .
```

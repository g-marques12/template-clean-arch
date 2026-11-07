# Build do Executável (`.exe`)

Esta pasta contém os scripts responsáveis por empacotar o projeto em um executável standalone utilizando **PyInstaller**.

---

## Como Gerar o Executável

A partir da raiz do projeto, escolha qualquer uma das opções abaixo:

### Via Python (Multiplataforma)
```powershell
python build/build_exe.py
```

### Via PowerShell (Windows)
```powershell
.\build\build.ps1
```

### Via Prompt / Duplo Clique (Windows)
```cmd
build\build.bat
```

---

## Opções Avançadas de Build

Você pode passar parâmetros extras para personalizar o executável gerado:

- **Ocultar janela de console** (ideal para projetos com interface gráfica ou execução silenciosa em background):
  ```powershell
  python build/build_exe.py --noconsole
  ```
- **Alterar o nome do executável** (por padrão, usa o `name` definido no `src/config/settings.ini`):
  ```powershell
  python build/build_exe.py --name meu-projeto
  ```
- **Definir ícone personalizado** (ou basta salvar um arquivo `resources/icon.ico` que ele será detectado automaticamente):
  ```powershell
  python build/build_exe.py --icon resources/meu_icone.ico
  ```
- **Gerar em modo pasta (`--onedir`)** em vez de arquivo único (`--onefile`):
  ```powershell
  python build/build_exe.py --onedir
  ```

---

## Saída do Build (`dist/`)

Ao finalizar, serão gerados na pasta `dist/`:
1. **`<nome-do-app>.exe`**: O executável pronto para distribuição.
2. **`settings.ini`**: Uma cópia externa das configurações ao lado do `.exe`. O projeto prioriza automaticamente o `settings.ini` que estiver na mesma pasta do executável (permitindo alterar URLs, timeouts ou `dry_run` sem precisar recompilar), e usa o `settings.ini` embutido como fallback caso o externo seja removido.

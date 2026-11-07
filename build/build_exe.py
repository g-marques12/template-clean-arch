"""Script de automação de build para gerar executável (.exe) via PyInstaller."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config.settings import Settings  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera o executável (.exe) do projeto utilizando PyInstaller."
    )
    parser.add_argument(
        "--name",
        type=str,
        default=None,
        help="Nome do executável (padrão: lido de application.name no settings.ini).",
    )
    parser.add_argument(
        "--noconsole",
        action="store_true",
        help="Oculta a janela de terminal ao rodar o executável (ideal para apps GUI ou background).",
    )
    parser.add_argument(
        "--onedir",
        action="store_true",
        help="Gera uma pasta com dependências em vez de um arquivo único (--onefile é o padrão).",
    )
    parser.add_argument(
        "--icon",
        type=str,
        default=None,
        help="Caminho para arquivo .ico (padrão: usa resources/icon.ico se existir).",
    )
    return parser.parse_args()


def build_executable() -> int:
    args = parse_args()
    settings = Settings.load()
    app_name = args.name or settings.application_name

    dist_dir = PROJECT_ROOT / "dist"
    work_dir = PROJECT_ROOT / "build" / ".work"
    entrypoint = PROJECT_ROOT / "main.py"
    settings_ini = PROJECT_ROOT / "src" / "config" / "settings.ini"
    resources_dir = PROJECT_ROOT / "resources"

    # Limpa artefatos anteriores
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if work_dir.exists():
        shutil.rmtree(work_dir)

    sep = os.pathsep
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name",
        app_name,
        "--distpath",
        str(dist_dir),
        "--workpath",
        str(work_dir),
        "--specpath",
        str(work_dir),
        "--add-data",
        f"{settings_ini}{sep}src/config",
    ]

    if resources_dir.exists():
        cmd.extend(["--add-data", f"{resources_dir}{sep}resources"])

    if args.onedir:
        cmd.append("--onedir")
    else:
        cmd.append("--onefile")

    if args.noconsole:
        cmd.append("--noconsole")

    icon_path = Path(args.icon) if args.icon else resources_dir / "icon.ico"
    if icon_path.is_file():
        cmd.extend(["--icon", str(icon_path)])

    cmd.append(str(entrypoint))

    print(f"[BUILD] Iniciando geração do executável '{app_name}'...")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, check=False)

    if result.returncode != 0:
        print(
            "\n[ERRO] Falha ao gerar o executável. "
            "Verifique se o PyInstaller está instalado (pip install -r requirements.txt)."
        )
        return result.returncode

    # Copia uma versão externa do settings.ini para a pasta dist/ para facilitar ajustes pós-build
    target_ini_dir = dist_dir / app_name if args.onedir else dist_dir
    target_ini_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(settings_ini, target_ini_dir / "settings.ini")

    exe_suffix = ".exe" if os.name == "nt" else ""
    exe_path = (
        dist_dir / app_name / f"{app_name}{exe_suffix}"
        if args.onedir
        else dist_dir / f"{app_name}{exe_suffix}"
    )

    print("\n[SUCESSO] Build finalizado!")
    print(f" -> Executável: {exe_path}")
    print(f" -> Configuração externa: {target_ini_dir / 'settings.ini'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(build_executable())

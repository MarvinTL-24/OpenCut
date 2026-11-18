"""
The Dark Archive - Google Drive Asset Synchronizer
Mapeia e baixa automaticamente elementos de textura, SFX, overlays e branding da pasta do Google Drive
para o diretório de assets local do OpenCut (E:\\OpenCut\\assets\\the_dark_archive).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path("E:/OpenCut")
ASSETS_DIR = BASE_DIR / "assets" / "the_dark_archive"

GDRIVE_CMD = os.environ.get(
    "GDRIVE_BIN",
    r"C:\Users\User\.gemini\config\plugins\gdrive\skills\gdrive\scripts\gdrive.cmd"
)
if not Path(GDRIVE_CMD).exists():
    GDRIVE_CMD = shutil.which("gdrive") or "gdrive"

CATALOG = {
    "overlays": {
        "old_film_grain.mp4": "1K9ld8MFFP5oAw97GrT-yhKaepWCVGOtz",
        "crumpled_paper.mp4": "14EseRiM7pGm_vbuUf5IhNQpQ0EVnlW5-",
        "vintage_film_effect.mp4": "1VMLGhAts8q6qbuPT9t20Pi4HSaaLb7ww",
        "overlay_video_effect.mp4": "15TFFmAmQM79hfSfDuAjSwGFDNoyY8e0C",
    },
    "sfx_drones": {
        "drone_tension_c29.wav": "15dgxceG6YMGWEvJvTL3Q0b2y6i--0Bbd",
        "drone_tension_c32.wav": "13n9ds2xjIlte5BuvLB9_SlFcGJcvu5aK",
    },
    "sfx_foley": {
        "vento_lento.mp3": "1MLfY6Nqd-MwZifGFecnHGextuRXxZk6D",
        "click_mecanico.mp3": "18GiIT4HRHayAvlnW5lrexlwSc7UEcaHH",
        "bip_radio.mp3": "1hTB53gFY6od1GtwAXDMkEnXhLfUUI1_d",
        "alerta_impacto.mp3": "1jaaV9wRu-rB7b6zbUV-8Y2l--Cr_H1SH",
    }
}

def sync_assets(force=False):
    """Baixa e sincroniza arquivos essenciais do Google Drive."""
    print("=" * 60)
    print(">>> SINCRONIZADOR DE ASSETS - GOOGLE DRIVE -> OPENCUT")
    print(f"Utilizando gdrive executável: {GDRIVE_CMD}")
    print("=" * 60)
    
    for category, files in CATALOG.items():
        cat_dir = ASSETS_DIR / category
        cat_dir.mkdir(parents=True, exist_ok=True)
        
        for filename, file_id in files.items():
            dest = cat_dir / filename
            if dest.exists() and not force:
                print(f"[OK] Já existe: {category}/{filename}")
                continue
            
            print(f"[BAIXANDO] {category}/{filename} (ID: {file_id})...")
            cmd = [str(GDRIVE_CMD), "readonly", "download", file_id, "--out", str(dest)]
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
                size_mb = dest.stat().st_size / (1024 * 1024) if dest.exists() else 0
                print(f"      -> Concluído ({size_mb:.2f} MB)")
            except subprocess.CalledProcessError as e:
                print(f"      [ERRO ao baixar {filename}]: {e.stderr.strip() if e.stderr else e}")

    print("=" * 60)
    print("Sincronização de assets concluída.")

if __name__ == "__main__":
    force_download = "--force" in sys.argv
    sync_assets(force=force_download)

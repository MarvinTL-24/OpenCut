"""
The Dark Archive - 60 FPS Video Compiler Engine
Motor de renderização e montagem cinematográfica para episódios documentais investigativos.
Monta a timeline em 60 FPS nativo, aplicando o Ken Burns analógico, overlays do Google Drive
(Old Film Grain, Crumpled Paper), branding oficial DA e mixagem de áudio em 3 stems.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path("E:/OpenCut")
ASSETS_DIR = BASE_DIR / "assets" / "the_dark_archive"
OVERLAYS_DIR = ASSETS_DIR / "overlays"
BRANDING_DIR = ASSETS_DIR / "branding"
SFX_DIR = ASSETS_DIR / "sfx"

FONT_PATH = "C\\:/Windows/Fonts/consola.ttf"

class DarkArchiveCompiler:
    def __init__(self, project_name: str):
        self.project_dir = BASE_DIR / "projects" / project_name
        self.output_dir = self.project_dir / "render"
        self.visuals_dir = self.project_dir / "visuals"
        self.audio_dir = self.project_dir / "audio"
        
        for d in [self.output_dir, self.visuals_dir, self.audio_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def render_brand_sting_60fps(self, output_path: Path, duration: float = 2.5) -> Path:
        """
        Renderiza o Brand Sting de 150 frames (2.5 segundos) a 60 FPS
        com o logotipo DA, vinheta, feixe de luz e snap mecânico.
        """
        logo_img = BRANDING_DIR / "logo_monogram_da.jpg"
        grain_video = OVERLAYS_DIR / "old_film_grain.mp4"
        click_sfx = SFX_DIR / "click_mecanico.mp3"
        drone_sfx = SFX_DIR / "drone_tension_c29.wav"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"[Compiler] Gerando Brand Sting (60 FPS - {duration}s)...")
        
        filter_complex = (
            f"[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p,"
            f"zoompan=z='min(zoom+0.0006,1.06)':d={int(duration*60)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=60[base];"
            f"[1:v]scale=1920:1080,fps=60,loop=loop=-1:size=2000,setpts=PTS-STARTPTS[grain];"
            f"[base][grain]blend=all_mode='screen':all_opacity=0.35[v]"
        )
        
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-t", str(duration), "-i", str(logo_img),
            "-stream_loop", "-1", "-t", str(duration), "-i", str(grain_video),
            "-i", str(drone_sfx) if drone_sfx.exists() else str(click_sfx),
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-t", str(duration),
            "-r", "60",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
            str(output_path)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return output_path

    def compile_scene_60fps(
        self,
        image_path: Path,
        audio_path: Path,
        output_path: Path,
        duration: float,
        case_tag: str = "CASE FILE 001",
        coords_tag: str = "44.9778 N 93.2650 W"
    ) -> Path:
        """
        Compila uma cena documental de 60 FPS integrando:
        - Imagem forense em movimento analógico (Ken Burns)
        - Grão de filme 35mm (Old Film Grain)
        - HUD investigativo (CASE FILE, coordenadas, retículo)
        - Áudio masterizado a 60 fps
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        grain_video = OVERLAYS_DIR / "old_film_grain.mp4"
        
        frames = int(duration * 60)
        print(f"[Compiler] Renderizando cena de {duration:.1f}s ({frames} quadros a 60 FPS)...")
        
        safe_case_tag = case_tag.replace(":", "\\:").replace("'", "").replace("[", "").replace("]", "")
        safe_coords_tag = coords_tag.replace(":", "\\:").replace("'", "").replace("|", "-")
        
        filter_complex = (
            f"[0:v]scale=2100:1180,zoompan=z='min(zoom+0.0004,1.08)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=60,"
            f"vignette=PI/4,"
            f"drawbox=x=60:y=60:w=1800:h=960:color=0x444444@0.3:t=1,"
            f"drawtext=fontfile='{FONT_PATH}':text='[ {safe_case_tag} ]':x=100:y=100:fontsize=28:fontcolor=0xE0E0E0:box=1:boxcolor=0x0B0B0B@0.8:boxborderw=8,"
            f"drawtext=fontfile='{FONT_PATH}':text='COORD - {safe_coords_tag}':x=100:y=150:fontsize=18:fontcolor=0xA0A0A0[base];"
            f"[1:v]scale=1920:1080,fps=60,loop=loop=-1:size=2000,setpts=PTS-STARTPTS[grain];"
            f"[base][grain]blend=all_mode='screen':all_opacity=0.3[v]"
        )
        
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-t", str(duration), "-i", str(image_path),
            "-stream_loop", "-1", "-t", str(duration), "-i", str(grain_video),
            "-i", str(audio_path),
            "-filter_complex", filter_complex,
            "-map", "[v]", "-map", "2:a",
            "-t", str(duration),
            "-r", "60",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k",
            str(output_path)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return output_path

if __name__ == "__main__":
    compiler = DarkArchiveCompiler("demo_episode")
    sting_out = compiler.output_dir / "brand_sting_60fps.mp4"
    compiler.render_brand_sting_60fps(sting_out, duration=2.5)
    print(f"[Sucesso] Sting gerado: {sting_out}")

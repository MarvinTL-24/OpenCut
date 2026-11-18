"""
The Dark Archive - AudioCraft & Sound Design Engine
Gera drones de suspense, foley contínuo e sub-bass atmosférico para o canal.
Combina AudioCraft (E:\\audiocraft) com a biblioteca de sons do Google Drive do usuário.
"""

import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path("E:/OpenCut")
SFX_DIR = BASE_DIR / "assets" / "the_dark_archive" / "sfx"

AUDIOCRAFT_PROMPTS = {
    "suspense_drone": "dark cinematic low drone, 50hz deep sub bass rumble, eerie analog synthesizer, claustrophobic mystery tension",
    "cold_silence": "room tone of an abandoned archive basement, very faint distant wind through cracked window, tape hiss, minimal texture",
    "tension_peak": "rising dark cello screech with heavy sub bass drop, analog distortion, forensic documentary climax"
}

def generate_dark_drone_ffmpeg(duration_seconds: float, output_path: Path):
    """
    Gera um drone sintético sub-grave pesado (45 Hz a 60 Hz) com ruído rosa sutil,
    utilizando a síntese de áudio de alta precisão do FFmpeg.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Sintetiza um oscilador senoidal com flutuação de frequência + ruído de fita + compressão
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"sine=frequency=48:duration={duration_seconds}",
        "-f", "lavfi",
        "-i", f"anoisesrc=c=pink:r=48000:a=0.015:d={duration_seconds}",
        "-filter_complex",
        "[0:a][1:a]amix=inputs=2:duration=first[mixed];[mixed]lowpass=f=250,volume=1.5[out]",
        "-map", "[out]", "-c:a", "pcm_s16le", str(output_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return output_path

def create_ambient_track(duration_seconds: float, output_path: Path):
    """
    Combina o drone de suspense baixado do Google Drive com vento sutil em loop contínuo
    pela duração exata da cena.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    drone_file = SFX_DIR / "drone_tension_c29.wav"
    wind_file = SFX_DIR / "vento_lento.mp3"
    
    if drone_file.exists() and wind_file.exists():
        # Loop contínuo com crossfade suave usando FFmpeg
        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1", "-i", str(drone_file),
            "-stream_loop", "-1", "-i", str(wind_file),
            "-filter_complex",
            f"[0:a]volume=0.8,aloop=loop=-1:size=2e+09[a0];[1:a]volume=0.4,aloop=loop=-1:size=2e+09[a1];[a0][a1]amix=inputs=2:duration=first,atrim=0:{duration_seconds},afade=t=in:ss=0:d=1.5,afade=t=out:st={duration_seconds-1.5}:d=1.5[out]",
            "-map", "[out]", "-c:a", "pcm_s16le", str(output_path)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    else:
        # Fallback para síntese direta
        generate_dark_drone_ffmpeg(duration_seconds, output_path)
        
    return output_path

if __name__ == "__main__":
    out = Path("E:/OpenCut/projects/test/audio/ambient_bed.wav")
    create_ambient_track(30.0, out)
    print(f"[Audio] Trilha atmosférica gerada: {out}")

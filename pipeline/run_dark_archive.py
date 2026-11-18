"""
The Dark Archive - Master AI Video Production Pipeline
Orquestrador central que integra:
- Google Drive Assets (Overlays, SFX, Texturas)
- E:\\ComfyUI (Geração visual e Ken Burns)
- E:\\audiocraft (Drones e ambiência)
- E:\\F5-TTS & E:\\faster-whisper (Narração do Arquivista e legendas)
- E:\\OpenCut (Montagem em 60 FPS nativo para episódios de até 25 min)
"""

import argparse
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path("E:/OpenCut")
PIPELINE_DIR = BASE_DIR / "pipeline"

from audiocraft_bridge import create_ambient_track
from comfyui_bridge import generate_shot
from engine_60fps import DarkArchiveCompiler
from narration_whisper import generate_subtitles_srt, generate_voiceover

# Roteiro demonstrativo baseado na estrutura de 8 atos de O Arquivista
DEMO_EPISODE_SCENES = [
    {
        "id": "cena_01_hook",
        "description": "Uma encruzilhada de terra no interior deserto, noite fria, neblina rasteira, poste de madeira com lâmpada piscando",
        "script": "Naquela madrugada de janeiro... o silêncio no vale não foi comum. Menos na casa de Bento. Lá dentro... as janelas amanheceram congeladas por dentro.",
        "duration": 8.0,
        "case_tag": "CASE FILE 001 - O VALE",
        "coords": "24.7136° S | 48.9211° W"
    },
    {
        "id": "cena_02_origem",
        "description": "Arquivo do necrotério com pastas desbotadas empilhadas em estante de ferro oxidada, luz lateral",
        "script": "Nenhum relatório oficial quis documentar o que os moradores viram na mata. Mas os arquivos pessoais do inspetor guardaram cada detalhe.",
        "duration": 7.5,
        "case_tag": "EVIDENCE ROOM - ARQUIVO B",
        "coords": "SETOR 04 | COFRE 12"
    }
]

def build_episode(episode_name: str, skip_comfy: bool = False):
    print("=" * 70)
    print(f">>> THE DARK ARCHIVE: INICIANDO COMPILAÇÃO - {episode_name.upper()}")
    print("=" * 70)
    
    compiler = DarkArchiveCompiler(episode_name)
    project_dir = compiler.project_dir
    visuals_dir = compiler.visuals_dir
    audio_dir = compiler.audio_dir
    render_dir = compiler.output_dir
    
    # 1. Renderiza o Brand Sting de 2.5s (150 frames a 60 FPS)
    sting_path = render_dir / "00_brand_sting_60fps.mp4"
    if not sting_path.exists():
        compiler.render_brand_sting_60fps(sting_path, duration=2.5)
        
    scene_clips = []
    
    # 2. Renderiza as cenas
    for idx, sc in enumerate(DEMO_EPISODE_SCENES):
        scene_id = sc["id"]
        print(f"\n--- Processando Ato {idx+1}: {scene_id} ---")
        
        # A. Visual (ComfyUI / Fallback)
        img_out = visuals_dir / f"{scene_id}.png"
        if not img_out.exists():
            generate_shot(sc["description"], img_out, seed=1980 + idx)
            
        # B. Narração & Áudio
        voice_out = audio_dir / f"{scene_id}_voice.wav"
        if not voice_out.exists():
            generate_voiceover(sc["script"], voice_out)
            
        amb_out = audio_dir / f"{scene_id}_amb.wav"
        if not amb_out.exists():
            create_ambient_track(sc["duration"], amb_out)
            
        mixed_audio = audio_dir / f"{scene_id}_mixed.wav"
        # Mixa voz (-1 dB) com ambiência (-14 dB)
        cmd_mix = [
            "ffmpeg", "-y",
            "-i", str(voice_out),
            "-i", str(amb_out),
            "-filter_complex", "[0:a]volume=1.0[v];[1:a]volume=0.35[a];[v][a]amix=inputs=2:duration=first[out]",
            "-map", "[out]", "-c:a", "pcm_s16le", str(mixed_audio)
        ]
        subprocess.run(cmd_mix, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        # C. Compilação da Cena a 60 FPS
        scene_clip = render_dir / f"{scene_id}_60fps.mp4"
        compiler.compile_scene_60fps(
            image_path=img_out,
            audio_path=mixed_audio,
            output_path=scene_clip,
            duration=sc["duration"],
            case_tag=sc["case_tag"],
            coords_tag=sc["coords"]
        )
        scene_clips.append(scene_clip)
        
    # 3. Concatenação da Timeline Final
    # Estrutura: Cena 01 (Hook) -> Brand Sting (2.5s) -> Cena 02...
    final_render = render_dir / "final_episode_60fps.mp4"
    concat_list_file = render_dir / "concat_list.txt"
    
    with open(concat_list_file, "w", encoding="utf-8") as f:
        # Hook
        f.write(f"file '{scene_clips[0].name}'\n")
        # Brand Sting após o hook (Regra de retenção)
        f.write(f"file '{sting_path.name}'\n")
        # Cenas restantes
        for sc_clip in scene_clips[1:]:
            f.write(f"file '{sc_clip.name}'\n")
            
    print(f"\n[Compiler] Concatenando linha do tempo final (60 FPS)...")
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(final_render)
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=str(render_dir), check=True)
    
    print("=" * 70)
    print(f">>> EPISÓDIO CONCLUÍDO COM SUCESSO A 60 FPS!")
    print(f"Vídeo final: {final_render}")
    print("=" * 70)
    return final_render

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The Dark Archive Pipeline")
    parser.add_argument("--episode", default="caso_001_o_vale", help="Nome do episódio")
    args = parser.parse_args()
    build_episode(args.episode)

"""
The Dark Archive - ComfyUI AI Visual Generation Bridge
Conecta o OpenCut ao ComfyUI local (E:\\ComfyUI, padrão http://127.0.0.1:8188)
para gerar fotografias forenses, documentos e planos de época alinhados ao roteiro.
"""

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

COMFYUI_HOST = os.environ.get("COMFYUI_HOST", "http://127.0.0.1:8188")

# Modificador estético de The Dark Archive
DARK_ARCHIVE_STYLE_PROMPT = (
    "archival 35mm monochrome photograph, vintage 1970s forensic evidence file, "
    "kodak tri-x 400 film grain, moody chiaroscuro lighting, deep shadows, authentic texture, "
    "gritty, desaturated dark tone, analog photo imperfections, highly detailed historical documentation"
)

NEGATIVE_PROMPT = (
    "vibrant colors, oversaturated, cartoon, anime, 3d render, cgi, plastic skin, "
    "modern digital camera, high saturation, smiling, text watermark, distortion"
)

def is_comfyui_running() -> bool:
    """Verifica se o servidor ComfyUI está ativo."""
    try:
        req = urllib.request.Request(f"{COMFYUI_HOST}/system_stats", headers={"User-Agent": "OpenCut-Agent"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False

def build_workflow_prompt(positive_prompt: str, seed: int = 42, width: int = 1280, height: int = 720) -> dict:
    """
    Constrói um workflow básico compatível com checkpoints SD1.5 / SDXL instalados no ComfyUI.
    """
    full_prompt = f"{positive_prompt}, {DARK_ARCHIVE_STYLE_PROMPT}"
    return {
        "3": {
            "inputs": {
                "seed": seed,
                "steps": 25,
                "cfg": 7.0,
                "sampler_name": "euler_ancestral",
                "scheduler": "karras",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "4": {
            "inputs": {
                "ckpt_name": "v1-5-pruned-emaonly.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "text": full_prompt,
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {
                "text": NEGATIVE_PROMPT,
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "8": {
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            },
            "class_type": "VAEDecode"
        },
        "9": {
            "inputs": {
                "filename_prefix": "dark_archive",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        }
    }

def queue_prompt(prompt_workflow: dict) -> str:
    """Envia o prompt para a fila do ComfyUI e retorna o prompt_id."""
    data = json.dumps({"prompt": prompt_workflow}).encode("utf-8")
    req = urllib.request.Request(f"{COMFYUI_HOST}/prompt", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
        return result.get("prompt_id")

def generate_shot(scene_description: str, output_path: Path, seed: int = 1984) -> bool:
    """
    Gera o plano visual para uma cena do roteiro.
    Se o ComfyUI estiver online, gera via IA; caso contrário, cria placeholder estilizado.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if is_comfyui_running():
        print(f"[ComfyUI] Servidor ativo. Gerando visual: '{scene_description[:45]}...'")
        try:
            workflow = build_workflow_prompt(scene_description, seed=seed)
            pid = queue_prompt(workflow)
            print(f"[ComfyUI] Job submetido com ID: {pid}. Aguardando render...")
            # Aguarda a finalização
            for _ in range(60):
                time.sleep(2)
                req = urllib.request.Request(f"{COMFYUI_HOST}/history/{pid}")
                with urllib.request.urlopen(req) as resp:
                    history = json.loads(resp.read().decode("utf-8"))
                    if pid in history:
                        outputs = history[pid].get("outputs", {})
                        if "9" in outputs and "images" in outputs["9"]:
                            img_info = outputs["9"]["images"][0]
                            view_url = f"{COMFYUI_HOST}/view?filename={img_info['filename']}&subfolder={img_info.get('subfolder', '')}&type={img_info.get('type', 'output')}"
                            urllib.request.urlretrieve(view_url, str(output_path))
                            print(f"[ComfyUI] Imagem salva em: {output_path}")
                            return True
        except Exception as e:
            print(f"[ComfyUI] Erro ao processar via API ({e}). Usando fallback de textura local.")

    # Fallback elegante usando FFmpeg caso o ComfyUI esteja desligado
    print(f"[ComfyUI Bridge] Gerando frame investigativo atmosférico para: {output_path.name}")
    import subprocess
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"color=c=0x0D0D0D:s=1920x1080:d=1,noise=alls=25:allf=t+u,drawbox=x=40:y=40:w=1840:h=1000:color=0x222222@0.5:t=2",
        "-frames:v", "1", str(output_path)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return True

if __name__ == "__main__":
    test_out = Path("E:/OpenCut/projects/test/visuals/scene_01.png")
    generate_shot("Uma estrada deserta no interior em noite de neblina espessa", test_out)

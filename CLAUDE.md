# OpenCut - The Dark Archive AI Video Studio

Este repositório (`E:\OpenCut`) integra o editor OpenCut ao ecossistema de produção automatizada por IA para o canal **The Dark Archive** (vídeos documentais investigativos em **60 FPS nativo** de até 25 minutos).

---

## 🛠️ Ferramentas & Ecossistema Integrado

1. **Google Drive Sync (`pipeline/drive_assets.py`):**
   - Baixa e sincroniza automaticamente overlays de filme antigo (`old_film_grain.mp4`, `crumpled_paper.mp4`, `vintage_film_effect.mp4`), pacotes de áudio (`drone_tension`, `vento_lento`, `click_mecanico`) e logos oficiais.
2. **ComfyUI Bridge (`pipeline/comfyui_bridge.py`):**
   - Conectado a `E:\ComfyUI` (`http://127.0.0.1:8188`) para gerar fotos de arquivos dos anos 70/80 em preto e branco (estilo Kodak Tri-X 400), recortes de jornal e documentos censurados.
3. **AudioCraft Engine (`pipeline/audiocraft_bridge.py`):**
   - Conectado a `E:\audiocraft` e FFmpeg para sintetizar drones sub-graves de 45–60 Hz, ruído de fita e ambiências contínuas sem corte.
4. **Narração & Whisper (`pipeline/narration_whisper.py`):**
   - Integrado a `E:\F5-TTS` (locução sóbria do Arquivista com pausas dramáticas de linha dupla) e `E:\faster-whisper` para legendas milimétricas.
5. **Compilador 60 FPS (`pipeline/engine_60fps.py`):**
   - Renderizador em 60 FPS nativo com Ken Burns orgânico, grão analógico em modo `screen`, vinheta óptica periférica e HUD investigativo (`CASE FILE 001`, `LOCATION`, `EVIDENCE`).
6. **Orquestrador Central (`pipeline/run_dark_archive.py`):**
   - Monta o episódio completo em 4 atos, posicionando o **Brand Sting de 2.5s (150 quadros)** aos 20–30s de vídeo após o gancho inicial.

---

## ⚡ Comandos Rápidos no Terminal (Claude Code)

- **Sincronizar assets do Drive:**
  ```powershell
  python E:\OpenCut\pipeline\drive_assets.py
  ```
- **Gerar ou testar visual no ComfyUI:**
  ```powershell
  python E:\OpenCut\pipeline\comfyui_bridge.py
  ```
- **Renderizar episódio completo a 60 FPS:**
  ```powershell
  python E:\OpenCut\pipeline\run_dark_archive.py --episode caso_001
  ```

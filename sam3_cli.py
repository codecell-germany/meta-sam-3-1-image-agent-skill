#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib
import json
import platform
import sys
import textwrap
from typing import Any
from pathlib import Path


def choose_cli_device(requested_device: str) -> str:
    runtime_utils = load_runtime_utils()
    if requested_device != "auto":
        return runtime_utils.normalize_device(requested_device)

    detected = runtime_utils.get_default_device()
    # SAM 3 Image läuft auf Apple Silicon aktuell deutlich stabiler auf CPU
    # als im gemischten MPS/CPU-Fallback-Modus.
    if detected == "mps":
        return "cpu"
    return detected


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Lokaler Helfer für SAM 3 im geklonten Repo."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Prüft die lokale Installation.")
    doctor.set_defaults(func=cmd_doctor)

    setup = subparsers.add_parser(
        "setup",
        help="Gibt eine plattformbezogene Setup-Anleitung für Agenten und Menschen aus.",
    )
    setup.add_argument(
        "--platform",
        default="auto",
        choices=["auto", "macos-apple-silicon", "windows-cuda"],
        help="Zielplattform für die Anleitung.",
    )
    setup.add_argument(
        "--language",
        default="de",
        choices=["de", "en"],
        help="Sprache der Setup-Ausgabe.",
    )
    setup.set_defaults(func=cmd_setup)

    download = subparsers.add_parser(
        "download", help="Lädt einen Hugging-Face-Checkpoint lokal herunter."
    )
    download.add_argument(
        "--version",
        default="sam3.1",
        choices=["sam3", "sam3.1"],
        help="Checkpoint-Version.",
    )
    download.set_defaults(func=cmd_download)

    image = subparsers.add_parser(
        "image", help="Führt Text-Prompt-Segmentierung auf einem Bild aus."
    )
    image.add_argument("--image", required=True, help="Pfad zum Eingabebild.")
    image.add_argument("--prompt", required=True, help="Text-Prompt.")
    image.add_argument(
        "--output",
        help="Ausgabepfad für das Overlay-PNG. Standard: <bild>.sam3.overlay.png",
    )
    image.add_argument(
        "--checkpoint",
        help="Optionaler lokaler Checkpoint. Wenn leer, wird via Hugging Face geladen.",
    )
    image.add_argument(
        "--version",
        default="sam3.1",
        choices=["sam3", "sam3.1"],
        help="Welche Checkpoint-Version automatisch geladen werden soll.",
    )
    image.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cuda", "mps", "cpu"],
        help="Ausführungsgerät.",
    )
    image.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Confidence-Schwelle für erkannte Masken.",
    )
    image.add_argument(
        "--mask-threshold",
        type=float,
        default=0.5,
        help="Schwelle zum Binarisieren der Masken.",
    )
    image.add_argument(
        "--resolution",
        type=int,
        default=1008,
        help="Interne Modellauflösung. Größer kann präziser, aber langsamer sein.",
    )
    image.add_argument(
        "--top-k",
        type=int,
        default=0,
        help="Optional nur die Top-K Detections nach Score behalten. 0 = alle.",
    )
    image.add_argument(
        "--crop-padding",
        type=int,
        default=0,
        help="Zusätzlicher Pixel-Rand für die ausgeschnittenen Bounding-Box-Crops.",
    )
    image.add_argument(
        "--alpha",
        type=int,
        default=120,
        help="Overlay-Alpha zwischen 0 und 255.",
    )
    image.set_defaults(func=cmd_image)

    return parser


def cmd_doctor(_: argparse.Namespace) -> int:
    runtime_utils = load_runtime_utils()
    torch_info = probe_module("torch")
    cuda_available = False
    mps_available = False
    if torch_info["available"]:
        torch = importlib.import_module("torch")
        cuda_available = bool(torch.cuda.is_available())
        mps_available = bool(torch.backends.mps.is_available())

    info = {
        "python": sys.version.split()[0],
        "torch": torch_info["version"],
        "torch_available": torch_info["available"],
        "torch_import_error": torch_info["error"],
        "cuda_available": cuda_available,
        "mps_available": mps_available,
        "default_device": runtime_utils.get_default_device(),
        "repo_root": str(Path(__file__).resolve().parent),
    }
    print(json.dumps(info, indent=2))
    return 0


def cmd_setup(args: argparse.Namespace) -> int:
    target_platform = choose_setup_platform(args.platform)
    if args.language == "en":
        print(render_setup_en(target_platform))
    else:
        print(render_setup_de(target_platform))
    return 0


def cmd_download(args: argparse.Namespace) -> int:
    download_ckpt_from_hf = load_download_helper()
    checkpoint_path = download_ckpt_from_hf(version=args.version)
    print(checkpoint_path)
    return 0


def cmd_image(args: argparse.Namespace) -> int:
    torch, np, Image, _ = load_image_stack()
    build_sam3_image_model, download_ckpt_from_hf, Sam3Processor = load_image_runtime()
    device = choose_cli_device(args.device)
    image_path = Path(args.image).expanduser().resolve()
    if not image_path.exists():
        raise FileNotFoundError(f"Bild nicht gefunden: {image_path}")

    checkpoint_path = args.checkpoint
    if checkpoint_path is None:
        checkpoint_path = download_ckpt_from_hf(version=args.version)

    model = build_sam3_image_model(
        device=device,
        checkpoint_path=str(checkpoint_path),
        load_from_HF=False,
    )
    processor = Sam3Processor(
        model,
        resolution=args.resolution,
        device=device,
        confidence_threshold=args.threshold,
        mask_threshold=args.mask_threshold,
    )

    image = Image.open(image_path).convert("RGB")
    state = processor.set_image(image)
    state = processor.set_text_prompt(prompt=args.prompt, state=state)

    if args.top_k > 0 and int(state["scores"].numel()) > args.top_k:
        state = select_top_k(state, args.top_k)

    requested_output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else image_path.with_name(f"{image_path.stem}.sam3.overlay.png")
    )
    output_path = choose_unique_output_path(requested_output_path)
    overlay = render_overlay(
        image=image,
        masks=state["masks"].detach().cpu(),
        boxes=state["boxes"].detach().cpu(),
        scores=state["scores"].detach().cpu(),
        alpha=args.alpha,
    )
    overlay.save(output_path)

    metadata_path = output_path.with_suffix(".json")
    crops_dir = output_path.with_suffix("").with_name(
        f"{output_path.with_suffix('').name}.crops"
    )
    detections = export_detections(
        image=image,
        source_path=image_path,
        crops_dir=crops_dir,
        masks=state["masks"].detach().cpu(),
        boxes=state["boxes"].detach().cpu(),
        scores=state["scores"].detach().cpu(),
        crop_padding=args.crop_padding,
    )
    metadata = {
        "image": str(image_path),
        "prompt": args.prompt,
        "device": device,
        "checkpoint": str(checkpoint_path),
        "overlay": str(output_path),
        "crops_dir": str(crops_dir),
        "resolution": args.resolution,
        "threshold": args.threshold,
        "mask_threshold": args.mask_threshold,
        "top_k": args.top_k,
        "crop_padding": args.crop_padding,
        "detections": detections,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2))

    result = {
        "output": str(output_path),
        "json": str(metadata_path),
        "crops_dir": str(crops_dir),
        "detections": int(state["scores"].numel()),
        "device": device,
        "checkpoint": str(checkpoint_path),
    }
    print(json.dumps(result, indent=2))
    return 0


def choose_setup_platform(requested_platform: str) -> str:
    if requested_platform != "auto":
        return requested_platform

    if sys.platform == "darwin" and platform.machine().lower() in {"arm64", "aarch64"}:
        return "macos-apple-silicon"

    if sys.platform.startswith("win"):
        return "windows-cuda"

    return "macos-apple-silicon"


def render_setup_de(target_platform: str) -> str:
    repo_hint = "git clone https://github.com/codecell-germany/meta-sam-3-1-image-agent-skill.git"
    if target_platform == "windows-cuda":
        body = f"""
        Meta SAM 3.1 Setup für Windows mit NVIDIA/CUDA

        Ziel:
        Dieses Setup richtet die lokale CLI ein, damit ein Agent Bilder mit Meta SAM 3.1
        segmentieren und daraus Overlay, JSON und Crops erzeugen kann.

        Voraussetzungen:
        - Python 3.12
        - NVIDIA-GPU mit funktionierender CUDA-Umgebung
        - freigeschalteter Hugging-Face-Zugriff auf `facebook/sam3.1`

        Empfohlene Reihenfolge:
        1. Repo holen:
           {repo_hint}
        2. In das Repo wechseln
        3. Virtuelle Umgebung anlegen:
           py -3.12 -m venv .venv
        4. Aktivieren:
           .venv\\Scripts\\activate
        5. PyTorch mit CUDA installieren:
           pip install torch==2.10.0 torchvision --index-url https://download.pytorch.org/whl/cu128
        6. Repo installieren:
           pip install -e .
        7. Fehlende Runtime-Dependency ergänzen:
           pip install einops
        8. Installation prüfen:
           sam3-cli doctor
        9. Checkpoint laden:
           sam3-cli download --version sam3.1
        10. Testsegmentierung ausführen:
            sam3-cli image --version sam3.1 --device cuda --image C:\\pfad\\zum\\bild.jpg --prompt "object of interest"

        Hugging Face:
        - Vor dem Download muss Zugriff auf `facebook/sam3.1` freigeschaltet sein.
        - Falls `sam3-cli download` mit 401 scheitert, zuerst den Zugang zum gated Modell prüfen.

        Ergebnis:
        - Overlay-PNG
        - JSON mit Bounding-Boxes, Scores und Crop-Pfaden
        - Crop-Ordner mit Bildausschnitten

        Agentische Empfehlung:
        Für Folge-Workflows bevorzugt die JSON-Datei und die Crops verwenden, nicht nur das Overlay.
        """
        return textwrap.dedent(body).strip()

    body = f"""
    Meta SAM 3.1 Setup für macOS auf Apple Silicon

    Ziel:
    Dieses Setup richtet die lokale CLI ein, damit ein Agent Bilder mit Meta SAM 3.1
    segmentieren und daraus Overlay, JSON und Crops erzeugen kann.

    Voraussetzungen:
    - macOS auf Apple Silicon
    - Python 3.12
    - freigeschalteter Hugging-Face-Zugriff auf `facebook/sam3.1`

    Empfohlene Reihenfolge:
    1. Repo holen:
       {repo_hint}
    2. In das Repo wechseln
    3. Virtuelle Umgebung anlegen:
       python3.12 -m venv .venv
    4. Aktivieren:
       source .venv/bin/activate
    5. PyTorch installieren:
       pip install torch==2.10.0 torchvision==0.25.0
    6. Repo installieren:
       pip install -e .
    7. Fehlende Runtime-Dependency ergänzen:
       pip install einops
    8. Installation prüfen:
       sam3-cli doctor
    9. Checkpoint laden:
       sam3-cli download --version sam3.1
    10. Testsegmentierung ausführen:
        sam3-cli image --version sam3.1 --device cpu --image /pfad/zum/bild.jpg --prompt "object of interest"

    Wichtige Plattformregel:
    Auf Apple Silicon ist `cpu` derzeit der stabile Standardpfad.
    `mps` ist aktuell kein verlässlicher Produkt-Default.

    Hugging Face:
    - Vor dem Download muss Zugriff auf `facebook/sam3.1` freigeschaltet sein.
    - Falls `sam3-cli download` mit 401 scheitert, zuerst den Zugang zum gated Modell prüfen.

    Ergebnis:
    - Overlay-PNG
    - JSON mit Bounding-Boxes, Scores und Crop-Pfaden
    - Crop-Ordner mit Bildausschnitten

    Agentische Empfehlung:
    Für Folge-Workflows bevorzugt die JSON-Datei und die Crops verwenden, nicht nur das Overlay.
    """
    return textwrap.dedent(body).strip()


def render_setup_en(target_platform: str) -> str:
    repo_hint = "git clone https://github.com/codecell-germany/meta-sam-3-1-image-agent-skill.git"
    if target_platform == "windows-cuda":
        body = f"""
        Meta SAM 3.1 setup for Windows with NVIDIA/CUDA

        Goal:
        Install the local CLI so an agent can segment images with Meta SAM 3.1 and
        produce overlays, JSON metadata, and crops.

        Requirements:
        - Python 3.12
        - NVIDIA GPU with a working CUDA environment
        - approved Hugging Face access to `facebook/sam3.1`

        Recommended order:
        1. Clone the repo:
           {repo_hint}
        2. Change into the repo
        3. Create a virtual environment:
           py -3.12 -m venv .venv
        4. Activate it:
           .venv\\Scripts\\activate
        5. Install CUDA-enabled PyTorch:
           pip install torch==2.10.0 torchvision --index-url https://download.pytorch.org/whl/cu128
        6. Install the repo:
           pip install -e .
        7. Add the missing runtime dependency:
           pip install einops
        8. Verify the installation:
           sam3-cli doctor
        9. Download the checkpoint:
           sam3-cli download --version sam3.1
        10. Run a test segmentation:
            sam3-cli image --version sam3.1 --device cuda --image C:\\path\\to\\image.jpg --prompt "object of interest"

        Hugging Face:
        - Access to `facebook/sam3.1` must be approved before checkpoint download works.
        - If `sam3-cli download` fails with 401, verify gated model access first.

        Output:
        - overlay PNG
        - JSON with bounding boxes, scores, and crop paths
        - crop directory with per-box image snippets

        Agent guidance:
        For downstream workflows, prefer the JSON file and crops over the overlay alone.
        """
        return textwrap.dedent(body).strip()

    body = f"""
    Meta SAM 3.1 setup for macOS on Apple Silicon

    Goal:
    Install the local CLI so an agent can segment images with Meta SAM 3.1 and
    produce overlays, JSON metadata, and crops.

    Requirements:
    - Apple-Silicon macOS machine
    - Python 3.12
    - approved Hugging Face access to `facebook/sam3.1`

    Recommended order:
    1. Clone the repo:
       {repo_hint}
    2. Change into the repo
    3. Create a virtual environment:
       python3.12 -m venv .venv
    4. Activate it:
       source .venv/bin/activate
    5. Install PyTorch:
       pip install torch==2.10.0 torchvision==0.25.0
    6. Install the repo:
       pip install -e .
    7. Add the missing runtime dependency:
       pip install einops
    8. Verify the installation:
       sam3-cli doctor
    9. Download the checkpoint:
       sam3-cli download --version sam3.1
    10. Run a test segmentation:
        sam3-cli image --version sam3.1 --device cpu --image /path/to/image.jpg --prompt "object of interest"

    Important platform rule:
    On Apple Silicon, `cpu` is currently the stable default path.
    `mps` should not be treated as a reliable production default yet.

    Hugging Face:
    - Access to `facebook/sam3.1` must be approved before checkpoint download works.
    - If `sam3-cli download` fails with 401, verify gated model access first.

    Output:
    - overlay PNG
    - JSON with bounding boxes, scores, and crop paths
    - crop directory with per-box image snippets

    Agent guidance:
    For downstream workflows, prefer the JSON file and crops over the overlay alone.
    """
    return textwrap.dedent(body).strip()


def render_overlay(
    image: Any,
    masks: Any,
    boxes: Any,
    scores: Any,
    alpha: int,
) -> Any:
    import numpy as np
    from PIL import Image, ImageDraw

    base = image.convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    mask_canvas = np.array(overlay, dtype=np.uint8)
    draw = ImageDraw.Draw(base)
    colors = [
        (255, 99, 71),
        (64, 224, 208),
        (255, 215, 0),
        (123, 104, 238),
        (50, 205, 50),
    ]

    for idx in range(int(scores.numel())):
        color = colors[idx % len(colors)]
        mask = masks[idx, 0].numpy().astype(bool)
        mask_canvas[mask] = (*color, alpha)

        x0, y0, x1, y1 = boxes[idx].tolist()
        draw.rectangle((x0, y0, x1, y1), outline=color, width=3)
        draw.text((x0 + 4, y0 + 4), f"{scores[idx].item():.2f}", fill=color)

    overlay = Image.fromarray(mask_canvas, mode="RGBA")
    return Image.alpha_composite(base, overlay).convert("RGB")


def choose_unique_output_path(base_path: Path) -> Path:
    candidate = base_path
    index = 1
    while output_bundle_exists(candidate):
        candidate = base_path.with_name(f"{base_path.stem} ({index}){base_path.suffix}")
        index += 1
    return candidate


def output_bundle_exists(output_path: Path) -> bool:
    metadata_path = output_path.with_suffix(".json")
    crops_dir = output_path.with_suffix("").with_name(
        f"{output_path.with_suffix('').name}.crops"
    )
    return output_path.exists() or metadata_path.exists() or crops_dir.exists()


def select_top_k(state: dict, top_k: int) -> dict:
    torch = importlib.import_module("torch")
    if top_k <= 0 or int(state["scores"].numel()) <= top_k:
        return state

    top_scores, top_indices = torch.topk(state["scores"], k=top_k)
    state["scores"] = top_scores
    state["boxes"] = state["boxes"][top_indices]
    state["masks"] = state["masks"][top_indices]
    state["masks_logits"] = state["masks_logits"][top_indices]
    return state


def export_detections(
    image: Any,
    source_path: Path,
    crops_dir: Path,
    masks: Any,
    boxes: Any,
    scores: Any,
    crop_padding: int,
) -> list[dict]:
    import numpy as np

    crops_dir.mkdir(parents=True, exist_ok=True)
    detections: list[dict] = []

    for idx in range(int(scores.numel())):
        x0, y0, x1, y1 = clamp_box(
            boxes[idx].tolist(), image.size, padding=max(0, crop_padding)
        )
        crop = image.crop((x0, y0, x1, y1))
        crop_name = f"{source_path.stem}.det_{idx:03d}.png"
        crop_path = crops_dir / crop_name
        crop.save(crop_path)

        mask = masks[idx, 0].numpy().astype(np.uint8)
        detections.append(
            {
                "index": idx,
                "score": round(float(scores[idx].item()), 6),
                "bbox_xyxy": [x0, y0, x1, y1],
                "bbox_wh": [x0, y0, max(0, x1 - x0), max(0, y1 - y0)],
                "crop_padding": max(0, crop_padding),
                "crop_path": str(crop_path),
                "mask_pixels": int(mask.sum()),
            }
        )

    return detections


def clamp_box(
    box: list[float], image_size: tuple[int, int], padding: int = 0
) -> tuple[int, int, int, int]:
    width, height = image_size
    x0, y0, x1, y1 = box
    x0 = max(0, min(int(round(x0)) - padding, width))
    y0 = max(0, min(int(round(y0)) - padding, height))
    x1 = max(x0, min(int(round(x1)) + padding, width))
    y1 = max(y0, min(int(round(y1)) + padding, height))
    return x0, y0, x1, y1


def probe_module(module_name: str) -> dict[str, Any]:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:  # pragma: no cover - environment dependent
        return {"available": False, "version": None, "error": str(exc)}

    version = getattr(module, "__version__", None)
    return {"available": True, "version": version, "error": None}


def load_runtime_utils():
    try:
        return importlib.import_module("sam3.runtime_utils")
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "Die lokale SAM-3-Runtime ist nicht vollständig verfügbar. "
            "Installiere zuerst das Repo mit `pip install -e .`."
        ) from exc


def load_download_helper():
    try:
        module_builder = importlib.import_module("sam3.model_builder")
        return module_builder.download_ckpt_from_hf
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "Checkpoint-Download ist noch nicht verfügbar. "
            "Installiere zuerst die Python-Runtime und die Paketabhängigkeiten."
        ) from exc


def load_image_stack():
    try:
        torch = importlib.import_module("torch")
        np = importlib.import_module("numpy")
        pil_image_module = importlib.import_module("PIL.Image")
        pil_draw_module = importlib.import_module("PIL.ImageDraw")
        return torch, np, pil_image_module, pil_draw_module
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "Für Bildsegmentierung fehlen Python-Abhängigkeiten. "
            "Führe zuerst `sam3-cli setup --language de` aus und installiere danach "
            "PyTorch, Pillow und die Repo-Abhängigkeiten."
        ) from exc


def load_image_runtime():
    try:
        module_builder = importlib.import_module("sam3.model_builder")
        module_processor = importlib.import_module("sam3.model.sam3_image_processor")
        return (
            module_builder.build_sam3_image_model,
            module_builder.download_ckpt_from_hf,
            module_processor.Sam3Processor,
        )
    except Exception as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "Die SAM-3.1-Bildruntime konnte nicht geladen werden. "
            "Installiere zuerst die Python-Runtime und die benötigten Abhängigkeiten."
        ) from exc


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except Exception as exc:  # pragma: no cover - CLI surface
        print(f"Fehler: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

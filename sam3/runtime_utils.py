try:
    import torch
except Exception:  # pragma: no cover - environment dependent
    torch = None


def get_default_device() -> str:
    if torch is None:
        return "cpu"
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def normalize_device(device: str | None = None) -> str:
    if device in (None, "auto"):
        return get_default_device()

    normalized = str(device).lower()
    if torch is None:
        if normalized == "cpu":
            return normalized
        raise RuntimeError(
            "PyTorch ist auf diesem System noch nicht installiert. "
            "Verwende zunächst `sam3-cli setup --language de` und installiere danach die Runtime."
        )
    if normalized == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA ist auf diesem System nicht verfügbar.")
    if normalized == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("Apple Metal (MPS) ist auf diesem System nicht verfügbar.")
    if normalized not in {"cuda", "mps", "cpu"}:
        raise ValueError(
            f"Unbekanntes Gerät {device!r}. Erlaubt sind: auto, cuda, mps, cpu."
        )
    return normalized

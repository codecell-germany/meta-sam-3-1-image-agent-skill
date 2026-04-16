# meta-sam-3-1-image-agent-skill

---

# English

## Purpose

`meta-sam-3-1-image-agent-skill` turns Meta SAM 3.1 into an agent-friendly image reduction layer.

The practical goal is not only to segment images, but to help agents work better with images afterward:

- better OCR on relevant image regions instead of the whole frame
- better object- or component-level analysis through crops
- better downstream automation through structured JSON metadata
- better iteration because multiple segmentation runs can coexist without overwriting each other

This repository combines:

- the Meta SAM 3.1 model codebase
- a local CLI surface built around `sam3-cli`
- a skill payload under `skills/sam3-image-cli/`
- setup guidance for macOS Apple Silicon and Windows with NVIDIA/CUDA

## Public release surfaces

- GitHub repo:
  `codecell-germany/meta-sam-3-1-image-agent-skill`
- npm package:
  `@codecell-germany/meta-sam-3-1-image-agent-skill`
- CLI binary:
  `sam3-cli`
- skill installer binary:
  `sam3-image-skill`
- skill name:
  `sam3-image-cli`

## What the repository contains

- a local segmentation CLI
- a skill that teaches agents how to install and use it
- platform-specific setup guidance
- references for onboarding and output handling
- knowledge files for architecture, platform support, limitations, and release hygiene

## Why this matters for agents

Many image tasks get better when the original image is reduced to the most relevant regions first.

Instead of sending one noisy image into OCR or visual reasoning, an agent can:

1. segment the image with Meta SAM 3.1
2. keep the overlay for quick validation
3. use the JSON file for structured routing
4. run OCR or visual analysis on the generated crops

That creates a new operating mode for agent workflows:
less noise, smaller image regions, clearer semantics, and better follow-up automation.

## Supported platform strategy

- macOS Apple Silicon:
  verified image segmentation path via `cpu`
- Windows with NVIDIA/CUDA:
  intended high-performance path via `cuda`

Important:

- this repo is deliberately positioned around image segmentation
- video and multiplex tracking are not the default product story here
- model weights are not stored in this repository

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/codecell-germany/meta-sam-3-1-image-agent-skill.git
cd meta-sam-3-1-image-agent-skill
```

### 2. Create and activate a virtual environment

macOS or Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
```

### 3. Install PyTorch

macOS Apple Silicon:

```bash
pip install torch==2.10.0 torchvision==0.25.0
```

Windows with CUDA:

```powershell
pip install torch==2.10.0 torchvision --index-url https://download.pytorch.org/whl/cu128
```

### 4. Install the repository

```bash
pip install -e .
pip install einops
```

### 5. Verify the CLI

```bash
sam3-cli --help
sam3-cli doctor
```

### 6. Optionally install the skill payload for Codex

```bash
npm install -g @codecell-germany/meta-sam-3-1-image-agent-skill
sam3-image-skill install --force
```

Or without a global npm install:

```bash
npx -y -p @codecell-germany/meta-sam-3-1-image-agent-skill sam3-image-skill install --force
```

This installs:

- the skill payload under `~/.codex/skills/sam3-image-cli`
- the runtime files under `~/.codex/tools/sam3-image-cli`
- CLI shims under `~/.codex/bin/`
  - `sam3-cli`
  - `sam3-cli.cmd`
  - `sam3-cli.ps1`

## Canonical first-run sequence

### 1. Verify the public CLI

```bash
sam3-cli --help
```

### 2. Check the environment

```bash
sam3-cli doctor
```

### 3. If setup is incomplete, print the setup guide

```bash
sam3-cli setup --language en
sam3-cli setup --platform macos-apple-silicon --language en
sam3-cli setup --platform windows-cuda --language en
```

### 4. Make sure Hugging Face access exists

The user must have approved access to the gated model:

- `facebook/sam3.1`

### 5. Download the checkpoint

```bash
sam3-cli download --version sam3.1
```

### 6. Run the first real segmentation

macOS Apple Silicon:

```bash
sam3-cli image --version sam3.1 --device cpu --image /absolute/path/image.jpg --prompt "object of interest"
```

Windows with CUDA:

```powershell
sam3-cli image --version sam3.1 --device cuda --image C:\absolute\path\image.jpg --prompt "object of interest"
```

## Quick start

```bash
sam3-cli setup --language en
sam3-cli doctor
sam3-cli download --version sam3.1
sam3-cli image --version sam3.1 --device cpu --image /absolute/path/image.jpg --prompt "object of interest"
```

## Output contract

Every successful segmentation run produces:

- an overlay PNG
- a JSON metadata file
- a crop directory

The JSON metadata preserves bounding boxes, scores, crop paths, and other run settings.
The crop directory is usually the best follow-up input for OCR or fine-grained visual analysis.

## Important parameters

- `--device auto|cpu|cuda|mps`
- `--threshold`
- `--mask-threshold`
- `--resolution`
- `--top-k`
- `--crop-padding`
- `--alpha`
- `--checkpoint`

Example:

```bash
sam3-cli image \
  --version sam3.1 \
  --device cpu \
  --threshold 0.5 \
  --mask-threshold 0.5 \
  --resolution 1008 \
  --top-k 0 \
  --crop-padding 5 \
  --alpha 120 \
  --image /absolute/path/image.jpg \
  --prompt "object of interest"
```

## Agent guardrails

- use `sam3-cli` instead of ad-hoc Python entry points
- run `doctor` before the first real segmentation in a new shell
- do not assume model weights are bundled with the repo
- on Apple Silicon, prefer `cpu`
- prefer the JSON file and crop directory over the overlay alone for downstream work
- do not commit weights, private input images, or generated outputs

## Hugging Face and model access

Meta SAM 3.1 weights are hosted separately from this repository.
This repo does not ship them.

If `sam3-cli download --version sam3.1` fails with `401`, treat that as an access or authentication issue against the gated Hugging Face model first.

## Known limitations

- macOS Apple Silicon is currently a stability-first path via `cpu`
- `mps` should not be treated as the production default yet
- video and multiplex workflows are not the default product surface in this repository
- the image path can emit checkpoint `missing_keys` warnings while still producing correct output

## Skills ecosystem

Repository listing check:

```bash
npx -y skills add codecell-germany/meta-sam-3-1-image-agent-skill -l
```

Global install example:

```bash
npx -y skills add codecell-germany/meta-sam-3-1-image-agent-skill -g --skill sam3-image-cli -a '*' -y
```

npm skill installer example:

```bash
npm install -g @codecell-germany/meta-sam-3-1-image-agent-skill
sam3-image-skill install --force
```

Direct npx installer example:

```bash
npx -y -p @codecell-germany/meta-sam-3-1-image-agent-skill sam3-image-skill install --force
```

## Release verification

```bash
sam3-cli --help
sam3-cli setup --language en
sam3-cli doctor
npm run test:unit
npm pack --dry-run
npm run test:release
```

## References

- `skills/sam3-image-cli/SKILL.md`
- `skills/sam3-image-cli/references/overview.md`
- `skills/sam3-image-cli/references/agent-onboarding.md`
- `skills/sam3-image-cli/references/command-cheatsheet.md`
- `skills/sam3-image-cli/references/macos-first-run.md`
- `skills/sam3-image-cli/references/windows-cuda-first-run.md`
- `skills/sam3-image-cli/references/output-contract.md`
- `knowledge/ARCHITECTURE.md`
- `knowledge/PLATFORM_SUPPORT.md`
- `knowledge/OUTPUT_CONTRACT.md`
- `knowledge/KNOWN_LIMITATIONS.md`
- `knowledge/RELEASE_CHECKLIST.md`

---

# Deutsch

## Zweck

`meta-sam-3-1-image-agent-skill` macht aus Meta SAM 3.1 eine agententaugliche Bild-Reduktionsschicht.

Das praktische Ziel ist nicht nur Segmentierung, sondern bessere Folgearbeit mit Bildern:

- bessere OCR auf relevanten Bildausschnitten statt auf dem ganzen Bild
- bessere Objekt- oder Komponentenanalysen über Crops
- bessere Automatisierung über strukturierte JSON-Metadaten
- bessere Vergleichbarkeit, weil mehrere Segmentierungsläufe nebeneinander existieren können, ohne sich zu überschreiben

Dieses Repo kombiniert:

- den Meta-SAM-3.1-Modellcode
- eine lokale CLI-Oberfläche rund um `sam3-cli`
- einen Skill unter `skills/sam3-image-cli/`
- Setup-Anleitungen für macOS auf Apple Silicon und Windows mit NVIDIA/CUDA

## Öffentliche Release-Oberflächen

- GitHub-Repo:
  `codecell-germany/meta-sam-3-1-image-agent-skill`
- npm-Paket:
  `@codecell-germany/meta-sam-3-1-image-agent-skill`
- CLI-Binary:
  `sam3-cli`
- Skill-Installer-Binary:
  `sam3-image-skill`
- Skill-Name:
  `sam3-image-cli`

## Was das Repo enthält

- eine lokale Segmentierungs-CLI
- einen Skill, der Agenten die Installation und Nutzung erklärt
- plattformspezifische Setup-Anleitungen
- Referenzen für Onboarding und Ergebnisweiterverarbeitung
- Knowledge-Dateien für Architektur, Plattformsupport, Grenzen und Release-Hygiene

## Warum das für Agenten wichtig ist

Viele Bildaufgaben werden besser, wenn das Originalbild zuerst auf die relevantesten Regionen reduziert wird.

Statt ein volles, verrauschtes Bild direkt an OCR oder visuelles Reasoning zu geben, kann ein Agent:

1. das Bild mit Meta SAM 3.1 segmentieren
2. das Overlay für eine schnelle Sichtprüfung behalten
3. die JSON-Datei für strukturierte Weiterleitung nutzen
4. OCR oder Bildanalyse auf den erzeugten Crops ausführen

Dadurch entsteht ein neuer Arbeitsmodus für Agenten:
weniger Rauschen, kleinere Bildregionen, klarere Semantik und bessere Folgeautomatisierung.

## Unterstützte Plattformstrategie

- macOS Apple Silicon:
  verifizierter Bildpfad über `cpu`
- Windows mit NVIDIA/CUDA:
  geplanter Hochleistungs-Pfad über `cuda`

Wichtig:

- dieses Repo ist bewusst auf Bildsegmentierung ausgerichtet
- Video und Multiplex-Tracking sind hier nicht die Standard-Produktgeschichte
- Modellgewichte liegen nicht in diesem Repo

## Installation

### 1. Repo klonen

```bash
git clone https://github.com/codecell-germany/meta-sam-3-1-image-agent-skill.git
cd meta-sam-3-1-image-agent-skill
```

### 2. Virtuelle Umgebung anlegen und aktivieren

macOS oder Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
```

### 3. PyTorch installieren

macOS Apple Silicon:

```bash
pip install torch==2.10.0 torchvision==0.25.0
```

Windows mit CUDA:

```powershell
pip install torch==2.10.0 torchvision --index-url https://download.pytorch.org/whl/cu128
```

### 4. Repo installieren

```bash
pip install -e .
pip install einops
```

### 5. CLI prüfen

```bash
sam3-cli --help
sam3-cli doctor
```

### 6. Optional den Skill-Payload für Codex installieren

```bash
npm install -g @codecell-germany/meta-sam-3-1-image-agent-skill
sam3-image-skill install --force
```

Oder ohne globale npm-Installation:

```bash
npx -y -p @codecell-germany/meta-sam-3-1-image-agent-skill sam3-image-skill install --force
```

Dabei werden installiert:

- der Skill-Payload unter `~/.codex/skills/sam3-image-cli`
- die Runtime-Dateien unter `~/.codex/tools/sam3-image-cli`
- CLI-Shims unter `~/.codex/bin/`
  - `sam3-cli`
  - `sam3-cli.cmd`
  - `sam3-cli.ps1`

## Kanonische First-Run-Reihenfolge

### 1. Öffentliche CLI prüfen

```bash
sam3-cli --help
```

### 2. Umgebung prüfen

```bash
sam3-cli doctor
```

### 3. Wenn das Setup unvollständig ist, Setup-Guide ausgeben

```bash
sam3-cli setup --language de
sam3-cli setup --platform macos-apple-silicon --language de
sam3-cli setup --platform windows-cuda --language de
```

### 4. Hugging-Face-Zugriff sicherstellen

Der Nutzer braucht freigeschalteten Zugriff auf das gated Modell:

- `facebook/sam3.1`

### 5. Checkpoint herunterladen

```bash
sam3-cli download --version sam3.1
```

### 6. Erste echte Segmentierung ausführen

macOS Apple Silicon:

```bash
sam3-cli image --version sam3.1 --device cpu --image /absoluter/pfad/bild.jpg --prompt "object of interest"
```

Windows mit CUDA:

```powershell
sam3-cli image --version sam3.1 --device cuda --image C:\absoluter\pfad\bild.jpg --prompt "object of interest"
```

## Schnellstart

```bash
sam3-cli setup --language de
sam3-cli doctor
sam3-cli download --version sam3.1
sam3-cli image --version sam3.1 --device cpu --image /absoluter/pfad/bild.jpg --prompt "object of interest"
```

## Ergebnisvertrag

Jeder erfolgreiche Segmentierungslauf erzeugt:

- ein Overlay-PNG
- eine JSON-Metadatendatei
- einen Crop-Ordner

Die JSON-Datei enthält Bounding-Boxes, Scores, Crop-Pfade und Laufparameter.
Der Crop-Ordner ist meist der beste Folgeinput für OCR oder feinkörnige Bildanalyse.

## Wichtige Parameter

- `--device auto|cpu|cuda|mps`
- `--threshold`
- `--mask-threshold`
- `--resolution`
- `--top-k`
- `--crop-padding`
- `--alpha`
- `--checkpoint`

Beispiel:

```bash
sam3-cli image \
  --version sam3.1 \
  --device cpu \
  --threshold 0.5 \
  --mask-threshold 0.5 \
  --resolution 1008 \
  --top-k 0 \
  --crop-padding 5 \
  --alpha 120 \
  --image /absoluter/pfad/bild.jpg \
  --prompt "object of interest"
```

## Agentische Guardrails

- `sam3-cli` statt ad-hoc Python-Einstiegspunkte verwenden
- vor der ersten echten Segmentierung in einer neuen Shell `doctor` ausführen
- nicht annehmen, dass Modellgewichte im Repo enthalten sind
- auf Apple Silicon `cpu` bevorzugen
- für Folgearbeit JSON und Crop-Ordner dem Overlay vorziehen
- keine Gewichte, privaten Bilder oder generierten Outputs committen

## Hugging Face und Modellzugriff

Die Meta-SAM-3.1-Gewichte werden separat von diesem Repo gehostet.
Dieses Repo liefert sie nicht mit.

Wenn `sam3-cli download --version sam3.1` mit `401` scheitert, sollte das zuerst als Zugriffs- oder Authentifizierungsproblem gegen das gated Hugging-Face-Modell behandelt werden.

## Bekannte Grenzen

- macOS Apple Silicon ist aktuell ein Stabilitätspfad über `cpu`
- `mps` ist derzeit kein belastbarer Produktions-Default
- Video- und Multiplex-Workflows sind hier nicht die Standard-Produktoberfläche
- der Bildpfad kann `missing_keys`-Warnungen beim Checkpoint-Laden ausgeben und trotzdem korrekt funktionieren

## Skills-Ökosystem

Repo-Listing prüfen:

```bash
npx -y skills add codecell-germany/meta-sam-3-1-image-agent-skill -l
```

Globales Installationsbeispiel:

```bash
npx -y skills add codecell-germany/meta-sam-3-1-image-agent-skill -g --skill sam3-image-cli -a '*' -y
```

npm-Skill-Installer-Beispiel:

```bash
npm install -g @codecell-germany/meta-sam-3-1-image-agent-skill
sam3-image-skill install --force
```

Direktes `npx`-Installer-Beispiel:

```bash
npx -y -p @codecell-germany/meta-sam-3-1-image-agent-skill sam3-image-skill install --force
```

## Release-Verifikation

```bash
sam3-cli --help
sam3-cli setup --language de
sam3-cli doctor
npm run test:unit
npm pack --dry-run
npm run test:release
```

## Referenzen

- `skills/sam3-image-cli/SKILL.md`
- `skills/sam3-image-cli/references/overview.md`
- `skills/sam3-image-cli/references/agent-onboarding.md`
- `skills/sam3-image-cli/references/command-cheatsheet.md`
- `skills/sam3-image-cli/references/macos-first-run.md`
- `skills/sam3-image-cli/references/windows-cuda-first-run.md`
- `skills/sam3-image-cli/references/output-contract.md`
- `knowledge/ARCHITECTURE.md`
- `knowledge/PLATFORM_SUPPORT.md`
- `knowledge/OUTPUT_CONTRACT.md`
- `knowledge/KNOWN_LIMITATIONS.md`
- `knowledge/RELEASE_CHECKLIST.md`

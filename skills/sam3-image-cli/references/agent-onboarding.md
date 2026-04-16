# sam3-image-cli agent onboarding

Use this runbook when a new agent receives the skill and the SAM 3.1 environment may not be ready yet.

## Core rule

Do not start by improvising Python calls or notebook code.
Start with setup detection.

The correct order is:

1. verify the public CLI
2. run `doctor`
3. if setup is incomplete, print `setup`
4. follow the platform-specific guide
5. download the checkpoint
6. rerun `doctor`
7. only then run real segmentation

## Step 1: verify the CLI

```bash
sam3-cli --help
```

If that fails, treat the CLI as not installed yet and install the repo first.

## Step 2: detect setup state

```bash
sam3-cli doctor
```

Treat the environment as not ready if:

- the CLI is missing
- PyTorch is missing
- the runtime has not been installed yet
- the checkpoint is missing
- the user says this is the first setup

## Step 3: print the setup guide

German:

```bash
sam3-cli setup --language de
```

English:

```bash
sam3-cli setup --language en
```

Platform-specific:

```bash
sam3-cli setup --platform macos-apple-silicon --language de
sam3-cli setup --platform windows-cuda --language en
```

## Step 4: checkpoint download

```bash
sam3-cli download --version sam3.1
```

If this fails with `401`, do not guess.
Treat it as a Hugging Face access or authentication issue against the gated model.

## Step 5: real segmentation

macOS Apple Silicon:

```bash
sam3-cli image --version sam3.1 --device cpu --image /absolute/path/image.jpg --prompt "object of interest"
```

Windows with CUDA:

```bash
sam3-cli image --version sam3.1 --device cuda --image C:\absolute\path\image.jpg --prompt "object of interest"
```

## What not to do

- do not treat `mps` as a reliable Apple-Silicon default
- do not commit model weights or example images
- do not continue with OCR from the overlay alone when JSON and crops exist
- do not assume the checkpoint is bundled with the Git repo

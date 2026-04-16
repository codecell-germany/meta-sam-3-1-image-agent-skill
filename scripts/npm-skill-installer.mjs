#!/usr/bin/env node

import fs from "node:fs";
import os from "node:os";
import path from "node:path";

function printHelp() {
  console.log(`sam3-image-skill

Usage:
  sam3-image-skill install [--codex-home <path>] [--force] [--dry-run]
  sam3-image-skill doctor [--codex-home <path>]
  sam3-image-skill uninstall [--codex-home <path>]

This installer copies:
- the skill payload to ~/.codex/skills/sam3-image-cli
- the Python runtime to ~/.codex/tools/sam3-image-cli
- sam3-cli shims to ~/.codex/bin/
  - sam3-cli
  - sam3-cli.cmd
  - sam3-cli.ps1

The Python dependencies still have to be installed by the user or by the setup flow.`);
}

function parseArgs(argv) {
  const [command, ...rest] = argv;
  const options = {
    command: command ?? "help",
    codexHome: process.env.CODEX_HOME || path.join(os.homedir(), ".codex"),
    force: false,
    dryRun: false
  };

  for (let i = 0; i < rest.length; i += 1) {
    const value = rest[i];
    if (value === "--codex-home") {
      options.codexHome = rest[i + 1];
      i += 1;
      continue;
    }
    if (value === "--force") {
      options.force = true;
      continue;
    }
    if (value === "--dry-run") {
      options.dryRun = true;
      continue;
    }
    if (value === "--help" || value === "-h") {
      options.command = "help";
      return options;
    }
  }

  return options;
}

function pathExists(targetPath) {
  return fs.existsSync(targetPath);
}

function copyDir(sourceDir, targetDir) {
  fs.mkdirSync(targetDir, { recursive: true });
  for (const entry of fs.readdirSync(sourceDir, { withFileTypes: true })) {
    const sourcePath = path.join(sourceDir, entry.name);
    const targetPath = path.join(targetDir, entry.name);
    if (entry.isDirectory()) {
      copyDir(sourcePath, targetPath);
      continue;
    }
    fs.copyFileSync(sourcePath, targetPath);
  }
}

function ensureParent(targetPath) {
  fs.mkdirSync(path.dirname(targetPath), { recursive: true });
}

function renderPosixShim(runtimeRoot) {
  const cliPath = path.join(runtimeRoot, "sam3_cli.py");
  return `#!/usr/bin/env sh
set -eu
if [ -n "\${PYTHON_BIN:-}" ]; then
  SELECTED_PYTHON="$PYTHON_BIN"
elif [ -x "/opt/homebrew/bin/python3.12" ]; then
  SELECTED_PYTHON="/opt/homebrew/bin/python3.12"
elif command -v python3.12 >/dev/null 2>&1; then
  SELECTED_PYTHON="$(command -v python3.12)"
elif command -v python3 >/dev/null 2>&1; then
  SELECTED_PYTHON="$(command -v python3)"
else
  SELECTED_PYTHON="$(command -v python)"
fi
exec "$SELECTED_PYTHON" "${cliPath}" "$@"
`;
}

function renderCmdShim(runtimeRoot) {
  const cliPath = path.join(runtimeRoot, "sam3_cli.py");
  return `@echo off
setlocal
if not "%PYTHON_BIN%"=="" (
  "%PYTHON_BIN%" "${cliPath}" %*
  exit /b %ERRORLEVEL%
)
where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py -3.12 "${cliPath}" %*
  exit /b %ERRORLEVEL%
)
where python >nul 2>nul
if %ERRORLEVEL%==0 (
  python "${cliPath}" %*
  exit /b %ERRORLEVEL%
)
where python3 >nul 2>nul
if %ERRORLEVEL%==0 (
  python3 "${cliPath}" %*
  exit /b %ERRORLEVEL%
)
echo Python runtime not found. 1>&2
exit /b 1
`;
}

function renderPowerShellShim(runtimeRoot) {
  const cliPath = path.join(runtimeRoot, "sam3_cli.py");
  return `$cliPath = "${cliPath}"
if ($env:PYTHON_BIN) {
  & $env:PYTHON_BIN $cliPath @args
  exit $LASTEXITCODE
}
if (Get-Command py -ErrorAction SilentlyContinue) {
  & py -3.12 $cliPath @args
  exit $LASTEXITCODE
}
if (Get-Command python -ErrorAction SilentlyContinue) {
  & python $cliPath @args
  exit $LASTEXITCODE
}
if (Get-Command python3 -ErrorAction SilentlyContinue) {
  & python3 $cliPath @args
  exit $LASTEXITCODE
}
Write-Error "Python runtime not found."
exit 1
`;
}

function installSkill(codexHome, force, dryRun) {
  const packageRoot = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
  const sourceSkillDir = path.join(packageRoot, "skills", "sam3-image-cli");
  const sourceKnowledgeDir = path.join(packageRoot, "knowledge");
  const runtimeSources = [
    path.join(packageRoot, "sam3"),
    path.join(packageRoot, "sam3_cli.py"),
    path.join(packageRoot, "pyproject.toml"),
    path.join(packageRoot, "README.md"),
    path.join(packageRoot, "LICENSE")
  ];

  const targetSkillDir = path.join(codexHome, "skills", "sam3-image-cli");
  const targetKnowledgeDir = path.join(codexHome, "knowledge", "sam3-image-cli");
  const targetToolDir = path.join(codexHome, "tools", "sam3-image-cli");
  const targetBinDir = path.join(codexHome, "bin");
  const targetShim = path.join(targetBinDir, "sam3-cli");
  const targetCmdShim = path.join(targetBinDir, "sam3-cli.cmd");
  const targetPowerShellShim = path.join(targetBinDir, "sam3-cli.ps1");

  const existingTargets = [
    targetSkillDir,
    targetKnowledgeDir,
    targetToolDir,
    targetShim,
    targetCmdShim,
    targetPowerShellShim
  ].filter(pathExists);
  if (existingTargets.length > 0 && !force) {
    throw new Error(`Existing installation detected: ${existingTargets.join(", ")}. Re-run with --force.`);
  }

  const report = {
    codexHome,
    targetSkillDir,
    targetKnowledgeDir,
    targetToolDir,
    targetShim,
    targetCmdShim,
    targetPowerShellShim,
    force
  };

  if (dryRun) {
    console.log(JSON.stringify({ ok: true, mode: "dry-run", ...report }, null, 2));
    return;
  }

  for (const existing of existingTargets) {
    fs.rmSync(existing, { recursive: true, force: true });
  }

  copyDir(sourceSkillDir, targetSkillDir);
  copyDir(sourceKnowledgeDir, targetKnowledgeDir);
  fs.mkdirSync(targetToolDir, { recursive: true });

  for (const sourcePath of runtimeSources) {
    const name = path.basename(sourcePath);
    const targetPath = path.join(targetToolDir, name);
    if (fs.statSync(sourcePath).isDirectory()) {
      copyDir(sourcePath, targetPath);
    } else {
      ensureParent(targetPath);
      fs.copyFileSync(sourcePath, targetPath);
    }
  }

  ensureParent(targetShim);
  fs.writeFileSync(targetShim, renderPosixShim(targetToolDir), "utf8");
  fs.chmodSync(targetShim, 0o755);
  fs.writeFileSync(targetCmdShim, renderCmdShim(targetToolDir), "utf8");
  fs.writeFileSync(targetPowerShellShim, renderPowerShellShim(targetToolDir), "utf8");

  console.log(JSON.stringify({ ok: true, installed: report }, null, 2));
}

function doctorSkill(codexHome) {
  const skillPath = path.join(codexHome, "skills", "sam3-image-cli");
  const knowledgePath = path.join(codexHome, "knowledge", "sam3-image-cli");
  const toolPath = path.join(codexHome, "tools", "sam3-image-cli");
  const shimPath = path.join(codexHome, "bin", "sam3-cli");
  const cmdShimPath = path.join(codexHome, "bin", "sam3-cli.cmd");
  const powerShellShimPath = path.join(codexHome, "bin", "sam3-cli.ps1");

  console.log(
    JSON.stringify(
      {
        ok: true,
        codexHome,
        paths: {
          skillPath,
          knowledgePath,
          toolPath,
          shimPath,
          cmdShimPath,
          powerShellShimPath
        },
        exists: {
          skillPath: pathExists(skillPath),
          knowledgePath: pathExists(knowledgePath),
          toolPath: pathExists(toolPath),
          shimPath: pathExists(shimPath),
          cmdShimPath: pathExists(cmdShimPath),
          powerShellShimPath: pathExists(powerShellShimPath)
        }
      },
      null,
      2
    )
  );
}

function uninstallSkill(codexHome) {
  const targets = [
    path.join(codexHome, "skills", "sam3-image-cli"),
    path.join(codexHome, "knowledge", "sam3-image-cli"),
    path.join(codexHome, "tools", "sam3-image-cli"),
    path.join(codexHome, "bin", "sam3-cli"),
    path.join(codexHome, "bin", "sam3-cli.cmd"),
    path.join(codexHome, "bin", "sam3-cli.ps1")
  ];
  for (const target of targets) {
    fs.rmSync(target, { recursive: true, force: true });
  }
  console.log(JSON.stringify({ ok: true, removed: targets }, null, 2));
}

const options = parseArgs(process.argv.slice(2));

switch (options.command) {
  case "install":
    installSkill(options.codexHome, options.force, options.dryRun);
    break;
  case "doctor":
    doctorSkill(options.codexHome);
    break;
  case "uninstall":
    uninstallSkill(options.codexHome);
    break;
  default:
    printHelp();
    break;
}

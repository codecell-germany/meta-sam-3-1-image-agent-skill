#!/usr/bin/env node

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";

const repoRoot = process.cwd();
const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), "sam3-skill-smoke-"));
const npmBin = process.platform === "win32" ? "npm.cmd" : "npm";
const npxBin = process.platform === "win32" ? "npx.cmd" : "npx";

function run(command, args, options = {}) {
  return execFileSync(command, args, {
    cwd: options.cwd || repoRoot,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
    shell: options.shell || false
  }).trim();
}

function packTarball() {
  const stdout = run(npmBin, ["pack", "--json"], { cwd: repoRoot });
  const match = stdout.match(/(\[\s*\{[\s\S]*\])\s*$/);
  if (!match) {
    throw new Error(`npm pack --json did not return parseable JSON.\n${stdout}`);
  }
  const parsed = JSON.parse(match[1]);
  const tarballName = parsed.at(-1)?.filename;
  if (!tarballName) {
    throw new Error("npm pack --json did not return a tarball filename.");
  }
  return path.join(repoRoot, tarballName);
}

function resolveInstalledCli(codexHome) {
  const candidates = [
    path.join(codexHome, "bin", "sam3-cli"),
    path.join(codexHome, "bin", "sam3-cli.cmd"),
    path.join(codexHome, "bin", "sam3-cli.ps1")
  ];
  return candidates.find((candidate) => fs.existsSync(candidate)) ?? null;
}

function runInstalledCli(installedCliPath, args) {
  if (!installedCliPath) {
    throw new Error("Installed CLI shim not found after installer smoke.");
  }

  if (installedCliPath.endsWith(".cmd")) {
    return run(installedCliPath, args, { cwd: tempRoot, shell: true });
  }

  if (installedCliPath.endsWith(".ps1")) {
    const powershell = process.platform === "win32" ? "powershell.exe" : "pwsh";
    return run(powershell, ["-ExecutionPolicy", "Bypass", "-File", installedCliPath, ...args], { cwd: tempRoot });
  }

  return run(installedCliPath, args, { cwd: tempRoot });
}

let tarballPath = null;

try {
  tarballPath = packTarball();
  const codexHome = path.join(tempRoot, "codex");

  const installOutput = run(
    npxBin,
    ["-y", "-p", tarballPath, "sam3-image-skill", "install", "--codex-home", codexHome, "--force"],
    { cwd: tempRoot }
  );

  const installedCliPath = resolveInstalledCli(codexHome);
  const shimHelp = runInstalledCli(installedCliPath, ["--help"]);
  const shimDoctor = runInstalledCli(installedCliPath, ["doctor"]);

  console.log(
    JSON.stringify(
      {
        ok: true,
        tarballPath,
        codexHome,
        installedCliPath,
        installOutput: JSON.parse(installOutput),
        shimHelpFirstLine: shimHelp.split("\n")[0],
        shimDoctor: JSON.parse(shimDoctor)
      },
      null,
      2
    )
  );
} finally {
  if (tarballPath) {
    fs.rmSync(tarballPath, { force: true });
  }
  fs.rmSync(tempRoot, { recursive: true, force: true });
}

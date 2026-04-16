import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";

const repoRoot = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..", "..");
const installerPath = path.join(repoRoot, "scripts", "npm-skill-installer.mjs");

function runNode(args, cwd = repoRoot) {
  return execFileSync(process.execPath, [installerPath, ...args], {
    cwd,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"]
  }).trim();
}

test("installer dry-run reports target paths", () => {
  const codexHome = path.join(os.tmpdir(), "sam3-installer-dry-run-home");
  const report = JSON.parse(runNode(["install", "--codex-home", codexHome, "--force", "--dry-run"]));

  assert.equal(report.ok, true);
  assert.equal(report.mode, "dry-run");
  assert.equal(report.targetSkillDir, path.join(codexHome, "skills", "sam3-image-cli"));
  assert.equal(report.targetToolDir, path.join(codexHome, "tools", "sam3-image-cli"));
  assert.equal(report.targetShim, path.join(codexHome, "bin", "sam3-cli"));
  assert.equal(report.targetCmdShim, path.join(codexHome, "bin", "sam3-cli.cmd"));
  assert.equal(report.targetPowerShellShim, path.join(codexHome, "bin", "sam3-cli.ps1"));
});

test("installer creates skill, runtime, and all cli shims", () => {
  const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), "sam3-installer-unit-"));
  const codexHome = path.join(tempRoot, "codex");

  try {
    JSON.parse(runNode(["install", "--codex-home", codexHome, "--force"]));
    const doctor = JSON.parse(runNode(["doctor", "--codex-home", codexHome]));

    assert.equal(doctor.ok, true);
    assert.equal(doctor.exists.skillPath, true);
    assert.equal(doctor.exists.knowledgePath, true);
    assert.equal(doctor.exists.toolPath, true);
    assert.equal(doctor.exists.shimPath, true);
    assert.equal(doctor.exists.cmdShimPath, true);
    assert.equal(doctor.exists.powerShellShimPath, true);

    const posixShim = fs.readFileSync(path.join(codexHome, "bin", "sam3-cli"), "utf8");
    const cmdShim = fs.readFileSync(path.join(codexHome, "bin", "sam3-cli.cmd"), "utf8");
    const powerShellShim = fs.readFileSync(path.join(codexHome, "bin", "sam3-cli.ps1"), "utf8");

    assert.match(posixShim, /sam3_cli\.py/);
    assert.match(posixShim, /PYTHON_BIN/);
    assert.match(cmdShim, /sam3_cli\.py/);
    assert.match(cmdShim, /where py/);
    assert.match(powerShellShim, /sam3_cli\.py/);
    assert.match(powerShellShim, /Get-Command py/);
  } finally {
    fs.rmSync(tempRoot, { recursive: true, force: true });
  }
});

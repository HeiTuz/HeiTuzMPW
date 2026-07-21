#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const base = fs.mkdtempSync(path.join(os.tmpdir(), "mpw-runtime-smoke-"));

function completeAgentTree(candidate) {
  return ["hermes", "claude", "codex"].every((host) => fs.existsSync(path.join(candidate, "agents", host)));
}

let distributionRoot = root;
if (!completeAgentTree(root)) {
  distributionRoot = path.join(base, "fixture-source");
  fs.cpSync(root, distributionRoot, {
    recursive: true,
    filter(candidate) {
      const relative = path.relative(root, candidate);
      return !relative.split(path.sep).some((part) => [".git", ".gjc", ".omx", "node_modules", "agents"].includes(part));
    },
  });
  const canonical = fs.readFileSync(path.join(root, "SKILL.md"), "utf8");
  for (const host of ["hermes", "claude", "codex"]) fs.mkdirSync(path.join(distributionRoot, "agents", host), { recursive: true });
  fs.writeFileSync(path.join(distributionRoot, "agents", "hermes", "README.md"), "Hermes uses the canonical entry point.\n");
  fs.writeFileSync(path.join(distributionRoot, "agents", "claude", "SKILL.md"), `${canonical}\n<!-- Claude fixture integration surface -->\n`);
  fs.writeFileSync(path.join(distributionRoot, "agents", "codex", "SKILL.md"), `${canonical}\n<!-- Codex fixture integration surface -->\n`);
}
const installer = path.join(distributionRoot, "scripts", "install.mjs");
const targets = ["claude", "gpt", "codex", "hermes", "gjc", "agents"];
const required = [
  "SKILL.md",
  "references/templates.md",
  "references/model-playbooks.md",
  "references/adapters.md",
  "references/image/compiler.md",
  "references/image/lanes.md",
];
const sharedCore = required.filter((relative) => relative !== "SKILL.md");
const adapterHeadings = {
  claude: "Claude",
  gpt: "GPT/Codex",
  codex: "GPT/Codex",
  hermes: "Hermes",
  gjc: "GJC",
};

function fail(message) {
  console.error(`FAIL ${message}`);
  console.error(`Artifacts preserved at ${base}`);
  process.exit(1);
}

function run(args, env = process.env) {
  const result = spawnSync(process.execPath, [installer, ...args], {
    cwd: distributionRoot,
    env: { ...env, HOME: env.HOME, USERPROFILE: env.HOME, CI: "1" },
    encoding: "utf8",
  });
  if (result.status !== 0) fail(`${args.join(" ")}\n${result.stderr || result.stdout}`);
}

function runCommand(command, args, cwd, env) {
  const result = spawnSync(command, args, { cwd, env, encoding: "utf8" });
  if (result.status !== 0) fail(`${command} ${args.join(" ")}\n${result.stderr || result.stdout}`);
}

function readInstalled(destination, relative) {
  const file = path.join(destination, relative);
  if (!fs.existsSync(file)) fail(`${relative} missing in ${destination}`);
  return fs.readFileSync(file, "utf8");
}

function checkLinks(destination, relative) {
  const text = readInstalled(destination, relative);
  const dir = path.dirname(path.join(destination, relative));
  const links = [...text.matchAll(/\]\(([^)#][^)]+\.md)(?:#[^)]+)?\)/g)].map((match) => match[1]);
  for (const link of links) {
    const target = path.resolve(dir, link);
    if (!target.startsWith(destination + path.sep)) fail(`${relative} link escapes install: ${link}`);
    if (!fs.existsSync(target)) fail(`${relative} missing link target: ${link}`);
  }
}

function destination(home, target) {
  if (target === "hermes") return path.join(home, ".hermes", "skills", "prompt-writing", "MPW");
  if (target === "claude") return path.join(home, ".claude", "skills", "MPW");
  if (target === "gjc") return path.join(home, ".gjc", "agent", "skills", "MPW");
  if (target === "agents") return path.join(home, ".agents", "skills", "MPW");
  return path.join(home, ".codex", "skills", "MPW");
}

function overlayHost(target) {
  if (target === "gpt") return "codex";
  return ["hermes", "claude", "codex"].includes(target) ? target : null;
}

function section(markdown, heading) {
  const startToken = `## ${heading}`;
  const start = markdown.indexOf(startToken);
  if (start < 0) fail(`adapter section missing: ${heading}`);
  const next = markdown.indexOf("\n## ", start + startToken.length);
  return markdown.slice(start, next < 0 ? markdown.length : next);
}

function assertTerms(name, text, terms) {
  for (const term of terms) {
    if (!text.includes(term)) fail(`${name}: missing ${term}`);
  }
}

function assertInstalled(home, target) {
  const installDestination = destination(home, target);
  const installed = Object.fromEntries(required.map((relative) => [relative, readInstalled(installDestination, relative)]));
  if (fs.existsSync(path.join(installDestination, "agents"))) fail(`${target}: agents/ leaked into installed payload`);
  for (const relative of ["SKILL.md", "references/templates.md", "references/model-playbooks.md", "references/adapters.md", "references/image/lanes.md"]) {
    checkLinks(installDestination, relative);
  }
  const host = overlayHost(target);
  const overlaySkill = host ? path.join(distributionRoot, "agents", host, "SKILL.md") : null;
  if (overlaySkill && fs.existsSync(overlaySkill)) {
    if (installed["SKILL.md"] !== fs.readFileSync(overlaySkill, "utf8")) fail(`${target}: host overlay SKILL.md was not applied`);
    if (installed["SKILL.md"] === fs.readFileSync(path.join(distributionRoot, "SKILL.md"), "utf8")) fail(`${target}: adapted SKILL.md is byte-identical to canonical`);
  }
  return installed;
}

let canonicalHash = null;
for (const target of targets) {
  const home = path.join(base, `home-${target}`);
  fs.mkdirSync(home, { recursive: true });
  run(["--target", target, "--force", "--quiet"], { ...process.env, HOME: home });
  const installed = assertInstalled(home, target);

  const hash = crypto.createHash("sha256")
    .update(sharedCore.map((relative) => `${relative}\0${installed[relative]}`).join("\0"))
    .digest("hex");
  if (canonicalHash === null) canonicalHash = hash;
  if (hash !== canonicalHash) fail(`${target}: shared canonical references diverged`);

  assertTerms(`${target}: generic execution contract`, installed["references/model-playbooks.md"], [
    "`prime`", "`planner`", "`worker`", "`critic`", "Human-only", "Surface-matched evidence",
  ]);
  assertTerms(`${target}: decomposition canon`, installed["references/model-playbooks.md"], [
    "Topology-first intake", "Validation-coupled decomposition", "Join gate", "Blocker classification",
  ]);
  assertTerms(`${target}: team insertion block`, installed["references/templates.md"], [
    "model-playbooks.md", "작업 방식: prime", "frozen artifact", "human-only blocker",
  ]);
  if (adapterHeadings[target]) {
    const adapter = section(installed["references/adapters.md"], adapterHeadings[target]);
    assertTerms(`${target}: adapter`, adapter, ["설치/발견", "역할 매핑", "모델 선택 위치", "fallback"]);
  }
}

for (const host of ["hermes", "claude", "codex"]) {
  const home = path.join(base, `auto-${host}`);
  fs.mkdirSync(path.join(home, `.${host}`), { recursive: true });
  run(["--target", "auto", "--force", "--quiet"], { ...process.env, HOME: home });
  assertInstalled(home, host);
}

const noDetectedHome = path.join(base, "auto-none");
fs.mkdirSync(noDetectedHome, { recursive: true });
run(["--force", "--quiet"], { ...process.env, HOME: noDetectedHome });
assertInstalled(noDetectedHome, "hermes");

const multipleHome = path.join(base, "auto-multiple");
for (const host of ["hermes", "claude", "codex"]) fs.mkdirSync(path.join(multipleHome, `.${host}`), { recursive: true });
run(["--target", "auto", "--force", "--quiet"], { ...process.env, HOME: multipleHome });
assertInstalled(multipleHome, "hermes");
if (fs.existsSync(path.join(destination(multipleHome, "claude"), "SKILL.md"))) fail("non-interactive auto installed more than the preferred target");
if (fs.existsSync(path.join(destination(multipleHome, "codex"), "SKILL.md"))) fail("non-interactive auto installed more than the preferred target");
run(["--target", "all", "--force", "--quiet"], { ...process.env, HOME: multipleHome });
for (const host of ["hermes", "claude", "codex"]) assertInstalled(multipleHome, host);

for (const runtime of ["npm", "bun"]) {
  const project = path.join(base, `${runtime}-entrypoint`);
  const home = path.join(project, "home");
  const installDestination = path.join(project, "installed");
  fs.mkdirSync(project, { recursive: true });
  fs.writeFileSync(path.join(project, "package.json"), JSON.stringify({ private: true }) + "\n");
  const env = {
    ...process.env,
    HOME: home,
    USERPROFILE: home,
    CI: "1",
    BUN_INSTALL_CACHE_DIR: path.join(project, "bun-cache"),
  };
  if (runtime === "npm") {
    runCommand("npm", ["install", "--no-save", "--ignore-scripts", distributionRoot], project, env);
    runCommand("npx", ["--no-install", "heituzmpw", "--", "--dest", installDestination, "--force", "--quiet"], project, env);
  } else {
    runCommand("bun", ["add", "--no-save", "--ignore-scripts", distributionRoot], project, env);
    runCommand("bunx", ["--no-install", "heituzmpw", "--", "--dest", installDestination, "--force", "--quiet"], project, env);
  }
  if (!fs.existsSync(path.join(installDestination, "SKILL.md"))) fail(`${runtime}: forwarded package entrypoint did not install SKILL.md`);
  if (fs.existsSync(path.join(installDestination, "agents"))) fail(`${runtime}: forwarded package entrypoint leaked agents/`);
}

fs.rmSync(base, { recursive: true, force: true });
console.log(`OK — explicit, auto, all, and non-interactive installs share canonical references (${canonicalHash.slice(0, 12)})`);

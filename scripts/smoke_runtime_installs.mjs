#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const installer = path.join(root, "scripts", "install.mjs");
const base = fs.mkdtempSync(path.join(os.tmpdir(), "mpw-runtime-smoke-"));
const targets = ["claude", "gpt", "codex", "hermes", "gjc"];
const required = [
  "SKILL.md",
  "references/templates.md",
  "references/model-playbooks.md",
  "references/adapters.md",
  "references/image/compiler.md",
];
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
    cwd: root,
    env,
    encoding: "utf8",
  });
  if (result.status !== 0) {
    fail(`${args.join(" ")}\n${result.stderr || result.stdout}`);
  }
}

function readInstalled(dest, rel) {
  const file = path.join(dest, rel);
  if (!fs.existsSync(file)) fail(`${rel} missing in ${dest}`);
  return fs.readFileSync(file, "utf8");
}

function checkLinks(dest, rel) {
  const text = readInstalled(dest, rel);
  const dir = path.dirname(path.join(dest, rel));
  const links = [...text.matchAll(/\]\(([^)#][^)]+\.md)(?:#[^)]+)?\)/g)].map((m) => m[1]);
  for (const link of links) {
    const target = path.resolve(dir, link);
    if (!target.startsWith(dest + path.sep)) fail(`${rel} link escapes install: ${link}`);
    if (!fs.existsSync(target)) fail(`${rel} missing link target: ${link}`);
  }
}

function destination(home, target) {
  if (target === "hermes") return path.join(home, ".hermes", "skills", "prompt-writing", "master-prompt-writer");
  if (target === "claude") return path.join(home, ".claude", "skills", "master-prompt-writer");
  if (target === "gjc") return path.join(home, ".gjc", "agent", "skills", "master-prompt-writer");
  return path.join(home, ".codex", "skills", "master-prompt-writer");
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

let canonicalHash = null;
for (const target of targets) {
  const home = path.join(base, `home-${target}`);
  fs.mkdirSync(home, { recursive: true });
  run(["--target", target, "--force", "--quiet"], { ...process.env, HOME: home });
  const dest = destination(home, target);

  const installed = Object.fromEntries(required.map((rel) => [rel, readInstalled(dest, rel)]));
  for (const rel of ["SKILL.md", "references/templates.md", "references/model-playbooks.md", "references/adapters.md"]) {
    checkLinks(dest, rel);
  }

  const hash = crypto.createHash("sha256")
    .update(required.map((rel) => `${rel}\0${installed[rel]}`).join("\0"))
    .digest("hex");
  if (canonicalHash === null) canonicalHash = hash;
  if (hash !== canonicalHash) fail(`${target}: installed core diverged from other targets`);

  assertTerms(`${target}: generic execution contract`, installed["references/model-playbooks.md"], [
    "`prime`", "`planner`", "`worker`", "`critic`", "Human-only", "Surface-matched evidence",
  ]);
  assertTerms(`${target}: decomposition canon`, installed["references/model-playbooks.md"], [
    "Topology-first intake", "Validation-coupled decomposition", "Join gate", "Blocker classification",
  ]);
  assertTerms(`${target}: team insertion block`, installed["references/templates.md"], [
    "model-playbooks.md", "작업 방식: prime", "frozen artifact", "human-only blocker",
  ]);

  const adapter = section(installed["references/adapters.md"], adapterHeadings[target]);
  assertTerms(`${target}: adapter`, adapter, ["설치/발견", "역할 매핑", "모델 선택 위치", "fallback"]);
}

for (const forbiddenDir of ["claude", "gpt", "codex", "hermes", "gjc", "agents"]) {
  if (fs.existsSync(path.join(root, forbiddenDir))) fail(`duplicated runtime tree exists: ${forbiddenDir}/`);
}

fs.rmSync(base, { recursive: true, force: true });
console.log(`OK — one byte-identical shared core installed for ${targets.join(", ")} (${canonicalHash.slice(0, 12)})`);

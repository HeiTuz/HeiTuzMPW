#!/usr/bin/env node
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import readline from "node:readline/promises";
import { fileURLToPath } from "node:url";
import {
  AGENT_HOST_PRIORITY,
  detectAgentHosts,
  deterministicAgentHosts,
  formatDetectedHosts,
  normalizeAgentHost,
  parseInteractiveAgentHosts,
} from "./agent_targets.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const skillName = "MPW";
const legacyTargets = new Set(["gjc", "agents"]);
const knownTargets = new Set(["auto", "all", "hermes", "claude", "codex", "gpt", ...legacyTargets]);

export function destinationForTarget(homeDir, target) {
  const normalized = normalizeAgentHost(target);
  if (normalized === "hermes") return path.join(homeDir, ".hermes", "skills", "prompt-writing", skillName);
  if (normalized === "claude") return path.join(homeDir, ".claude", "skills", skillName);
  if (normalized === "codex") return path.join(homeDir, ".codex", "skills", skillName);
  if (normalized === "gjc") return path.join(homeDir, ".gjc", "agent", "skills", skillName);
  if (normalized === "agents") return path.join(homeDir, ".agents", "skills", skillName);
  throw new Error(`Unknown target: ${target}`);
}

function usage(exitCode = 0) {
  const out = exitCode === 0 ? console.log : console.error;
  out(`MPW installer

Usage:
  npx --yes github:HeiTuz/MPW
  bunx github:HeiTuz/MPW --target codex
  node scripts/install.mjs --target all
  node scripts/install.mjs --dest /custom/skills/MPW

Options:
  --target <auto|all|hermes|codex|gpt|claude|gjc|agents>
                                              Auto-detect by default, or install to a known target.
  --dest <path>                               Install to an explicit directory.
  --force                                     Replace an existing destination.
  --quiet                                     Print only errors.
  -h, --help                                  Show this help.
`);
  process.exit(exitCode);
}

export function parseArgs(argv) {
  const opts = { target: "auto", targetExplicit: false, dest: null, force: false, quiet: false };
  for (let i = 0; i < argv.length; i += 1) {
    const argument = argv[i];
    if (argument === "-h" || argument === "--help") usage(0);
    if (argument === "--") continue;
    if (argument === "--force") { opts.force = true; continue; }
    if (argument === "--quiet") { opts.quiet = true; continue; }
    if (argument === "--target") {
      if (!argv[i + 1]) usage(2);
      opts.target = argv[++i];
      opts.targetExplicit = true;
      continue;
    }
    if (argument.startsWith("--target=")) {
      opts.target = argument.slice("--target=".length);
      opts.targetExplicit = true;
      continue;
    }
    if (argument === "--dest") {
      if (!argv[i + 1]) usage(2);
      opts.dest = argv[++i];
      continue;
    }
    if (argument.startsWith("--dest=")) {
      opts.dest = argument.slice("--dest=".length);
      continue;
    }
    console.error(`Unknown argument: ${argument}`);
    usage(2);
  }
  opts.target = String(opts.target || "").toLowerCase();
  if (!knownTargets.has(opts.target)) {
    console.error(`Unknown target: ${opts.target}`);
    usage(2);
  }
  return opts;
}

function isEmptyDir(candidate) {
  return fs.existsSync(candidate) && fs.statSync(candidate).isDirectory() && fs.readdirSync(candidate).length === 0;
}

export const ALLOWED_INSTALL_ROOTS = new Set([
  "AGENTS.md", "LICENSE", "README.md", "SKILL.md", "package.json",
  "agents", "contracts", "examples", "references", "scripts",
]);

const EXCLUDED_PARTS = new Set([".git", "node_modules", ".gjc", ".omx", "__pycache__", "docs-internal"]);

export function shouldSkip(rel, { includeAgents = false } = {}) {
  const parts = rel.split(path.sep);
  if (!ALLOWED_INSTALL_ROOTS.has(parts[0])) return true;
  if (!includeAgents && parts[0] === "agents") return true;
  return parts.some((part) => EXCLUDED_PARTS.has(part) || part.startsWith(".")) ||
    rel.endsWith(".pyc") ||
    rel === "package-lock.json" ||
    rel === "bun.lockb" ||
    rel === "bun.lock";
}

function copyCanonicalTree(current, destination, sourceRoot) {
  for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
    const from = path.join(current, entry.name);
    const rel = path.relative(sourceRoot, from);
    if (shouldSkip(rel)) continue;
    const to = path.join(destination, rel);
    if (entry.isDirectory()) {
      fs.mkdirSync(to, { recursive: true });
      copyCanonicalTree(from, destination, sourceRoot);
    } else if (entry.isFile()) {
      fs.mkdirSync(path.dirname(to), { recursive: true });
      fs.copyFileSync(from, to);
      fs.chmodSync(to, fs.statSync(from).mode & 0o777);
    } else if (entry.isSymbolicLink()) {
      const link = fs.readlinkSync(from);
      fs.mkdirSync(path.dirname(to), { recursive: true });
      try { fs.symlinkSync(link, to); } catch (error) {
        if (error.code !== "EEXIST") throw error;
      }
    }
  }
}

function overlayEntryIsSafe(relative) {
  const parts = relative.split(path.sep);
  return !parts.some((part) => EXCLUDED_PARTS.has(part) || part.startsWith(".")) &&
    !relative.endsWith(".pyc");
}

function copyOverlayTree(current, destination, overlayRoot) {
  for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
    const from = path.join(current, entry.name);
    const rel = path.relative(overlayRoot, from);
    if (!overlayEntryIsSafe(rel)) continue;
    const to = path.join(destination, rel);
    if (entry.isDirectory()) {
      fs.mkdirSync(to, { recursive: true });
      copyOverlayTree(from, destination, overlayRoot);
    } else if (entry.isFile()) {
      fs.mkdirSync(path.dirname(to), { recursive: true });
      fs.copyFileSync(from, to);
      fs.chmodSync(to, fs.statSync(from).mode & 0o777);
    }
  }
}

function validateHostOverlay(sourceRoot, host) {
  const normalized = normalizeAgentHost(host);
  const overlay = path.join(sourceRoot, "agents", normalized);
  if (!fs.existsSync(overlay) || !fs.statSync(overlay).isDirectory()) {
    throw new Error(`Install source is missing the ${normalized} agent overlay`);
  }
  if (normalized !== "hermes" && !fs.existsSync(path.join(overlay, "SKILL.md"))) {
    throw new Error(`Install source is missing agents/${normalized}/SKILL.md`);
  }
  const allowed = new Set(["AGENTS.md", "README.md", "SKILL.md"]);
  for (const entry of fs.readdirSync(overlay)) {
    if (!allowed.has(entry)) throw new Error(`Unsupported ${normalized} overlay entry: ${entry}`);
  }
  return overlay;
}

function countSkillEntries(directory) {
  let count = 0;
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const candidate = path.join(directory, entry.name);
    if (entry.isDirectory()) count += countSkillEntries(candidate);
    else if (entry.isFile() && entry.name === "SKILL.md") count += 1;
  }
  return count;
}

export function installPayload({ sourceRoot = root, destination, host = null }) {
  fs.mkdirSync(destination, { recursive: true });
  copyCanonicalTree(sourceRoot, destination, sourceRoot);
  const overlay = host ? validateHostOverlay(sourceRoot, host) : null;
  if (overlay) copyOverlayTree(overlay, destination, overlay);
  if (fs.existsSync(path.join(destination, "agents"))) {
    throw new Error(`Install verification failed: agents/ must not appear in ${destination}`);
  }
  if (!fs.existsSync(path.join(destination, "SKILL.md"))) {
    throw new Error(`Install verification failed: SKILL.md missing in ${destination}`);
  }
  if (countSkillEntries(destination) !== 1) {
    throw new Error(`Install verification failed: expected exactly one SKILL.md in ${destination}`);
  }
}

function expandDestination(value, homeDir) {
  if (value === "~") return homeDir;
  if (value.startsWith("~/") || value.startsWith("~\\")) return path.join(homeDir, value.slice(2));
  return value;
}

function inferHostFromDestination(homeDir, destination) {
  for (const host of AGENT_HOST_PRIORITY) {
    if (path.normalize(destination) === path.normalize(destinationForTarget(homeDir, host))) return host;
  }
  return null;
}

async function chooseInteractiveHosts(detected) {
  console.log(`Detected agent environments: ${formatDetectedHosts(detected)}`);
  const recommended = deterministicAgentHosts("auto", detected)[0];
  const prompt = `Install target(s) [${recommended}] (comma-separated ${AGENT_HOST_PRIORITY.join(", ")}; all = every detected): `;
  const terminal = readline.createInterface({ input: process.stdin, output: process.stdout });
  try {
    return parseInteractiveAgentHosts(await terminal.question(prompt), detected);
  } finally {
    terminal.close();
  }
}

function pathsOverlap(left, right) {
  const a = path.resolve(left);
  const b = path.resolve(right);
  return a === b || a.startsWith(b + path.sep) || b.startsWith(a + path.sep);
}

function validateDestination(destination, homeDir, sourceRoot = root) {
  const resolved = path.resolve(destination);
  const filesystemRoot = path.parse(resolved).root;
  const protectedContainers = [
    ".hermes",
    path.join(".hermes", "skills"),
    path.join(".hermes", "skills", "prompt-writing"),
    ".claude",
    path.join(".claude", "skills"),
    ".codex",
    path.join(".codex", "skills"),
    ".gjc",
    path.join(".gjc", "agent"),
    path.join(".gjc", "agent", "skills"),
    ".agents",
    path.join(".agents", "skills"),
  ].map((relative) => path.resolve(homeDir, relative));
  if (resolved === filesystemRoot || path.dirname(resolved) === filesystemRoot) {
    throw new Error(`Refusing unsafe install destination: ${resolved}`);
  }
  if (resolved === path.resolve(homeDir) || protectedContainers.includes(resolved) || pathsOverlap(resolved, sourceRoot)) {
    throw new Error(`Refusing unsafe install destination: ${resolved}`);
  }
}

async function resolvePlans(opts, homeDir) {
  if (opts.dest) {
    if (opts.targetExplicit && opts.target === "all") {
      throw new Error("--target all cannot be combined with --dest; omit --dest to use host-specific locations");
    }
    const destination = path.resolve(expandDestination(opts.dest, homeDir));
    const explicitHost = opts.targetExplicit && !["auto", "all", ...legacyTargets].includes(opts.target)
      ? normalizeAgentHost(opts.target)
      : inferHostFromDestination(homeDir, destination);
    return [{ host: explicitHost, destination }];
  }
  if (legacyTargets.has(opts.target)) {
    return [{ host: null, destination: destinationForTarget(homeDir, opts.target) }];
  }
  const detected = detectAgentHosts({ homeDir, existsSync: fs.existsSync });
  let hosts;
  const interactive = opts.target === "auto" && process.stdin.isTTY && process.stdout.isTTY && !process.env.CI;
  if (interactive) hosts = await chooseInteractiveHosts(detected);
  else hosts = deterministicAgentHosts(opts.target, detected);
  return hosts.map((host) => ({ host, destination: destinationForTarget(homeDir, host) }));
}

function prepareDestinations(plans, force, homeDir) {
  for (let index = 0; index < plans.length; index += 1) {
    validateDestination(plans[index].destination, homeDir);
    for (let other = index + 1; other < plans.length; other += 1) {
      if (pathsOverlap(plans[index].destination, plans[other].destination)) {
        throw new Error("Install destinations must not overlap");
      }
    }
  }
  for (const { destination } of plans) {
    if (!fs.existsSync(destination) || isEmptyDir(destination)) continue;
    if (!force) {
      throw new Error(`Destination already exists and is not empty: ${destination}\nUse --force to replace it, or pass --dest to install elsewhere.`);
    }
  }
}

export function installPlansTransaction(plans, { sourceRoot = root } = {}) {
  const staged = [];
  try {
    for (const plan of plans) {
      const parent = path.dirname(plan.destination);
      fs.mkdirSync(parent, { recursive: true });
      const stageRoot = fs.mkdtempSync(path.join(parent, ".heituzmpw-stage-"));
      const payload = path.join(stageRoot, "payload");
      staged.push({ ...plan, stageRoot, payload });
      installPayload({ sourceRoot, destination: payload, host: plan.host });
    }

    const applied = [];
    try {
      for (let index = 0; index < staged.length; index += 1) {
        const item = staged[index];
        const backup = `${item.destination}.heituzmpw-backup-${process.pid}-${Date.now()}-${index}`;
        const hadDestination = fs.existsSync(item.destination);
        if (hadDestination) fs.renameSync(item.destination, backup);
        try {
          fs.renameSync(item.payload, item.destination);
        } catch (error) {
          if (hadDestination) fs.renameSync(backup, item.destination);
          throw error;
        }
        applied.push({ destination: item.destination, backup: hadDestination ? backup : null });
      }
    } catch (error) {
      for (const item of applied.reverse()) {
        fs.rmSync(item.destination, { recursive: true, force: true });
        if (item.backup && fs.existsSync(item.backup)) fs.renameSync(item.backup, item.destination);
      }
      throw error;
    }
    for (const item of applied) {
      if (item.backup) fs.rmSync(item.backup, { recursive: true, force: true });
    }
  } finally {
    for (const item of staged) fs.rmSync(item.stageRoot, { recursive: true, force: true });
  }
}

export async function main(argv = process.argv.slice(2)) {
  const opts = parseArgs(argv);
  const homeDir = os.homedir();
  const plans = await resolvePlans(opts, homeDir);
  prepareDestinations(plans, opts.force, homeDir);
  installPlansTransaction(plans);
  for (const plan of plans) {
    if (!opts.quiet) console.log(`Installed ${skillName} (${plan.host || opts.target}) -> ${plan.destination}`);
  }
  if (!opts.quiet) console.log('Verify by asking your agent: "프롬프트 만들어줘"');
}

function isMainModule() {
  if (!process.argv[1]) return false;
  try {
    return fs.realpathSync(process.argv[1]) === fs.realpathSync(fileURLToPath(import.meta.url));
  } catch {
    return path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
  }
}

if (isMainModule()) {
  main().catch((error) => {
    console.error(`MPW installer: ${error.message}`);
    process.exitCode = 1;
  });
}

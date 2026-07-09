#!/usr/bin/env node
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const skillName = "master-prompt-writer";

const targetMap = {
  hermes: path.join(os.homedir(), ".hermes", "skills", "prompt-writing", skillName),
  codex: path.join(os.homedir(), ".codex", "skills", skillName),
  // `gpt` is a user-facing alias for the GPT/Codex skill surface.
  gpt: path.join(os.homedir(), ".codex", "skills", skillName),
  claude: path.join(os.homedir(), ".claude", "skills", skillName),
  gjc: path.join(os.homedir(), ".gjc", "agent", "skills", skillName),
  agents: path.join(os.homedir(), ".agents", "skills", skillName),
};

function usage(exitCode = 0) {
  const out = exitCode === 0 ? console.log : console.error;
  out(`master-prompt-writer installer

Usage:
  npx --yes github:HeiTuz/master-prompt-writer --target hermes
  bunx github:HeiTuz/master-prompt-writer --target codex
  node scripts/install.mjs --target claude
  node scripts/install.mjs --dest /custom/skills/master-prompt-writer

Options:
  --target <hermes|codex|gpt|claude|gjc|agents>   Install to a known agent skill directory.
  --dest <path>                               Install to an explicit directory.
  --force                                     Replace an existing destination.
  --quiet                                     Print only errors.
  -h, --help                                  Show this help.
`);
  process.exit(exitCode);
}

function parseArgs(argv) {
  const opts = { target: "hermes", dest: null, force: false, quiet: false };
  for (let i = 0; i < argv.length; i += 1) {
    const a = argv[i];
    if (a === "-h" || a === "--help") usage(0);
    if (a === "--force") { opts.force = true; continue; }
    if (a === "--quiet") { opts.quiet = true; continue; }
    if (a === "--target") { opts.target = argv[++i]; continue; }
    if (a.startsWith("--target=")) { opts.target = a.slice("--target=".length); continue; }
    if (a === "--dest") { opts.dest = argv[++i]; continue; }
    if (a.startsWith("--dest=")) { opts.dest = a.slice("--dest=".length); continue; }
    console.error(`Unknown argument: ${a}`);
    usage(2);
  }
  if (opts.dest) return opts;
  if (!Object.hasOwn(targetMap, opts.target)) {
    console.error(`Unknown target: ${opts.target}`);
    usage(2);
  }
  opts.dest = targetMap[opts.target];
  return opts;
}

function isEmptyDir(p) {
  return fs.existsSync(p) && fs.statSync(p).isDirectory() && fs.readdirSync(p).length === 0;
}

function shouldSkip(rel) {
  const parts = rel.split(path.sep);
  return parts.some((p) => [".git", "node_modules", "docs-internal", ".gjc"].includes(p)) ||
    rel === "package-lock.json" ||
    rel === "bun.lockb" ||
    rel === "bun.lock";
}

function copyDir(src, dest) {
  for (const ent of fs.readdirSync(src, { withFileTypes: true })) {
    const srcPath = path.join(src, ent.name);
    const rel = path.relative(root, srcPath);
    if (shouldSkip(rel)) continue;
    const destPath = path.join(dest, rel);
    if (ent.isDirectory()) {
      fs.mkdirSync(destPath, { recursive: true });
      copyDir(srcPath, dest);
    } else if (ent.isFile()) {
      fs.mkdirSync(path.dirname(destPath), { recursive: true });
      fs.copyFileSync(srcPath, destPath);
      fs.chmodSync(destPath, fs.statSync(srcPath).mode & 0o777);
    } else if (ent.isSymbolicLink()) {
      const link = fs.readlinkSync(srcPath);
      fs.mkdirSync(path.dirname(destPath), { recursive: true });
      try { fs.symlinkSync(link, destPath); } catch (e) {
        if (e.code !== "EEXIST") throw e;
      }
    }
  }
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  const dest = path.resolve(opts.dest.replace(/^~/, os.homedir()));

  if (fs.existsSync(dest) && !isEmptyDir(dest)) {
    if (!opts.force) {
      console.error(`Destination already exists and is not empty: ${dest}`);
      console.error("Use --force to replace it, or pass --dest to install elsewhere.");
      process.exit(1);
    }
    fs.rmSync(dest, { recursive: true, force: true });
  }

  fs.mkdirSync(dest, { recursive: true });
  copyDir(root, dest);

  if (!fs.existsSync(path.join(dest, "SKILL.md"))) {
    console.error(`Install verification failed: SKILL.md missing in ${dest}`);
    process.exit(1);
  }

  if (!opts.quiet) {
    console.log(`Installed ${skillName} -> ${dest}`);
    console.log('Verify by asking your agent: "프롬프트 만들어줘"');
  }
}

main();

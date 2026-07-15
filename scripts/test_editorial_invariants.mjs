#!/usr/bin/env node
// 컨셉-콜리전 에디토리얼 그래머(§15) 불변식 행동 테스트.
// - 유명 사진 제어구·문화 앵커 보존(positive preservation)
// - 국적-피부 고정 / malformed 피부 토큰 거절(negative stereotype)
// - 글로우 토큰 적층 경고 + 매트존으로 해제(token-stack)
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const validator = path.join(root, "scripts", "check_prompt.mjs");
const temp = fs.mkdtempSync(path.join(os.tmpdir(), "heituzmpw-editorial-"));

function validate(prompt, flags = []) {
  const file = path.join(temp, `p-${Math.random().toString(36).slice(2)}.txt`);
  fs.writeFileSync(file, prompt);
  const result = spawnSync(process.execPath, [validator, file, ...flags], { encoding: "utf8" });
  return JSON.parse(result.stdout);
}
const codes = (list) => list.map((entry) => entry.code);

try {
  // 1. Positive preservation — Portra film tonality / medium-format clarity / East Asian woman /
  //    자격화된 glass skin translucency 가 전부 error 없이 통과한다.
  const preserved = fs.readFileSync(path.join(root, "scripts/fixtures/good/editorial_collision.txt"), "utf8");
  const good = validate(preserved);
  assert.equal(good.ok, true, `preserved control tokens must pass: ${JSON.stringify(good.errors)}`);
  assert.equal(good.errors.length, 0, "preserved editorial prompt must have zero errors");
  for (const token of ["Portra film tonality", "medium-format clarity", "East Asian woman", "glass skin translucency", "chok-chok"]) {
    assert.ok(preserved.includes(token), `fixture lost preserved control token: ${token}`);
  }

  // 2. Negative stereotype — 국적-피부 고정 + malformed AI 토큰은 error.
  const stereo = validate("East Asian woman, 노란 피부(yellow undertone skin), micro skin texture AI, 팔레트 #F2ECE1 #D8C7B0 #9FB0C4, soft key light, matte 마감, AR 3:4");
  assert.equal(stereo.ok, false, "nationality-locked skin + malformed token must fail");
  assert.ok(codes(stereo.errors).includes("E-NAT-SKIN"), "yellow skin must raise E-NAT-SKIN");
  assert.ok(codes(stereo.errors).includes("E-SKIN-AI"), "micro skin texture AI must raise E-SKIN-AI");

  // 3. Token-stack — 글로우 4종+ 매트존 부재는 W-GLOW-STACK 경고.
  const stacked = "East Asian woman, dewy luminous skin, wet-look strands, subsurface glow, glass skin 마감, 팔레트 #F2ECE1 #D8C7B0 #9FB0C4, soft key light, film grain, AR 3:4";
  const stackWarn = validate(stacked);
  assert.ok(codes(stackWarn.warnings).includes("W-GLOW-STACK"), "4+ glow tokens w/o matte must warn W-GLOW-STACK");

  // 4. 같은 스택에 매트존을 넣으면 경고가 사라진다(주 글로우 1 + 매트존 레시피).
  const withMatte = validate(stacked.replace("glass skin 마감", "glass skin 마감, 매트한 T존 대비"));
  assert.equal(codes(withMatte.warnings).includes("W-GLOW-STACK"), false, "matte zone must clear W-GLOW-STACK");

  console.log("editorial concept-collision invariants: OK");
} finally {
  fs.rmSync(temp, { recursive: true, force: true });
}

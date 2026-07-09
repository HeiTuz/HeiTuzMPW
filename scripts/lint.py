#!/usr/bin/env python3
"""master-prompt-writer self-lint.

Checks the skill's own hardlines against its files:
- every measured-length label — "(N자 실측)" / "실측: N자" / "N자 실측" / bare "(…, N자)"
  — matches the adjacent ```text block's body length across ALL core files.
  Count method = trimmed body, code points (equivalent to check_prompt.mjs's
  trimmed .length and to grapheme count for this repo's BMP/no-combining text;
  blocks containing combining marks or ZWJ fail loudly instead of miscounting).
  Labels bind to the nearest ```text fence before or after within BIND_WINDOW
  chars; far references (checklist/table mentions) must match some block in the
  same file.
- every ```text example block is <= 2000 chars (all core files)
- no approximate labels (`약 N자`)
- YAML frontmatter parses and carries version + model_claims_reviewed_at
- no Cyrillic/Greek lookalike letters
- canonical rules defined exactly once (gate necessity test, non-inferable slot list)
- package.json version matches SKILL.md frontmatter version
- runtime/model names stay out of core prompt files except image/video engine names
- Tier-2 frozen strings byte-identical 3-way: editorial-fashion.md §2 code blocks
  (SSOT) == compiler.md §2 inline copy == check_prompt.mjs TAIL/ANCHORS constants

Exit 0 on pass, 1 on any failure. No dependencies beyond PyYAML (optional:
falls back to a minimal frontmatter parse when PyYAML is missing).
"""
import json, re, sys, unicodedata, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILES = ["SKILL.md", "references/templates.md", "references/model-playbooks.md", "references/adapters.md",
         "references/image/compiler.md", "references/image/categories.md",
         "references/image/editorial-fashion.md", "references/image/look-and-concept.md",
         "references/image/typography.md", "references/image/production.md",
         "references/image/realism.md"]
SSOT = "references/image/editorial-fashion.md"   # Tier-2 동결 문자열 정본 (§2 코드블록)
COMPILER = "references/image/compiler.md"
VALIDATOR = ROOT / "scripts" / "check_prompt.mjs"
# 라벨 3+1포맷: "N자 실측"(괄호형 포함) / "실측: N자" / bare "(…, N자)" — "블록당 N자"(규칙 문구)와
# "제3자" 같은 비라벨은 제외. bare 포맷은 실길이 라벨만 대상(N >= 50).
LABEL_PATTERNS = [r"(?<!블록당 )(?<!\d)(\d+)자 실측", r"실측:\s*(\d+)자", r"(?<!제)(?<!\d)(\d+)자\)"]
BARE_PATTERN_MIN = 50
BIND_WINDOW = 200  # 라벨-코드블록 펜스 간 인접 판정 거리(문자)


def fail(msgs):
    for m in msgs: print("FAIL", m)
    sys.exit(1)


def measured_len(body):
    """트림된 본문 코드포인트 수 — check_prompt.mjs의 trim() 후 .length와 등가."""
    return len(body.strip())


def grapheme_unsafe(body):
    return any(unicodedata.combining(c) or c == "\u200d" for c in body)


def line_of(s, pos):
    return s.count("\n", 0, pos) + 1


def check_labels(f, s, errors):
    blocks = [(m.start(), m.end(), m.group(1)) for m in re.finditer(r"```text\n(.*?)```", s, re.S)]
    lengths = {measured_len(b) for _, _, b in blocks}
    seen = set()
    for pi, pat in enumerate(LABEL_PATTERNS):
        for lm in re.finditer(pat, s):
            span = lm.span(1)
            if span in seen:
                continue
            seen.add(span)
            n = int(lm.group(1))
            if pi == 2 and n < BARE_PATTERN_MIN:
                continue
            fwd = next(((b[0] - lm.end(), b) for b in blocks if b[0] >= lm.end()), None)
            back = None
            for b in blocks:
                if b[1] <= lm.start():
                    back = (lm.start() - b[1], b)
            cands = [c for c in (fwd, back) if c is not None and c[0] <= BIND_WINDOW]
            ln = line_of(s, lm.start())
            if cands:
                body = min(cands, key=lambda c: c[0])[1][2]
                if grapheme_unsafe(body):
                    errors.append(f"{f}:{ln}: text block has combining marks/ZWJ — grapheme 재측정 필요")
                actual = measured_len(body)
                if actual != n:
                    errors.append(f"{f}:{ln}: label {n}자 != 실측 {actual}자 (인접 text 블록)")
            elif n not in lengths:
                errors.append(f"{f}:{ln}: label {n}자 — 인접 블록 없음 + 파일 내 어떤 text 블록과도 불일치")


def check_frozen_strings(texts, errors):
    """Tier-2 동결 문자열 3자 byte 대조: SSOT(editorial-fashion §2) / compiler.md 인라인 / check_prompt.mjs."""
    ssot = texts.get(SSOT, "")
    comp = texts.get(COMPILER, "")

    def ssot_block(header):
        m = re.search(re.escape(header) + r".*?```text\n(.*?)```", ssot, re.S)
        return m.group(1).strip() if m else None

    a = ssot_block("**SAFETY_ASSERT")
    t = ssot_block("**NEGATIVE_TAIL")
    if a is None or t is None:
        errors.append(f"{SSOT}: §2 SAFETY_ASSERT/NEGATIVE_TAIL SSOT 코드블록을 찾지 못함")
        return
    ca = re.search(r"SAFETY_ASSERT: `([^`]+)`", comp)
    ct = re.search(r"NEGATIVE_TAIL: `([^`]+)`", comp)
    if not ca or not ct:
        errors.append(f"{COMPILER}: §2 인라인 SAFETY_ASSERT/NEGATIVE_TAIL 복사본을 찾지 못함")
    else:
        if ca.group(1).encode("utf-8") != a.encode("utf-8"):
            errors.append(f"{COMPILER}: SAFETY_ASSERT 인라인 복사본이 SSOT({SSOT} §2)와 byte 불일치")
        if ct.group(1).encode("utf-8") != t.encode("utf-8"):
            errors.append(f"{COMPILER}: NEGATIVE_TAIL 인라인 복사본이 SSOT({SSOT} §2)와 byte 불일치")
    try:
        mjs = VALIDATOR.read_text(encoding="utf-8")
    except OSError:
        errors.append("scripts/check_prompt.mjs missing — 동결 문자열 대조 불가")
        return
    mt = re.search(r"const TAIL = \[(.*?)\];", mjs)
    if not mt:
        errors.append("check_prompt.mjs: TAIL 상수를 찾지 못함")
    elif ", ".join(re.findall(r'"([^"]*)"', mt.group(1))).encode("utf-8") != t.encode("utf-8"):
        errors.append("check_prompt.mjs: TAIL 상수가 SSOT NEGATIVE_TAIL과 byte 불일치")
    ma = re.search(r"const ANCHORS = \[(.*?)\];", mjs)
    if not ma:
        errors.append("check_prompt.mjs: ANCHORS 상수를 찾지 못함")
    else:
        for pat in re.findall(r"/((?:[^/\\]|\\.)*)/", ma.group(1)):
            lit = pat.replace("\\+", "+")
            m2 = re.match(r"^(.*)\(\?\:([^)]*)\)(.*)$", lit)
            variants = [m2.group(1) + alt + m2.group(3) for alt in m2.group(2).split("|")] if m2 else [lit]
            if not any(v.lower() in a.lower() for v in variants):
                errors.append(f"check_prompt.mjs: ANCHORS 패턴 /{pat}/ 이 SSOT SAFETY_ASSERT에 없음")


def main():
    errors = []
    missing = [f for f in FILES if not (ROOT / f).exists()]
    if missing:
        fail([f"missing file: {m}" for m in missing])
    texts = {f: (ROOT / f).read_text(encoding="utf-8") for f in FILES}

    # frontmatter
    skill = texts["SKILL.md"]
    m = re.match(r"---\n(.*?)\n---\n", skill, re.S)
    if not m:
        errors.append("SKILL.md: no frontmatter")
    else:
        fm = m.group(1)
        skill_version = None
        try:
            import yaml
            d = yaml.safe_load(fm)
            skill_version = d.get("version")
            if not skill_version: errors.append("frontmatter: version missing")
            if not d.get("metadata", {}).get("model_claims_reviewed_at"):
                errors.append("frontmatter: model_claims_reviewed_at missing")
        except ImportError:
            vm = re.search(r"^version:\s*([^\n]+)", fm, re.M)
            skill_version = vm.group(1).strip().strip('"') if vm else None
            if not skill_version: errors.append("frontmatter: version missing")
            if "model_claims_reviewed_at" not in fm: errors.append("frontmatter: model_claims_reviewed_at missing")

        try:
            pkg_version = json.loads((ROOT / "package.json").read_text(encoding="utf-8")).get("version")
            if skill_version and pkg_version != skill_version:
                errors.append(f"version mismatch: package.json {pkg_version} != SKILL.md {skill_version}")
        except Exception as e:
            errors.append(f"package.json version check failed: {e}")

    tm = texts.get("references/templates.md", "")

    # label == adjacent block length (전 FILES)
    for f, s in texts.items():
        check_labels(f, s, errors)

    # all example blocks under 2000 (전 FILES)
    for f, s in texts.items():
        for i, b in enumerate(re.findall(r"```text\n(.*?)```", s, re.S)):
            if len(b) > 2000:
                errors.append(f"{f}: text block #{i} is {len(b)} chars (> 2000)")

    # no approximate labels
    for f, s in texts.items():
        if re.search(r"약 [\d,]+자", s):
            errors.append(f"{f}: approximate length label found")

    # lookalike scan
    for f, s in texts.items():
        bad = sorted({c for c in s if unicodedata.category(c).startswith("L")
                      and ("CYRILLIC" in unicodedata.name(c, "") or "GREEK" in unicodedata.name(c, ""))})
        if bad:
            errors.append(f"{f}: lookalike letters {bad}")

    # canonical single definitions
    if skill.count("게이트 필요성 테스트** —") != 1:
        errors.append("gate necessity test must be defined exactly once in SKILL.md")
    if tm.count("질문이 정당한 유일 목록 (정본)") != 1:
        errors.append("non-inferable slot canon must appear exactly once in templates.md")

    core_runtime_names = {
        "SKILL.md": [r"\bClaude\b", r"\bCodex\b", r"\bHermes\b", r"\bGJC\b", r"\bSol\b", r"\bTerra\b", r"\bLuna\b", r"\bOpus\b", r"\bSonnet\b"],
        "references/templates.md": [r"\bClaude\b", r"\bCodex\b", r"\bHermes\b", r"\bGJC\b", r"\bSol\b", r"\bTerra\b", r"\bLuna\b", r"\bOpus\b", r"\bSonnet\b"],
        "references/model-playbooks.md": [r"\bClaude\b", r"\bCodex\b", r"\bHermes\b", r"\bGJC\b", r"\bSol\b", r"\bTerra\b", r"\bLuna\b", r"\bOpus\b", r"\bSonnet\b"],
    }
    for f, pats in core_runtime_names.items():
        scan_text = texts[f]
        if f == "references/model-playbooks.md":
            scan_text = scan_text.split("\n## 호환 노트", 1)[0]
        for pat in pats:
            m = re.search(pat, scan_text)
            if m:
                errors.append(f"{f}:{line_of(scan_text, m.start())}: runtime/model name belongs in references/adapters.md or dated compatibility notes, not core ({m.group(0)})")

    # Tier-2 동결 문자열 3자 byte 대조
    check_frozen_strings(texts, errors)

    if errors: fail(errors)
    total_labels = sum(len(re.findall(p, s)) for p in LABEL_PATTERNS[:2] for s in texts.values())
    print(f"OK — {len(texts)} files, {total_labels} measured labels, all checks passed")


if __name__ == "__main__":
    main()

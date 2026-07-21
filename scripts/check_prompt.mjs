#!/usr/bin/env node
// MPW 이미지 프롬프트 검증기 (gpt-image-2 레인) — SPEC-FREEZE-v2 동결 스펙 준수. zero-dependency Node ESM.
// 사용: node check_prompt.mjs <file> (stdin 파이프 가능) | --jsonl <file> | --tier <0|1|2> | --api | --test
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const SIZE_WHITELIST = ["1024x1024","1536x1024","1024x1536","1792x1024","1024x1792","2048x2048"];
const AR_SIZE_MAP = { "1:1":["1024x1024","2048x2048"], "2:3":["1024x1536"], "3:4":["1024x1536"],
  "4:5":["1024x1536"], "3:2":["1536x1024"], "4:3":["1536x1024"], "16:9":["1792x1024"], "9:16":["1024x1792"] };
const HARD = { maxEdge:3840, multiple:16, maxRatio:3, minPx:655360, maxPx:8294400 };
const TIER1 = ["verbatim, no extra characters","no duplicate text","no invented glyphs","no extra words","no extra text","no watermark","no logo"];
const TAIL = ["no nudity","no nipple or genital exposure","no wardrobe malfunction","no extra people","no text","no watermark"];
// 동결 스펙 — lint.py 3자 byte 대조용 synchronized copy.
const SAFETY_ASSERT = "adult Korean woman in her late 20s, 25+, original character, non-nude fashion editorial styling, fully opaque fabric, covered chest line, editorial upright pose";
const TAIL_ONLY = TAIL.slice(0, 4); // Tier-2 전용 항목 — 이게 있어야 tail로 간주
const ANCHORS = [/25\+/, /original character/i, /fully opaque/i, /covered (?:chest|bust)/i, /editorial upright/i];
const REWRITE_MAP = {
  "no people": "빈 배경, 인물 없는 구성", "no text": "텍스트 없음(한국어 긍정형)", "no watermark": "브랜드 없는 클린 마감",
  "no logo": "로고 없는 클린 마감", "no background": "단색 스튜디오 배경", "no blur": "엣지까지 또렷한 포커스",
  "no shadow": "균등광의 평면 조명", "without": "뺄 요소 대신 원하는 요소만 서술", "avoid": "피할 상태 대신 원하는 상태를 서술",
};
// 에디토리얼 뷰티 마감 불변식 (2026-07 컨셉-콜리전 그래머 §15 반영)
const GLOW_TOKENS = [/\bdewy\b/i, /\bluminous skin\b/i, /subsurface (?:glow|sheen|scatter)/i, /\bglass skin\b/i, /\bwet[- ]?look\b/i, /\bhigh[- ]?shine\b/i, /\bglistening skin\b/i];
const MATTE_QUALIFIER = /(matte|무광|매트|비유광|semi[- ]?matte|restrained sheen)/i;
const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const err = (list, code, msg, hint) => list.push(hint ? { code, msg, hint } : { code, msg });
const quotesOf = (p) => [...p.matchAll(/"([^"\n]+)"|“([^”\n]+)”/g)].map((m) => (m[1] ?? m[2]).replace(/\s+/g, " ").trim());

function localFailureTokens() { // editorial-hwabo.local.md의 FAILURE_TOKENS: 라인 — 없으면 조용히 무시
  try {
    const md = readFileSync(resolve(SCRIPT_DIR, "../references/editorial-hwabo.local.md"), "utf8");
    const line = md.split(/\r?\n/).find((l) => l.startsWith("FAILURE_TOKENS:"));
    return line ? line.slice(15).split(",").map((s) => s.trim()).filter(Boolean) : [];
  } catch { return []; }
}

function detectFormat(p) {
  const labels = p.match(/(?:^|\n)\s*(?:#+\s*\d*\.?\s*)?(?:Scene|Camera|Lighting|Color grading|Texture\/Medium|Text-in-image)\s*[:\n]/g);
  if (labels && labels.length >= 3) return "A";
  const hex = (p.match(/#[0-9A-Fa-f]{6}/g) || []).length;
  if ((/팔레트/.test(p) || hex >= 3) && /AR\s+\d+\s*:\s*\d+$/i.test(p)) return "B";
  return "A";
}

function checkNegatives(p, tier, renderText, errors) {
  if (/\bNegative\s*:/i.test(p)) err(errors, "E-NEG-SECTION", "`Negative:` 섹션 금지 — 전부 긍정형 서술로.");
  let scan = p.replace(/negative\s+space/gi, ""); // 디자인 여백 용어는 허용
  const alt = TAIL.map(esc).join("|");
  const runs = [...scan.matchAll(new RegExp(`(?:${alt})(?:\\s*,\\s*(?:${alt}))*`, "gi"))].map((m) => ({ str: m[0], idx: m.index }));
  const t2 = runs.filter((r) => TAIL_ONLY.some((it) => r.str.toLowerCase().includes(it)));
  if (t2.length) {
    if (tier !== 2) err(errors, "E-NEG-TIER", "티어 미선언 상태에서 Tier-2 NEGATIVE_TAIL 사용 — `--tier 2`(또는 jsonl tier/lane) 명시 선언 시에만 허용, 추론 승격 금지.");
    else {
      if (t2.length > 1) err(errors, "E-TIER2-DUP", "NEGATIVE_TAIL이 2회 이상 — 정확히 1회만.");
      const r = t2[t2.length - 1];
      let last = -1;
      for (const it of r.str.split(/\s*,\s*/).map((s) => s.toLowerCase().trim())) {
        const i = TAIL.indexOf(it);
        if (i <= last) { err(errors, "E-TIER2-EXTRA", "tail은 캐노니컬 고정 순서의 부분집합만 허용 — 항목 추가·중복·순서 변경 금지."); break; }
        last = i;
      }
      const after = scan.slice(r.idx + r.str.length);
      if (/^\s*,\s*no\s+[A-Za-z]/i.test(after)) err(errors, "E-TIER2-EXTRA", "캐노니컬 외 항목이 tail에 추가됨 — 항목 삭제만 허용.");
      else if (!/^[\s.,]*AR\s+\d+\s*:\s*\d+\s*$/i.test(after)) err(errors, "E-TIER2-POS", "NEGATIVE_TAIL은 트레일링 `AR x:y` 직전 마지막 절이어야 함.");
      if (ANCHORS.filter((a) => a.test(p)).length < 3)
        err(errors, "E-TIER2-PAIR", "tail 단독 금지 — SAFETY_ASSERT 앵커(25+/original character/fully opaque/covered chest/editorial upright) 3개 이상과 페어.");
    }
    for (const r of t2) scan = scan.replace(r.str, " ");
  }
  const t1 = TIER1.filter((ph) => scan.toLowerCase().includes(ph));
  if (t1.length) {
    if (tier < 1) err(errors, "E-NEG-TIER", `티어 0에서 Tier-1 화이트리스트 문구 사용(${t1.join("; ")}) — --tier 1 선언 필요.`);
    else if (!renderText) err(errors, "E-NEG-TIER", "렌더 텍스트(따옴표 카피)가 없는데 Tier-1 문구 사용 — 렌더 텍스트가 실제로 있을 때만 유효.");
    for (const ph of t1) scan = scan.replace(new RegExp(esc(ph), "gi"), " ");
  }
  const neg = scan.match(/\b(?:no|without|avoid|exclude|never|free of|devoid of|do not|don't)\s+[A-Za-z][A-Za-z'-]*(?:\s+[A-Za-z'-]+)?/gi);
  if (neg) {
    const uniq = [...new Set(neg.map((s) => s.toLowerCase().trim()))].slice(0, 5);
    const w = uniq[0].split(/\s+/);
    const to = REWRITE_MAP[w.slice(0, 2).join(" ")] || REWRITE_MAP[w[0]] || "빼려는 요소 대신 원하는 결과 상태를 구체 명사로 서술";
    err(errors, "E-NEG-001", `화이트리스트 밖 영어 부정문 금지(${uniq.join(", ")}…) — 전부 긍정형으로.`, `긍정형 재작성 제안: "${uniq[0]}" → ${to}`);
  }
}


function checkEditorialFinish(p, errors, warnings) {
  if (/\b(?:micro[\s-]?skin texture|skin texture\s+ai|realistic skin\s+ai)\b/i.test(p))
    err(errors, "E-SKIN-AI", "malformed 피부 토큰(micro·AI) — `natural skin texture, visible pores, fine vellus hair`처럼 관찰 결과로.");
  if (/\byellow(?:ish)?\s+(?:undertone\s+)?skin\b/i.test(p) || /(?:노란|누런|황색)\s*피부/.test(p))
    err(errors, "E-NAT-SKIN", "국적-피부 고정 톤(yellow skin 류) — 피부색은 국적이 아니라 관찰(hydrated base, flushed cheeks)로 쓴다.");
  const glow = GLOW_TOKENS.filter((re) => re.test(p)).length;
  if (glow >= 4 && !MATTE_QUALIFIER.test(p))
    err(warnings, "W-GLOW-STACK", `피부 글로우 토큰 ${glow}종 적층 + 매트존 부재 — 주 글로우 1개 + 전략적 매트존으로 (§15.4).`);
}
function validateText(raw, opts = {}, rec = null) {
  const errors = [], warnings = [];
  const p = raw.replace(/^﻿/, "").trim();
  const codePoints = [...p].length;
  if (codePoints > 2000) err(errors, "E-OVERFLOW-2000", `프롬프트 코드포인트 수 ${codePoints}자 — 블록당 2000자를 초과함.`);
  const has = (re) => re.test(p);
  const format = rec && (rec.format === "A" || rec.format === "B") ? rec.format : detectFormat(p);
  const quotes = quotesOf(p);
  const renderText = quotes.length > 0 || /Text-in-image\s*:/.test(p) || !!(rec && rec.korean_copy);
  const tier = [0, 1, 2].includes(opts.tier) ? opts.tier // Tier-2는 명시 선언만 — 휴리스틱 승격 불가
    : rec && [0, 1, 2].includes(rec.tier) ? rec.tier
    : rec && rec.lane === "editorial" ? 2 : renderText ? 1 : 0;

  if (!/AR\s+\d+\s*:\s*\d+$/i.test(p)) err(errors, "E-AR-END", "끝에 `AR 3:4` 형태의 종횡비 토큰이 없음(반드시 프롬프트 맨 끝).");
  const hexCount = (p.match(/#[0-9A-Fa-f]{6}/g) || []).length;
  if (format === "A") { // v1 4대 섹션-언어 체크 유지
    if (p.length < 220) err(warnings, "W-SHORT-A", "프롬프트가 짧음 — 프로덕션 프롬프트는 구체 시각 명세가 더 필요.");
    if (!has(/(Scene\s*[:\n]|# ?\d*\.? ?Scene|한국|포스터|카드뉴스|도감|목업|아이콘|웹툰|만화|제품|패션|뷰티|인포그래픽)/)) err(errors, "E-CAT-LANG", "첫 절에 매체/카테고리(결과물 장르)가 드러나지 않음.");
    if (!has(/(Camera\s*[:\n]|# ?\d*\.? ?Camera|정면|톱다운|아이레벨|eye-level|로우앵글|클로즈업|와이드|중앙|레이아웃|컷|거터|읽힘)/)) err(errors, "E-CAM-LANG", "카메라·구도·레이아웃 언어가 없음.");
    if (!has(/(Lighting\s*[:\n]|# ?\d*\.? ?Lighting|조명|키라이트|소프트박스|자연광|림라이트|그림자|컨택트 섀도|반사|flash|key light|fill|shadow|glow|ambient|tungsten)/i)) err(errors, "E-LIGHT-LANG", "명시적 조명 지시가 없음.");
    if (!has(/(Texture(\/Medium)?\s*[:\n]|# ?\d*\.? ?Texture|재질|질감|광택|종이|실크|리넨|유리|포일|베벨|셀 쉐이딩|스크린톤|수채|잉킹|grain|matte|glossy|finish)/i)) err(errors, "E-TEX-LANG", "재질·질감·매체 디테일이 없음.");
  } else { // Format B — 콘텐츠 토큰 체크로 대체
    if (!has(/(조명|키라이트|소프트박스|자연광|필라이트|림라이트|역광|그림자|광원|채광|정면광|측광|lighting|rim light|backlight|flash|key light|directional key|fill light|natural light|shadow|glow|specular|ambient light)/i)) err(errors, "E-LIGHT-LANG", "Format B 콘텐츠 토큰: 조명 어휘가 없음.");
    if (!has(/(재질|질감|텍스처|그레인|광택|매트|마감|texture|grain|finish)/i)) err(errors, "E-TEX-LANG", "Format B 콘텐츠 토큰: 질감 어휘가 없음.");
    if (hexCount < 3 || hexCount > 5) err(errors, "E-FMT-B-HEX", `Format B는 팔레트 HEX 3~5개 필수(현재 ${hexCount}개).`);
    if (p.length < 300 || p.length > 550) err(warnings, "W-LEN-B", `Format B 길이 ${p.length}자 — 300~550자 밴드 밖(타깃 350~450).`);
  }
  if (hexCount === 0) err(warnings, "W-HEX-MISS", "HEX 팔레트 없음 — 장면 팔레트와 일치하는 HEX가 최종 3~5개가 되도록 추가.");

  // ── 텍스트 프로토콜 ──
  if ((/Text-in-image\s*:/.test(p) || !!(rec && rec.korean_copy)) && quotes.length === 0)
    err(errors, "E-TEXT-QUOTE", "Text-in-image/korean_copy가 있는데 따옴표 카피가 0개 — 렌더 카피는 따옴표로 고정.");
  const dup = [...new Set(quotes.filter((q, i) => quotes.indexOf(q) !== i))];
  if (dup.length) err(errors, "E-TEXT-DUP", `동일 따옴표 카피 2회 이상(${dup.join(" / ")}) — 모든 카피는 한 번씩만.`);
  if (quotes.length >= 2 && !has(/(상단|하단|중앙|좌측|우측|타이틀|부제|서브|라벨|캡션|헤드|말풍선|SFX|headline|subhead|callout|billing|caption|centered|upper|lower)/i)) err(warnings, "W-TEXT-ROLE", "따옴표 카피 2개 이상인데 롤 라벨(타이틀/부제/위치)이 없음.");
  const mix = quotes.find((q) => /[가-힣]/.test(q) && /[A-Za-z]/.test(q));
  if (mix) err(warnings, "W-TEXT-MIXLANG", `한 따옴표 문자열 안 KO+EN 혼합: "${mix}" — 언어별로 분리.`);
  if ((renderText || has(/(텍스트|한글|타이틀|부제|라벨|말풍선|내레이션|SFX|카피|문구)/)) && !has(/(또렷|가독|한 번씩만|1~2개만|legible|appears once)/))
    err(warnings, "W-TEXT-GUARD", "텍스트가 있는데 가독성/반복 가드가 없음 (예: \"모든 텍스트는 한 번씩만, 또렷하게\").");

  checkNegatives(p, tier, renderText, errors);
  checkEditorialFinish(p, errors, warnings);

  // ── 앞브래킷 / 슬롯 잔존 / SD 폐기 문법 (v1 유지) ──
  if (/^\[[^\]\n]*(\d+\s*:\s*\d+|SIZE|size)[^\]\n]*\]/.test(p.slice(0, 80))) err(errors, "E-HEAD-BRACKET", "앞머리 `[AR x:y SIZE wxh]` 브래킷 금지 — size는 API 파라미터, 프롬프트엔 끝의 `AR x:y`만.");
  const slots = p.match(/\[[A-Z_]{3,}\]/g); // ASCII 대문자 전용 — 한글 브래킷 라벨은 비대상
  if (slots) err(errors, "E-SLOT-LEAK", `슬롯 토큰 잔존: ${[...new Set(slots)].join(", ")} — 최종 프롬프트에는 치환 완료된 값만.`);
  const banned = p.match(/\b(masterpiece|best[ _]quality|(?:4|8)k|uhd|trending on artstation|ultra[- ]?detailed|hyper[- ]?detailed|highly detailed|intricate details?|sharp focus|award[- ]winning|raw photo)\b/gi);
  if (banned) err(errors, "E-SD-VOCAB", `SD 품질태그 폐기 어휘: ${[...new Set(banned.map((s) => s.toLowerCase()))].join(", ")}.`);
  if (has(/\([^()]*:\s*[01]?\.\d+\s*\)/)) err(errors, "E-WEIGHT", "가중치 문법 `(word:1.3)` 금지.");
  if (has(/--(ar|v|no|style|niji)\b/)) err(errors, "E-MJ-FLAG", "Midjourney식 슬래시 플래그(`--ar/--v/--no`) 금지.");
  if (has(/(^|\n)\s*§|§\s*\d/)) err(warnings, "W-SECTION-MARK", "본문에 `§` 기호 사용 — 헤더 `# 1.` 형식만 허용.");
  const filler = p.match(/(어워드 수준|전문가처럼|(?:멋지게|감성적으로|고급스럽게|예쁘게|세련되게|감도있게|world-class|beautifully|stunning|atmospheric|perfect|professional)(?![\p{L}\p{N}_]))/giu);
  if (filler) err(warnings, "W-FILLER", `빈 형용사(구체 명세로 대체): ${[...new Set(filler.map((s) => s.toLowerCase()))].join(", ")}.`);

  if (tier === 2) { // 화보 실패 토큰
    const toks = [];
    if (/cleavage-forward/i.test(p)) toks.push("cleavage-forward");
    if ((p.match(/plung(?:ing|e)/gi) || []).length >= 2) toks.push("plunging×2+");
    if (/bustier/i.test(p) && /photoreal/i.test(p)) toks.push("bustier+photoreal");
    for (const t of localFailureTokens()) if (p.toLowerCase().includes(t.toLowerCase())) toks.push(t);
    if (toks.length) err(warnings, "W-HWABO-TOKEN", `화보 실패 토큰 감지: ${[...new Set(toks)].join(", ")} — 단정한 스타일링 어휘로 교체.`);
  }
  return { ok: errors.length === 0, format, tier, errors, warnings };
}

function checkHardConstraints(size, errors) {
  const m = /^(\d+)x(\d+)$/.exec(size);
  if (!m) return;
  const w = +m[1], h = +m[2], px = w * h;
  if (Math.max(w, h) > HARD.maxEdge) err(errors, "E-SIZE-EDGE", `최대 변 ${HARD.maxEdge}px 초과: ${size}.`);
  if (w % HARD.multiple || h % HARD.multiple) err(errors, "E-SIZE-MULT", `가로·세로는 ${HARD.multiple}의 배수여야 함: ${size}.`);
  if (Math.max(w, h) / Math.min(w, h) > HARD.maxRatio) err(errors, "E-SIZE-RATIO", `종횡비 ${HARD.maxRatio}:1 초과: ${size}.`);
  if (px < HARD.minPx || px > HARD.maxPx) err(errors, "E-SIZE-PIXELS", `총 픽셀 ${HARD.minPx.toLocaleString()}~${HARD.maxPx.toLocaleString()} 밖: ${px.toLocaleString()}.`);
}

function nearestSize(size) {
  const m = /^(\d+)x(\d+)$/.exec(size);
  if (!m) return SIZE_WHITELIST[0];
  const w = +m[1], h = +m[2];
  const d = (s) => { const [W, H] = s.split("x").map(Number); return Math.abs(W - w) + Math.abs(H - h) + Math.abs(W / H - w / h) * 512; };
  return [...SIZE_WHITELIST].sort((a, b) => d(a) - d(b))[0];
}
function validatePromo(rec, errors) {
  const isPromo = rec.cut_type === "promo_poster" || rec.promo_pattern !== undefined;
  if (!isPromo) return;

  const prompt = typeof rec.full_prompt === "string" ? rec.full_prompt : "";
  const scene = prompt.split(/\bCamera\s*:/i)[0];
  const patternEffects = new Map([
    ["P1", "mask"], ["P2", "extrusion"], ["P3", "occlusion"],
    ["P4", "interlock"], ["P5", "printed_meta_ui"], ["P6", "occlusion"],
    ["P7", "rotated_axis"], ["P8", "staging"],
  ]);
  if (!new Set(["C3", "C5"]).has(rec.category))
    err(errors, "E-PROMO-ROUTE", "디자인 promo_poster는 C3/C5 + P 패턴으로만 라우팅할 수 있음.");
  if (!patternEffects.has(rec.promo_pattern))
    err(errors, "E-PROMO-PATTERN", "promo_poster는 promo_pattern P1~P8 중 정확히 1개가 필요.");
  if (!/^L[1-8]$/.test(rec.look_preset ?? ""))
    err(errors, "E-PROMO-LOOK", "promo_poster는 구현된 look_preset L1~L8 중 정확히 1개가 필요.");
  if (patternEffects.has(rec.promo_pattern) && rec.promo_text_effect !== patternEffects.get(rec.promo_pattern))
    err(errors, "E-PROMO-EFFECT", `${rec.promo_pattern}의 promo_text_effect는 ${patternEffects.get(rec.promo_pattern)}여야 함.`);
  if (typeof rec.promo_subject !== "string" || !rec.promo_subject.trim() || !scene.includes(rec.promo_subject.trim()))
    err(errors, "E-PROMO-SUBJECT", "promo_subject는 비어 있지 않고 Scene에 그대로 등장해야 함.");

  const authority = rec.palette_authority;
  const sources = rec.palette_sources;
  if (!["P", "L"].includes(authority) || !Array.isArray(sources) || sources.length !== 1 || sources[0] !== authority)
    err(errors, "E-PROMO-PALETTE-CONFLICT", "promo 팔레트 권한은 P 또는 L 하나이며 palette_sources도 같은 단일 소스여야 함.");

  const hexes = new Set(prompt.match(/#[0-9A-Fa-f]{6}\b/g) || []);
  if (hexes.size < 2 || hexes.size > 3)
    err(errors, "E-PROMO-COLOR-LOCK", `promo는 중복 제거한 HEX 2~3색 하드 락(현재 ${hexes.size}색).`);

  const physical = /(mask(?:ed|ing)?|마스킹|extrud(?:ed|ing)|압출|overlap(?:ping)?|오클루전|behind|뒤로|interlock(?:ing)?|break(?:ing)? (?:out|outside)|프레임 밖|rotat(?:ed|ing)|회전|printed (?:on|at)|인쇄된|emboss(?:ed|ing)|deboss(?:ed|ing)|지지 구조)/i;
  if (!physical.test(scene))
    err(errors, "E-PROMO-TYPE-STRUCTURE", "Scene에서 promo_subject와 마스크·압출·가림·회전·인쇄 구조가 함께 확인되지 않음.");

  const finishers = rec.finishing_devices;
  if (!Array.isArray(finishers) || finishers.length < 1 || finishers.length > 3 || finishers.some((value) => typeof value !== "string" || !value.trim()))
    err(errors, "E-PROMO-FINISH", "promo finishing_devices는 비어 있지 않은 문자열 1~3개여야 함.");

  const driftSignals = [
    /(3D|three-dimensional).{0,20}(clay|클레이)/i,
    /(?:3\s*[~–-]\s*5|three to five).{0,20}(props?|소품)/i,
    /(badge|배지|리본 밴드|스티커 칩|체크리스트 미니카드)/i,
  ];
  if (driftSignals.filter((token) => token.test(prompt)).length >= 2)
    err(errors, "E-PROMO-CARD-DRIFT", "promo가 C7의 3D 히어로·소품·배지 밀도 문법으로 후퇴함.");

  if (typeof rec.korean_copy === "string" && rec.korean_copy.trim()) {
    const copy = rec.korean_copy.replace(/\s+/g, " ").trim();
    const quotedCount = quotesOf(prompt).filter((quoted) => quoted === copy).length;
    const totalCount = prompt.split(copy).length - 1;
    if (quotedCount !== 1 || totalCount !== 1)
      err(errors, "E-PROMO-COPY", `promo korean_copy는 전체 prompt와 따옴표 안에 각각 정확히 1회여야 함(전체 ${totalCount}, 따옴표 ${quotedCount}).`);
    const syllables = [...copy].filter((char) => /[가-힣]/.test(char)).length;
    if (["mask", "extrusion"].includes(rec.promo_text_effect) && syllables > 2)
      err(errors, "E-PROMO-KO-MASK-LEN", `한글 마스킹·압출 안전권은 2음절(현재 ${syllables}음절).`);
  }

  if (rec.promo_pattern === "P5" && (!/(printed|인쇄)/i.test(prompt) || /(app screenshot|앱 스크린샷|실제 앱 화면)/i.test(prompt)))
    err(errors, "E-PROMO-METAUI", "P5는 실제 앱 스크린샷이 아니라 인쇄된 메타 UI 그래픽이어야 함.");
}

function validateTypographyPoster(rec, errors) {
  const isTp = typeof rec.tp_pattern === "string" || rec.cut_type === "typography_poster";
  if (!isTp) return;
  const patterns = new Set(Array.from({ length: 14 }, (_, i) => `TP${i + 1}`));
  if (!patterns.has(rec.tp_pattern)) err(errors, "E-TP-PATTERN", "typography_poster는 TP1~TP14 중 정확히 하나가 필요.");
  if (!["exact_primary", "repeated_texture"].includes(rec.legibility_target))
    err(errors, "E-TP-LEGIBILITY", "legibility_target은 exact_primary 또는 repeated_texture여야 함.");
  if (rec.legibility_target === "repeated_texture" && !["TP2", "TP14"].includes(rec.tp_pattern))
    err(errors, "E-TP-LEGIBILITY", "repeated_texture는 반복/미세 텍스트 패턴 TP2 또는 TP14에서만 허용.");
  if (!Array.isArray(rec.palette_sources) || rec.palette_sources.length !== 1 || rec.palette_sources[0] !== "TP")
    err(errors, "E-TP-PALETTE", "TP 팔레트 권한은 TP 단일 소스여야 함.");
  if (!Array.isArray(rec.palette) || rec.palette.length < 2 || rec.palette.length > 4)
    err(errors, "E-TP-PALETTE-RANGE", "TP 팔레트는 HEX 2~4개여야 함.");
  if (rec.material_graft !== undefined && (typeof rec.material_graft !== "string" || !/^TP7 surface material: \S(?:.*\S)?$/.test(rec.material_graft)))
    err(errors, "E-TP-GRAFT", "material_graft는 `TP7 surface material: <nonempty description>` 형식의 단일 TP7 표면 재질 이식 설명이어야 함.");
  else if (rec.material_graft !== undefined && !["TP2", "TP3"].includes(rec.tp_pattern))
    err(errors, "E-TP-GRAFT", "material_graft는 TP7 표면 재질을 TP2 또는 TP3에 이식할 때만 허용.");
  const prompt = typeof rec.full_prompt === "string" ? rec.full_prompt : "";
  if (rec.legibility_target === "exact_primary" && !/"[^"\n]*\S[^"\n]*"/.test(prompt))
    err(errors, "E-TP-EXACT-PRIMARY", "exact_primary는 full_prompt에 비어 있지 않은 큰따옴표 primary copy가 필요.");
  if (rec.legibility_target === "repeated_texture" && /no duplicate text/i.test(prompt))
    err(errors, "E-TP-DUP-GUARD", "repeated_texture TP2/TP14에는 no duplicate text를 쓰지 않음.");
  if (rec.legibility_target === "repeated_texture" && !/text-like texture|text-like micro|미세.*텍스처|반복.*텍스처/i.test(prompt))
    err(errors, "E-TP-TEXTURE", "repeated_texture는 반복부를 비판독 텍스처로 선언해야 함.");
  if (rec.legibility_target === "repeated_texture" && (!/no invented glyphs/i.test(prompt) || !/no watermark/i.test(prompt)))
    err(errors, "E-TP-REPEATED-GUARDS", "repeated_texture TP2/TP14에는 no invented glyphs와 no watermark 가드가 모두 필요.");
  if (rec.legibility_target === "exact_primary" && !/no duplicate text/i.test(prompt))
    err(errors, "E-TP-EXACT-GUARD", "exact_primary는 no duplicate text 가드가 필요.");
}

function validateRecord(rec, ids, opts) {
  const errors = [], warnings = [];
  for (const f of ["id", "category", "ar", "size", "quality", "full_prompt", "output_path"])
    if (rec[f] === undefined || rec[f] === null || rec[f] === "") err(errors, "E-REC-FIELD", `필수 필드 누락: ${f}.`);
  if (rec.id !== undefined) { if (ids.has(rec.id)) err(errors, "E-REC-DUPID", `중복 id: ${rec.id}.`); ids.add(rec.id); }
  if (rec.quality === "auto") err(errors, "E-REC-QUALITY", 'quality "auto" 금지 — high/medium/low를 명시.');
  if (typeof rec.size === "string") {
    if (!SIZE_WHITELIST.includes(rec.size)) {
      const msg = `size ${rec.size}는 6종 화이트리스트 밖.`, hint = `가장 가까운 허용 size: ${nearestSize(rec.size)}`;
      if (opts.api) err(warnings, "E-SIZE-LOCK", `${msg} ${hint} (--api: warning 강등)`);
      else err(errors, "E-SIZE-LOCK", msg, hint);
    }
    checkHardConstraints(rec.size, errors); // 하드 제약은 --api에서도 유지
  }
  if (rec.ar && rec.size && AR_SIZE_MAP[rec.ar] && !AR_SIZE_MAP[rec.ar].includes(rec.size))
    err(errors, "E-SIZE-AR", `ar ${rec.ar} ↔ size ${rec.size} 매핑 불일치(허용: ${AR_SIZE_MAP[rec.ar].join(", ")}).`);
  validatePromo(rec, errors);
  validateTypographyPoster(rec, errors);
  let t = { format: rec.format ?? null, tier: rec.tier ?? null };
  if (typeof rec.full_prompt === "string") {
    const m = rec.full_prompt.trim().match(/AR\s+(\d+)\s*:\s*(\d+)$/i);
    if (m && rec.ar && `${m[1]}:${m[2]}` !== rec.ar) err(errors, "E-REC-ARMATCH", `프롬프트 끝 AR ${m[1]}:${m[2]} ≠ record.ar ${rec.ar}.`);
    if (Array.isArray(rec.palette) && rec.palette.some((c) => !rec.full_prompt.includes(c)))
      err(warnings, "W-PALETTE-MISS", "record palette가 full_prompt에 반영되지 않음.");
    if ((rec.korean_copy || /Text-in-image\s*:|["“]/.test(rec.full_prompt)) && rec.quality !== "high")
      err(warnings, "W-TEXT-QUALITY", '텍스트 heavy record는 quality "high" 권장.');
    t = validateText(rec.full_prompt, opts, rec);
    errors.push(...t.errors); warnings.push(...t.warnings);
  }
  return { id: rec.id ?? null, ok: errors.length === 0, format: t.format, tier: t.tier, errors, warnings };
}

function runJsonl(content, opts) {
  const results = [], ids = new Set();
  content.split(/\r?\n/).forEach((line, i) => {
    if (!line.trim()) return;
    let rec;
    try { rec = JSON.parse(line); } catch (e) {
      results.push({ line: i + 1, id: null, ok: false, errors: [{ code: "E-REC-JSON", msg: `line ${i + 1} JSON 파싱 실패: ${e.message}` }], warnings: [] });
      return; // 파싱 실패해도 다음 라인 계속
    }
    results.push({ line: i + 1, ...validateRecord(rec, ids, opts) });
  });
  const pass = results.filter((r) => r.ok).length;
  return { ok: pass === results.length, results, summary: { total: results.length, pass, fail: results.length - pass } };
}

function parseFlags(flags) {
  const o = { api: false, tier: undefined };
  for (let i = 0; i < flags.length; i++) { if (flags[i] === "--api") o.api = true; else if (flags[i] === "--tier") o.tier = Number(flags[++i]); }
  return o;
}

function runTest() { // fixtures/manifest.json 셀프테스트 — 경로는 스크립트 기준(import.meta.url)
  const entries = JSON.parse(readFileSync(resolve(SCRIPT_DIR, "fixtures/manifest.json"), "utf8"));
  let fails = 0;
  const rows = entries.map((e) => {
    const opts = parseFlags(e.flags || []);
    const content = readFileSync(resolve(SCRIPT_DIR, e.path), "utf8");
    const res = e.mode === "jsonl" ? runJsonl(content, opts) : validateText(content, opts);
    const codes = e.mode === "jsonl" ? res.results.flatMap((r) => r.errors.map((x) => x.code)) : res.errors.map((x) => x.code);
    const missing = (e.expect.codes || []).filter((c) => !codes.includes(c)); // expect.codes ⊆ 실코드
    const pass = res.ok === e.expect.ok && missing.length === 0;
    if (!pass) fails++;
    return [pass ? "PASS" : "FAIL", e.path, e.mode, pass ? "" : `ok=${res.ok}(기대 ${e.expect.ok})${missing.length ? ` 누락코드:${missing.join(",")}` : ""} 실코드:${[...new Set(codes)].join(",") || "-"}`];
  });
  const wp = Math.max(...rows.map((r) => r[1].length), 4);
  console.log(`RESULT  ${"PATH".padEnd(wp)}  MODE   DETAIL`);
  for (const r of rows) console.log(`${r[0].padEnd(6)}  ${r[1].padEnd(wp)}  ${r[2].padEnd(5)}  ${r[3]}`);
  console.log(`\n${rows.length - fails}/${rows.length} fixtures green`);
  process.exit(fails ? 1 : 0);
}

// ── CLI ──
const argv = process.argv.slice(2);
const opts = { api: false, tier: undefined };
let file = null, jsonlPath = null, test = false;
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === "--api") opts.api = true;
  else if (a === "--test") test = true;
  else if (a === "--tier") opts.tier = Number(argv[++i]);
  else if (a === "--jsonl") jsonlPath = argv[++i];
  else file = a;
}
if (test) runTest();
else {
  let out;
  try {
    out = jsonlPath ? runJsonl(readFileSync(jsonlPath, "utf8"), opts) : validateText(readFileSync(file ?? 0, "utf8"), opts);
  } catch (e) {
    console.log(JSON.stringify({ ok: false, errors: [{ code: "E-INPUT", msg: `입력을 읽지 못함: ${e.message}` }], warnings: [] }, null, 2));
    process.exit(1);
  }
  console.log(JSON.stringify(out, null, 2));
  process.exitCode = out.ok ? 0 : 1;
}

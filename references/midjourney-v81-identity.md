# Midjourney v8.1 — identity-locked portrait and turnaround prompts

Use this only when the target is Midjourney v8.1 and the user needs face identity preserved from a reference image.

## Reference syntax

- (2026-07 실측) Midjourney v8.1에서 `--oref` / `--ow`를 사용하지 않는다.
- 참조 이미지는 일반 image prompt URL로 프롬프트 맨 앞에 둔다: `<reference-url> <text prompt>`.
- 이미지 영향도 조절이 필요하면 해당 v8.1 런타임 UI에서 실제 지원되는 image-weight 설정을 먼저 확인한다. 확인되지 않은 플래그를 추정해 붙이지 않는다.
- 얼굴 재현 우선 패스에서는 moodboard·personalization modifier를 생략하고, 기본 이미지 프롬프트가 안정된 뒤 하나씩 추가한다.

## Parameter and account-setting hygiene

- 최종 파라미터는 ASCII 이중 하이픈 `--`만 허용한다. U+2013 en dash(`–`)와 U+2014 em dash(`—`)는 모양이 비슷해도 파라미터가 아니므로 출력 전 거부·교정한다.
- 개인 `--profile` ID, private style code, `--preview` 같은 실험 토글은 이미지 레시피가 아니라 계정·현재 UI 설정이다. 사용자가 명시한 값을 임의로 공용 템플릿에 복제하지 말고, active UI에서 존재·지원 여부를 확인한 뒤 해당 실행에만 붙인다.
- `--raw`, stylize, weird, HD/SD 같은 옵션도 선택 버전의 visible UI와 결과 카드가 정본이다. 서로 다른 버전 가이드의 파라미터를 한 줄에 섞지 않는다.

## Compact prompt delivery

- Midjourney prompts should be materially shorter than the general 2000-character ceiling. For a single portrait, target roughly **400–800 characters** unless the user explicitly requests a dense prompt.
- Put the user-provided image URL directly at the beginning of the copyable prompt; do not merely mention the link outside it.
- Preserve only identity geometry, pose, styling, lighting, lens, and mood. Remove explanatory prose, repeated synonyms, and low-impact micro-details.
- If the user rejects a nationality label, replace it with the requested broad descriptor (for example, `East Asian`) and preserve the intended appearance through directly observable facial geometry rather than nationality-based inference.
- Return the finished prompt first in one copyable block. Keep notes to one short line or omit them.

## Output layout

- **Four full-body turnaround views on one canvas:** use horizontal `--ar 3:2`; explicitly state one horizontal row, generous spacing, and full body from head to feet.
- **Face reconstruction:** do not make a grid. Generate independent chest-up portraits at `--ar 3:4` with the same reference supplied for every job.

## Active UI and ten-angle sequence

1. Inspect the Midjourney Web **Create settings** first. The visible model setting and the result-card label are authoritative; do not add a remembered `--v` token merely to force the UI selection.
2. Verify one minimal front-facing reference job in that same UI/model configuration before any batch. Parameter forms and batch support are runtime-sensitive.
3. For face fidelity, use ten independent jobs with the same reference and identity core; change **only** the angle clause per job: front, 15°/30°/45° left, left profile, 15°/30°/45° right, right profile, and a near-front high 15° view.
4. Do not assume permutation/batch syntax will compose with an external identity reference. If a single job is proven but a batch errors, keep the sequence as independent jobs instead of retrying an opaque batch.
5. A repeat count produces variants of one angle, not a controlled ten-angle set.

## Identity delta workflow

- 동일 인물 시리즈는 identity core와 프로젝트 style source를 먼저 고정하고, 한 번에 **한 축만** 바꾼다: background → pose → wardrobe → hair/age처럼 단계별로 진행한다. 여러 축을 동시에 바꾸면 어떤 변화가 identity drift를 만들었는지 판정할 수 없다.
- 각 단계에서 얼굴 윤곽, 눈 간격, 눈썹 각도, 코·입술 외곽, 턱선, 헤어라인을 직전 승인 컷과 비교한다. 드리프트가 생기면 새 금지어를 쌓기보다 마지막 delta를 되돌리고 최소 front-facing job부터 재검증한다.
- 다중 캐릭터 프로젝트는 `one character = one reference set`, `one project = one frozen style source`로 관리한다. 캐릭터별 참조와 style source를 같은 슬롯이나 한 장의 군상 레퍼런스로 뭉개지 않는다.
- 완벽한 동일성을 보장한다고 쓰지 않는다. `identity fidelity is the highest priority`와 관찰 가능한 앵커를 사용하고, 결과는 확률이 아니라 비교 가능한 얼굴 지오메트리로 판정한다.

## Identity prompt core

State that facial identity is the highest priority and name stable, visible characteristics: face geometry, eye shape and spacing, brow angle/density, nose bridge and tip, lip outline, cheek contour, jawline, hairline, hairstyle. Specify chest-up framing and neutral expression for angle-comparison cuts.

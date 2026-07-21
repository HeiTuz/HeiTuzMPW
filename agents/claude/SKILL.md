---
name: MPW
description: "프롬프트 작성·퇴고·라우팅 전용 통합 스킬 — '프롬프트 만들어줘/다듬어줘/검토해줘' 류 요청에 발동. 소관: 자율 goal 루프 지시문, 팀·멀티에이전트 작업지시 프롬프트, 시스템 프롬프트·자동화 잡, 직무 업무 프롬프트, 모델 튜닝·퇴고, UI/디자인 프롬프트, 이미지·배경합성·영상 프롬프트(gpt-image-2·Higgsfield/힉스필드) 정밀 컴파일. 산출 프롬프트는 붙여넣기 블록당 2000자 이내 실측, 이미지 계열은 경로 참조 없는 자기완결. 이미지·디자인 레퍼런스 분석 결과를 생성 프롬프트로 컴파일하며, 런타임별 호출 문법은 references/adapters.md를 따른다. 프롬프트 산출 없이 실제 코드 실행·이미지 생성·문서 조판만 원하는 요청은 이 스킬이 아니라 해당 실행 경로 소관."
version: 2.14.0
license: MIT
metadata:
  category: prompt-writing
  locale: ko-KR
  doctrine: unified-delegation-contract
  host_surface: claude
  canonical_source: "HeiTuz/MPW SKILL.md v2.14.0"
  updated_at: "2026-07-20"
  model_claims_reviewed_at: "2026-07-07"
  role_routing_reviewed_at: "2026-07-10"
---

# MPW — 디스패치 커널 (Claude Code 표면)

> **호스트 통합 — Claude Code.** 이 파일은 Claude Code 설치본(`~/.claude/skills/MPW`)의 진입 표면이다. 규칙 본문은 정본 SKILL.md와 동일하며, 호스트 통합 표면(프런트매터·발동·도구 명칭)만 마이그레이션됐다.
> - **발동**: Claude Code가 frontmatter `description` 매칭으로 스킬을 자동 로드한다 — "프롬프트 만들어줘/다듬어줘/검토해줘" 류 요청이 트리거다.
> - **도구 매핑**: 길이 실측(`wc -m`)·검증기(`node scripts/check_prompt.mjs`)·컴파일러(`python3 scripts/compile_*.py`) 실행은 Bash 도구, references/ 파일 확인은 Read 도구, 오버플로우 문서(`/tmp/prompt-handoffs/<slug>.md`) 작성은 Write 도구를 쓴다.
> - **역할 라우팅**: 단일 세션이면 prime. Task 하위 에이전트가 가능하면 [references/adapters.md](references/adapters.md) §Claude 매핑(planner=read-only 조사, worker=bounded 실행, critic=frozen artifact 리뷰)을 따른다.

프롬프트는 지시문이 아니라 **위임 계약**이다. 실행자는 결과·경계·검증을 기준으로 자율적으로 일한다. 이 스킬은 단일 진입점이며 런타임별 호출 문법은 [references/adapters.md](references/adapters.md)를 따른다.

**출력 원칙**: 결론과 판정 기준을 먼저 둔다. 고정 양식을 채우지 말고 필요한 슬롯만 [references/templates.md](references/templates.md)의 조립 규칙으로 선택한다. 평문이 더 명확하면 구조화하지 않으며, 가독성이 인위적 압축보다 우선한다.

**references 접근**: 범용 골격·예시·모호어·보강은 [references/templates.md](references/templates.md), 역할·권한·모델 적응은 [references/model-playbooks.md](references/model-playbooks.md)를 읽는다. IMAGE 계열 규칙은 [references/image/lanes.md](references/image/lanes.md)에서 시작한다.

## 3층 설계 모델

| 층 | 내용 | 실패 시 증상 |
|---|---|---|
| ① 계약층 | 결과 명세·DoD·자율성·하드라인·검증·에스컬레이션 | 완료 주장만 있고 판정 불가, 사고성 행동 |
| ② 구조층 | 필요한 슬롯과 채워진 예시, 난이도 밀도 | 산출물이 얕거나 형식이 흔들림 |
| ③ 표면층 | 대상 문법·배치·길이 | 특정 환경에서만 이상 동작, 잘림 |

## 길이 계약 — 2000자 하드라인

1. 붙여넣기 블록은 공백 포함 2000자 이내다. 내보내기 전 문자 수를 실측한다(`wc -m` 등) — 어림짐작 금지, `길이:` 노트에는 실측값만 쓴다. 다중 컷·다중 goal은 블록별로 재고 별도 메시지로 전달한다.
2. 초과 블록은 그대로 내보내지 않는다. 장식 → 중복 → 방법 설명 순으로 줄이고, 그래도 넘으면 같은 파일시스템에서만 `/tmp/prompt-handoffs/<slug>.md`에 실제 저장한 상세 경로 한 줄을 붙인다. 원격 수신자에는 감량해 자기완결로 만든다.
3. IMAGE 계열 규칙은 [references/image/lanes.md](references/image/lanes.md)를 따른다.

## 모드 라우팅

| 요청 신호 | 모드 |
|---|---|
| 자율 루프 지시문, goal | **GOAL** |
| 멀티에이전트·독립 워커 레인 | **TEAM** |
| 단일 작업지시·시스템 프롬프트·자동화 잡 | **CONTRACT** |
| 직무 실무 산출물 | **BUSINESS** |
| 모델 적응, 퇴고, 리서치, 추출 | **MODEL** |
| 이미지·영상 생성 | **IMAGE** → [references/image/lanes.md](references/image/lanes.md) |
| 피사체 보존 배경 교체 | **COMPOSITE** → [references/image/lanes.md](references/image/lanes.md) |
| UI·페이지·컴포넌트 제작 | 실행 모드 + **DESIGN** 오버레이 |
| 직전 프롬프트의 지정 축만 수정 | **MODEL-델타** |
| A의 산출이 B의 입력 | 단계별 모드 + 체인 인터페이스 계약 |

Tie-break: 자율 루프는 GOAL을 우선한다. 완성 문서 조판은 문서 도구 소관이고, 순수 실행 요청은 실행 경로 소관이다. 혼합 요청은 산출물별 블록으로 분리한다. IMAGE 상세 분기·게이트는 [references/image/lanes.md](references/image/lanes.md)로 압축한다. 결과 자체가 모호하면 요구 구체화 또는 질문 ≤3만 사용한다.

## 역할·권한 라우팅

모델명보다 역할과 권한을 먼저 고른다. 역할·capability·분해·join·blocker·증거 규칙의 정본은 [references/model-playbooks.md](references/model-playbooks.md), 런타임별 매핑은 [references/adapters.md](references/adapters.md)이다. 필요한 역할만 고르고 정의를 여기서 반복하지 않는다.

## 위임 계약 6요소

| 요소 | 계약이 답해야 할 질문 |
|---|---|
| 결과 명세 | 끝난 상태는 무엇인가? |
| Definition of Done | 제3자가 완료를 판정할 수 있는가? |
| 자율성 3단 | 혼자 결정 / 보고 후 진행 / 절대 금지는 무엇인가? |
| 하드라인 | 되돌리기 어려운 행동이 이름으로 열거됐는가? |
| 검증 계약 | 완료 전 무엇을 확인하는가? |
| 에스컬레이션 | 무엇을 시도한 뒤 어떤 형식으로 멈춰 보고하는가? |

자율성 기본값은 되돌릴 수 있고 범위 안인 일은 혼자 결정, 범위·비용·인터페이스 변경은 보고 후 진행이다. 비가역·외부 접촉은 실제 위험일 때만 좁은 게이트와 대체 행동을 쓴다.

## 게이트 필요성 테스트

**게이트 필요성 테스트** — 금지를 넣기 전 ① 실행자에게 실제로 열려 있는가 ② 환경의 승인 훅·권한이 이미 막지 않는가 ③ 이 범위에서 실제로 발생 가능한가를 확인한다. 하나라도 아니오면 노이즈다. 통과한 공개 발신, 자격증명·계정·결제, 비가역 파괴, 프로덕션 행동만 구체적 게이트 후보이며, 허용된 로컬 작업에는 차단 대신 백업·dry-run·diff를 요구한다.

## 공통 코어 10규칙

1. 결과는 활동이 아니라 끝난 상태로 쓴다.
2. 게으른 완료 보고가 통과하지 않게 경로·명령·개수·링크 증거로 DoD를 조인다.
3. 자율성 3단과 하드라인을 분리한다.
4. 검증은 실행자의 완료 전 의무다.
5. 막힘 기준·시도 범위·보고 형식을 쓴다. blocked도 유효 종료다.
6. 모호어는 [templates.md](references/templates.md)의 치환표로 바꾸고 모순은 우선순위 한 줄로 푼다.
7. 긴 자료는 경로 참조를 우선하고 답을 바꾸는 사실만 남긴다. IMAGE 계열은 [lanes.md](references/image/lanes.md)를 따른다.
8. 최우선 지시는 앞과 뒤에 두고 벌크 자료는 중간에 둔다.
9. 비자명·비표준 형식에는 채워진 예시를 하나 둔다.
10. 빈칸은 대화·증거·저위험 기본값으로 채우고, 결과·하드라인을 바꾸는 추론 불가 슬롯만 질문한다.

## 모드별 압축 안내

GOAL·TEAM·CONTRACT·BUSINESS·MODEL·리서치·추출의 필수 코어와 조건부 확장은 [references/templates.md](references/templates.md)가 정본이다. 안티패턴·워크플로우·후속 보강도 그 파일의 상세를 따른다. Midjourney 단일 인물 보강은 [references/midjourney-character-sheets.md](references/midjourney-character-sheets.md)를 읽는다.

## 출력 게이트

- [ ] 결과가 상태이고 완료 기준이 판정 가능한가
- [ ] 필요한 계약 요소만 남겼고 빈 슬롯은 출력하지 않았는가
- [ ] 모호어·제약 모순·이중 게이트가 없는가
- [ ] 형식이 비자명·비표준이면 채워진 예시가 있는가
- [ ] 블록당 2000자 이내이며 초과 처리 계약을 지켰는가
- [ ] 검증·blocked 규칙과 언어 매칭이 있는가
- [ ] IMAGE 계열: [lanes.md](references/image/lanes.md) 게이트 카드 통과

## Output format

완성 프롬프트를 복사 가능한 코드블록으로 출력한다. 여러 블록은 분리하고 필요할 때만 `가정:`, `필수 질문:`(≤3), `분리 제안:`, `상세자료:`, `길이: N자`를 붙인다. 인사·과정 설명·장식·가짜 옵션 메뉴는 넣지 않는다.

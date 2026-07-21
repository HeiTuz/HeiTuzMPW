# 런타임 어댑터 — 실행 환경별 로컬라이즈 지점

코어 스킬은 런타임 중립이다. 특정 에이전트 제품에 묶인 값(설치 위치, 호출 접두어, 모델 선택, per-role routing 지원 여부)은 전부 이 파일에서만 다룬다. 코어 파일은 `prime`/`planner`/`worker`/`critic`과 capability label만 쓴다.

## 공통 코어 참조

역할 책임과 capability 선택은 [model-playbooks.md](model-playbooks.md) §역할·권한 라우팅이 유일한 정본이다. 이 파일은 설치 위치, 런타임 역할 매핑, 실제 모델 선택 위치, per-role routing이 없을 때의 fallback만 기록한다. 실제 모델명과 로컬 선택값은 각 런타임의 설정 파일, CLI 옵션, 또는 사용자의 세션 설정에 두며 private local selector를 하드코딩하지 않는다.

## 의류 핸드오프 소비자

휴대 가능한 의류 생성 계약은 `contracts/v1/apparel-handoff.schema.json`이 정의한다. `python3 scripts/compile_apparel_handoff.py request.json --output handoff.json`으로 생성하며, 런타임은 네트워크 호출 없이 이 파일을 읽어 후보 작업을 준비한다. Hermes 설치에서는 `ImgGen2`가 소비자이며, 핸드오프의 `unique_color_count`와 검증된 `vision_role_map`을 다시 확인한 뒤 동일한 전체 인벤토리를 가진 격리 작업을 만든다. 알 수 없는 버전이나 불일치는 자유형 프롬프트로 강등하지 않고 거부한다.


## Claude

- 설치/발견: `npx --yes github:HeiTuz/MPW --target claude` 또는 `git clone <repo> ~/.claude/skills/MPW`.
- 역할 매핑: 단일 Claude 세션이면 prime이 기본이다. 하위 에이전트나 task 기능이 있으면 planner는 read-only 조사, worker는 bounded edit/research, critic은 frozen artifact review로 보낸다.
- 모델 선택 위치: Claude 앱/CLI/프로젝트 설정. 이 저장소에는 모델명이나 plan 이름을 쓰지 않는다.
- fallback: per-role 모델 라우팅이 없으면 같은 세션에서 역할 헤더만 바꾼다. worker 결과는 prime이 다시 읽고 검증한다.

## GPT/Codex

- 설치/발견: `npx --yes github:HeiTuz/MPW --target codex` 또는 `--target gpt`; 둘 다 `~/.codex/skills/MPW`에 설치한다.
- 역할 매핑: Codex coding surface는 prime으로 운용한다. native subagent가 있으면 planner=read-only planning/research, worker=bounded implementation, critic=independent verifier로 할당한다.
- 모델 선택 위치: Codex profile, model picker, CLI config, or API caller configuration. 공개 routing vocabulary는 fast/read-only, balanced/agentic, strongest-reasoning/high-risk만 쓴다.
- fallback: subagent/per-role model routing이 없으면 prime 단일 세션이 topology-first intake, decomposition, implementation, and surface-matched verification을 순서대로 수행한다.

## Hermes

- 설치/발견: 기본 installer target은 Hermes다. `npx --yes github:HeiTuz/MPW` 또는 `--target hermes`는 `~/.hermes/skills/prompt-writing/MPW`에 설치한다.
- 역할 매핑: Hermes skill invocation이 prime이다. Hermes에 planner/worker/reviewer skill 또는 agent lane이 있으면 core 역할에 매핑한다. 로컬 전용 경로나 동반 workflow 이름은 공개 core로 올리지 않는다.
- 모델 선택 위치: Hermes runtime config. 이 저장소는 로컬 선택값이나 채널 선택값을 쓰지 않는다.
- fallback: role lanes가 없으면 Hermes prime이 단일 실행 계약을 산출하고, critic 역할은 최종 self-check checklist로 축소한다.
- 생성 실행 표면: 이 스킬은 IMAGE 컴파일을 끝낸 완성 프롬프트를 반환한다. 실제 생성은 사용자가 선택한 이미지·영상 도구가 담당하며, 비율·프리셋·미디어 참조 같은 구조화 옵션은 해당 도구 호출에 직접 전달한다.

## GJC

- 설치/발견: `npx --yes github:HeiTuz/MPW --target gjc` 또는 `git clone <repo> ~/.gjc/agent/skills/MPW`.
- 역할 매핑: active coding agent is prime. Built-in role agents map naturally: planner/architect → `planner`, worker/executor → `worker`, critic/verifier → `critic`. The prime/integrator remains responsible for state, joins, final verification, and completion claim.
- 모델 선택 위치: GJC settings outside this repo. Do not hardcode backend IDs, local selector names, session lifecycle details, or workflow CLI verbs in public core prompts.
- fallback: if role-agent routing is unavailable, run the shared core as one prime session and use explicit role sections in the generated prompt.

## 어댑터 작성 규칙

아키타입당 4항목만 기록한다: ① 설치/로드 방법 ② 역할 매핑 ③ 실제 모델 선택 위치 ④ per-role routing unavailable fallback. 코어 규칙을 복사하지 않는다. 코어와 충돌하는 어댑터 문장은 무효다.

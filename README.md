# master-prompt-writer

프롬프트 작성·퇴고·라우팅 전용 통합 에이전트 스킬. 프롬프트를 "지시서"가 아니라 **위임 계약**(결과·경계·검증)으로 설계한다.

A runtime-agnostic agent skill that turns rough requests into paste-ready prompts — treating every prompt as a **delegation contract** (outcome, boundaries, verification) instead of a to-do list. Korean-first, works with any skill-aware agent or as a plain system prompt.

## 무엇을 하나

| 요청 | 산출 |
|---|---|
| "flaky 테스트 고치는 goal 써줘" | 자율 에이전트 goal 지시문 (판정 가능한 DoD·게이트·에스컬레이션) |
| "결제 모듈 리팩토링 팀 킥오프" | 멀티에이전트 팀 킥오프 (레인·검증·경계) |
| "고객응대 봇 시스템 프롬프트" | 상시 규범형 시스템 프롬프트 |
| "변호사 계약검토 프롬프트" | 직무 5요소 + 난이도 1~7 업무 프롬프트 |
| "카페 신메뉴 포스터" | 자기완결 이미지 프롬프트 (HEX·AR·긍정형, C1~C12 카테고리 컴파일) |
| "패션 화보 한 컷" | 에디토리얼 화보 프롬프트 (포즈·조명 시그니처·컴플라이언스 레인) |
| "이 사진 배경만 파리로" | 픽셀 고정 배경 합성 프롬프트 (프레임/정체성 락) |
| "방금 프롬프트 톤만 바꿔" | 델타 수정 (전체 재작성 금지) |

## 핵심 계약

- **블록당 2000자** — 메신저 1메시지 복붙 기준, 실측(`wc -m`) 필수. 초과 상세는 오버플로우 문서+경로.
- **이미지 자기완결** — 이미지 모델은 파일을 못 읽는다. 경로 참조 금지, 넘치면 감량→컷 분할.
- **빈칸은 묻기 전에 채운다** — 대화→저장소 증거→저위험 기본값 순으로 추론, 채운 값은 `가정:` 노트. 질문은 추론 불가 슬롯(원본·정확한 카피·실계정 등)만.
- **게이트 필요성 테스트** — 금지문은 ①실행자에게 열려 있고 ②시스템이 안 막고 ③실제 발생 가능할 때만. 환경 훅이 이미 막는 배포·재시작을 재금지하는 노이즈를 넣지 않는다.
- **레인 게이트 카드** — 이미지/합성/영상/디자인 레인별로 네거티브 정책·비율·필수 요소가 다르다. 단일 규칙으로 뭉개지 않는다.

## 구조

```
SKILL.md                      # 디스패치 커널 — 라우팅·공통 계약·출력 게이트
references/templates.md       # 모드별 골격 + 실측 라벨 예시 + 레인 게이트 카드
references/model-playbooks.md # 모델별 문법 (검증 스탬프 포함, 6개월 만료 규칙)
references/image/             # 이미지 정밀 컴파일 계층 — compiler(철칙·템플릿·사이즈 락),
                              #   categories(C1~C12), editorial-fashion(화보·패션·사진 어휘),
                              #   look-and-concept(룩 프리셋·컨셉 축), typography(한글 렌더),
                              #   production(jsonl 양산·모델 팩트)
references/adapters.md        # 런타임 아키타입별 로컬라이즈 지점 (포크 후 자기 값 기입)
scripts/lint.py               # 자기 린트 — 라벨 실측 일치·2000자·정본 단일성
scripts/check_prompt.mjs      # 이미지 프롬프트 검증기 (tier 인지형, zero-dependency Node)
scripts/install.mjs           # npm/bun one-shot 설치기
examples/                     # 실측 캘리브레이션 3컷 — 컴파일 프롬프트+생성 결과 쌍
```

## 설치

가장 짧은 설치는 npm/bun one-shot이다. 기본 대상은 Hermes다.

```sh
npx --yes github:eusine/master-prompt-writer
# 또는
bunx github:eusine/master-prompt-writer
```

다른 에이전트에 넣을 때는 대상만 지정한다.

```sh
npx --yes github:eusine/master-prompt-writer --target codex
npx --yes github:eusine/master-prompt-writer --target claude
npx --yes github:eusine/master-prompt-writer --target gjc
npx --yes github:eusine/master-prompt-writer --target agents
```

GitHub CLI/직접 클론을 선호하면 아래 방식도 된다.

```sh
REPO=https://github.com/eusine/master-prompt-writer.git

# Hermes 전용 명령
hermes skills install "$REPO" --category prompt-writing

# Claude Code
git clone "$REPO" ~/.claude/skills/master-prompt-writer

# Codex CLI
git clone "$REPO" ~/.codex/skills/master-prompt-writer

# GJC (gajae-code) — 유저 레벨
git clone "$REPO" ~/.gjc/agent/skills/master-prompt-writer
# GJC — 특정 프로젝트에만
git clone "$REPO" <project>/.gjc/skills/master-prompt-writer

# Hermes 직접 클론
git clone "$REPO" ~/.hermes/skills/prompt-writing/master-prompt-writer

# 공용 스킬 디렉토리 컨벤션(~/.agents/skills)을 읽는 에이전트
git clone "$REPO" ~/.agents/skills/master-prompt-writer
```

설치 확인: 에이전트에게 "프롬프트 만들어줘"라고 하면 이 스킬이 발동해야 한다. 이미지 레인은 "카페 포스터 프롬프트 만들어줘" 같은 이미지 프롬프트 요청으로 확인한다.

**스킬 시스템이 없는 챗/API** — `SKILL.md` 전문을 시스템 프롬프트로, 필요한 references 섹션만 이어붙인다.

런타임별 호출 접두어·턴 예산·관례 경로는 [references/adapters.md](references/adapters.md)의 아키타입에 자기 환경 값을 채워 로컬라이즈한다.

## 검증

```sh
python3 scripts/lint.py            # 스킬 자기 린트
node scripts/check_prompt.mjs --test  # 이미지 검증기 셀프테스트 (14 fixtures)
```

스킬이 자기 자신에게 요구하는 하드라인(예시 라벨=실제 길이, 블록당 2000자, 모호어 표기, 정본 단일 정의, 유사문자 0)을 기계 검증한다. PR 전 필수.

## 설계 계보

5개 프롬프트 스킬(위임 계약·goal 작성·모델 패턴·직무 프롬프트·팀 킥오프)을 통합한 뒤, 다중 모델 적대 검증(critic/architect 교차 리뷰)과 5스토리×2패스 반복 개선을 거쳐 v2.1.0으로 고정했고, 이후 개정을 거쳐 현행 버전은 v2.3.0이다(SKILL.md frontmatter 기준). 모델별 행동 주장에는 검증 날짜 스탬프가 붙어 있으며 6개월 경과 시 재검증이 규칙이다.

## License

MIT

# master-prompt-writer

### 길게 설명하지 마세요. 실행이 끝나는 프롬프트를 쓰세요.

[![Release](https://img.shields.io/github/v/release/HeiTuz/master-prompt-writer?style=flat-square)](https://github.com/HeiTuz/master-prompt-writer/releases/latest)
[![CI](https://img.shields.io/github/actions/workflow/status/HeiTuz/master-prompt-writer/ci.yml?branch=main&style=flat-square&label=lint)](https://github.com/HeiTuz/master-prompt-writer/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-black?style=flat-square)](LICENSE)

**master-prompt-writer**는 거친 요청 한 줄을 에이전트가 실제 결과와 검증까지 끝내는 프롬프트로 바꿉니다.
할 일 목록에서 멈추지 않습니다. 결과물, 완료 기준, 자율 범위, 검증, 중단 조건을 한 번에 잠급니다.

프롬프트가 결과를 만들지 못하면 아무리 길어도 소음입니다. 이 스킬은 실행에 필요한 것만 남깁니다.

## 왜 이걸 쓰나요?

흔한 프롬프트는 “일단 시작해”에서 끝납니다.

> “알아서 잘 고쳐줘. 꼼꼼하게 확인해줘.”

결과는 뻔합니다. 범위는 흔들리고 검증은 빠진 채, “완료했습니다”라는 말만 남습니다.

master-prompt-writer는 모호한 부탁을 실행 계약으로 정리합니다.

- **끝난 모습을 먼저 정합니다.** 무엇을 만들어야 완료인지 먼저 고정합니다.
- **말이 아니라 증거를 남깁니다.** 경로, 테스트, 개수, 링크처럼 직접 확인할 근거를 요구합니다.
- **방법은 맡기고 경계만 세웁니다.** 에이전트를 마이크로매니징하지 않아도 범위는 흔들리지 않습니다.
- **끝낼 때를 분명히 합니다.** 검증을 마치면 멈추고, 막히면 시도한 것과 차단 지점을 남깁니다.
- **채널에서 잘리지 않습니다.** 붙여넣기 블록은 2,000자 하드라인을 지킵니다.

## 한 스킬로 어디까지?

| 요청 | 바뀌는 결과 |
|---|---|
| “flaky 테스트 고치는 지시문 써줘” | 테스트 증거가 있어야 끝나는 자율 실행 계약 |
| “결제 모듈 리팩토링 팀 킥오프” | 역할·경계·통합 순서까지 정한 팀 작업지시 |
| “고객응대 봇 시스템 프롬프트” | 매 턴 같은 기준을 지키는 상시 규범 |
| “변호사 계약검토 프롬프트” | 현실 제약과 출력 형식을 반영한 업무 프롬프트 |
| “카페 신메뉴 포스터” | 타이포·비율·카피까지 정한 이미지 프롬프트 |
| “패션 화보 한 컷” | 포즈·조명·렌즈 감각을 맞춘 에디토리얼 프롬프트 |
| “이 사진 배경만 파리로” | 인물과 프레임은 보존하는 배경 합성 계약 |
| “방금 프롬프트 톤만 바꿔” | 나머지는 그대로 두고 지정한 축만 바꾸는 델타 수정 |

코딩과 리서치, 시스템 프롬프트, 팀 작업지시, 직무 문서, 이미지와 영상까지 같은 원칙으로 다룹니다.

## 모델 이름보다 역할을 먼저 고릅니다

가장 비싼 모델부터 부르는 건 실력이 아니라 낭비입니다. 먼저 누가 어떤 권한을 가져야 하는지 정합니다.

- **prime / integrator** — 결과, 결정, 통합, 최종 검증, 완료 claim
- **planner / architect** — 읽기 전용 범위 파악, 옵션, 위험, 수용 기준
- **worker / executor** — 명시된 target과 acceptance가 있는 bounded slice
- **critic / verifier** — 같은 frozen artifact를 독립 검토

그다음 런타임이 가진 가장 낮은 충분 capability를 붙입니다: fast/read-only, balanced/agentic, strongest-reasoning/high-risk. 역할과 모델 강도는 별개입니다. 낮은 위험의 prime은 balanced로도 충분하고, 보안·광역 통합·실패 복구만 strongest로 올립니다. Claude, GPT/Codex, Hermes, GJC 모두 같은 역할 계약을 쓰며, 실제 모델 선택은 각 런타임 설정에 둡니다.

## 복잡한 작업이 무너지지 않게 하는 다섯 규칙

GJC에서 검증된 방식 중 다른 런타임에서도 그대로 통하는 것만 남겼습니다.

- 깊게 들어가기 전에 최상위 결과 목록부터 확정합니다.
- 파일이 아니라 검증 표면이 독립적일 때만 병렬로 나눕니다.
- worker에는 target, scope, non-goals, acceptance가 닫힌 일만 맡깁니다.
- 모든 결과와 리뷰가 같은 frozen artifact를 볼 때만 최종 판정을 냅니다.
- 증거는 실제 출시 표면에 맞추고, 사람만 풀 수 있는 blocker에서만 멈춥니다.

## 이미지 프롬프트도 대충 쓰지 않습니다

이미지는 형용사를 늘린다고 좋아지지 않습니다. 카테고리, 구도, 조명, 타이포, 비율, 보존 대상이 한 장면 안에서 맞물려야 합니다.

필요한 범위는 여기까지 담았습니다.

- C1~C12 이미지 카테고리 라우팅
- 패션·화보·에디토리얼 사진 어휘
- 한글 타이포와 카드뉴스 구조
- 배경 합성용 프레임·정체성 고정 계약
- JSONL 양산 규칙과 zero-dependency 검증기
- 이미지·영상 레인별 실패 조건과 검수 기준

## 30초 설치

기본값은 Hermes 설치입니다.

```sh
npx --yes github:HeiTuz/master-prompt-writer
# 또는
bunx github:HeiTuz/master-prompt-writer
```

다른 에이전트에 설치하려면 대상만 지정하세요.

```sh
npx --yes github:HeiTuz/master-prompt-writer --target codex
npx --yes github:HeiTuz/master-prompt-writer --target gpt
npx --yes github:HeiTuz/master-prompt-writer --target claude
npx --yes github:HeiTuz/master-prompt-writer --target gjc
npx --yes github:HeiTuz/master-prompt-writer --target agents
```

직접 설치하는 방법도 있습니다.

```sh
REPO=https://github.com/HeiTuz/master-prompt-writer.git

hermes skills install "$REPO" --category prompt-writing
git clone "$REPO" ~/.codex/skills/master-prompt-writer
git clone "$REPO" ~/.claude/skills/master-prompt-writer
git clone "$REPO" ~/.gjc/agent/skills/master-prompt-writer
git clone "$REPO" ~/.agents/skills/master-prompt-writer
```

스킬 시스템이 없는 챗이나 API에서는 `SKILL.md`를 시스템 프롬프트로 넣고 필요한 reference만 붙이세요.

## 설치 후 바로 써보기

설치가 끝나면 평소처럼 요청하세요.

```text
이 기능 구현하게 프롬프트 써줘. 실제 테스트까지 돌리고, 무관한 리팩토링은 하지 않게 해.
```

```text
이 상품 사진은 그대로 두고 배경만 서울의 새벽 골목으로 바꾸는 이미지 편집 프롬프트 만들어줘.
```

```text
이 리서치 프롬프트를 fast/read-only 조사 역할에 맞게 줄이고, 출처 검증과 중단 조건을 넣어줘.
```

## 약속이 아니라 테스트

```sh
python3 scripts/lint.py
npm test
npm run smoke:install
npm run smoke:runtime
```

- 프롬프트 예시의 실제 글자 수 확인
- 블록당 2,000자 초과 차단
- 이미지 프롬프트 good/bad fixture 14종 회귀 테스트
- 설치기 스모크 테스트
- GitHub Actions에서도 같은 항목 검증

<details>
<summary><strong>저장소 구조 보기</strong></summary>

```text
SKILL.md                       디스패치 커널
references/templates.md        모드별 골격과 출력 게이트
references/model-playbooks.md  역할·권한 라우팅과 capability 플레이북
references/image/              이미지 정밀 컴파일 계층
references/adapters.md         런타임별 설치·호출 어댑터
scripts/lint.py                스킬 자기 린트
scripts/check_prompt.mjs       이미지 프롬프트 검증기
scripts/install.mjs            npm/bun 설치기
examples/                      프롬프트와 생성 결과 캘리브레이션
```

</details>

## License

MIT

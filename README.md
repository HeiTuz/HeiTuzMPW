# MPW

## AI에게 말은 그만 시키고, **결과를 내게 만드세요.**

[![Release](https://img.shields.io/github/v/release/HeiTuz/MPW?style=flat-square)](https://github.com/HeiTuz/MPW/releases/latest)
[![CI](https://img.shields.io/github/actions/workflow/status/HeiTuz/MPW/ci.yml?branch=main&style=flat-square&label=CI)](https://github.com/HeiTuz/MPW/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-black?style=flat-square)](LICENSE)

**MPW**는 “대충 잘해줘”를 결과물, 검증, 완료 기준이 박힌 실행 지시로 바꿉니다.

긴 프롬프트보다 중요한 건 끝난 작업입니다.

코드는 테스트를 통과하고, 리서치는 결론을 만들고, 콘텐츠는 바로 쓸 수 있어야 합니다. MPW는 짧은 요청 하나를 **실행, 검증, 완료까지 밀어붙이는 프롬프트**로 컴파일합니다.

## 요청 한 줄이 실제 결과로 바뀝니다

### “고쳐줘”를 테스트 통과까지 밀어붙입니다

> “이 버그 고쳐줘”를 코드 변경에서 끝내지 않습니다.

고칠 범위와 건드리지 말아야 할 경계를 잡고, 통과해야 할 테스트를 박습니다. 불필요한 리팩터링으로 판을 키우지 않고도 결과를 검증 가능한 상태까지 끌고 갑니다.

### 여러 에이전트를 한 목표에 꽂습니다

기획, 구현, 리뷰, 검증이 서로 다른 목표를 쫓으면 에이전트가 많을수록 더 빨리 망가집니다.

MPW는 역할과 경계를 정리해 **여러 에이전트가 하나의 결과물을 향해 움직이게** 합니다. 누가 판단하고, 누가 실행하고, 무엇으로 최종 판정할지 처음부터 못 박습니다.

### 리서치를 읽을거리에서 결정 도구로 바꿉니다

출처만 잔뜩 붙은 리서치는 브라우저 탭만 늘립니다.

조사 범위, 신뢰할 근거, 비교 기준, 결론의 형식을 잡아 **바로 다음 행동으로 이어지는 답**을 만듭니다.

### 이미지와 영상은 예쁜 말보다 보이는 장면으로

화려한 형용사를 쌓지 않습니다. 모델이 무엇을 그려야 하는지 장면 단위로 지시합니다.

패션 화보, 브랜드 비주얼, 포스터, 카드뉴스, 제품 사진, 배경 편집까지. 구도, 조명, 스타일, 보존해야 할 요소를 한 장면 안에 정리해 **첫 생성부터 적중률을 높이는 제작 지시**를 만듭니다.

“서브컬처·독립잡지 스타일 레퍼런스 100장”처럼 아이데이션 수량이 큰 요청은 한 문장을 반복하지 않습니다. 내장 variation compiler가 구도·시점·조명·팔레트·재질·공간 리듬을 서로 다르게 조합해 자기완결 프롬프트 JSONL을 만듭니다.

```sh
python3 scripts/compile_image_variations.py --request request.json --count 100 --output variations.jsonl --seed 42
```

이 단계는 외부 호출이나 이미지 QC를 실행하지 않습니다. 생성·재개·최종 이미지 수집은 호환 이미지 실행기가 맡습니다.

### 잘된 프롬프트는 살리고, 틀린 축만 벱니다

톤만 바꾸고 싶다면 톤만. 구도만 바꾸고 싶다면 구도만.

좋았던 부분까지 갈아엎는 재작성 대신, 바꿔야 할 축만 잡아 **의도를 보존한 채 정밀하게 수정**합니다.

## 이런 답답함이 있다면 바로 맞습니다

- 결과 없이 말만 번듯한 AI 작업이 지겨운 사람
- 코딩·리서치·기획·콘텐츠 제작을 한 기준으로 굴리고 싶은 사람
- 여러 에이전트를 써도 통제력을 잃고 싶지 않은 사람
- 이미지 프롬프트를 “예쁜 말 모음”이 아니라 제작 지시로 쓰고 싶은 사람
- 완료했다는 말보다 파일·링크·테스트·검증을 보고 싶은 사람

## 30초면 붙습니다

한 줄이면 설치기가 이 컴퓨터의 에이전트 환경을 자동 감지해 맞는 위치에 설치합니다.

```sh
npx --yes github:HeiTuz/MPW
# 또는
bunx github:HeiTuz/MPW
```

### 자동 감지가 하는 일

- **감지 신호**: `~/.hermes`, `~/.claude`, `~/.codex` 같은 잘 알려진 스킬 디렉터리·CLI 설치 흔적만 봅니다. 비밀값이나 설정 파일 내용은 읽지 않습니다.
- **대화형 터미널**: 감지된 대상을 보여주고 하나 또는 여러 개를 선택·확인합니다.
- **CI·비대화형**: 절대 묻지 않습니다. 1개 감지 → 그대로 설치. 여러 개 감지 → Hermes 우선, Hermes가 없으면 `hermes > claude > codex` 우선순위의 첫 감지 대상. 0개 감지 → Hermes 위치에 설치(문서화된 기본값).
- 명시 `--target`/`--dest`는 항상 자동 감지를 이깁니다.

### 어디에, 어떤 payload가 설치되나

| 대상 | 설치 위치 | payload |
|---|---|---|
| `hermes` (기본·권장) | `~/.hermes/skills/prompt-writing/MPW` | 정본 Hermes-native 표면 |
| `claude` | `~/.claude/skills/MPW` | **Claude Code용 마이그레이션 표면** |
| `codex` / `gpt` | `~/.codex/skills/MPW` | **GPT/Codex용 마이그레이션 표면** |
| `gjc` | `~/.gjc/agent/skills/MPW` | 정본 표면 |
| `agents` | `~/.agents/skills/MPW` | 정본 표면 |

Hermes가 기본·선호 환경입니다. Claude Code와 Codex는 규칙 본문이 동일한 채 호스트 통합 표면(발동·도구 명칭·frontmatter)만 마이그레이션된 변형을 받습니다 — 구조와 근거는 [agents/README.md](agents/README.md).

### 명시 설치

```sh
npx --yes github:HeiTuz/MPW -- --target hermes
npx --yes github:HeiTuz/MPW -- --target claude
npx --yes github:HeiTuz/MPW -- --target codex     # --target gpt 동일
npx --yes github:HeiTuz/MPW -- --target all       # 감지된 전부에 설치
npx --yes github:HeiTuz/MPW -- --dest /custom/skills/MPW
```

재설치는 `--force`, 조용한 설치는 `--quiet`. `--target auto`는 기본 동작인 자동 감지를 명시적으로 켭니다.

### 이미지 제작까지 한 번에 붙일 때: 추천

```sh
npx --yes --package github:HeiTuz/ImgGen2 heituz-imggen2
# 또는
bunx --package github:HeiTuz/ImgGen2 heituz-imggen2
```

이 unified 설치는 **공식 Codex CLI + ImgGen2 + MPW**를 함께 세팅합니다. 같은 자동 감지를 쓰며, ImgGen2와 MPW는 항상 같은 호스트에 나란히 설치됩니다 — ImgGen2는 Hermes에, MPW는 다른 곳에 가는 어긋남이 없습니다. 이후에는 아래 한 줄로 둘 다 갱신합니다.

```sh
imggen update
```

### 직접 설치

```sh
REPO=https://github.com/HeiTuz/MPW.git

hermes skills install "$REPO" --category prompt-writing
git clone "$REPO" ~/.codex/skills/MPW
git clone "$REPO" ~/.claude/skills/MPW
git clone "$REPO" ~/.gjc/agent/skills/MPW
git clone "$REPO" ~/.agents/skills/MPW
```

git clone은 정본 표면을 그대로 복사합니다. Claude·Codex용 마이그레이션 표면까지 적용하려면 installer를 쓰세요.

## 짧게 던져도 단단하게 끝냅니다

```text
이 기능 구현하게 프롬프트 써줘.
실제 테스트까지 돌리고, 무관한 리팩터링은 하지 않게 해.
```

```text
이 리서치 요청을 의사결정용으로 바꿔줘.
출처 신뢰도와 결론의 한계도 분명히 남겨.
```

```text
이 상품 사진은 그대로 두고 배경만 서울의 새벽 골목으로 바꾸는 이미지 편집 프롬프트 만들어줘.
```

```text
이 팀 작업의 역할과 완료 기준을 정리해줘.
결과물을 합치는 사람과 검증하는 사람을 분리해.
```

## 프롬프트의 가치는 결과로 증명됩니다

그럴듯한 문장만 남기는 프롬프트는 실패입니다.

**실행할 수 있는 지시, 확인할 수 있는 결과, 완료를 증명하는 근거.**

MPW는 AI의 답변을 작업 결과로 바꿉니다.

## License

MIT

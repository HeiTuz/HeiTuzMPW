# HeiTuzMPW

## 한 줄 요청을, **실제로 끝나는 작업**으로 바꿉니다.

[![Release](https://img.shields.io/github/v/release/HeiTuz/HeiTuzMPW?style=flat-square)](https://github.com/HeiTuz/HeiTuzMPW/releases/latest)
[![CI](https://img.shields.io/github/actions/workflow/status/HeiTuz/HeiTuzMPW/ci.yml?branch=main&style=flat-square&label=CI)](https://github.com/HeiTuz/HeiTuzMPW/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-black?style=flat-square)](LICENSE)

**HeiTuzMPW**는 “대충 잘해줘”를 결과물·검증·완료 기준이 박힌 실행 지시로 바꿉니다.

프롬프트가 길다고 일이 끝나는 건 아닙니다.

산출물이 나오고, 확인할 증거가 남고, 막히면 이유가 드러나야 끝난 거죠. **그 차이를 만드는 스킬입니다.**

## 이런 일을 합니다

### 개발 작업을 끝까지 밀어붙입니다

> “이 버그 고쳐줘”에서 멈추지 않습니다.

무엇을 고쳐야 하는지, 어디까지 건드릴지, 어떤 테스트가 통과해야 끝인지 선명하게 잡습니다. 불필요한 리팩터링으로 판을 키우지 않으면서도, 결과는 실제로 검증 가능한 상태까지 끌고 갑니다.

### 복잡한 팀 작업을 한 방향으로 묶습니다

기획, 구현, 리뷰, 검증이 서로 다른 얘기를 하면 팀 작업은 바로 산으로 갑니다.

HeiTuzMPW는 역할과 경계를 정리해 **여러 에이전트가 한 결과물을 향해 움직이게** 합니다. 누가 판단하고, 누가 실행하고, 무엇으로 최종 판정을 내릴지 흐리지 않습니다.

### 리서치를 ‘읽었다’에서 ‘쓸 수 있다’로 바꿉니다

출처만 잔뜩 붙은 리서치는 결정을 못 만듭니다.

조사 범위, 신뢰할 근거, 비교 기준, 결론의 형식을 잡아 **바로 다음 행동으로 이어지는 조사 결과**를 만듭니다.

### 이미지와 영상도 결과 중심으로 설계합니다

화려한 형용사를 늘어놓는 대신, 장면이 실제로 보이게 만듭니다.

패션 화보, 브랜드 비주얼, 포스터, 카드뉴스, 제품 사진, 배경 편집까지. 구도·조명·스타일·보존해야 할 요소를 한 장면 안에서 정리해 **재작업을 줄이는 제작 지시**를 만듭니다.

### 이미 만든 프롬프트는 필요한 부분만 정확히 고칩니다

톤만 바꾸고 싶다면 톤만. 구도만 바꾸고 싶다면 구도만.

좋았던 부분까지 갈아엎는 무식한 재작성 대신, 바꿔야 할 축만 잡아 **의도를 보존한 채 정밀하게 수정**합니다.

## 이런 사람에게 맞습니다

- 결과 없이 말만 번듯한 AI 작업이 지겨운 사람
- 코딩·리서치·기획·콘텐츠 제작을 한 기준으로 굴리고 싶은 사람
- 여러 에이전트를 써도 통제력을 잃고 싶지 않은 사람
- 이미지 프롬프트를 “예쁜 말 모음”이 아니라 제작 지시로 쓰고 싶은 사람
- 완료했다는 말보다 파일·링크·테스트·검증을 보고 싶은 사람

## 30초 설치

### 이미지 제작까지 한 번에 붙일 때 — 추천

```sh
npx --yes --package github:HeiTuz/HeiTuzImgGen2 heituz-imggen2
# 또는
bunx --package github:HeiTuz/HeiTuzImgGen2 heituz-imggen2
```

이 unified 설치는 **공식 Codex CLI + HeiTuzImgGen2 + HeiTuzMPW**를 함께 세팅합니다. 이후에는 아래 한 줄로 둘 다 갱신합니다.

```sh
heituz update
```

### MPW만 독립 설치할 때

```sh
npx --yes --package github:HeiTuz/HeiTuzMPW heituzmpw
# 또는
bunx --package github:HeiTuz/HeiTuzMPW heituzmpw
```

다른 에이전트 환경에 설치할 때는 대상만 지정하면 됩니다.

```sh
npx --yes --package github:HeiTuz/HeiTuzMPW heituzmpw -- --target codex
bunx --package github:HeiTuz/HeiTuzMPW heituzmpw -- --target gpt
npx --yes --package github:HeiTuz/HeiTuzMPW heituzmpw -- --target claude
npx --yes --package github:HeiTuz/HeiTuzMPW heituzmpw -- --target agents
```

직접 설치도 가능합니다.

```sh
REPO=https://github.com/HeiTuz/HeiTuzMPW.git

hermes skills install "$REPO" --category prompt-writing
git clone "$REPO" ~/.codex/skills/HeiTuzMPW
git clone "$REPO" ~/.claude/skills/HeiTuzMPW
git clone "$REPO" ~/.gjc/agent/skills/HeiTuzMPW
git clone "$REPO" ~/.agents/skills/HeiTuzMPW
```

## 바로 이렇게 쓰세요

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

## 말보다 증거

HeiTuzMPW는 그럴듯한 문장을 목표로 하지 않습니다.

**실행할 수 있는 지시, 확인할 수 있는 결과, 끝났다고 말할 수 있는 근거.**

그 세 가지를 남기기 위해 만들어졌습니다.

## License

MIT

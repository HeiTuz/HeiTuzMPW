# agents/ — 호스트별 배포 오버레이

이 폴더는 MPW의 **호스트별 설치 오버레이**다. 저장소 루트(SKILL.md + references/ + scripts/ + contracts/ + examples/)가 유일한 정본이며, 각 호스트 폴더는 그 위에 얹는 최소 진입/안내 표면만 담는다 — 저장소 전체 포크가 아니다.

## 설치 모델

```
설치본 = 정본 allowlist 트리 + agents/<host>/ 오버레이 (같은 이름 파일은 오버레이가 대체)
```

- 설치된 트리에는 `agents/` 폴더 자체가 들어가지 않는다 — 선택된 호스트의 오버레이만 적용되어, 설치본의 스킬 진입점은 `SKILL.md` 정확히 하나다.
- 오버레이가 바꿀 수 있는 것은 **호스트 통합 표면**뿐이다: frontmatter, 발동/호출 안내, 도구 명칭 매핑, 진입 프레이밍. 스킬의 실제 규칙·동작은 정본과 동일해야 한다.
- 설치 후에도 상대 참조(`references/`, `scripts/`, `contracts/`)는 전부 유효해야 한다.

## 호스트 폴더

| 폴더 | 내용 |
|---|---|
| `hermes/` | 얇은 노트만. **정본 루트 payload가 곧 Hermes-native 표면**이므로 별도 마이그레이션이 없다. |
| `claude/` | Claude Code용 진입 표면(`SKILL.md`): Claude Code 스킬 발동 방식, Bash/Read/Write 도구 매핑, Task 하위 에이전트 역할 라우팅 노트. |
| `codex/` | GPT/Codex용 진입 표면(`SKILL.md` + 설치본용 `AGENTS.md`): Codex skills 디렉터리 발견 방식, shell 도구 매핑, native subagent 역할 라우팅 노트. |

`gjc`·`agents` 등 그 외 설치 target은 정본(Hermes-native) 표면을 그대로 받는다. `--target gpt`는 `codex` 오버레이와 동일하다.

## 왜 `agents/<host>/`인가 — 관례 조사 근거 (2026-07 실측)

공개 멀티에이전트 스킬/설치 저장소 5종을 조사한 결과, 더 강한 공개 관례는 없었다:

| 저장소 | 호스트별 payload 구조 |
|---|---|
| oh-my-hermes | 없음 — 단일 호스트(Hermes) 대상 `skills/` 컬렉션 |
| tw93/Waza | 없음 — `skills/` 컬렉션 + 루트 `AGENTS.md`/`CLAUDE.md` 지시 파일로만 호스트 적응 |
| higgsfield-skills | 없음 — 루트에 스킬 폴더 나열 + `INSTALL_FOR_AGENTS.md` 단일 안내 |
| god-tibo-imagen | 없음 — `skills/` + 루트 `AGENTS.md`, 단일 payload |
| master-prompt-writer | 없음 — 루트 `SKILL.md` 단일 payload, 호스트 변형 없음 |

즉 기존 관례는 "정본 하나 + 루트 지시 파일"까지만 커버하고, **호스트별로 실제 마이그레이션된 진입 표면**을 배포하는 관례는 부재했다. `AGENTS.md` 표준이 에이전트 지시 표면의 사실상 명칭인 점에 맞춰, 호스트별 오버레이 우산 폴더를 `agents/`로 명명하고 그 아래 `hermes/`·`claude/`·`codex/`를 두는 것이 가장 자기설명적이며 기존 루트(`references/`, `scripts/`)와 충돌하지 않는다.

## 동기화 규칙 (드리프트 방지)

`agents/*/SKILL.md`의 규칙 본문은 정본 `SKILL.md`를 따라간다. 정본 SKILL.md를 수정하면 각 호스트 SKILL.md의 본문도 같은 내용으로 갱신하고, 호스트별 차이는 frontmatter(`host_surface`, `canonical_source`)와 상단 "호스트 통합" 블록(+ codex의 AGENTS.md)에만 남긴다. 호스트 파일은 정본과 byte-identical이면 안 되고(마이그레이션 증거), 규칙 본문이 다르면 안 된다(동작 동일성). 런타임 고유명 규칙(AGENTS.md 하드라인 5)은 코어 파일에만 적용된다 — `agents/<host>/`는 `references/adapters.md`와 같은 런타임 어댑터 표면이므로 해당 호스트 제품명을 쓸 수 있다.

# MPW — Hermes 설치본

이 디렉터리는 MPW의 Hermes 설치 payload다. **정본 루트 payload가 곧 Hermes-native 표면**이므로 이 오버레이는 이 노트 하나뿐이다 — 별도 마이그레이션 파일이 없다.

- 스킬 진입점: `SKILL.md` (디스패치 커널)
- 설치 위치: `~/.hermes/skills/prompt-writing/MPW`
- 역할 매핑·호출 문법: [references/adapters.md](references/adapters.md) §Hermes
- 정본·문서: https://github.com/HeiTuz/MPW

이 트리는 설치 산출물이다. 수정은 정본 저장소에서 하고 installer로 재설치한다(`npx --yes github:HeiTuz/MPW -- --target hermes --force`).

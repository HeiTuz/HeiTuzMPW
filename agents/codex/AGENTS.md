# AGENTS.md — MPW 설치본 (GPT/Codex 호스트)

이 디렉터리는 MPW **설치 payload**다. 정본 저장소가 아니다 — 저장소 기여 규칙(커밋·리뷰·정본 단일성 유지보수)은 여기에 적용되지 않는다.

- 스킬 진입점은 `SKILL.md` 하나다. 프롬프트 작성·퇴고·라우팅 요청이 오면 `SKILL.md`를 읽고 그 계약을 따른다.
- 상세 규칙은 `references/`(templates·model-playbooks·adapters·image/*), 기계 계약은 `contracts/`, 컴파일러·검증기는 `scripts/`에 있다. 전부 이 디렉터리 기준 상대 경로로 유효하다.
- 이 트리를 제자리에서 편집하지 않는다. 수정은 정본 https://github.com/HeiTuz/MPW 에서 하고 installer로 재설치한다(`npx --yes github:HeiTuz/MPW -- --target codex --force`).
- 스킬 사용 중 실행하는 검증 명령: 프롬프트 길이 실측 `wc -m`, 이미지 프롬프트 검증 `node scripts/check_prompt.mjs`, 핸드오프 컴파일 `python3 scripts/compile_*.py`.

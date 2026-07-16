# AGENTS.md — 이 레포에서 일하는 에이전트 규칙

이 레포는 **HeiTuzMPW 스킬의 정본**이다. 배포 정본은 이 git 저장소와 `github:HeiTuz/HeiTuzMPW`이며, `~/.hermes/skills/…` 같은 설치 트리는 배포 산출물이다 — 설치 트리에서 편집한 규칙은 **이 저장소로 업스트림되어 푸시되기 전까지 배포되지 않은 것**이다.

## 하드라인 (위반 = 완료 아님)

1. **정본 단일성** — 규칙은 한 곳에서 1회 정의, 다른 파일은 참조만. 같은 규칙을 두 파일에 다시 쓰면 드리프트가 시작된다. 현재 정본 배치:
   - 네거티브 Tier 정책·철칙·사이즈 락: `references/image/compiler.md`
   - 레인별 게이트(비율·길이·필수 요소): `references/image/lanes.md` §레인 게이트 카드
   - 이미지 슬롯 기본값: `references/image/lanes.md` §이미지 슬롯 기본값
   - 추론 불가 슬롯 목록: `references/templates.md` §슬롯 자동 채움
   - jsonl 스키마: `references/image/production.md` §2
   - 영상 규칙: `references/image/lanes.md` §영상 공통 규칙
2. **기존 강점 후퇴 금지** — 위임 계약 6요소, 블록당 2000자 실측, 이미지 자기완결, 게이트 필요성 테스트, 레인 게이트 카드.
3. **예시 라벨 = 실측** — `(N자 실측)` 라벨은 뒤따르는 ```text 블록의 실제 문자수와 정확히 일치해야 한다. 예시를 고치면 라벨을 재계산한다. "약 N자" 표기 금지.
4. **모델·엔진 주장은 스탬프와 함께** — 근거 없는 모델 능력/플래그 서술 금지. 검증된 주장엔 날짜 스탬프(예: (YYYY-MM 실측)), 스탬프 6개월 경과 시 재검증 후 갱신.
5. **런타임 고유명은 `references/adapters.md`에만** — 코어 파일(SKILL.md·templates.md·image/*)에 특정 에이전트 제품명을 다시 들이지 않는다. 모델·엔진명(gpt-image-2, Higgsfield 등)은 허용.

## 검증 루틴 (변경 후 필수)

```sh
python3 scripts/lint.py               # 항상 — 라벨 실측·2000자·정본 단일성·유사문자
node scripts/check_prompt.mjs --test  # references/image/ 또는 검증기 변경 시 — 19 fixtures
```

검증기(`check_prompt.mjs`)와 문서 규칙이 어긋나면 어느 쪽이 맞는지 판정하고 한쪽을 고쳐 정렬한다 — 괴리를 남기는 게 최악이다(2026-07 캘리브레이션에서 헤더형 감지·조명 토큰 괴리를 이렇게 잡았다).

## 배포 게이트 — 세션 종료 전 필수

규칙·버전을 바꾼 세션은 아래를 통과해야 "배포 완료"다. 로컬 green은 배포가 아니다.

1. **롤백 폭탄 주의**: `heituz update`는 MPW를 GitHub에서 재설치한다. 푸시되지 않은 로컬 개선분은 업데이트 한 번에 통째로 구버전으로 덮인다. 2026-07-16에 v2.11~v2.13 세 릴리스분이 설치 트리에만 존재한 채 발견됐다 — 소비자 스킬의 fallback 관용 동작(가드너 사전 등) 때문에 겉으로는 멀쩡해 보여서 알아차리기 어렵다.
2. **버전 일치 확인(필수)**: 종료 전에 원격 버전이 로컬 SKILL.md/package.json과 같은지 직접 확인한다:
   ```sh
   curl -s https://raw.githubusercontent.com/HeiTuz/HeiTuzMPW/main/package.json | python3 -c "import json,sys; print(json.load(sys.stdin)['version'])"
   ```
   값이 다르면 미배포 상태이며 세션을 끝낼 수 없다.
3. **업스트림 절차**: 설치 트리의 편집분을 이 저장소에 반영(설치 트리 루트 `README.md`는 hermes 오버레이 산출물이므로 루트로 복사 금지, `agents/` 오버레이 본문은 canonical SKILL.md와 재동기화 + frontmatter version/canonical_source 갱신) → `npm test` exit 0 → 영어 커밋 → push → CI green 확인.

## 작업 방식

- 규칙 신설·변경 전에 해당 정본 파일을 먼저 읽는다. `SKILL.md`는 디스패치 커널 — 상세를 넣지 말고 references로 내린다(커널 비대화 금지).
- 큰 규칙 변경(레인 정책·모드 라우팅·게이트)은 반영 후 architect류 read-only 리뷰 1회를 거치고, 발견을 수정한 뒤 완료 처리한다.
- 이미지 어휘 추가는 가능하면 실측 캘리브레이션(실제 생성 대조)으로 뒷받침하고 `(YYYY-MM 실측)` 스탬프를 단다. `examples/`가 회귀 기준선이다 — 컴파일 규칙을 바꾸면 examples의 요청 3종을 재컴파일해 검증기 통과를 확인한다.
- 커밋 메시지는 영어, 변경 요지+검증 결과 포함. 관련 없는 리팩토링 금지.

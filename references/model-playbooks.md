# 모델 플레이북 (표면층) — Capability-first

**이 요약판이 운영 정본이다.** 모델명은 공개 라우팅 어휘가 아니다. 먼저 역할 권한을 정하고, 실제 모델·프로필 선택은 런타임 어댑터 또는 사용자 환경 설정에 둔다. 여기 없는 모델 능력·API 플래그를 지어내지 않는다.

**라우팅 계약 검토: 2026-07-10.** 아래 코어는 특정 공급자 우열 주장이 아니다. 모델별 행동 차이는 맨 아래 dated compatibility note에만 두고, 이미지/영상 엔진 주장은 templates/image 계층의 dated note가 이긴다. 각 노트의 날짜로부터 6개월 이상 지났거나 해당 런타임 메이저 버전이 바뀌었으면 재검증 전까지 단정하지 않는다.

## 역할·권한 라우팅

| 역할 | 권한 | 대표 작업 | 최소 capability |
|---|---|---|---|
| `prime` / integrator | 결과 소유, 결정, 상태, 통합, 최종 검증, 완료 claim | 전체 goal, 다중 레인 통합, release 판정 | balanced/agentic 기본; 고위험·광역 통합만 strongest-reasoning/high-risk |
| `planner` / architect | 읽기 전용 범위 파악, 옵션, 의존성, 위험, 수용 기준 설계 | 사전 조사, 경계 설계, acceptance matrix | bounded fact map은 fast/read-only; 아키텍처·고위험 판단은 strongest-reasoning/high-risk |
| `worker` / executor | 명시 목표와 acceptance가 있는 bounded slice 실행 | 파일 1~5개 구현, 자료 조사, fixture 작성 | 기계적 변환은 fast/read-only; 쓰기·도구 실행은 balanced/agentic |
| `critic` / verifier | frozen artifact와 같은 계약을 독립 검토 | code review, prompt review, release gate | bounded review는 balanced/agentic; release·보안·광역 검토는 strongest-reasoning/high-risk |

라우팅 원칙:

1. **권한을 만족하는 가장 낮은 capability**를 쓴다. 역할은 권한이고 capability는 난이도다. 특정 역할을 특정 강도에 영구 고정하지 않는다.
2. `prime`은 상태·결정·통합·최종 claim을 소유한다. worker가 "완료"를 주장해도 prime이 같은 표면으로 검증하기 전에는 완료가 아니다.
3. `planner`와 `critic`은 기본 read-only다. 둘 다 쓰는 경우 같은 frozen artifact와 같은 계약을 보게 하고, 둘 다 돌아온 뒤 prime이 결론을 합친다.
4. `worker`는 target, scope, acceptance, non-goals가 명시된 slice만 받는다. 누락된 acceptance를 worker에게 추론시키지 않는다.
5. per-role routing이 없는 런타임은 같은 모델에 역할 헤더만 붙인다. 역할 권한은 유지하고 모델명 고정은 하지 않는다.

## 구조·분해 규칙

### Topology-first intake

작업이 여러 산출물·레인·컴포넌트를 가질 수 있으면 깊게 들어가기 전에 최상위 결과 목록부터 확정한다. 가장 잘 설명된 컴포넌트 하나가 형제 scope를 가리면 실패다.

프롬프트에 넣을 축약 문장:

```text
먼저 최상위 결과/컴포넌트 목록을 1회 열거하고, 누락된 형제가 없는지 확인한 뒤 각 항목의 acceptance를 채운다. 한 항목의 세부가 충분하다는 이유로 다른 항목의 scope를 생략하지 않는다.
```

### Validation-coupled decomposition

같은 acceptance/review 표면을 공유하는 일은 함께 둔다. 병렬화는 파일이 나뉘는지가 아니라 **검증이 독립적인지**로 판단한다.

| 같이 둔다 | 나눠도 된다 |
|---|---|
| 같은 API 계약을 바꾸는 구현+테스트 | 독립 문서/fixture 작성 |
| 한 UI 화면의 상태·스타일·접근성 | 서로 다른 페이지나 독립 컴포넌트 |
| 하나의 release claim에 묶인 버전·README·installer | 각 런타임 install smoke |
| 같은 schema를 읽고 쓰는 producer/consumer | read-only 조사와 bounded implementation |

### Join gate

독립 레인이 있으면 prime은 아래 join gate 전에는 최종 승인하지 않는다.

```text
Join gate: 모든 worker 산출물, planner risk note, critic/verifier review가 같은 frozen artifact 기준으로 도착한 뒤에만 통합 판단을 내린다. 누락 레인이 있으면 완료가 아니라 pending/blocker다.
```

## Blocker classification

에스컬레이션은 human-only blocker에만 쓴다. 아래 표를 프롬프트에 맞게 압축해 넣는다.

| 분류 | 처리 |
|---|---|
| Resolvable | 파일 누락, 테스트 실패, 불명확한 내부 구현 선택, 재현 실패 초기 단계 → 탐색·대체 접근·최소 재현을 계속 |
| Scope-changing | 공개 API 변경, 비용/외부 호출, 데이터 삭제, product 방향 양자택일 → 선택지와 영향 정리 후 보고 |
| Human-only | 비밀값, 계정 권한, 승인 필요한 외부 발신, 사용자가 가진 원본 자료, 결과를 가르는 취향 결정 → 멈춰 질문 |

## Surface-matched evidence

검증 증거는 claim의 표면과 폭을 맞춘다.

| Claim | 맞는 증거 |
|---|---|
| CLI/installer가 작동한다 | 실제 명령 실행, 설치 위치의 파일 존재, help/error path |
| Web UI가 작동한다 | 실제 브라우저 조작, 콘솔/스크린샷/뷰포트 |
| API가 작동한다 | live process에 curl 또는 driver script |
| Prompt contract가 개선됐다 | fixture/길이/린트 + 예시 산출물이 새 규칙을 통과 |
| Release-ready다 | version sync, lint/test/smoke, public scan, diff check |

## 공통 배치 규칙

- 최우선 지시는 앞 또는 뒤, 벌크 자료는 중간, 긴 프롬프트는 자료 뒤 요구 재진술.
- 구조화 출력: 플랫폼에 JSON-schema 기능이 있으면 그걸 쓴다고 명시, 없으면 정확한 스키마+null-on-missing+필드 추가 금지를 프롬프트에.
- reasoning-effort 같은 런타임 레버가 있으면 프롬프트 우회보다 레버를 올린다. 레버명이 런타임 고유라면 adapters.md에만 둔다.
- outcome-first 모델/런타임에는 "더 깊게 생각해" 반복, 추론 과정 공개 요구, 긴 how 단계 강제를 피한다. 결과·경계·검증만 계약한다.
- 리터럴하게 해석하는 런타임에는 범위("첫 섹션만이 아니라 모든 섹션")와 이유를 짧게 붙인다.

## 목적 블록 (토큰 값어치 할 때만)

- 코딩: 기존 패턴·테스트·스코프 경계·무관 리팩토링 금지. 리뷰/평가: 커버리지와 필터링 분리 — 전 이슈를 신뢰도·심각도와 함께 보고, 필터링은 다운스트림("high만 보고" 생성 지시는 recall 붕괴).
- 리서치/팩트체크: 출처 투명성·불확실성·모순 처리·시점 확인.
- Grounded/RAG: knowledge cutoff+현재 날짜 명시, 제공 컨텍스트로 답 제한, 누락 정보 시 행동 정확 지정("정보 없음이라고 답하라") — 미지정 시 모델 지식이 샌다.
- 추출: 정확한 스키마, null-on-missing, 필드 추가 금지.
- 에이전트: 툴 지속성, 독립 읽기 병렬화, 빈 결과 복구, 최종 검증. 장기 실행엔 진행 그라운딩: "진행 보고 전 각 주장을 이 세션의 툴 결과와 대조, 증거를 지목할 수 있는 작업만 보고, 미검증은 미검증이라고 명시, 테스트 실패는 출력과 함께 보고."
- 영상: 정본은 templates.md §영상 공통 규칙(스토리보드 선행·씬당 지배 모션 1개·명사 나열 네거티브·비영어 대사 영어 지문). 이 파일엔 중복 서술하지 않는다.
- 슬라이드: 아웃라인 먼저(장수·서사·밀도·청중). 슬라이드 이미지: 16:9, 덱 전체 공유 스타일 블록(HEX·배경·타이포), 폰트명 대신 외형 서술("bold geometric sans"), 슬라이드당 메시지 1개.

## 호환 노트

구체 모델명·공급자명·프로필명은 실제 프롬프트 동작 차이를 보존하는 dated note에서만 쓴다. 공개 canonical routing vocabulary로 승격하지 않는다. 런타임별 설치와 역할 매핑은 [adapters.md](adapters.md)가 유일한 표면이다.

### 2026-07-07 — Claude 계열

- 범위를 리터럴하게 해석하므로 영향 범위와 이유를 짧게 함께 쓴다. `CRITICAL`/`MUST`/`NEVER`를 겹쳐 세우지 않는다.
- 비공개 추론 과정이나 chain-of-thought를 응답에 복사하라고 요구하지 않는다. 대신 결론의 근거를 짧게 요구한다.

### 2026-07-10 — GPT/Codex 계열

- outcome-first·최소 스캐폴딩을 쓴다. 결과·경계·검증·stop rule을 계약하고, 장황한 how나 "더 깊게 생각해" 반복은 제거한다.
- effort 레버가 있으면 프롬프트로 우회하지 않는다. 코딩 작업은 기존 프로젝트 패턴, 작은 diff, 실제 실행 검증을 요구한다.

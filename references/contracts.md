# GardenRecipe · PromptBundle 공유 계약

## 정본과 배포

`contracts/`는 이 인터페이스의 유일한 편집 정본이다. `image-reference-gardener`와 `design-reference-gardener`는 독립 설치를 위해 동일한 상대 경로 `contracts/`에 바이트 동일 미러를 포함할 수 있지만, 미러에서 계약을 편집하지 않는다. `contracts/manifest.json`의 SHA-256 목록이 릴리스 provenance다.

소스 레포가 편집 권한을 가진다. `~/.hermes/skills/...` 같은 설치본은 배포 산출물이며 직접 수정하지 않는다. 설치본 전용 변경이 발견되면 먼저 해당 소스 레포로 분리·검토한 뒤 배포한다. 계약 갱신 순서는 다음과 같다.

1. `HeiTuzMPW/contracts/`에서 스키마·검증기·fixture를 함께 변경한다.
2. manifest SHA-256을 갱신하고 `python3 scripts/test_contracts.py`를 통과한다.
3. `python3 scripts/sync_contracts.py --sync --dest <gardener-source>`로 각 독립 소스에 미러한다.
4. 각 스킬의 기존 설치 절차로 소스 전체를 설치본에 배포한다. 정본에서 설치본으로 역복사하지 않는다.
5. 정본 레포에서 `python3 scripts/sync_contracts.py --dest <gardener-source> --dest <installed-skill>`로 drift가 없음을 확인한다.

스키마 major가 다른 payload는 자동 승격하지 않는다. 기존 analysis JSON을 GardenRecipe로 바꾸는 adapter는 각 gardener 소관이고, 컴파일·PromptBundle 생성은 Master 소관이다. 이 문서는 분석 필드나 컴파일 규칙을 복제하지 않는다.

## 인터페이스 표

| 경계 | 생산자 → 소비자 | 필수 불변식 | 실패 방식 |
|---|---|---|---|
| `GardenRecipe v1` | image/design gardener → Master | opaque `ref_*` ID + `sha256:*`만, observation/inference 분리, 근거 confidence, qualified token, identity/subject lock, camera/light/palette evidence, exclusions, intended use | 검증 오류와 함께 컴파일 거부 |
| `PromptBundle v1` | Master → executor/bridge | validated recipe hash, 단일 `handoff`, 블록별 Unicode code point ≤2,000, lock 보존, variable axes, negatives, reference requirements, QC | handoff 거부; 자동 완화 금지 |
| `generation-handoff/v1` | Master → 모든 실행 adapter | `handoff` 객체만으로 실행 입력·lock·QC 해석 가능, 런타임 고유 key 없음 | adapter가 모르는 protocol이면 거부 |
| contract mirror | canonical source → independent source/install | manifest와 모든 listed file의 SHA-256 바이트 일치 | drift check 실패 |

## GardenRecipe v1

정본 스키마: `contracts/v1/garden-recipe.schema.json`.

- `source`에는 opaque `reference_id`와 content `reference_hash`만 둔다. 원본, caption, 파일/URL 경로, 계정·채팅 식별자, secret은 허용하지 않는다.
- `observations`는 `subject`, `camera`, `lighting`, `palette` 축을 항상 포함한다. 적용할 수 없는 축은 `status: not_applicable`과 빈 `items`로 명시한다. UI/layout은 선택 `layout` evidence와 `layout_tokens`를 사용한다.
- 각 inference는 `based_on` observation ID를 1개 이상 참조한다. 관찰 문장을 inference에 복사해 provenance를 흐리지 않는다.
- `locks.identity`는 해당 사항이 없으면 빈 배열일 수 있다. `locks.subject`는 비어 있을 수 없다.
- `intended_use`는 컴파일 목표의 mode/engine/goal만 나타낸다. 분석·저장 동작은 포함하지 않는다.

## PromptBundle v1

정본 스키마: `contracts/v1/prompt-bundle.schema.json`.

`PromptBundle`의 실행 표면은 `handoff` 하나다. Higgsfield를 포함한 실행 adapter는 다른 Master 내부 상태나 gardener 저장소를 읽지 않고 이 객체만 소비한다. 엔진 선택은 `handoff.engine` 값이며, 엔진별 비공개 옵션을 새 key로 추가하지 않는다.

각 `prompt_blocks[].unicode_char_count`는 JSON 문자열의 Unicode code point 수와 정확히 같아야 하고 2,000 이하여야 한다. 블록은 파일 경로나 외부 파일 읽기 지시 없이 자기완결이어야 한다. `--recipe` 교차 검증은 다음을 함께 증명한다.

- `source_recipe.recipe_id`와 canonical JSON SHA-256 일치
- `immutable_locks`의 identity/subject byte-for-byte 보존
- intended mode/engine 보존

## 검증 CLI

```sh
python3 contracts/validate.py contracts/v1/fixtures/garden-recipe.image.valid.json
python3 contracts/validate.py contracts/v1/fixtures/prompt-bundle.valid.json \
  --recipe contracts/v1/fixtures/garden-recipe.image.valid.json
python3 scripts/sync_contracts.py
python3 scripts/test_contracts.py
```

`contracts/validate.py`는 Python 표준 라이브러리만 사용하며 미러된 독립 스킬에서도 같은 명령 표면을 유지한다. 오류 시 exit 1, `--json` 사용 시 `{ok, schema_version, errors}`를 출력한다.

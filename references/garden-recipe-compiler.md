# GardenRecipe → PromptBundle 컴파일 계약

이 문서는 Master Prompt Writer의 구조화 컴파일·핸드오프 정본이다. GardenRecipe 필드 정의·개인정보 금지·provenance 검증은 `contracts/` 정본을 참조하며 여기서 반복하지 않는다. 이미지 문장 구성 규칙은 `references/image/compiler.md`, 레인 게이트는 `references/templates.md`가 정본이다.

## 입력 게이트

`scripts/compile_garden_recipe.py`는 `contracts/validate.py`가 오류 0개로 판정한 `garden-recipe/v1` JSON만 받는다. 원시 분석 JSON, 과거 자유형 레시피, schema version 없는 객체는 컴파일하지 않는다. 호출자가 먼저 gardener 출력물을 GardenRecipe로 승격·검증해야 한다. 계약 파일이 설치되지 않았으면 추측성 fallback 대신 `contract_validator_missing`으로 실패한다.

```sh
python3 scripts/compile_garden_recipe.py recipe.json --output prompt-bundle.json
```

## 출력 불변식

출력은 `prompt-bundle/v1`이며 다음을 한 번에 운반한다.

- 원본 GardenRecipe의 canonical hash와 recipe ID
- mode·engine 및 `generation-handoff/v1` 프로토콜
- Unicode code point 실측값이 붙은 자기완결 prompt block(각각 1~2000자); mode/engine에 따라 `templates.md` 레인 게이트 렌더러를 적용
- GardenRecipe와 byte-for-byte 의미가 같은 immutable identity/subject locks
- 명시적으로 허용된 축만 담는 variable axes; GardenRecipe v1에는 unlock 필드가 없으므로 빈 배열
- exclusions에서 보존한 negative constraints
- opaque reference ID 기반 reference requirement
- locks·negative·reference·길이를 검사하는 QC acceptance criteria

필수 공통 문맥·locks·exclusions를 유지한 자기완결 블록이 2000자를 넘으면 내용을 누락하거나 경로로 빼지 않고 `self_contained_prompt_overflow`로 실패한다. 긍정형 전용 이미지 레인의 exclusion은 의미가 검증된 positive boundary로 번역하고, 번역 규칙이 없으면 `untranslatable_positive_exclusion`으로 거부한다. gpt-image-2 입력은 관찰 evidence에서 서로 다른 `#RRGGBB` 3~5개가 확인되어야 한다. 호출자는 GardenRecipe를 보완·재검증한 뒤 다시 컴파일한다.

## 기계 핸드오프와 마이그레이션

기본 출력은 엔진 불가지 `PromptBundle`이다. 다운스트림은 `handoff.protocol`로 버전을 협상하고 `prompt_blocks`, `immutable_locks`, `variable_axes`, `negative_constraints`, `reference_requirements`, `qc_acceptance_criteria`를 직접 소비한다. 구형 소비자 어댑터는 `references/adapters.md`에만 정의한다.

검증:

```sh
python3 scripts/test_compile_garden_recipe.py
python3 contracts/validate.py prompt-bundle.json --recipe recipe.json
```

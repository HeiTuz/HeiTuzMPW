# 에디토리얼 패션 — Format B·템플릿·Soul 교차

우선순위: [../lanes.md](../lanes.md) §레인 게이트 카드 > [../compiler.md](../compiler.md) 철칙 > 이 파일. 철칙 전문은 [../compiler.md](../compiler.md).

## 1. Format B 정식 스펙 — 화보 플랫 콤마형

Format B는 콤마로 이어지는 평탄화 단문 1개다. 라벨 섹션(`Scene:` 등) 없이, 정해진 슬롯 순서대로 절을 이어 붙인다. 화보 배치에서 축 조합·diff·검증이 쉬우므로 에디토리얼 패션 레인의 기본형이다.

**슬롯 순서 (고정, 재배열 금지):**

```text
피사체 → 얼굴 → 헤어 → 장르앵커 → 장면/포즈 → 의상 → 구도 → 조명 → 팔레트 #HEX×3~5 → 질감 → [Tier-2 tail] → AR x:y
```

| 규칙 | 값 |
|---|---|
| 길이 밴드 | **350~450자** 타깃. 검증기는 300~550 밖이면 `W-LEN-B` |
| 기본 AR | **2:3** (`size: 1024x1536`) — 세로 화보 표준 |
| 장르앵커 | **`한국 남성지풍 클린 화보 컷`** — 고정 스타일 앵커, 모든 컷에 동일 문구 |
| HEX | 팔레트 절에 3~5개 (`E-FMT-B-HEX`) |
| 끝 토큰 | `AR x:y` 하나만, 앞머리 브래킷 금지. 철칙: ../compiler.md |
| Tier-2 tail | 선언된 tier 2에서만, [tier2-safety.md](tier2-safety.md) §2 규칙대로 팔레트·질감 뒤 · AR 직전 |

- 피사체 절이 attention을 가장 강하게 받는다. 단독 인물 선언과 성인 선언을 맨 앞에 둔다.
- 첫 절에서 `1인 단독`을 선언하면 군중 드리프트가 줄어든다. 네거티브가 아니라 긍정형으로 해결한다.
- 검증기 탐지: 라벨 섹션 <3 + 팔레트 키워드 또는 HEX≥3 + 끝 AR + 평탄 단문 → Format B로 자동 판정.

**완성 예제 — Tier-0 (일반 안전 화보, 네거티브 0개, 검증기 `ok:true` 확인 완료):**

```text
20대 후반 한국 여성 모델 1인 단독, 차분한 자신감이 도는 표정과 natural skin texture, visible pores, subtle film grain 은은한 윤기, 낮게 묶은 로우 번 헤어에 잔머리 몇 가닥, 한국 남성지풍 클린 화보 컷, 미니멀한 스튜디오 세트에서 우드 스툴에 걸터앉아 상체를 곧게 세우고 정면을 응시하는 포즈, 아이보리 오버사이즈 울 코트에 크림 터틀넥 니트와 하이웨이스트 와이드 슬랙스, 전신이 여유 있게 담기는 세로 구도 아이레벨 시점 상하 여백 넉넉, 부드러운 창가 자연광이 왼쪽에서 들어와 얼굴에 잔잔한 하이라이트와 긴 소프트 섀도, 팔레트 #F5F0E8 #D8CBB8 #8A7A66 #2E2A26, 매트한 울 질감과 니트 짜임 디테일에 미세한 필름 그레인, AR 2:3
```

실측: 400자. Tier 0이므로 부정문 0개다.

jsonl 레코드로 쓸 때:

```json
{"id": "hwabo_001", "ar": "2:3", "size": "1024x1536", "format": "B", "tier": 0, "quality": "high", "full_prompt": "…위 프롬프트 전문…"}
```

- `ar`과 프롬프트 끝 `AR` 토큰이 다르면 `E-REC-ARMATCH`.
- `size`가 6종 밖이면 `E-SIZE-LOCK`.
- 팔레트 HEX는 record와 `full_prompt` 양쪽에 존재해야 `W-PALETTE-MISS`가 발생하지 않는다.

### 1.1 슬롯 토큰 시스템 — 작성 단계 전용

12개 대괄호 슬롯은 작성·변주 단계의 내부 표기다. 배치 설계 때 슬롯 단위로 조합을 짜고, 방출 직전에 전부 실문구로 치환한다.

| 슬롯 | 정의 (1줄) | 채움 예 |
|---|---|---|
| `[PERSONA_LOCK]` | 컷 간 얼굴 일관성. 동일 페르소나 블록을 글자 단위로 반복 | 20대 후반 한국 여성 모델, 균형 잡힌 이목구비, 컷마다 동일 문구 |
| `[SOLO_ASSERT]` | 프레임 내 인물 1인 단독 선언 | 1인 단독, 프레임 안에 인물 한 명 |
| `[EDITORIAL_TONE]` | 장르앵커. 상업 화보/룩북 맥락 고정 | 한국 남성지풍 클린 화보 컷 |
| `[POSE_CONFIDENCE]` | 절제된 자신감의 바디랭귀지. 유혹 어휘 대체 | 상체를 곧게 세운 자세, 정면 응시, 턱 살짝 든 |
| `[SILHOUETTE]` | 신체가 아니라 실루엣 라인을 서술 | 길게 떨어지는 바디라인, 깨끗한 허리 라인, 목과 어깨 선 |
| `[OUTFIT_SCHEMA]` | 의상 4요소. 색·소재·의류종·핏/디테일 + 무로고 | 크림색 새틴 로브 세트, 발목 길이, 여유로운 핏 |
| `[GARMENT_SAFE_SET]` | 검증된 안전 의상 조합 풀에서 선택 | 테일러드 블레이저 + 불투명 이너 + 하이웨이스트 팬츠 |
| `[CAMERA_SLOT]` | 렌즈감·거리·시점·여백 1줄 | 85mm 느낌, 전신 세로, 아이레벨, 여백 넉넉 |
| `[LIGHT_MOMENT]` | 시간대·방향·soft/hard·그림자 결과. 장비명 직접 나열 금지 | 골든아워 사이드라이트, 길게 눕는 소프트 섀도 |
| `[COLOR_BREATH]` | 팔레트 키워드 + HEX 3~5 + 피사체·배경 온도 관계 | 팔레트 웜 뉴트럴 #F2E8DA #D9B48F #24303B |
| `[SAFETY_ASSERT]` | Tier-2 성인·비노출 선언. [tier2-safety.md](tier2-safety.md) §2 동결 문구 그대로 | [tier2-safety.md](tier2-safety.md) §2 참조. 수정 금지 |
| `[NEGATIVE_TAIL]` | Tier-2 전용 화이트리스트 부정 꼬리. [tier2-safety.md](tier2-safety.md) §2 동결 문구 | [tier2-safety.md](tier2-safety.md) §2 참조. 수정 금지 |

> SAFETY_ASSERT/NEGATIVE_TAIL의 유일한 정본은 [tier2-safety.md](tier2-safety.md) §2다. 이 파일에는 동결 문자열을 두지 않으며, 사용할 때 해당 문서에서 byte-for-byte로 인용한다.


배치 변주 규칙: 50컷 배치는 **`[OUTFIT_SCHEMA]×[CAMERA_SLOT]×[LIGHT_MOMENT]` 세 축만 변주**하고, `[SAFETY_ASSERT]`·`[SOLO_ASSERT]`·`[NEGATIVE_TAIL]`은 전 컷 고정한다. 안전 선언을 축에 섞으면 컷 간 비교 가능성과 안전성이 동시에 깨진다.

방출 규칙: 최종 프롬프트는 모든 슬롯이 치환된 상태여야 한다. 대괄호 토큰이 한 글자라도 남으면 검증기 `E-SLOT-LEAK`. 슬롯 표기는 이 문서와 배치 설계 메모 안에서만 산다. 철칙: ../compiler.md.
## 6. MASTER_TEMPLATE_V4 — 10섹션 페이스트 블록

판정문: **단독 인물 화보는 Format B 우선**이다. V4 10섹션은 룩북/챕터 시퀀스용이다.

| 섹션 | 내용 |
|---|---|
| §0 Creative Direction | 사진가 voice 한 단락 |
| §1 목적/용도 | 컬렉션명 + publication tier |
| §2 핵심 브리프·페르소나·장면 | 나이+캐스팅 + 미감 어휘 A/B/C에서 5~8개 |
| §3 필수 요소/Material | 의상 HEX·소재·핏, 배경 HEX+거리 |
| §4 환경 호흡 | 피부톤↔배경 HEX 색온도/밝기 통합 단락. 필수 |
| §5 빛의 모먼트 | L1~L6 여섯 줄, 장비 스펙은 결과로 환원 |
| §6 구도/공간 | C-NN + `Lens character:` + `Director signature:` |
| §7 재질/매체 | Texture + Film 3파트 |
| §8 제약 | 긍정형 스타일링 가이드로 작성. 예: `modest styling, tasteful editorial framing` |
| §9 narrative link | 전후 컷과 이어지는 제스처·색·공간 단서 |
| §10 출력 | `{ar} · {size}` |
| 메타 | look_id / style / look_title / ar / size / persona / collection / composition / chapter / status / output_path |

작성 원칙:

- 8룩 = 5챕터 시퀀스(1-ARRIVAL / 2-STILLNESS / 3-MATERIAL / 4-GESTURE / 5-ESCAPE).
- Composition C-NN은 8룩 unique. AR 7종: 2:3·4:5·1:1·3:2·9:16·16:9·4:3.
- §2 페르소나는 8룩 char-by-char 동일. 얼굴 일관성 목적이다.
- §5 L1~L6 전부 한 줄씩, 장비명 대신 결과. §6 `Lens character:` + `Director signature:` 필수.
- 미감 어휘를 사용하고 해부학/클리니컬 어휘는 쓰지 않는다. 이미지 첨부 없이 텍스트만으로 작성한다.
## 12. Format B ↔ Higgsfield Soul 교차 규칙

같은 화보 요청이라도 표면이 다르면 어휘를 변환한다. **gpt-image-2 Format B**로 갈 때는 슬롯 순서, 끝 `AR x:y`, HEX 3~5, Tier-2 assert/tail 페어, 장르앵커를 유지하고 사진 장비는 결과 기반 lens character로 압축한다. **Higgsfield Soul V2**로 갈 때는 6섹션 장문이 아니라 [../soul-v2-director.md](../soul-v2-director.md)의 4레이어 고정 순서(피사체·의상·동작·구도 → 미학·브랜드 앵커·환경 → 조명·그림자 → 카메라·렌즈·질감)를 따르는 콤마 명사구 1문단으로 줄이고, `[프리셋: X · 비율 — UI에서 선택]` 라벨을 본문 밖에 둔다. 빈 품질어는 보이는 특성 토큰으로 치환하고 카메라 바디 1·주 렌즈 1을 지킨다. 전역 팔레트·무드·컬러 그레이드는 Soul 2.0 웹 `Color signature`에 레퍼런스 1~20장을 넣어 전달하며, 대상별 역할형 HEX 3~5를 Soul 프롬프트 기본값으로 강제하지 않는다. Soul은 텍스트 렌더 정확도에 의존하지 않으므로 카피가 필요하면 gpt-image-2 컷으로 분리한다. 동일 인물 시리즈는 Soul ID 훈련 절차의 영역이므로 프롬프트에서 외모 반복으로 정체성을 고정하려 들지 않고, 장면·스타일·행동만 쓴다. 브랜드: Format B는 가상 컬렉션·가상 라벨 유지, Soul 레인은 디자인 앵커로 주1+보조1까지 허용하되 로고·텍스트 렌더와 의복 구조 치환은 금지. 공통으로 자기완결, 2000자, 긍정형 재서술, `natural skin texture, visible pores, subtle film grain`, 실재 인물 금지를 지킨다.

| 요청 요소 | Format B 변환 | Soul 변환 |
|---|---|---|
| 비율 | 끝에 `AR 2:3` | `[프리셋: Flash Editorial · 비율 2:3 — UI에서 선택]` 라벨 |
| 장르 | `한국 남성지풍 클린 화보 컷` 슬롯 | 프리셋 + `fashion editorial still` 성격만 본문에 |
| 안전 | Tier-2면 assert 첫 절 + tail AR 직전 | 긍정형 안전 스타일링 문장. 고정 tail을 본문에 억지 삽입하지 않음 |
| 조명 | `부드러운 창가 자연광이 왼쪽에서...` 같은 결과 절 | L3 골격: `direct on-camera flash, rapid highlight falloff, dense background shadow` 식 키라이트 방향·경도 명시 |
| 팔레트 | HEX 3~5 + 장면 팔레트 절 | `Color signature` 레퍼런스 1~20장으로 전역 톤 전달. 필요 시 `observed_palette` 3~5개는 soft handoff/QC metadata만 |
| 브랜드 | 가상 컬렉션·가상 라벨 | 디자인 앵커 ≤1+1 (매핑: [../soul-v2-director.md](../soul-v2-director.md)), 로고 렌더 금지 |
| 카메라·질감 | 장비명 대신 lens character | L4에 바디 1·렌즈 1·필름 색 반응·소재 질감 명시 (선택 로직: [../soul-v2-director.md](../soul-v2-director.md)) |
| 텍스트 | 필요 시 gpt-image-2 텍스트 렌더 가드 사용 | 텍스트 비의존. 카피 컷 분리 |

Soul 스틸 예시 형식 (4레이어: L1 피사체·의상·포즈·구도 → L2 미학·환경 → L3 조명 → L4 카메라·필름·질감):

```text
[프리셋: Flash Editorial · 비율 2:3 | Color signature: cool urban night reference 1장 — UI에서 선택/업로드]
late-20s Korean woman, 짧은 웨이브 단발, 무광 블랙 레더 재킷에 실버 이어커프, 밤의 도심 주차장 콘크리트 기둥 앞에 단독으로 서서 카메라를 정면으로 응시, three-quarter 구도 아이레벨, Y2K street snap 무드, 어두운 콘크리트와 소듐등 톤 배경, direct on-camera flash 특유의 강한 정면광과 rapid highlight falloff, 뒤로 짙게 떨어지는 dense shadow, Contax G2, 35mm lens, Fujifilm Superia 400 color response, cracked patent leather reflections, natural skin texture, visible pores, subtle film grain.
```
## 14. 작성 체크리스트

| 체크 | 통과 기준 |
|---|---|
| Format B | 슬롯 순서 고정, 라벨 섹션 없음, 끝 `AR x:y` 하나 |
| 길이 | Tier-0은 350~450자 타깃, 검증기 300~550 범위. Tier-2 예제 실측은 [tier2-safety.md](tier2-safety.md) §2 예시 라벨 참조 |
| 팔레트 | HEX 3~5개, record와 prompt 양쪽 일치 |
| 페르소나 | 가상 인물, 25+ 필요 시 선언, 실존 인물 금지 |
| 한국 로컬리티 | 국적 단독 금지, 스타일·공간·조명·잡지 톤의 관찰 가능한 단서 4축 이상 |
| 브랜드 | 가상 컬렉션·가상 라벨, 실재 상표 금지 |
| 피부 | `natural skin texture, visible pores, subtle film grain` exact token (정본: ../compiler.md 철칙) |
| Tier-2 | SAFETY_ASSERT byte-for-byte, NEGATIVE_TAIL byte-for-byte 또는 순서 보존 부분집합, tail 단독 금지, 휴리스틱 승격 금지 |
| 의상 | 신체/노출이 아니라 색·소재·의류종·핏/디테일·불투명 원단 |
| 사진 어휘 | 장비명 직접 나열보다 빛·심도·질감·색 결과 |
| 언어 혼용 | 한국어 골격 + 영어 기술 토큰, 렌더 텍스트는 한 줄 한 언어 |
| 철칙 참조 | 철칙 전문 복사 금지. 철칙: ../compiler.md 참조 |

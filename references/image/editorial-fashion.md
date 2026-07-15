# 에디토리얼 패션·화보·사진 레인 통합 정본

우선순위: ../templates.md §레인 게이트 카드 > compiler.md 철칙 > 이 파일. 철칙 전문은 [compiler.md](compiler.md).

이 문서는 성인 대상 패션 에디토리얼·룩북·사진 어휘를 하나로 묶은 작성 정본이다. 목적은 프롬프트가 **성인 25+ · 비노출 · 완전 불투명 원단 · 가상 페르소나**를 정책적으로 분명하게 선언하고, 결과물을 패션 제품·실루엣·사진 결과 중심으로 읽히게 만드는 것이다. 경계 탐색·우회 목적 사용은 이 레인 밖이다.

공통 판정문: 피사체는 실존 인물·실재 상표가 아니라 가상 페르소나와 가상 컬렉션이다. 피부는 `natural skin texture, visible pores, subtle film grain`를 유지한다. 워터마크·로고 제거 의도는 부정문이 아니라 `clean, brand-free, copy-free finish` 같은 긍정형 마감으로 쓴다. 철칙 전문은 복사하지 않고 **철칙: compiler.md**를 참조한다.

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
| 끝 토큰 | `AR x:y` 하나만, 앞머리 브래킷 금지. 철칙: compiler.md |
| Tier-2 tail | 선언된 tier 2에서만, §2 규칙대로 팔레트·질감 뒤 · AR 직전 |

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
| `[SAFETY_ASSERT]` | Tier-2 성인·비노출 선언. §2 동결 문구 그대로 | §2 참조. 수정 금지 |
| `[NEGATIVE_TAIL]` | Tier-2 전용 화이트리스트 부정 꼬리. §2 동결 문구 | §2 참조. 수정 금지 |

> 검증기(`scripts/check_prompt.mjs`)는 SAFETY_ASSERT를 앵커 기반으로, NEGATIVE_TAIL을 허용 목록 기반으로 검사한다 — 전문 바이트 대조가 아니므로 **고정 문자열의 정본은 이 문서**다. 붙여넣을 때 이 문서의 문자열을 그대로 쓴다.


배치 변주 규칙: 50컷 배치는 **`[OUTFIT_SCHEMA]×[CAMERA_SLOT]×[LIGHT_MOMENT]` 세 축만 변주**하고, `[SAFETY_ASSERT]`·`[SOLO_ASSERT]`·`[NEGATIVE_TAIL]`은 전 컷 고정한다. 안전 선언을 축에 섞으면 컷 간 비교 가능성과 안전성이 동시에 깨진다.

방출 규칙: 최종 프롬프트는 모든 슬롯이 치환된 상태여야 한다. 대괄호 토큰이 한 글자라도 남으면 검증기 `E-SLOT-LEAK`. 슬롯 표기는 이 문서와 배치 설계 메모 안에서만 산다. 철칙: compiler.md.

## 2. Tier-2 컴플라이언스 레인 (동결)

Tier-2는 **명시 선언 시에만** 활성화한다. 우선순위는 `--tier 2` 플래그 > jsonl `tier: 2` > jsonl `lane: "editorial"`다. **휴리스틱 승격 불가** — 검증기가 자동으로 켜주지 않는다. 아래 두 문구는 동결 스펙(SSOT)이다. **byte-for-byte 인용**하고 한 단어도 바꾸지 않는다.

**SAFETY_ASSERT (긍정형 — 피사체 절, 즉 프롬프트 첫 절에 배치):**

```text
adult Korean woman in her late 20s, 25+, original character, non-nude fashion editorial styling, fully opaque fabric, covered chest line, editorial upright pose
```

**NEGATIVE_TAIL (고정 순서 — 정확히 1회, 트레일링 `AR x:y` 직전 마지막 절):**

```text
no nudity, no nipple or genital exposure, no wardrobe malfunction, no extra people, no text, no watermark
```

| 규칙 | 내용 | 위반 코드 |
|---|---|---|
| 배치 | assert = 피사체 절(맨 앞), tail = AR 직전 마지막 절 | `E-TIER2-POS` |
| 횟수 | tail 정확히 1회 | `E-TIER2-DUP` |
| 페어링 | **tail 단독 금지**. assert 없이 tail만 있으면 invalid. 검증 앵커(`25+` / `original character` / `fully opaque` / `covered chest·bust` / `editorial upright`) ≥3개 존재해야 tail 허용 | `E-TIER2-PAIR` |
| 부분집합 | tail은 **순서 보존 부분집합만** 허용. 항목 삭제 OK, 임의 항목 추가 금지 | `E-TIER2-EXTRA` |
| 라벨 | `Negative:` 라벨 섹션은 전 티어 금지 | `E-NEG-SECTION` |
| 미선언 사용 | tier 0/1에서 tail 문구 사용 | `E-NEG-TIER` |

부분집합 예 — 텍스트·워터마크 걱정이 없는 컷이면 뒤 항목을 삭제할 수 있다. 순서는 그대로다.

```text
no nudity, no nipple or genital exposure, no wardrobe malfunction, no extra people
```

단, 항목을 끼워 넣거나(`no logo` 등) 순서를 바꾸면 `E-TIER2-EXTRA`다. 늘리고 싶은 제약은 tail이 아니라 본문 긍정형으로 해결한다. 예: 로고 → `브랜드 없는 클린 마감`.

**WHEN — 언제 Tier-2를 켜는가:**

| 상황 | Tier-2 |
|---|---|
| 피사체가 글래머·에디토리얼 + 노출성 의상 어휘(네크라인·보디스·스윔웨어 등) 포함 | 항상 켠다 |
| 일반 화보(코트·니트·수트 등 비노출 의상) | 끔. §1 Tier-0 형태 |
| photoreal 렌더 | 같은 소재라도 stylized보다 한 단계 더 보수적으로. 의상 어휘를 §3 원칙으로 한 칸 낮춤 |

**거부(refusal) 발생 시 대응 순서 (이 순서 고정):**

1. 의상 어휘를 더 안전한 쪽으로 교체한다. §3 치환 원칙 적용. 노출 서술 → 재단/실루엣 서술.
2. Tier-2 블록이 온전히 붙어 있는지 확인한다. assert 첫 절 + tail 마지막 절 + 페어링.

부정문을 늘리거나 표현을 우회적으로 비트는 건 대응이 아니다. 소재 자체를 안전한 서술로 바꾸는 것이 유일한 1차 수단이다.

실측: **v2 실험 B, 10피사체×2암**에서 NEGATIVE_TAIL이 이미지에 글자로 렌더된 사례 **0/9**. 장면 네거티브와 달리 tail은 렌더 누출이 없었다. 품질 비용도 없음(compliance·goal_fit 긍정형 단독 암과 동률). 거부율 개선은 N=10에서 판정 불가(양 암 모두 명시적 refusal 0건). Tier-2 채택 근거는 "무해 실증 + 정책 의도 명시"다.

**완성 예제 — Tier-2 포함:**

```text
adult Korean woman in her late 20s, 25+, original character, non-nude fashion editorial styling, fully opaque fabric, covered chest line, editorial upright pose, 맑은 눈매와 내추럴 메이크업, 느슨한 로우 번 헤어, 한국 남성지풍 클린 화보 컷, 리조트 풀 데크에 서서 어깨를 펴고 턱을 살짝 든 자세, 크림색 새틴 라운지 로브 세트와 발목 길이 와이드 팬츠 여유로운 핏, 전신 세로 구도 아이레벨 시점, 부드러운 골든아워 사이드라이트와 길게 눕는 그림자, 팔레트 #F2E8DA #D9B48F #7A8B99 #24303B, 새틴의 은은한 광택과 natural skin texture, visible pores, subtle film grain, no nudity, no nipple or genital exposure, no wardrobe malfunction, no extra people, no text, no watermark, AR 2:3
```

실측: 545자. Tier-2 동결 블록 265자(SAFETY_ASSERT 160+NEGATIVE_TAIL 105)가 포함되면 밴드 상단에 걸리는 게 정상이다. 한국어 본문을 압축해 550자를 넘기지 않는다. jsonl: `{"ar": "2:3", "size": "1024x1536", "tier": 2, "lane": "editorial", "format": "B"}`.

체크: 앵커 5종 전부 존재(`25+`·`original character`·`fully opaque`·`covered chest`·`editorial upright`) / tail 1회·AR 직전 / 캐노니컬 순서 그대로 / 대괄호 잔존 0.

## 3. 안전한 패션 서술 원칙 — 실루엣 우선

핵심 판정문: **"섹시한 신체"가 아니라 "성인 하이패션 실루엣"을 쓴다.** 실측상 해부학 중심(anatomy-forward) 문구는 실패하고, 의상·실루엣 중심(garment/silhouette-forward) 문구는 통과한다. 같은 컷도 서술 축을 바꾸면 결과가 갈린다.

| 실패 축 — 신체/노출 서술 | 성공 축 — 의상 디자인 서술 |
|---|---|
| 가슴 노출을 주제로 서술 | 네크라인을 의상 재단 디테일로 서술. 예: `구조적인 네크라인의 불투명 보디스` |
| 피부 노출 면적 강조 | 원단·핏·실루엣 강조. 예: `몸의 선을 따라 떨어지는 불투명 새틴` |
| seductive / provocative 류 무드 | `editorial poise`, `composed direct gaze`, `confident silhouette` |
| 신체 부위 나열 | `[SILHOUETTE]` 라인 어휘. 허리 라인, 어깨 선, 롱 레그 프로포션 |
| 노출 의상을 벗은 정도로 설명 | 제품 룩북 관점. 색·소재·의류종·재단·마감으로 설명 |

- 의상은 항상 패션 화보/룩북의 제품으로 다룬다. 시선의 목적어가 신체가 아니라 옷이 되게 한다.
- 의상 슬롯은 4요소(색·소재·의류종·핏/디테일)를 다 채운다. 요소가 빠질수록 모델이 노출 쪽으로 임의 보간할 여지가 커진다. `불투명(opaque)`은 노출성 의상 어휘가 하나라도 있으면 소재 수식어로 상시 부착한다.
- 반복 강조도 위험 신호다. 같은 노출 어휘를 컷마다 주제로 반복하면 단발성 사용보다 실패율이 뛴다. 배치에서는 노출성 어휘를 특정 컷 몇 개에만 두고 나머지는 다른 재단 축으로 분산한다.
- photoreal은 stylized/일러스트보다 판정이 엄격하다. 같은 의상이면 photoreal 쪽 어휘를 한 단계 보수적으로 쓴다.
- youth-coded 어휘(교복·학생·소녀 등)는 전면 금지다. Tier-2 여부와 무관하게 이 레인에 존재할 수 없다. 페르소나는 항상 실존 인물 아닌 가상(original character)으로 쓴다.
- 세부 생존/실패 토큰 표는 공개 문서에 두지 않는다. 로컬 상세판이 존재하면 그 토큰표를 우선 참조한다.

## 4. 패션 스타일 택소노미 21종

명명 규칙: 폴더 `NN_<snake>`, 스타일 ID `STY-NN`, 룩 ID `STY-NN-LMM`. 카탈로그 필드: ID / 슬러그 / 한글명 / 무드 한 줄 / 레퍼런스 인덱스. Tier-2 레인 필수 스타일은 `STY-15 boudoir_editorial`, `STY-17 resort_beach`다. 이 둘은 명시 선언된 Tier-2 컴플라이언스 레인에서만 작성한다.

| ID | slug | 한글명 | 패션 무드 판정문 | Tier |
|---|---|---|---|---|
| STY-01 | minimal_clean | 미니멀 클린 | 절제된 선, 뉴트럴 팔레트, 여백이 제품성을 만든다 | 0 |
| STY-02 | old_money | 올드 머니 | 로고 대신 소재·테일러링·관리된 태도가 계급감을 만든다 | 0 |
| STY-03 | y2k_revival | Y2K 리바이벌 | 글로시 표면, 로우 콘트라스트 팝 컬러, 액세서리 레이어가 시대감을 만든다 | 0/1 |
| STY-04 | streetwear | 스트리트웨어 | 오버사이즈 실루엣, 그래픽 없는 가상 라벨, 도시 질감이 컷을 지배한다 | 0 |
| STY-05 | avant_garde | 아방가르드 | 비대칭 구조와 과장된 볼륨이 신체보다 의상 구조를 앞세운다 | 0/1 |
| STY-06 | vintage_film_90s | 90년대 빈티지 필름 | 저채도, visible grain, 카탈로그식 정면성이 회고적 질감을 만든다 | 0 |
| STY-07 | cyberpunk_neon | 사이버펑크 네온 | practical neon glow와 젖은 반사면이 색 대비를 만든다 | 0/1 |
| STY-08 | cottagecore | 코티지코어 | 자연광, 리넨·면, 부드러운 목가적 배경이 의상 촉감을 만든다 | 0 |
| STY-09 | dark_academia | 다크 아카데미아 | 울·트위드·가죽 제본 톤, 낮은 키 조명이 지적 긴장을 만든다 | 0 |
| STY-10 | kpop_idol | K-pop 아이돌 | 클린 뷰티, 샤프한 헤어, 무대 전 사진 같은 선명도가 중심이다 | 0/1 |
| STY-11 | japanese_mode | 재패니즈 모드 | 블랙 레이어, 비대칭 드레이프, 빈 공간이 형태를 읽게 한다 | 0 |
| STY-12 | parisian_chic | 파리지앵 시크 | 트렌치·셔츠·데님, 낮은 채도의 도시광이 무심한 정제를 만든다 | 0 |
| STY-13 | athleisure_sporty | 애슬레저 스포티 | 기능성 원단의 매트·탄성 질감과 활동 자세가 실루엣을 만든다 | 0 |
| STY-14 | workwear_utility | 워크웨어 유틸리티 | 포켓·스티치·캔버스 질감이 실용적 리듬을 만든다 | 0 |
| STY-15 | boudoir_editorial | 부두아르 에디토리얼 | 라운지웨어를 성인 하이패션 제품 컷으로 읽히게 한다 | 2 필수 |
| STY-16 | bridal_modern | 모던 브라이덜 | 불투명 화이트 소재, 구조적 드레이프, 절제된 의례성이 중심이다 | 0/1 |
| STY-17 | resort_beach | 리조트 비치 | 리조트웨어를 노출이 아니라 소재·레이어·햇빛 반응으로 읽힌다 | 2 필수 |
| STY-18 | corporate_power | 코퍼레이트 파워 | 수트 구조, 견고한 어깨선, 도시 유리 반사가 권위를 만든다 | 0 |
| STY-19 | couture_runway | 쿠튀르 런웨이 | 과장된 실루엣과 공예적 표면이 단일 제품 히어로가 된다 | 0/1 |
| STY-20 | film_noir | 필름 누아르 | low key, split light, 단색 대비가 신비감을 만든다 | 0/1 |
| STY-21 | kpop_editorial_minimal | K-pop 에디토리얼 미니멀 | 아이돌식 정돈된 얼굴광과 미니멀 세트가 병치된다 | 0 |

### 4.1 style_card 한 장 구조

| 블록 | 필수 내용 |
|---|---|
| 정의 한 줄 | 해당 스타일이 다른 20종과 갈리는 기준 1문장 |
| 무드보드 키워드 | 톤·조명·컬러·소재·헤어메이크업 |
| 컬렉션 | 메인+보조 가상 브랜드. 실재 상표 금지 |
| 추천 페르소나 | P-NN 1순위·2순위 |
| 카메라 디폴트 | 바디명보다 결과 기반 lens character, 거리 m, 샷 사이즈 |
| 조명 디폴트 | L-NN, key:fill, 그림자·하이라이트 결과 |
| 컬러 그레이딩 | 필름 시뮬 결과, HEX 3~5 |
| 룩 리스트 | L01~L05 |
| 셀렉트 기준 | 성공/실패 판정문 |
| 꼭 들어갈 디테일 | 소재·마감·포즈·배경 중 해당 스타일 식별 요소 |

## 5. Persona DNA + Gold DNA

### 5.1 Persona DNA 고정 순서

챕터 내 신원 드리프트 0을 목표로, 페르소나 블록은 8룩 전체에서 char-by-char 동일하게 반복한다.

| 순서 | 필드 | 작성 규칙 |
|---|---|---|
| 1 | ethnicity+age | `20대 후반 한국 여성 모델`, Tier-2면 `adult Korean woman in her late 20s, 25+` |
| 2 | hair | 길이·질감·스타일. 예: 낮게 묶은 로우 번, 짧은 웨이브 단발 |
| 3 | eye | 쌍꺼풀·홍채색·눈매. 실존 인물 닮은꼴 금지 |
| 4 | beauty mark | 점 보통 1개. 위치를 1곳으로 고정 |
| 5 | lip finish | matte rose, sheer berry, satin nude 등 표면감 |
| 6 | outfit | 가상 컬렉션, 소재, HEX, 핏/디테일 |
| 7 | background | 배경 HEX, 소품 거리 m |
| 8 | camera distance | 카메라-피사체 거리 m, 샷 사이즈 |

### 5.2 Gold DNA — 367 골드 샘플 공통 규칙

| 축 | 공통 규칙 |
|---|---|
| 카메라 | 중형·필름 바디 선호. 렌즈 빈도 35>50>85>24mm. `Lens character:` 블록(초점거리·평면성·왜곡 적음·배경 분리) = 골드 100/100 필수 |
| 필름/컬러 | Portra·desaturated·teal&orange·CineStill 800T 빈출. Film 3파트 = `[필름] emulation — [스킨], [섀도], [하이라이트]. [매거진] roll-off` |
| 조명 | 결과 어휘로 쓴다. `key:fill 1:X` 비율 항상 명시. neon/practical/golden hour/창광 |
| 구도 | 카메라 거리 m 명시, rule of thirds, 포즈는 영문 표기(`contrapposto` 등), `Director signature:` 라인 = 골드 100/100 필수 |
| 무드 | light+color+expression 트리플. 예: `melancholic — desaturated cool, low key, downcast` |
| 페르소나 | ethnicity+age → hair → eye(쌍꺼풀·홍채색) → beauty mark(점 보통 1개) → lip finish → outfit(가상 브랜드+소재+HEX) → 배경 HEX → 카메라 거리 m. 4~7줄 |
| 퀄리티 앵커 | 전부 긍정형: `symmetrical facial features`, `eye-focus AF`, `natural skin texture, visible pores, subtle film grain`, 클로징 `The look must be unmistakable to a non-photographer viewer.`, `clean, brand-free, copy-free finish` |
| 배경 | 솔리드 컬러는 HEX, 소품은 m 거리 명시 |

v1→v2 업그레이드 7종: Lens character 블록 / Director signature 라인 / 클로징 명령문 / 페르소나 세분화(홍채·점·립피니시·쌍꺼풀) / Film 3파트 / 배경 HEX+소품 거리 / §1 publication tier.

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

## 7. 사진 어휘 풀 — 결과 기반 토큰

판정문: gpt-image-2에는 카메라·조명 장비명을 그대로 박지 말고 **결과(빛·심도·질감·색)**로 환원해서 쓴다. 표현은 긍정형 기본 + 티어 화이트리스트다. 장면 배제 부정문은 0개, `no ~`는 Tier-1/Tier-2 캐노니컬 문구로만 쓴다. SD 품질태그·가중치 문법은 쓰지 않는다.

### 7.1 심도·렌즈 character (결과로)

| 축 | 결과 토큰 |
|---|---|
| 광각 느낌 | `wide field of view, environment fully visible, mild edge stretch, deep focus front-to-back` |
| 표준 | `natural perspective, balanced compression, subject and setting in proportion` |
| 망원/압축 | `distant camera position, compressed perspective, flattened planes, subject lifted from a soft background` |
| 얕은 심도 | `shallow depth of field, background falls off softly into creamy blur` |
| 빈티지 보케 | `swirly painterly bokeh, gentle vintage rendering` |
| 아나모픽 | `wide cinematic frame, horizontal flares, oval highlights` |

### 7.2 조명 (방향·질·결과)

| 축 | 결과 토큰 |
|---|---|
| 패턴 | Rembrandt(뺨 삼각 하이라이트) / butterfly(코밑 나비 그림자) / split(반쪽광) / clamshell(위아래 부드러운 균등광) |
| 질 | `soft diffuse wraparound light, gentle gradient shadows` ↔ `hard directional light, crisp sharp-edged shadows` |
| 비율 | `key:fill 1:1`(평탄) / `1:2`(자연) / `1:3`(드라마틱). 결과로 `moderate shadow contrast` 식 병기 |
| 보조 | `cool rim light separating the edge`, `warm practical glow`, `window light from camera left` |
| 시간광 | golden hour 따뜻한 저각광 / blue hour 차분한 한기 / 정오 톱라이트 |

### 7.3 색·그레이딩 (HEX·켈빈·룩)

| 축 | 규칙 |
|---|---|
| 팔레트 | 항상 HEX 3~5개 |
| 색온도 | 켈빈 또는 `warm 3200K-feel` / `neutral` / `cool` |
| 조화 | complementary / analogous / triadic |
| 룩 | teal & orange, bleach bypass(저채도 고대비), desaturated muted, warm filmic roll-off |
| 필름 결과 | Portra 룩 = `warm skin, soft pastel midtones, gentle highlight roll-off`; Tri-X = `high-contrast monochrome, visible grain`; CineStill 800T = `tungsten night palette, soft red halation around highlights` |

### 7.4 필름/매체 3파트

```text
[필름 emulation] — [스킨], [섀도], [하이라이트]. [매거진/매체] characteristic roll-off
```

예: `Kodak Portra 400 emulation — warm luminous skin, soft green-leaning shadows, creamy highlights. Editorial magazine roll-off.`

조합 공식(감성 키워드는 필름/룩 이름과 병기해야 결과 차이가 선명해진다):

```text
[필름/룩 이름] + [빛의 방향] + [노출 방식] + [색감] + [그레인] + [분위기]
```

예: `Kodak Portra 400 film photography, soft window light from camera left, slightly overexposed highlights, warm creamy skin tones, fine film grain, low contrast, quiet romantic mood.`

#### 필름 스톡 결과 사전 (단어 단독 금지 — 결과·장면과 병기)

| 스톡 | 결과 묘사 | 어울리는 장면 | 영어 토큰 |
|---|---|---|---|
| Kodak Portra 400 | 부드러운 피부톤 · 크리미한 색감 · 낮은 대비 | 웨딩 · 인물 · 자연광 스냅 | `soft creamy skin, warm natural light, fine film grain` |
| Kodak Portra 800 | 크리미한 화이트 · 부드럽게 날린 하이라이트 · 로맨틱 | 웨딩 · 실내 인물 | `creamy white tones, soft blown-out highlights, warm glowing skin` |
| Kodak Gold 200 | 따뜻한 노란빛 · 선명한 색감 · 레트로 무드 | 일상 · 여행 · 가족사진 | `warm golden tones, everyday snapshot, retro feeling` |
| Fujifilm Pro 400H | 낮은 채도 · 부드러운 그린톤 · 청량함 | 숲 · 바다 · 자연 | `low saturation, soft green shift, dreamy softness` |
| Kodak Ektar 100 | 높은 채도 · 선명한 디테일 · 또렷함 | 풍경 · 건축 · 하늘 | `high saturation, sharp detail, vivid colors` |
| Ilford HP5 | 강한 명암 · 거친 그레인 · 흑백 다큐 무드 | 거리 스냅 · 흑백 인물 | `black and white, strong contrast, heavy grain` |

#### 노출·기법 결과 사전

| 기법 | 결과 묘사 | 영어 토큰 |
|---|---|---|
| Overexposure | 하이라이트를 밝게 날려 부드럽고 몽환적 | `soft overexposed highlights, bright airy atmosphere` |
| Underexposure | 그림자를 깊게 만들어 무게감 있는 분위기 | `slightly underexposed shadows, deep muted tones, dark cinematic mood` |
| Diffused light | 빛을 부드럽게 퍼뜨려 피부·경계가 자연스러움 | `soft diffused daylight, light filtered through sheer curtains` |
| Cross process | 색을 비현실적으로 변형한 실험적 필름 무드 | `cross-processed film colors, cyan color shift, unusual color palette` |
| Soft focus | 초점을 부드럽게 풀어 회상적·로맨틱 | `soft focus, dreamy blur, gentle lens softness` |
| Vignetting | 가장자리를 어둡게 해 시선을 중앙으로 | `subtle vignetting, center-focused composition` |
| Film grain | 필름 특유의 질감과 아날로그 분위기 | `fine film grain, visible analog texture` |

#### 감성 프리셋 (라벨 = 설명 + 키워드 블록, 필름/룩 이름과 병기)

| 감성 | 결과 묘사 | 키워드 블록 |
|---|---|---|
| 숲속 필름 | 습한 공기 · 낮은 채도 · 그린 그림자 | `Pro 400H-look, overexposed by one stop, green color shift, humid forest atmosphere, soft film grain` |
| 디스포저블 스냅 | 파스텔톤 · 핑크/크림 계열 · 소프트 포커스 | `disposable camera aesthetic, soft pastel tones, slight lens distortion, nostalgic snapshot` |
| 흐린 날 다큐 | 회색 하늘 · 다큐멘터리 무드 · 차분한 도시감 | `overcast diffused daylight, cool grey undertones, heavy visible grain, melancholic realism` |
| 시안 실험 | 시안·블루 색감 · 차갑고 몽환적 | `cross-processed film, cyan and blue shift, cool teal shadows, experimental film look` |
| 웨딩 필름 | 크리미한 화이트 · 자연광 · 로맨틱 | `Portra 800-look, creamy white tones, soft blown-out highlights, warm glowing skin` |
| 플래시 스냅 | 순간 포착 · 직사 플래시 · 생활감 | `snapshot aesthetic, direct flash, imperfect composition, natural unposed moment` |

### 7.5 구도·시지각

| 축 | 어휘 |
|---|---|
| 분할 | rule of thirds, golden ratio, centered iconic |
| 여백 | 카피용 여백 확보, 매거진 여백, Ma(여백의 호흡) |
| 유도 | leading lines, 시선 궤적, 삼각 안정 |
| 샷 사이즈 | ECU(극클로즈업) → CU → MS(미디엄) → FS(전신) → EWS(원경) |
| 앵글 | eye-level / low(우러름) / high(내려봄) / over-the-shoulder / dutch(기울임) |
| 거리 | 카메라-피사체 거리를 m로 명시 |

### 7.6 재질·후처리 (결과)

| 축 | 결과 토큰 |
|---|---|
| 표면 반응 | `matte buttery surface`, `wet specular highlights`, `translucent subsurface glow` |
| 마감 | `subtle film grain`, `gentle vignette`, `halation around bright edges`, `clean unbranded finish` |
| 피부 | `natural skin texture, visible pores, subtle film grain`, fine facial texture, soft tonal variation, fine vellus hair |
| 로고·워터마크 의도 | `clean, brand-free, copy-free finish` |

### 7.7 장르 즉시조합

| 장르 | 결과 토큰 묶음 |
|---|---|
| 패션 에디토리얼 | soft diffuse key + neutral palette + shallow DoF + magazine margins |
| 네온 누아르 | practical neon glow, teal&orange, wet reflective street, low-angle dutch |
| 스트리트 다큐 | available light, slightly desaturated, candid framing, deep focus |
| 제품 히어로 | clean softbox gradient, single hero spotlight, cool rim, HEX 배경 |
| 한국 웹툰 | soft cel shading, glossy K-beauty finish, dewy highlights, vertical scroll |

### 7.8 국문/영문 혼용 규칙

| 이기는 언어 | 영역 |
|---|---|
| **한국어 승** | 장면 서사 골격(누가·어디서·무엇을) · 무드 형용(아련한, 서늘한) · 문화 부하 명사(남성지풍, 청순, 물오른) · 렌더될 한글 카피 |
| **영어 승** | 심도(shallow DoF, deep focus) · 조명(rim light, key:fill 1:2, clamshell) · 필름(Portra emulation, halation) · 포즈 술어(contrapposto, over-the-shoulder) · 티어 고정 문구(Tier-1/Tier-2 캐노니컬) · HEX 주변 기술 토큰(gradient, duotone) |

하이브리드 패턴 = 한국어 골격 문장에 영어 기법 토큰 삽입.

1. `창가의 아침빛 아래 선 인물, soft window light from camera left, shallow DoF, 배경은 크림 #F7F4EC 단색.` — 한국어 골격 + 영어 조명/심도 토큰.
2. 조명 서술은 `부드러운 실내 자연광과 약한 필라이트` vs `soft window light, gentle fill` 어느 쪽도 허용한다. 단, 한 문장의 골격 언어는 통일한다. 반쪽짜리 번역체 금지.

렌더 텍스트는 한 줄 한 언어다. 한 따옴표 문자열 안 KO+EN 혼합 금지(`W-TEXT-MIXLANG`). 인물 신원은 고정 디테일로 쓴다. 실재 인물·상표 대신 가상 페르소나/브랜드를 쓴다.

## 8. 포즈·시선 디렉션 어휘

**방향 기준 규칙 (2026-07 실측).** 시선·조명 방향은 항상 뷰어 기준 영어 토큰(`camera left`/`camera right`)으로 명시한다 — 한국어 "왼쪽/오른쪽" 단독은 피사체 기준과 뷰어 기준이 갈려 실측에서 방향이 뒤집혔다.

포즈는 신체 노출이 아니라 균형·무게중심·의상 실루엣을 읽히게 하는 방향으로 쓴다. 영어 토큰은 룩북 현장에서 쓰는 짧은 술어만 삽입한다.

| 자세 축 | 정면 응시 | 시선 회피 | 오프카메라 | 의상 판독 포인트 |
|---|---|---|---|---|
| 서서 | `standing tall, composed direct gaze`, 발은 어깨너비, 상체 직립 | `downcast gaze`, 턱을 낮춰 코트 라펠 그림자 강조 | `looking off-camera left`, 몸은 정면·시선만 측면 | 코트 길이, 팬츠 브레이크, 숄더 라인 |
| 앉아서 | `seated upright, direct eye contact`, 무릎 각도 정돈 | `eyes lowered to hands`, 손끝은 원단 위 | `three-quarter seated, gaze beyond frame` | 스커트·팬츠 주름, 니트 짜임, 허리선 |
| 기대서 | `leaning against wall, calm front gaze`, 한쪽 어깨만 벽에 접촉 | `averted gaze`, 벽 그림자가 턱선 아래로 떨어짐 | `profile lean, looking past camera` | 재킷 구조, 소매 길이, 직물 눌림 |
| 걷는 중 | `mid-step, confident silhouette`, 카메라와 눈맞춤 | `candid stride, eyes to ground line` | `walking past camera, gaze to street` | 코트 플레어, 밑단 움직임, 신발 윤곽 |
| 회전/제스처 | `subtle contrapposto`, `relaxed neutral hips`, `balanced shoulders` | `hand adjusts cuff, eyes lowered` | `over-the-shoulder, gaze off frame` | 커프스, 칼라, 백 실루엣 |

안전 판정문: `seductive arch`, `provocative pose` 대신 `editorial upright pose`, `composed direct gaze`, `confident silhouette`, `subtle contrapposto`를 쓴다.

## 9. 소재·질감 어휘 — 빛 반응 기반

소재는 촉감 형용이 아니라 빛이 표면에서 어떻게 움직이는지로 쓴다. 의상 슬롯에는 색·소재·의류종·핏/디테일을 함께 둔다.

| 소재 | 빛 반응 결과 | 안전한 패션 문구 |
|---|---|---|
| 레더 leather | hard highlight가 접힌 부분에서 얇게 끊기고 그림자는 밀도 있게 떨어진다 | 무광 블랙 레더 재킷, 가는 하이라이트 라인, 구조적인 어깨선 |
| 스웨이드 suede | specular가 죽고 표면이 파우더처럼 빛을 흡수한다 | 카멜 스웨이드 코트, 매트한 파일감, 낮은 채도 |
| 니트 knit | 짜임 골이 soft shadow를 만들고 보풀 가장자리에 미세광이 생긴다 | 크림 터틀넥 니트, 리브 조직, visible knit texture |
| 울 wool | 매트한 면이 넓게 빛을 받으며 그림자가 부드럽다 | 아이보리 울 코트, 두꺼운 드레이프, 소프트 섀도 |
| 실크 silk | 흐르는 하이라이트가 곡면을 따라 이동하고 암부가 얇다 | 샴페인 실크 블라우스, liquid highlight, 부드러운 드레이프 |
| 새틴 satin | 넓은 광택 띠와 매끈한 roll-off가 생긴다 | 크림색 새틴 라운지 세트, 은은한 광택, 불투명 원단 |
| 데님 denim | 트윌 조직이 거친 입자를 만들고 엣지 워싱이 밝게 뜬다 | 인디고 데님 셋업, 트윌 결, 페이드 가장자리 |
| 트위드 tweed | 다색 실이 작은 점광처럼 분리되어 보인다 | 차콜 트위드 재킷, 직조 입자, 클래식 구조감 |
| 리넨 linen | 주름 골이 밝고 어두운 선을 만들며 표면이 건조하다 | 오트밀 리넨 셋업, dry matte surface, 여름 질감 |
| 오간자 organza | 반투명으로 쓰지 않는다. 레이어의 외곽선과 겹침 그림자만 제품 디테일로 쓴다 | 불투명 이너 위 구조적 오간자 오버레이, 레이어 그림자 |
| 벨벳 velvet | 빛 방향에 따라 깊은 암부와 부드러운 하이라이트가 갈린다 | 딥네이비 벨벳 블레이저, plush shadow, 낮은 광택 |
| 테크 패브릭 tech fabric | 물방울·코팅 표면에 작은 specular가 생긴다 | 그레이 테크 파카, 코팅 표면, crisp fold |

## 10. 조명 시그니처 레시피

장비명이 아니라 그림자·하이라이트 거동으로 쓴다. `key:fill` 비율은 결과 콘트라스트 판정을 같이 둔다.

| 레시피 | 결과 서술 | 그림자·하이라이트 거동 | 권장 스타일 |
|---|---|---|---|
| direct flash | `direct on-camera flash`, 피사체 전면이 선명하고 배경 그림자가 뒤로 붙는다 | 얼굴 중앙 하이라이트가 작고 강함, 코·턱 그림자가 뒤쪽으로 짧고 진하게 떨어짐 | STY-04, STY-07, STY-21 |
| 창가 자연광 | `soft window light from camera left`, 한쪽 얼굴에 넓은 하이라이트 | 그림자 경계가 길고 부드러움, 피부와 니트에 gradient shadow | STY-01, STY-08, STY-12 |
| 골든아워 역광 | `golden hour backlight`, 헤어와 어깨선에 따뜻한 rim | 얼굴은 gentle fill로 유지, 윤곽선에 amber halo, 긴 바닥 그림자 | STY-02, STY-17 |
| 오버캐스트 | `overcast diffuse sky`, 전체 contrast가 낮고 색이 균일 | 하이라이트가 넓게 눌리고 그림자 방향성이 약함, 소재 색 재현이 안정됨 | STY-06, STY-11, STY-14 |
| 네온 혼합 | `practical neon glow`, 피부와 의상 가장자리에 컬러 분리 | 한쪽 rim은 cyan, 반대쪽 fill은 magenta/orange, 젖은 표면에 color streak | STY-07, STY-20 |
| low key split | `low key split light, key:fill 1:3`, 얼굴 반쪽만 읽힌다 | 암부가 깊고 의상 윤곽은 rim으로 분리, 하이라이트 면적 작음 | STY-09, STY-20 |
| clamshell beauty | `clamshell soft light, key:fill 1:1`, 눈 밑 그림자 완화 | 위아래 균등광, 피부 결은 유지하고 하이라이트는 부드럽게 퍼짐 | STY-10, STY-16, STY-21 |

## 11. 시즌/로케이션 × 패션 무드 매트릭스

계절·장소는 의상과 빛의 이유를 만든다. 실존 브랜드·실존 인물·실재 행사명 없이 가상 컬렉션 맥락으로 쓴다.

| 시즌/로케이션 | 어울리는 스타일 | 무드 판정문 | 팔레트 예 |
|---|---|---|---|
| 봄 / 스튜디오 화이트 사이클로라마 | STY-01, STY-16, STY-21 | 공기감과 여백이 실루엣을 선명하게 만든다 | #F7F4EC #D8D2C4 #111111 |
| 여름 / 리조트 풀 데크 | STY-17, STY-12 | 햇빛 반사와 리넨·새틴 질감이 휴양감을 만든다. Tier-2 검토 필수 | #F2E8DA #D9B48F #7A8B99 #24303B |
| 가을 / 오래된 도서관·목재 인테리어 | STY-02, STY-09 | 웜 브라운과 울·트위드가 지적 밀도를 만든다 | #6B4E3D #B08A63 #2E2A26 |
| 겨울 / 콘크리트 도심 야외 | STY-04, STY-14, STY-18 | 차가운 배경과 두꺼운 아우터가 구조감을 만든다 | #2A2A2A #8D949A #D8D3C7 |
| 밤 / 네온 골목·주차장 | STY-07, STY-20 | practical neon과 젖은 반사가 색 대비를 만든다 | #1A2233 #00A6C8 #D94C8A |
| 흐린 날 / 루프톱·광장 | STY-06, STY-11 | diffuse sky가 소재와 패턴의 실제 색을 드러낸다 | #C8C5BD #5E646B #1E1E1E |
| 실내 / 호텔 라운지 | STY-02, STY-15, STY-18 | 낮은 practical glow가 광택 소재와 재단선을 읽게 한다 | #2B2420 #B89B72 #EFE2CC |

## 12. Format B ↔ Higgsfield Soul 교차 규칙

같은 화보 요청이라도 표면이 다르면 어휘를 변환한다. **gpt-image-2 Format B**로 갈 때는 슬롯 순서, 끝 `AR x:y`, HEX 3~5, Tier-2 assert/tail 페어, 장르앵커를 유지하고 사진 장비는 결과 기반 lens character로 압축한다. **Higgsfield Soul**로 갈 때는 6섹션 장문이 아니라 1문단으로 줄이고, `[프리셋: X · 비율 2:3 — UI에서 선택]` 라벨을 본문 밖에 둔다. 전역 팔레트·무드·컬러 그레이드는 Soul 2.0 웹 `Color signature`에 레퍼런스 1~20장을 넣어 전달하며, 대상별 역할형 HEX 3~5를 Soul 프롬프트 기본값으로 강제하지 않는다. Soul은 텍스트 렌더 정확도에 의존하지 않으므로 카피가 필요하면 gpt-image-2 컷으로 분리한다. 동일 인물 시리즈는 Soul ID 훈련 절차의 영역이므로 프롬프트에서 외모 반복으로 정체성을 고정하려 들지 않고, 장면·스타일·행동만 쓴다. 공통으로 자기완결, 2000자, 긍정형 재서술, `natural skin texture, visible pores, subtle film grain`, 실재 인물/상표 금지를 지킨다.

| 요청 요소 | Format B 변환 | Soul 변환 |
|---|---|---|
| 비율 | 끝에 `AR 2:3` | `[프리셋: Flash Editorial · 비율 2:3 — UI에서 선택]` 라벨 |
| 장르 | `한국 남성지풍 클린 화보 컷` 슬롯 | 프리셋 + `fashion editorial still` 성격만 본문에 |
| 안전 | Tier-2면 assert 첫 절 + tail AR 직전 | 긍정형 안전 스타일링 문장. 고정 tail을 본문에 억지 삽입하지 않음 |
| 조명 | `부드러운 창가 자연광이 왼쪽에서...` 같은 결과 절 | `soft window light from camera left` 중심의 짧은 1문단 |
| 팔레트 | HEX 3~5 + 장면 팔레트 절 | `Color signature` 레퍼런스 1~20장으로 전역 톤 전달. 필요 시 `observed_palette` 3~5개는 soft handoff/QC metadata만 |
| 텍스트 | 필요 시 gpt-image-2 텍스트 렌더 가드 사용 | 텍스트 비의존. 카피 컷 분리 |

Soul 스틸 예시 형식:

```text
[프리셋: Flash Editorial · 비율 2:3 | Color signature: cool urban night reference 1장 — UI에서 선택/업로드]
late-20s Korean woman, 짧은 웨이브 단발, 무광 블랙 레더 재킷에 실버 이어커프, 밤의 도심 주차장 콘크리트 기둥 앞에 단독으로 서서 카메라를 정면으로 응시. direct on-camera flash 특유의 강한 정면광, 뒤로 짙게 떨어지는 그림자, 배경은 어두운 콘크리트 톤으로 정리. natural skin texture, visible pores, subtle film grain.
```

## 13. 한국 로컬리티·리얼리티 매트릭스 (2026-07 리서치 반영)

판정문: `Korean`, `K-beauty`, `K-pop`, `Seoul`은 결과가 아니라 느슨한 방향어다. 방출 프롬프트에서는 국적·도시명만 두지 말고 **관찰 가능한 스타일·공간·조명·광고/잡지 톤**으로 환원한다. 얼굴형·피부색·체형을 국적에서 추론하지 않는다. 실존 인물·실재 상표·실재 매장명은 이미지 콘텐츠에 넣지 않는다.

| 축 | 채택 패턴 | 버리는 패턴 |
|---|---|---|
| 피사체 | 성인 가상 페르소나, 나이대, 헤어 길이/질감, 립 피니시, 의상 소재·핏 | `Korean girl` 단독, 실존 아이돌/배우 닮은꼴, 미성년 암시 |
| 피부·얼굴 | `natural skin texture, visible pores, subtle film grain`, hydrated skin-like base, blurred rose lip tint, brushed brows, soft diffused color, fine vellus hair | porcelain/pale/yellow 같은 국적-피부 고정(검증기 E-NAT-SKIN), plastic skin, 무자격 glass skin 과잉(자격화는 §15.3) |
| 헤어·뷰티 | 짧은 웨이브 단발, 로우 번, 잔머리, 투명한 베이스 메이크업, subtle blush처럼 보이는 스타일 | "K-beauty처럼" 단독, 완벽한 대칭/무결점 피부 |
| 의상 | 색·소재·의류종·핏/디테일 4요소 + 무로고 가상 컬렉션 | 실재 브랜드명, 노출/신체 중심 서술, 로고가 읽히는 의상 |
| 서울/한국 공간 | 성수 붉은 벽돌 창고형 파사드, 한남/한강진 갤러리 거리와 쇼룸 창 반사, 익선동 한옥 처마·목재 문틀, DDP 은회색 곡면 건축과 패션위크 플래시, 젖은 서울 골목의 전선·낮은 상가 셔터처럼 공간 구조·재료·빛으로 명시 | 유명 매장·상표 간판, 관광 스테레오타입만 나열, 읽히는 실재 로고 |
| 광고/잡지 톤 | 매거진 여백, editorial upright pose, direct on-camera flash, clamshell beauty, 창가 자연광, 무광 종이 질감 | "프리미엄/고급/트렌디" 같은 판정 불가 형용사 |
| 리얼리티 | 손이 소매를 잡아 직물 주름이 생김, 발 접지 그림자, 머리카락 잔결, 배경 반사와 피사체 림라이트 방향 일치 | bad hands/no AI 같은 부정 토큰, 손·발·배경 상호작용 생략 |
| 필름/컬러 | 필름명 1개 이하 + 결과 3파트: 스킨, 섀도, 하이라이트. 예: Portra = warm skin, soft pastel midtones, gentle highlight roll-off | Kodak/Fuji/CineStill/Portra를 한 컷에 다 쌓기, 8K/masterpiece/ultra-realistic |

실무 변환 규칙:
- "한국인 느낌" → 성인 가상 페르소나 + 헤어/메이크업/의상/공간/조명 중 최소 4축으로 쪼갠다.
- "서울 감성" → 지역명보다 건물 재료·거리 폭·간판 처리·시간대 빛·팔레트 HEX를 쓴다. 간판은 `abstract light shapes, no readable real brand text`가 아니라 한국어로 "간판은 추상적 빛 형태, 읽히는 실재 상표 없음"처럼 장면 긍정형으로 쓴다.
- "AI 같지 않게" → `natural skin texture`, 접지 그림자, 직물 장력, 손-소품 접촉, 배경 반사/그레인 통일처럼 보이는 증거로 바꾼다.
- "필름톤" → 필름명은 앵커일 뿐이다. 한 컷엔 하나의 emulation만 쓰고, skin/shadow/highlight/halation/grain 결과를 직접 쓴다.

## 14. 작성 체크리스트

| 체크 | 통과 기준 |
|---|---|
| Format B | 슬롯 순서 고정, 라벨 섹션 없음, 끝 `AR x:y` 하나 |
| 길이 | Tier-0은 350~450자 타깃, 검증기 300~550 범위. Tier-2 예제는 545자 실측 |
| 팔레트 | HEX 3~5개, record와 prompt 양쪽 일치 |
| 페르소나 | 가상 인물, 25+ 필요 시 선언, 실존 인물 금지 |
| 한국 로컬리티 | 국적 단독 금지, 스타일·공간·조명·잡지 톤의 관찰 가능한 단서 4축 이상 |
| 브랜드 | 가상 컬렉션·가상 라벨, 실재 상표 금지 |
| 피부 | `natural skin texture, visible pores, subtle film grain` exact token (정본: compiler.md 철칙) |
| Tier-2 | SAFETY_ASSERT byte-for-byte, NEGATIVE_TAIL byte-for-byte 또는 순서 보존 부분집합, tail 단독 금지, 휴리스틱 승격 금지 |
| 의상 | 신체/노출이 아니라 색·소재·의류종·핏/디테일·불투명 원단 |
| 사진 어휘 | 장비명 직접 나열보다 빛·심도·질감·색 결과 |
| 언어 혼용 | 한국어 골격 + 영어 기술 토큰, 렌더 텍스트는 한 줄 한 언어 |
| 철칙 참조 | 철칙 전문 복사 금지. 철칙: compiler.md 참조 |

## 15. 컨셉-콜리전 에디토리얼 그래머 (2026-07 패턴 증류 — 생성 캘리브레이션 미실시)

Format B(§1)의 특수형이다. **하나의 컨셉 충돌**(office utility × balletcore, 로맨틱 돌, 초현실 콜라주 등)을 문장으로 선언만 하지 않고 **의상 + 소품 + 포즈로 증명**하는 화보에 쓴다. §7.4(필름)·§8(포즈)·§10(조명)·§13(로컬리티)을 대체하지 않고 그 위에 조합 규칙만 얹는다. 원본 팩의 raw 프롬프트 산문은 복사하지 않고, 아래 재사용 규칙으로만 증류한다.

**그래머 체인 (Format B 슬롯의 특수 배열, 재배열 금지):**

```text
성인 가상 페르소나/정체성 앵커 → 헤어·뷰티 구체 → 컨셉 충돌(의상+소품으로 가시화) → 바디 포즈(가구/오브젝트 지오메트리 결속 또는 포착된 모션) → 배경 소재/색 → 빛 방향·그림자 거동 → 표정/시선 → 구도/네거티브 스페이스 → real skin/매체 마감 → AR x:y
```

- **컨셉은 서술하지 말고 증명한다.** `balletcore × office utility`라고 쓰는 것으로 끝내지 않는다 — 발레 플랫·튜튜형 미디 스커트(발레)와 테일러드 블레이저·클립보드·머그컵·스캐너(오피스)를 **동시에** 프레임에 둬야 충돌이 읽힌다. 소품이 컨셉의 증거다.
- **소품 배치 3형(전부 긍정형 장면 서술):** (a) moodboard형 — 가방 내용물을 벽/바닥에 펼쳐 배열, (b) 부유형 — 오브젝트를 얇은 실·공중에 세로로 매달아 정지, (c) 콜라주형 — 배경에 미니 복제 피규어·떠 있는 테이블.
- **바디 포즈 = 한 절에 가구 지오메트리 + 신체.** `크롬 튜뷸러 체어에 무릎을 세우고 웅크려`, `등받이에 리본이 묶인 우드 체어에 languid recline·한쪽 다리 뻗음`처럼 가구 형태와 몸의 결속을 한 절로 묶는다. 또는 포착된 모션: `mid-step`, `arms outstretched mid-motion`, `one knee raised`, `walking mid-stride`.
- **raw 팩의 부정 서술은 긍정 전환.** 원본이 즐겨 쓰는 `no smile`·`no extra people`은 Tier-0 방출 프롬프트에서 금지(철칙 2·E-NEG-001) — `무표정의 aloof gaze`, `프레임 안 인물 한 명`으로 재서술한다. 예외는 명시 선언된 Tier-2 캐노니컬 tail(§2)뿐이다.

### 15.1 조명·구도 이분 선택 (각 축에서 하나만)

| 축 | A 선택 | B 선택 |
|---|---|---|
| 조명 | `soft high-key strobe, near-shadowless 5500K` — 평면·에어리·매거진 클린 | `hard side strobe, long cast shadow` — 방향성 강한 드라마 |
| 구도 | `subject offset with generous negative space` — 카피·호흡 공간 | `centered symmetrical composition` — 아이코닉·정면성 |

두 조명을 겹치면 그림자 거동이 모순돼 판정 불가 이미지가 나온다. 한 컷은 각 축에서 하나만 고른다.

### 15.2 control token 보존 — 유명 사진 제어구

아래 두 구는 **장비 카탈로그 노이즈(철칙 4)나 콘텐츠 상표 모방(철칙 8)이 아니다.** 넓게 학습된 사진 제어 토큰이므로 §7.4·철칙 10의 결과 병기 원칙으로 **보존**한다 — 반사적으로 삭제하지 않는다. 철칙 4의 `Lens character:`·`Director signature:` 예외와 같은 계열이다.

| 제어구 | 병기할 관찰 결과 |
|---|---|
| `Portra film tonality` | warm skin, restrained saturation, gentle highlight roll-off, natural skin response |
| `medium-format clarity` | clean tonal separation, crisp garment edges, non-oversharpened rendering |

- 정확한 제품·상표·인물 묘사 규칙(철칙 8)은 이와 **별개**다 — 필름 룩 토큰은 콘텐츠 상표가 아니다.
- 한 컷에 필름명은 여전히 1개 이하(§13). `Portra film tonality`는 필름 스택이 아니라 톤 앵커로 1회만 쓴다.

### 15.3 문화 앵커 보존 — 자격화 조건

`Korean woman`·`East Asian woman` 같은 정체성 앵커와 romanized 한국 뷰티어(`chok-chok skin`, `aegyo-sal`, 자격화된 `glass skin translucency`)는 **생성 제어력이 있을 때 보존**한다. §13은 이들의 **무자격 남용**(국적 단독·과잉)을 버릴 뿐 반사적 삭제를 요구하지 않는다.

| 앵커 | 자격화 규칙 |
|---|---|
| `Korean woman` / `East Asian woman` | 성인 가상 페르소나로. 관찰 가능한 해부/스타일/마감과 페어. **국적에서 피부색·얼굴형·체형 추론 금지**(§13, 검증기 `E-NAT-SKIN`) |
| `chok-chok skin` / `aegyo-sal` | 로마자 유지 + 관찰 결과 병기: chok-chok → `hydrated dewy base`, aegyo-sal → `soft under-eye fullness` |
| `glass skin translucency` | **controlled beauty term.** `soft subsurface glow, 유리·플라스틱 광택 아님`으로 자격화. 무자격 사용은 §13의 `glass skin 과잉` |

### 15.4 글로우 적층 금지 — 주 글로우 1 + 매트존

피부 마감 토큰(`dewy`, `luminous skin`, `subsurface glow/sheen`, `wet-look`, `glass skin`, `high-shine`)을 4종 이상 쌓으면 피부가 플라스틱·유리로 뭉갠다. **주 글로우 레시피 1개**를 고르고, 필요하면 전략적 **매트존**(`매트한 T존`, `semi-matte cheek`, `restrained sheen`)으로 대비를 준다. 검증기 `W-GLOW-STACK`(글로우 4종+ 매트존 부재).

malformed 피부 토큰 정규화: `micro skin texture AI`·`skin texture AI` 류는 관찰 언어로 — `natural skin texture, visible pores, fine vellus hair`. 검증기 `E-SKIN-AI`. 국적-피부 고정 톤(`yellow skin` 류)은 `E-NAT-SKIN` — 피부는 국적이 아니라 관찰(hydrated base, flushed cheeks)로 쓴다.

**완성 예제 — Tier-0 컨셉-콜리전(부정문 0, 검증기 `ok:true`·경고 0 확인 완료):**

```text
20대 후반 East Asian woman 1인 단독, chok-chok skin(dewy base)과 aegyo-sal, 슬릭백 번, 한국 남성지풍 클린 화보 컷, office utility × balletcore 충돌: 그레이 테일러드 블레이저와 새틴 발레 플랫, 클립보드·머그컵을 실로 매단 부유 소품, 리본 묶인 우드 체어에 languid recline·한쪽 다리 뻗음, 크림 심리스 배경, soft high-key strobe near-shadowless 5500K, 무표정의 aloof gaze, subject offset with generous negative space, 팔레트 #F2ECE1 #D8C7B0 #9FB0C4 #2B2A28, glass skin translucency는 유리 아닌 soft subsurface glow로 자격화 + 매트한 T존, real skin texture with visible pores, Portra film tonality, medium-format clarity(clean tonal separation), AR 3:4
```

실측: 546자. Tier-0이므로 부정문 0개다. 이 예제는 `scripts/fixtures/good/editorial_collision.txt` 회귀 기준선과 동일하다.
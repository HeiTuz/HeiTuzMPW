# Higgsfield Soul V2 — 프롬프트 디렉터 정본

우선순위: [lanes.md](lanes.md) §레인 게이트 카드 > [compiler.md](compiler.md) 철칙 > 이 파일. 이 파일은 Soul V2 스틸·영상 **프롬프트 텍스트 설계**만 소유한다. 실행(모델 ID·CLI/MCP 파라미터·soul_id·크레딧·QC 루프)은 공식 higgsfield-* 스킬이 정본이다.

## 핵심 원칙

1. **비주얼 명사구.** 콤마로 이어지는 시각 토큰만 쓴다. 대화체·명령문("Create a beautiful image of…") 금지. 최종 프롬프트는 패션 디렉터의 샷 리스트처럼 읽혀야 한다.
2. **빈 품질어 금지.** `photorealistic, ultra-realistic, beautiful, masterpiece, best quality, stunning, highly detailed, professional photography, 8K`와 구체 처리 없는 `cinematic`은 쓰지 않는다. 눈에 보이는 특성으로 치환한다: `visible skin pores, controlled specular highlights, dry wool fibers, dense silk sheen, fine halation, compressed flash shadows, low-saturation tungsten palette, coarse 35mm grain, soft highlight roll-off`.
3. **모든 토큰은 결과를 바꿔야 한다.** 결과에 보이지 않는 단어는 삭제한다.

## 지시 우선순위 (충돌 시 위가 이긴다)

1. 정체성 보존 → 2. 제품 디자인·의복 구조 → 3. 요구된 동작·포즈 → 4. 카메라 앵글·크롭 → 5. 배경·로케이션 → 6. 미학 방향 → 7. 조명 → 8. 카메라·필름 처리 → 9. 장식 디테일.

스타일링을 위해 제품 정확도나 정체성 일관성을 희생하지 않는다.

## 필수 4레이어 구조

최종 프롬프트는 영어 **한 문단**, 콤마 명사구, 내부 헤딩 없이 아래 순서를 고정한다.

| 레이어 | 내용 | 골격 |
|---|---|---|
| L1 피사체·의상·동작·구도 | 성인 연령대, 젠더 표현, (제공 시) 민족, 정확한 실루엣·색·소재·봉제 디테일, 포즈/동작, 방향, 샷 사이즈·카메라 앵글 | `[adult subject], [identity], [exact silhouette+materials], [construction], [pose], [orientation], [shot size+angle]` |
| L2 미학·환경 | 에디토리얼 장르, 서브컬처/시대 영향, 브랜드 앵커(≤1+1), 로케이션·세트, 팔레트 | `[editorial direction], [primary brand language], [supporting aesthetic], [environment], [palette]` |
| L3 조명·분위기·그림자 | 키라이트 방향·질, 필 수준, 림, 그림자 경도·깊이, 색온도, 대기 효과, 하이라이트 거동 | `[key light+direction], [fill/contrast], [shadow quality], [atmosphere], [highlight behavior]` |
| L4 카메라·렌즈·모션·질감 | 카메라 바디 1개, 주 렌즈 1개, 심도, 필름 스톡/컬러 사이언스, 그레인, 소재 질감, (영상) 카메라 무브·속도·2차 모션·셔터 | 이미지: `[body], [lens], [DoF], [film/color], [grain+texture], [ratio]` / 영상: `[body], [lens], [camera move], [speed], [secondary motion], [shutter], [texture], [ratio]` |

- 물리적으로 모순되는 조명을 섞지 않는다 (`soft overcast + hard noon sun + neon night` 금지).
- 비율·프리셋·Color signature는 본문이 아니라 UI 라벨 줄로 분리한다 ([lanes.md](lanes.md) §Higgsfield 레인). 이 사용자 기본 비율은 3:4.
- **훈련된 Soul ID 사용 시 L1의 얼굴·민족·정체성 서술은 soul_id가 권위다.** 프롬프트에는 장면·스타일·행동·의상만 쓰고 외모 반복으로 정체성을 고정하려 들지 않는다 (기존 레인 규칙 유지).

## 브랜드 = 디자인 앵커

실루엣·스타일링·서브컬처·에디토리얼 방향을 명확히 할 때만 브랜드를 쓴다. **주 1개 + 보조 1개 최대.** 브랜드 수프 금지. 브랜드가 실제 의복 구조를 대체하면 안 되고, 로고·텍스트·워터마크 렌더는 요청 없이는 금지한다.

| 방향 | 앵커 |
|---|---|
| 페미닌 프레피·영 럭셔리 | Miu Miu |
| 절제된 지적 미니멀리즘 | Prada, Jil Sander |
| 조각적 블랙 테일러링 | Rick Owens |
| 오버사이즈 어반 볼륨 | Balenciaga |
| 해체주의 테일러링 | Maison Margiela |
| 관능적 바디컨셔스 글램 | Mugler |
| 로맨틱 투명·텍스처 | Simone Rocha |
| 콰이어트 럭셔리·소프트 테일러링 | The Row |
| 유틸리티 테크니컬 | Stone Island, Arc'teryx Veilance |
| 고프코어 | Salomon, Oakley, And Wander |
| 미래주의 바디 아키텍처 | Courrèges, Coperni |
| 다크 재패니즈 아방가르드 | Yohji Yamamoto, Comme des Garçons |
| 슬릭 코리안 에디토리얼 | RECTO, Low Classic, Andersson Bell |

사용자가 특정 의복을 제공하면 그 실제 구조를 보존한다. 브랜드 시그니처로 갈아치우지 않는다.

## 카메라·렌즈·필름·조명 선택 로직

목적에 맞는 시스템 하나만 고른다. 미디엄 포맷 스튜디오 카메라로 raw 디스포저블 컨셉을 찍지 않는다.

| 목적 | 카메라 | 렌즈 | 필름/질감 | 조명 골격 |
|---|---|---|---|---|
| 럭셔리 스튜디오 패션 | Hasselblad X2D 100C / H6D / Phase One XF IQ4 | 80–110mm | Portra 160, fine grain, restrained saturation | `large directional softbox camera left, negative fill right, controlled deep shadows, narrow rim light` |
| 뷰티 포트레이트 | Phase One XF IQ4 / X2D | 100–120mm macro | fine pore detail, controlled skin highlights | `frontal octabox above lens, reflector below chin, low shadow depth` |
| 에디토리얼 로케이션 | Leica SL2-S / Canon R5 / (무빙) Sony Venice 2 | 50/65/85mm | Portra 400, warm skin, muted greens, soft grain | `golden-hour low warm backlight, soft reflector fill` 또는 `cool diffused overcast, low contrast` |
| 스트리트 스냅·Y2K | Contax G2 / Nikon F5 / Canon EOS-1V | 28/35/45mm | Superia 400, cool green cast, uneven grain, direct flash | `direct on-camera flash, rapid falloff, dense background shadow` |
| 시네마틱 내러티브 | ARRI Alexa 35/LF / Venice 2 + Cooke S4·Panavision Primo·Atlas Orion | 35/50/75mm (ana 40–75mm) | Vision3 500T, tungsten bias, restrained halation | `cool cyan side light, warm tungsten practicals, deep negative fill, volumetric haze` |
| 감시·raw 디지털 | MiniDV / early-2000s CCD | security perspective | clipped highlights, digital noise | (timestamp는 명시 요청 시만) |
| 나이트 패션 | 위 로케이션/스트리트 계열 | — | Portra 800, visible grain, warm practicals, soft halation | — |
| 새추레이티드 유스 | — | — | Ektar 100, saturated reds/blues, crisp contrast | — |
| 그리티 모노크롬 | — | — | Tri-X 400, dense black grain | — |

- 렌즈 의도: 24mm 환경 왜곡 / 28mm 에너지 스트리트 / 35mm 다큐 친밀 / 50mm 중립 시네마틱 / 65mm 정제 에디토리얼 / 80–85mm 패션 압축 / 100–120mm 뷰티·디테일 / 아나모픽 40–75mm 수평 플레어. 얼굴 비율 왜곡이 허용되지 않으면 24/28mm 금지.
- 컷 하나 = 카메라 바디 1 + 주 렌즈 1. 키라이트의 방향과 경도는 항상 명시한다.
- 질감은 소재 특정으로: `brushed wool fibers, dense satin highlights, translucent organza layering, creased technical nylon, cracked patent leather, visible denim twill, natural skin pores, flyaway hair strands`.
- 필름 스톡 언어는 색 반응·그레인 제어이지 물리 필름 프레임 허가가 아니다. 보더리스는 `digital color grade inspired by Kodak Portra 160` 형으로 쓴다 (실측 교훈: higgsfield-generate references/soul-v2-borderless-film-look.md).

## 이미지 모드

- 프롬프트 하나 = 한 프레임. 다중 장면·그리드·콜라주·contact sheet·diptych·split은 명시 요청 없이는 만들지 않으며, **부정형("no collage")으로도 레이아웃 어휘를 본문에 넣지 않는다** — Soul이 리터럴 렌더한다. N장 = N개의 독립 싱글 포즈 프롬프트.
- 구도(클로즈업/체스트업/하프/스리쿼터/풀바디)를 항상 선언한다. 풀바디 요청이면 head-to-toe 가시성을 지킨다.
- 로고·텍스트·액세서리·잠금장치·포켓·심·하드웨어를 발명하지 않는다. 제품 중심 컷에서는 의복 정확도 > 브랜드 스타일링.

## 영상 모드

모션은 짧은 연속 이벤트 하나로 쓰고 4요소를 갖춘다: ① 피사체 모션 ② 카메라 모션 ③ 2차 물리 모션(원단·머리카락) ④ 연속성 보호.

예: `model takes two slow steps toward camera, gaze shifting from left to lens, controlled handheld push-in, coat hem and loose hair moving in the crosswind, stable facial identity, unchanged garment construction, continuous anatomy throughout the shot`

- 측정·관찰 가능한 동사만: `takes two slow steps, turns the head gradually, pivots ninety degrees, shifts weight onto the rear leg, slow clockwise orbit`. `moves beautifully, acts naturally, dynamic movement` 금지.
- 클립당 지배 카메라 모션 1개·핵심 행동 1개는 레인 공통 규칙대로 유지한다.
- 연속성 보호 대상: 얼굴 드리프트, 의복 변형, 색 변화, 액세서리 소실, 사지 추가·손가락 융합, 배경 워핑, 점프컷, 속도 요동, 원단 관통, 포즈 리셋. 네거티브 명사 나열은 **영상에서만** 허용된다 ([lanes.md](lanes.md) §영상 공통 규칙).
- 럭셔리는 느리고 절제된 모션, 스트리트/Y2K는 핸드헬드 불완전성·플래시 노출 변화 허용, 액션은 방향·속도·트래킹을 명시.

## 오류 예방 토큰

요청과 직접 관련된 것만 골라 짧게 삽입한다. 스틸은 긍정형: `stable facial identity, anatomically continuous limbs, natural hands, unchanged garment construction, plain unbranded hardware, clean logo-free garments, coherent single-vanishing-point background`. 범용 네거티브 리스트를 모든 프롬프트에 달지 않는다.

## 일관성 락 (시리즈·컬러웨이·앞뒤 컷)

시리즈 요청이면 비주얼 마스터를 고정하고 요청된 요소 하나만 바꾼다. 보존 목록: 인물·얼굴 구조·헤어·신체 비율, 의복 패턴·치수·심/포켓 위치·클로저·헴 길이·하드웨어·원단 거동·색, 피사체 스케일·카메라 거리·렌즈 패밀리·조명 방향·배경 톤. 컬러웨이는 색만, 앞뒤 컷은 어깨너비·토르소·허리·힙·소매·헴 폭 동일.

## 레퍼런스 이미지 처리

가장 명확한 풀뷰 = 실루엣 권위, 클로즈업 = 디테일·질감 권위, 앞/뒤/옆/안감 = 구조 권위. 같은 물리 디자인만 결합하고, 안 보이는 디테일은 발명하지 말고 보이는 의복과 일관된 최소 구조로 채운다. 비대칭 디자인은 그대로 보존하고, 착용 왜곡·일시적 주름은 패턴과 구분해 교정하되 의도된 드레이핑·개더·플리츠·디스트레싱·불규칙 헴은 보존한다. (단일 패스 레퍼런스 누출·탈취 대응 실행은 higgsfield-generate references/soul-v2-reference-pitfalls.md 정본.)

## 산출 형식

1. **Optimized Soul V2 Prompt** — 복사 가능한 코드블록 1개. 한 문단, 4레이어 순서, 내부 헤딩·설명·대안 없음, 붙여넣기 즉시 사용 가능, 2000자 실측.
2. **UI 라벨 줄** — 본문 밖: `[프리셋/비율/Color signature — UI에서 선택]`.
3. **한국어 디렉션 노트** — 브랜드·조명·카메라 선택 이유 각 1줄.
4. 유용할 때만 옵션(출력 타입·비율·길이·모션 강도)을 붙이고, 미지원 파라미터는 적지 않는다.

## 금지 행동

요청 전체 반복, 대화체 장문, 무관 미학 스택, 브랜드 >2, 렌즈 다중 혼용, 주야 조명 혼합, 의도 없는 스튜디오+다큐 혼합, 의복 디테일의 브랜드 시그니처 치환, 불필요 액세서리, 지시 없는 민족·연령·정체성·체형 변경, 1개 요청에 다중 프롬프트, 요청 없는 그리드·텍스트·로고, 빈 품질어 의존.

## 최종 체크

피사체 식별 가능 / 의복 시각적 구체성 / 포즈 물리성 / 카메라 앵글 명시 / 지배 미학 1개 / 브랜드 ≤1+1 / 조명 물리 정합 / 카메라 1·렌즈 1 / 소재 특정 질감 / 연속성 요건 포함 / 요청 디테일 보존·비요청 요소 배제 / 콤마 한 문단 / 무편집 즉시 사용. 하나라도 아니면 수정 후 전달한다.

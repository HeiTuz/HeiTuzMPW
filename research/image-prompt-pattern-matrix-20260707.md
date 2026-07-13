# Image Prompt Pattern Matrix — Lane B (2026-07-07)

## Scope

사진·영화 제작 어휘와 한국 로컬리티/뷰티·패션 표현을 `HeiTuzMPW` 이미지/영상 레인에 넣기 위한 패턴 매트릭스다. 채택 기준은 기존 정본과 동일하다: 장비명/브랜드/마법 토큰 나열이 아니라 결과 기반 어휘, 긍정형 계약, 실존 인물·실재 상표 생성 유도 금지, 한국인 묘사는 고정관념이 아니라 관찰 가능한 스타일·공간·조명·잡지 톤 중심.

## Source table

| # | URL | 유형 | 핵심 주장 | 채택 | 주의점 |
|---|---|---|---|---|---|
| 1 | https://www.viewbug.com/knowledge/lens-compression | 사진 실무 가이드 | 압축감은 렌즈 자체보다 카메라-피사체 거리로 생기는 원근 효과이며, 망원은 배경을 쌓고 광각은 공간을 과장한다. | 채택 | 프롬프트에는 `85mm` 단독보다 `distant camera position, compressed background, flattened planes`처럼 결과를 병기. |
| 2 | https://www.studiobinder.com/blog/types-of-camera-shot-angles-in-film/ | 영화 제작 가이드 | eye level/low/high/Dutch/overhead 등 앵글은 권력감·취약감·긴장·관찰감 같은 내러티브 의미를 만든다. | 채택 | 특정 영화·감독·배우 이름은 생성 프롬프트에 넣지 않는다. |
| 3 | https://www.studiobinder.com/blog/film-lighting-techniques/ | 영화 조명 가이드 | key/fill/back, soft/hard, low-key, motivated/practical, natural light가 장면의 감정과 시선 유도를 만든다. | 채택 | 조명 장비명 나열 대신 그림자 경계·방향·광원 동기·비율로 환원. |
| 4 | https://www.kodak.com/en/motion/page/processing-techniques/ | 공식 필름 처리 문서 | bleach bypass/skip bleach는 retained silver로 contrast 증가, shadow darkening, saturation 감소를 만든다. | 채택 | `bleach bypass`는 결과 토큰과 함께 쓰고, 미용 화보에는 과도 적용하지 않는다. |
| 5 | https://cinestillfilm.com/products/800tungsten-c41-36exp-35mm-high-speed-color-negative-135 | 공식/제조사 필름 문서 | 800T는 tungsten-balanced, low-light tungsten 상황용이며 remjet-free로 slight halation effect가 난다. | 부분 채택 | 필름/브랜드명을 이미지 내용의 상표로 쓰지 않고, `tungsten night palette, soft red halation around practical highlights`로 환원. |
| 6 | https://www.blackmagicdesign.com/products/davinciresolve/color | 공식 컬러 도구 문서 | grading은 scene mood를 바꾸며 lift/gamma/gain, contrast, saturation, hue, temperature, curves로 tonal range를 조절한다. | 채택 | 프롬프트는 도구 조작 지시가 아니라 `lifted blacks`, `muted saturation`, `cool shadows` 같은 결과로 작성. |
| 7 | https://retouch-flow.com/how-to-avoid-plastic-looking-skin-in-portrait-retouching/ | 리터칭 실무 가이드 | plastic skin은 과한 healing/blur/smoothing으로 texture·pores·depth가 사라질 때 생긴다. | 채택 | 생성 레인은 부정형 금지이므로 `preserved pores, fine texture, dimensional skin` 같은 긍정형으로 전환. |
| 8 | https://english.seoul.go.kr/seongsu-dong-cafe-street/ | 서울시 공식 로컬 자료 | 성수동은 옛 공장·창고 클러스터가 도시재생을 거쳐 예술·문화 공간, 카페, 부티크, 전시가 있는 지역이 됐다. | 채택 | “브루클린” 같은 타국 비유 금지. 붉은 벽돌·콘크리트·창고형 파사드·카페/부티크를 관찰어로 사용. |
| 9 | https://english.visitseoul.net/area/Hangangjin-Station/ENPk0c3m0 | 공식 관광 자료 | 한강진/한남 일대는 리움미술관·블루스퀘어·쇼룸·대로/골목 공존, 조용한 고급 주거지 감각과 연결된다. | 채택 | 실재 브랜드 거리명은 자료 표에만; 생성 프롬프트에는 `gallery-lined street`, `quiet boutique mood`로 환원. |
| 10 | https://english.seoul.go.kr/ikseon-dong-in-seoul/ | 서울시 공식 로컬 자료 | 익선동은 오래된 한옥 구조가 늘어선 골목과 현대적 카페·식당·상점이 공존하는 newtro 장소다. | 채택 | “전통 느낌”으로 뭉개지 말고 한옥 처마·기와·낮은 목재 문틀·좁은 골목·따뜻한 실내광으로 구체화. |
| 11 | https://english.seoul.go.kr/ddp-emerges-as-a-hub-for-fashion-exports-seoul-fashion-week-records-usd-7-54-million-in-orders/ | 서울시 공식 패션 자료 | DDP에서 서울패션위크 runway/presentation/trade show, 뷰티 체험, AI 피부 진단, personal color 상담 등이 열렸다. | 채택 | DDP/서울패션위크 에너지는 공간·플래시·쇼룸·거리 스냅으로 쓰고 실재 행사 로고/브랜드 렌더는 피함. |
| 12 | https://www.vogue.com/article/k-beauty-makeup-trends | 패션/뷰티 매체 | K-beauty 메이크업은 skin-first 접근, soft/diffused color, blurred lips, softer brows 등으로 설명된다. | 부분 채택 | 제품/브랜드/전문가 이름은 생성 프롬프트에서 제거. `hydrated skin-like base`, `blurred lip tint`, `soft diffused color`만 채택. |

## Pattern matrix

### 1. 필름톤·컬러 그레이딩

| 축 | 결과 기반 채택어 | 프롬프트 문장 패턴 | 버린 표현 |
|---|---|---|---|
| Portra류 부드러운 컬러 네거티브 | natural skin tones, soft pastel midtones, gentle highlight roll-off, fine grain | `warm-neutral color negative look — natural skin tones, soft pastel midtones, creamy highlights, fine grain` | `Kodak vibe`, `film masterpiece`, 근거 없는 “Portra exactly” |
| CineStill/텅스텐 밤 | tungsten night palette, soft red halation around practical highlights, cool shadows, neon bloom | `tungsten night palette with soft red halation around bright practicals, cool blue shadows, wet reflective street` | 필름명만 단독 나열, 과한 `neon cyberpunk` 일반화 |
| Fuji/녹색·청색 계열 | cool green-leaning shadows, restrained reds, airy highlights | `Fuji-inspired cool shadows and restrained reds, airy daylight highlights` | 브랜드 토큰만 던지기 |
| Bleach bypass | desaturated high contrast, darker richer shadows, silver-gray highlights, pronounced grain | `bleach-bypass grade: desaturated palette, higher contrast, darker shadows, metallic highlights, visible grain` | 뷰티·스킨 컷에 무차별 적용, `gritty` 단독 |
| Halation | soft red-orange glow around practical lights, controlled highlight bloom | `controlled halation around neon and window highlights, not across skin midtones` | 장면 전체를 뿌옇게 만드는 bloom 남발 |
| Grain/gate feel | fine film grain / coarse 16mm grain / subtle gate weave | `fine 35mm grain in shadows and midtones, clean skin detail preserved` | `8K`, `ultra detailed`, `sharp focus` |
| 컬러 그레이딩 | muted saturation, lifted blacks, crushed blacks, cool shadows, amber highlights, gentle S-curve | `muted saturation, lifted blacks, cool gray-blue shadows, warm amber practical highlights, gentle S-curve` | 도구명만 지시(`DaVinci look`, LUT 이름), 과한 teal-orange 기본값 |

### 2. 렌즈 character·카메라 거리

| 축 | 결과 기반 채택어 | 프롬프트 문장 패턴 | 버린 표현 |
|---|---|---|---|
| 광각/공간감 | close camera distance, wide field of view, mild edge stretch, foreground feels larger, deep space | `close camera distance with a wide field of view; foreground elements feel larger, background recedes, mild edge stretch` | `24mm`만 단독, 얼굴 클로즈업에 광각 왜곡 방치 |
| 표준/관찰감 | natural perspective, balanced subject-setting proportion, documentary realism | `eye-level natural perspective, subject and setting stay in proportion, observational framing` | `realistic`만 단독 |
| 망원/압축감 | distant camera position, compressed background, flattened planes, subject isolated | `distant camera position, compressed background layers, flattened city lights behind the subject, shallow DoF` | 압축을 렌즈 magic으로만 설명 |
| 얕은 심도 | background falls off softly, creamy blur, eye plane crisp | `shallow DoF, eye plane crisp, background falls off into creamy blur` | `bokeh`만 반복 |
| 와이드 왜곡 | exaggerated perspective, warped edges, looming foreground, claustrophobic interior | `low wide-angle shot from close range, looming foreground and warped edges for tension` | 패션 얼굴 화보에 왜곡 어휘 혼입 |

### 3. 앵글·구도·장면 의미

| 축 | 효과 | 프롬프트 문장 패턴 | 주의 |
|---|---|---|---|
| eye level | 자연·연결·관찰 | `eye-level camera, neutral human viewpoint, direct but calm connection` | “보통”으로 흐르지 않게 샷 사이즈 병기 |
| low angle | 힘·기념비성·위압 | `low-angle shot from below waist height, subject feels monumental, vertical lines rise behind them` | 권력감이 필요할 때만 |
| high angle | 취약·감시·고립 | `high-angle view looking down, figure small within the floor geometry, isolated negative space` | 인물 비하/고정관념 표현 금지 |
| Dutch tilt | 불안·긴장·주관성 | `subtle Dutch angle, tilted horizon, off-kilter framing, psychological tension` | 기본 화보에는 과함 |
| over-the-shoulder | 대화·친밀·관점 정렬 | `over-the-shoulder framing, foreground shoulder softly blurred, tense eye contact across the table` | 얼굴 식별 요구가 핵심이면 OTS가 약할 수 있음 |
| long-lens street | 밀도·도시 레이어 | `long-lens street frame from across the road, stacked signage glow as abstract light shapes` | 읽히는 실제 간판·상표 금지 |
| negative space | 잡지 여백·카피 영역 | `large clean negative space on camera right, subject anchored on left third` | 이미지 내 정확 카피는 gpt-image-2 텍스트 레인 규칙 적용 |

### 4. 조명·현실감·anti-AI 긍정형 계약

| 축 | 채택어 | 긍정형 계약 | 버린 표현 |
|---|---|---|---|
| Soft light | soft diffuse wraparound light, gentle gradient shadows | `soft window light from camera left, gentle gradient shadows across cheek and garment texture` | `beautiful light` |
| Hard light | hard directional light, crisp shadow edges | `hard side light with crisp shadow edges, graphic contrast on wall` | 장비명 스택 |
| Practical/motivated | visible practical lamp, motivated glow, diegetic source | `warm practical lamp visible in frame motivates the amber highlights; cool window fill balances shadows` | 출처 없는 “cinematic” |
| Low key | deep shadows, key:fill 1:3, rim separation | `low-key split light, key:fill 1:3, rim light separates coat edge from dark background` | `dark moody`만 단독 |
| Skin realism | natural skin texture, visible pores, fine vellus hair, tonal variation | `skin remains dimensional: visible pores, fine facial texture, soft tonal variation, natural under-eye texture` | `flawless poreless`, `plastic skin`, `AI gloss` |
| 손·의상·배경 상호작용 | hand pressure on fabric, garment fold shadows, grounded contact shadow | `one hand lightly grips the coat lapel, fabric compresses under fingers, contact shadows anchor the feet to pavement` | 손을 숨기거나 “perfect hands” 주문만 반복 |
| 합성/접지감 | consistent grain, matching shadow direction, edge imperfections | `subject and background share fine film grain, shadow direction matches the practical light, tiny natural edge imperfections remain` | 오려붙인 느낌을 부정문으로만 나열 |

### 5. 한국 로컬리티 — “Korean” 단어 대체 체계

| 로컬 축 | 관찰 가능한 표현 | 프롬프트 문장 패턴 | 쓰면 안 되는 표현 |
|---|---|---|---|
| 성수 | renovated warehouse facade, red brick, concrete storefront, café/pop-up retail, low industrial windows | `성수동의 낮은 붉은 벽돌 창고형 파사드 앞, 콘크리트 바닥과 카페 쇼윈도 반사, 오후 자연광` | `Korean Brooklyn`, 힙하다고만 쓰기 |
| 한남/한강진 | quiet gallery street, boutique showroom, limestone/gray facade, calm luxury, narrow alley off a boulevard | `한남동 갤러리 거리의 조용한 회색 석재 파사드, 쇼룸 창 반사, 절제된 뉴트럴 팔레트` | 실재 명품 브랜드/상표명 노출 |
| 익선동 | hanok eaves, tiled roof, warm wood frame, narrow human-scale alley, modern café interior inside old shell | `익선동 좁은 한옥 골목, 낮은 기와 처마와 따뜻한 목재 문틀, 안쪽은 현대적 카페 조명` | 막연한 `traditional Korean vibe`, 타문화 의상 혼동 |
| DDP/동대문 | silver-gray curved architecture, fashion-week crowd energy, flash, runway-adjacent street style | `DDP의 은회색 곡면 건축 앞, 저녁 스트리트 스타일 군중은 추상 실루엣, 카메라 플래시가 재킷 가장자리를 때림` | 실재 행사 로고·브랜드 카피 렌더 유도 |
| 서울 골목 | overhead wires, delivery bikes as blurred shapes, mixed old-new storefronts, wet pavement | `비 온 뒤 젖은 보도, 낮은 상가 셔터와 전선, 원경 배달 오토바이는 모션 블러 실루엣` | 간판 텍스트를 임의 생성하게 두기 |
| 잡지 톤 | Korean fashion editorial, Seoul street-style diary, boutique lookbook, skincare-first beauty campaign | `현대 서울 스타일 다이어리 같은 패션 에디토리얼, 과장 없는 쇼룸 룩북 톤` | “Asian look”, “exotic Seoul”, 국적을 외모 본질로 사용 |

### 6. 얼굴·피부·헤어·뷰티·패션 표현

| 축 | 안전한 표현 | 문장 패턴 | 금지/회피 |
|---|---|---|---|
| 인물 신원 | 가상 페르소나, 성인, 관찰 가능한 스타일 | `20대 후반 한국 여성 모델, 가상 페르소나, 짧은 웨이브 단발` | 실존 인물 닮은꼴, 특정 연예인 이름 |
| 얼굴 | 눈매·메이크업·표정은 관찰어로 | `차분한 정면 응시, 소프트 브라운 아이라인, muted rose lip tint` | 민족 본질화, 두상/피부색 단일화 |
| 피부 | hydrated but natural, satin/dewy high points, pores preserved | `hydrated skin-like base, cheekbones softly luminous, T-zone satin, visible pores preserved` | “모든 한국인은 glass skin”, 과도한 유리광 |
| 헤어 | 길이·질감·스타일 | `턱선 길이 블런트 보브, 살짝 젖은 듯한 결, 잔머리 몇 가닥` | 귀여움/동안 강요, youth-coded 표현 |
| 패션 | 의상 제품·실루엣·소재 중심 | `오버사이즈 차콜 블레이저, 크림 리브 니트, 와이드 데님, 무로고 구조적 숄더백` | 실재 상표, 노출·신체 중심 서술 |
| 뷰티 메이크업 | skin-first, blurred lip, brushed brows, diffused blush | `skin-first makeup, brushed brows, soft diffused blush, blurred rose lip tint` | 제품명/브랜드명, 과한 Western glam 대비식 일반화 |
| 포즈 | 균형·의상 판독 | `standing tall, composed direct gaze, one hand adjusts cuff, fabric folds visible` | seductive/provocative, 신체 부위 강조 |

### 7. 쓰면 안 되는 표현 목록

- `Korean`만 단독으로 던지고 얼굴·헤어·의상·공간·조명 설명을 생략.
- “Asian beauty”, “exotic”, “oriental”, “cute/pale/youthful Korean girl” 같은 고정관념·타자화 표현.
- 실존 인물·연예인·인플루언서 닮은꼴, 실재 패션/뷰티 브랜드 로고·쇼핑백·간판 렌더 요구.
- `masterpiece`, `best quality`, `8K`, `ultra detailed`, `trending on artstation`, 가중치 문법, SD-era magic token.
- 장비/필름명만 나열하고 결과를 쓰지 않는 문장: `85mm Portra CineStill cinematic`.
- 피부 문장 안의 모순: `natural pores`와 `flawless poreless plastic skin` 동시 요구.
- 한국 로컬리티를 전통 의상/한복/궁궐로 자동 치환. 전통 의상이 목적이 아니면 공간·빛·재질만 사용.
- 간판·브랜드·한글 카피가 핵심이 아닌데 배경에 읽히는 텍스트를 많이 두는 방식.

## Adoption summary for Lane C

| 반영 패턴 | 넣을 정본 후보 | 이유 |
|---|---|---|
| 필름/렌즈/앵글을 결과 기반 문장으로 환원 | `references/image/editorial-fashion.md` §사진 어휘 풀 보강 또는 신규 reference | 이미 정본에 방향은 있으나 Lane B 근거로 압축 패턴·로컬리티를 추가하면 실전성이 올라감. |
| 한국 로컬리티 안전 표현 체계 | `references/image/editorial-fashion.md` 또는 `references/templates.md` IMAGE 요약 | “Korean” 단독을 성수/한남/익선/DDP 공간 어휘로 대체하는 규칙이 필요. |
| 피부/anti-AI 긍정형 계약 | `references/templates.md` IMAGE 요약 + editorial-fashion 체크리스트 | 기존 `natural skin texture...`를 손·의상·접지감까지 확장. |
| 쓰면 안 되는 표현 | 신규 reference 또는 compiler 철칙 링크 | 금지어 정본 중복을 피하고, 이 파일은 후속 패치 근거로만 유지. |

## Verification notes

- 이 산출물은 연구 문서라 예시 코드펜스/실측 라벨을 추가하지 않았다.
- 기존 `references/templates.md` 레인 게이트(블록당 2000자, gpt-image-2/Higgsfield/COMPOSITE 정책)를 변경하지 않았다.
- `image-prompt`, `higgsfield-prompt-bridge`, `higgsfield-*`는 수정하지 않았다.

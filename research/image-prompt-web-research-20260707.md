# Image Prompt Web Research — Lane A (2026-07-07)

## 범위와 카운트

- 담당: Lane A — 커뮤니티 실전 사례 + YouTube/공식 문서 리서치.
- 수집: 총 29개 항목. 채택 후보 27개 + 접근 실패/대체 경로 기록 2개.
- 출처 유형: Reddit 커뮤니티, YouTube transcript, 공식 API/Help 문서, 공식 제품 페이지, 공식 리소스/블로그 가이드, 접근 실패 기록.
- 복구 경로: Reddit 기본 URL은 `read`에서 403이 발생해 `old.reddit.com`을 headless browser로 열어 제목/본문/댓글을 확인했다. YouTube는 `yt-dlp --write-auto-subs`로 자동자막을 `/tmp/mpw-youtube/*.vtt`에 저장해 검색·readback했다. Google Cloud Veo prompt guide는 429 CAPTCHA라 `ai.google.dev/gemini-api/docs/veo`의 동일 계열 공식 prompt guide 섹션으로 대체했다.

## 채택 요약

- 이미지 스틸: `subject / action / environment / style / lighting / details`의 최소 슬롯은 유지하되, SD식 품질 태그는 버리고 결과 기반 어휘로 환원한다. 피부 리얼리티는 `natural skin texture, visible pores, subtle film grain, subtle asymmetry/fine lines`처럼 관찰 가능한 질감으로 쓴다.
- 제품·포스터: 제품을 hero object로 두고 라벨 가독성, 반사, 그림자, 주변 소품의 종속성을 명시한다. 실재 상표는 생성 대상에서 제외하고 가상 브랜드/카피만 쓴다.
- 카메라/구도: `camera angle + shot type`을 앞에 두면 관점·프레이밍이 분명해진다. 장비명 나열은 모델별로 흔들리므로 결과(`soft background separation`, `long soft-edged shadows`, `wide-angle spatial exaggeration`)로 변환한다.
- 영상: prompt 본문은 장면·행동·분위기, UI preset/camera motion preset은 라벨로 분리한다. 한 클립에는 지배 모션 1개와 핵심 행동 1개만 둔다. 긴 서사는 스토리보드/shot breakdown으로 나눈다.
- 버린 패턴: `masterpiece/best quality/8k`, 가중치 문법, 장비 스펙 과잉, 범용 negative list, 실재 인물·상표 호출, “realistic/beautiful/cinematic” 단독 의존, 모든 모델에 timestamp를 강제하는 방식.

## 출처 표

| # | URL | 유형 | 핵심 주장 / 확인 내용 | 채택 여부 | 주의점 |
|---:|---|---|---|---|---|
| 1 | https://old.reddit.com/r/StableDiffusion/comments/1dd2az3/ | Reddit 커뮤니티 사례 | realistic skin 질의. 댓글 다수가 flawless skin보다 subtle flaws, pores, smile lines, blemish 계열이 자연스럽다고 보고. | 채택 | SD 가중치·negative 실험은 gpt-image/Higgsfield 정본으로 가져오지 않는다. |
| 2 | https://old.reddit.com/r/StableDiffusion/comments/14h9gc5/ | Reddit 커뮤니티 사례 | ultra detailed skin 사례. pore, moles, goosebumps, 해상도 영향, SD prompt dump 공유가 있었음. | 부분 채택 | `masterpiece`, `best quality`, 가중치 문법은 폐기. 채택은 피부 질감·해상도 중요성만. |
| 3 | https://old.reddit.com/r/StableDiffusion/comments/114bzra/ | Reddit 커뮤니티 사례 | porcelain skin 회피 질의. short prompt, soft lighting, film grain, close-up, face restoration이 결을 지울 수 있다는 조언. | 채택 | SD 모델/복원기 설정은 해당 런타임 전용이라 정본에는 결과 언어만 반영. |
| 4 | https://old.reddit.com/r/StableDiffusion/comments/1t9gv4z/ | Reddit 커뮤니티 사례 | “realism” 단독이 사진이 아니라 삽화 스타일로 오해될 수 있고, 원하는 사진 상태를 직접 쓰라는 논의. | 채택 | “ultra realism” 같은 추상어는 사진 캡처·질감·조명으로 치환. |
| 5 | https://old.reddit.com/r/midjourney/comments/1oa7jsj/ | Reddit 커뮤니티 사례 | realistic skin texture 사례. visible pores, freckles, peach fuzz, low-key lighting, composition, no beauty filter 방향을 공유. | 부분 채택 | 특정 인종/나이 표본은 고정값으로 채택하지 않는다. 관찰 가능한 피부·조명 구조만 반영. |
| 6 | https://old.reddit.com/r/midjourney/comments/15av1qj/ | Reddit 커뮤니티 사례 | 이미지 프롬프트 팁. 단어의 connotation이 장면 요소를 끌고 오므로 핵심 명사 선택이 중요하다는 실무 조언. | 채택 | Midjourney 플래그/문법은 gpt-image 정본에 반영하지 않음. |
| 7 | https://old.reddit.com/r/ChatGPT/comments/1tt8id6/ | Reddit 커뮤니티 사례 | ChatGPT 이미지 결과 공유. 빈티지 포스터 사례에서 ornate frame, typography, centered illustration, textured print look 등 구조가 성과로 제시됨. | 채택 | 실제 문구는 예시로만; HeiTuzMPW는 정확한 렌더 카피를 추론 불가 슬롯으로 유지. |
| 8 | https://old.reddit.com/r/GenAIGallery/comments/1td2eni/ | Reddit 커뮤니티 사례 | 상업 광고 포스터 템플릿. hero product, glossy reflections, sharp label details, premium lighting, 모델이 라벨을 가리지 않게 하는 구조. | 채택 | 실재 상표/제품명은 금지. 가상 브랜드와 합법적 사용자 제공 카피만. |
| 9 | https://old.reddit.com/r/ChatGPT/comments/1k52gaz/ | Reddit 커뮤니티 사례 | ChatGPT 이미지 style-transfer/poster prompts. JSON형 구조로 장면, 스케일, 조명, debris 같은 레이어를 분리. | 부분 채택 | 웹 모음 재복붙 금지. 구조화 방식만 반영. |
| 10 | https://old.reddit.com/r/OpenAI/comments/1kei0eb/ | Reddit 커뮤니티 사례 | photorealistic template 사례. lens behavior, natural grain, shadows/highlights, skin pore texture, environmental reflections 등 micro-detail을 나열. | 부분 채택 | 장비명·렌즈 수치 과잉은 결과 기반 어휘로 축약. “Works great” 댓글은 보조 근거만. |
| 11 | https://www.youtube.com/watch?v=zQI_pWw9qWo | YouTube transcript | `ALL Camera Movement Prompts...`; 자막 확인. 카메라 모션을 subject/environment와 분리해야 모델 오해가 줄고, dolly in/out 등 모션은 camera action으로 써야 한다고 설명. | 채택 | 38개 모션을 한 프롬프트에 쌓지 않는다. 클립당 1개. |
| 12 | https://www.youtube.com/watch?v=t_QLoXw8hDU | YouTube transcript | timestamp prompt 튜토리얼. Runway 4.5 문서의 timestamp 언급을 실험하며, 모든 프롬프트에 필요하지 않고 모델 지원 여부를 확인해야 한다고 결론. | 채택 | Kling 등 일부 모델에는 timestamp가 맞지 않을 수 있어 범용 규칙으로 금지. |
| 13 | https://www.youtube.com/watch?v=cGTBzed4S4w | YouTube transcript | “Stop Writing Prompts” 튜토리얼. 모델 공식 문서를 기준으로 모델별 prompt formatter를 만들고, 아이디어와 모델 문법을 분리한다는 접근. | 채택 | 자동 생성 프롬프트라도 정본 2000자·레인 게이트를 통과해야 한다. |
| 14 | https://www.youtube.com/watch?v=RBnq_7GC1As | YouTube transcript | Seedance/Kling/Veo 비교. Higgsfield 안에서 여러 비디오 모델을 스위칭하며 multi-shot capability를 비교하는 튜토리얼. | 부분 채택 | 비교 평가는 제작자 체감이므로 모델 능력 주장 정본에는 공식 문서 우선. |
| 15 | https://www.youtube.com/watch?v=QT1nMo-QMDQ | YouTube transcript | GPT Image 튜토리얼. 성공 prompt는 subject, action, environment, style, lighting, details 6요소를 갖춘다는 실험적 주장. | 채택 | `GPT Image 1.5` 명칭/능력은 공식 확인 전 정본 모델 주장으로 쓰지 않는다. 6요소 구조만 채택. |
| 16 | https://www.youtube.com/watch?v=6RAStep_3OI | YouTube transcript | Shopify 이미지 prompt tutorial. 같은 단순 장면도 prompt ingredient를 바꾸면 평온/공포 등 톤이 바뀌는 사례를 설명. | 채택 | Midjourney 중심 예시는 포터블한 구조·무드 분해만 반영. |
| 17 | https://platform.openai.com/docs/guides/image-generation | 공식 API 문서 | OpenAI Image API/Responses image tool은 text prompt로 생성·편집하며 출력 size/quality/format 조정 가능. `gpt-image-2` 포함. | 채택 | API 사용법이므로 prompt 문법을 과장하지 않는다. 생성 실행은 이 스킬 소관 아님. |
| 18 | https://help.openai.com/en/articles/11084440-chatgpt-image-library | 공식 Help 문서 | ChatGPT Images는 원하는 이미지를 설명하고, 편집 시 영역을 지정하거나 대화로 변경을 설명할 수 있으며 aspect ratio를 prompt/UI로 지정 가능. | 채택 | UI 조작 안내는 adapters/런타임 영역. 정본에는 “정확한 영역·비율 명시”만 반영. |
| 19 | https://help.runwayml.com/hc/en-us/articles/30586818553107-Gen-3-Alpha-Prompting-Guide | 공식 Help 문서 | 직접적이고 descriptive한 prompt, 긍정형, `[camera movement]: [establishing scene]. [details]`, image+text는 입력 이미지를 재묘사하지 말고 motion만 쓰라는 가이드. | 채택 | Gen-3는 2026-07-30 종료 공지 있음. 원칙은 유지하되 모델명 스탬프 주의. |
| 20 | https://runwayml.com/resources/ai-camera-angle-shot-type-tips | 공식 리소스 | camera angle은 perspective, shot type은 framing. `low-angle medium close-up`처럼 결합하면 정밀도가 올라간다고 설명. | 채택 | 카메라 용어는 앞배치하되 장비명 나열로 확장하지 않는다. |
| 21 | https://runwayml.com/resources/ai-video-prompting-guide | 공식 리소스 | 영상 prompt 구조: camera movement + scene + action + details. 긍정형, 5–10초, one action per prompt, shot type first, one primary movement. | 채택 | HeiTuzMPW 영상 레인 “씬당 지배 모션 1개” 보강 근거. |
| 22 | https://higgsfield.ai/camera-controls | 공식 제품 페이지 | Higgsfield Camera Controls는 Dolly, Crash Zoom, FPV Drone, Bullet Time, Orbit, Static 등 50+ named motion presets를 제공. | 채택 | prompt 본문에 모션을 중복 장황하게 쓰지 말고 UI preset 라벨로 분리. |
| 23 | https://higgsfield.ai/soul-intro | 공식 제품 페이지 | Soul 2.0은 fashion-aware, culture-native, photoreal output, 20+ curated presets, Soul ID, HEX/moodboard를 강조. | 채택 | Soul ID는 훈련/레퍼런스 절차 영역. prompt로 외모 반복 고정하려 들지 않는다. |
| 24 | https://kling.ai/quickstart/klingai-video-3-model-user-guide | 공식 모델 가이드 | Kling VIDEO 3.0은 multi-shot, element reference, native audio, multilingual dialogue, 3–15s duration, custom multi-shot control을 문서화. | 채택 | multi-shot을 지원하더라도 짧은 클립은 shot별 역할을 분리. 실재 인물/브랜드 텍스트 유도 금지. |
| 25 | https://ai.google.dev/gemini-api/docs/veo | 공식 API 문서 | Veo prompt guide는 subject, action, style, camera positioning/motion, composition, focus/lens effects, ambiance, audio cues, reference images를 prompt 요소로 제시. | 채택 | audio/dialogue는 정확한 대사·효과음을 요구할 때만. 1024 token 제한 등 엔진 제약 주의. |
| 26 | https://seed.bytedance.com/en/seedance | 공식 제품 페이지 | Seedance 1.0은 text/image 기반 multi-shot video, smooth/stable motion, prompt following, subject/style/atmosphere consistency를 강조. | 채택 | 공식 페이지는 기능 홍보 중심이라 prompt 작성 세부는 다른 가이드와 교차 확인. |
| 27 | https://higgsfield.ai/blog/seedance-prompting-guide | 공식/준공식 제품 블로그 | Seedance 2.0 guide는 shot count, total duration, aspect ratio를 upfront로 쓰고 shot별 action을 번호로 분리하라고 안내. | 채택 | 블로그 예시의 `no 3D/no cartoon` 등 negative는 모델별 사례로만 보고, Runway류 positive rule과 충돌 시 레인별 우선. |
| 28 | https://cloud.google.com/vertex-ai/generative-ai/docs/video/video-gen-prompt-guide | 접근 실패 기록 | `read`에서 429 CAPTCHA 발생. 같은 Google 계열 `ai.google.dev/gemini-api/docs/veo` prompt guide 섹션으로 대체. | 대체 출처 사용 | 실패를 출처 수에 산입하지 않는다. |
| 29 | https://higgsfield.ai/blog/Prompt-Guide-to-Cinematic-AI-Videos | 접근 실패 기록 | web search에는 공식 Higgsfield blog로 색인되나 `read`는 404. camera-controls, soul-intro, seedance guide로 대체. | 대체 출처 사용 | 실패를 출처 수에 산입하지 않는다. |

## Lane C 패치 후보

1. `references/templates.md` 영상 공통 규칙에 Runway/YouTube 근거 기반으로 “one action + one primary movement per clip”과 “image-to-video는 이미지 재묘사보다 motion만”을 더 분명히 한다.
2. `references/templates.md` Higgsfield 레인에 UI preset 라벨과 prompt body 분리를 유지하고, camera-controls의 named motion preset은 본문이 아니라 라벨로 둔다고 재강조한다.
3. `references/image/compiler.md` 또는 `references/image/editorial-fashion.md`에는 커뮤니티 skin realism 패턴을 장비/SD 태그 없이 `natural skin texture, visible pores, subtle film grain, fine texture under directional light` 같은 결과 어휘로만 보강한다.
4. 제품·포스터 계열에는 hero object, readable label, glossy/reflection/shadow, supporting prop hierarchy, brand-free finish를 체크 항목으로 제안한다.
5. timestamp prompt는 “모델별 지원이 확인된 advanced video control”로만 두고 기본 영상 레인에는 넣지 않는다.

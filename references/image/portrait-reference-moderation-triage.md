# Portrait-reference moderation triage

Use when an image generator returns a generic sensitive-content warning during portrait reference or character-sheet work.

## Diagnose before rewriting

Use this minimal comparison:

1. Text only, no reference image, with a neutral portrait prompt.
2. One reference image with an extremely short scene-only prompt.
3. A different clearly synthetic portrait with the same short prompt, when available.

Interpretation:

- Text-only blocked: simplify the prompt first.
- Text-only passes but one-image input blocks: input-image moderation is the likely gate; repeated synonym rewrites are low-value.
- One reference passes but multiple references block: multi-reference composition is the likely trigger; use one authoritative reference or a supported character-reference surface.
- A specific reference blocks while another synthetic portrait passes: treat it as image-specific moderation or resemblance detection, regardless of how the source was generated.

Do not claim certainty about the provider's internal classifier unless its documentation or response exposes the reason. Say `likely input-image moderation` rather than inventing a precise celebrity/deepfake diagnosis.

## First retry

Remove process language and describe only the desired photograph:

- avoid `identity synthesis`, `blend faces`, `morph`, `combine identities`, `same person`, and defensive explanations such as `fictional` or `AI-generated`;
- omit detailed facial-anatomy inventories until a minimal reference job is proven;
- specify framing, pose, expression, camera, lighting, background, and finish only;
- do not promise that re-encoding, metadata removal, cropping, or euphemisms will bypass a visual classifier.

Minimal probe:

```text
Front-facing editorial portrait, centered head-and-shoulders composition, neutral expression, soft frontal daylight, warm-gray background, natural skin texture, restrained retouching.
```

If the single-image minimal probe still blocks, stop iterating prose. Recommend a supported reference/character feature, a different model/provider, or text-only reconstruction from observable traits.

## Character-sheet handoff

Once one approved reference image exists, describe the output rather than the manipulation process. Use a fixed panel map, one subject, consistent camera distance/head scale/lighting/wardrobe, unobstructed landmarks, and no text labels unless the engine renders labels reliably. For a 3x3 face sheet, nine distinct views are more useful than nine expression variants: front, graded left turns, left profile, graded right turns, right profile, slight high front, slight low front.

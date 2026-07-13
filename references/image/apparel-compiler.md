# Apparel Prompt Compiler

Use this reference when a validated Vision role map describes apparel sources and the requested result is a coherent pure-white product-image family.

## Ownership and input gate

Vision analysis owns pixel observations, role labels, occlusion maps, source-evidence coverage, and explicit color identities. The prompt compiler alone authors final generation prompts. An execution adapter consumes the compiled handoff without rewriting product facts.

The portable request format is `apparel-compile-request/v1`. It contains a product-folder identifier, source-folder location, complete source basename inventory, `vision_role_map`, and complete `requested_outputs` inventory. Every role-map source must occur in the inventory and every inventory source must exist. Filenames are identifiers, never color evidence.

Count colors only from records whose `role` is exactly `color_front`. Each such record requires `color_identity`; normalize it with Unicode NFKC, collapsed whitespace, and case folding, then count unique normalized values. Back and detail records do not add colors. Zero unique front colors is `blocked`; no default count is allowed.

## Prompt and evidence contract

Compile one self-contained `IMAGE` prompt per requested output. Each prompt is at most 2,000 Unicode code points and contains:

1. exact requested view, normalized color, and product description;
2. source-supported construction, silhouette, proportions, material, trim, print, and visible details;
3. complete removal of mannequin, hanger, stand, rod, cord, clip, hand, prop, and remnants;
4. uniform `#FFFFFF` with no cast/contact shadow, halo, floor line, or gradient;
5. source-only hidden-area reconstruction with no invented construction or decoration;
6. coherent series canvas, occupancy, centerline, scale, and lighting.

A prompt never contains a local path. If complete evidence cannot fit within 2,000 characters, return `self_contained_prompt_overflow`; do not drop a lock or move image instructions to another file.

## Portable handoff

`scripts/compile_apparel_handoff.py` emits the contract defined by `contracts/v1/apparel-handoff.schema.json`. The handoff preserves the complete `sources`, `vision_role_map`, normalized front-color identities, `unique_color_count`, folder master, QC contract, complete output inventory, and each output's ID, filename, and final prompt.

The handoff is sufficient for a network-free consumer to prepare isolated candidate tasks. Unknown versions, missing sources, missing front identities, zero colors, duplicate output ownership, or an overlong prompt fail closed. Runtime-specific installation and consumer routing belong only in `references/adapters.md`.

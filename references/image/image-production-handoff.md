# Portable image-production handoff

MPW owns prompt compilation. An image generator owns execution. The boundary between them is `image-production-handoff/v2`, a runtime-neutral JSON object validated by `contracts/v1/image-production-handoff.schema.json`.

## Compile

Create a request with `schema_version: image-production-request/v2`, then run:

```sh
python3 scripts/compile_image_handoff.py request.json --output handoff.json
```

Required request fields:

- `job_id`: portable identifier using letters, digits, `.`, `_`, or `-`.
- `operation`: `generate` or `edit`; edits require at least one input image.
- `subject`: the main image subject.
- `output.filename`: a PNG, JPEG, or WebP basename.

Optional prompt fields are `action`, `scene`, `composition`, `lighting`, `style`, and `text`. Optional execution hints are `negative_prompt`, `aspect_ratio`, `image_size`, and string-valued `metadata`.

`input_images` entries contain only `path` and `role`. Paths must be relative to the handoff bundle or public HTTPS URLs. Absolute paths, home-directory shortcuts, credentials in URLs, and traversal are rejected. Bundle relative assets beside the JSON when moving it between machines.

## Execute

A compatible executor reads the handoff, resolves relative inputs from the handoff bundle, uses `operation` to select generation or edit behavior, and writes the requested output filename. The executor may map `aspect_ratio` and `image_size` to its supported controls, but must reject unsupported required behavior rather than silently changing the request.

ImgGen2 can consume this contract. It is optional: MPW still writes standalone prompts, and the handoff is generic enough for any executor implementing the schema.

## Example request

```json
{
  "schema_version": "image-production-request/v2",
  "job_id": "launch-card-01",
  "operation": "edit",
  "subject": "A product launch card preserving the supplied product and label",
  "scene": "Pale stone surface with soft window light",
  "composition": "Centered 4:5 product framing",
  "style": "Restrained editorial design",
  "input_images": [
    {"path": "assets/product.png", "role": "Product identity reference"}
  ],
  "aspect_ratio": "4:5",
  "output": {"filename": "launch-card.png"}
}
```

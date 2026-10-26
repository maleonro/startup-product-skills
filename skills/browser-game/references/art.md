# Look and art (step 5)

## Pick one era and push it

A small team cannot win on realism. Pick one look with known limits and push it further than the
reference. The first game picked the PS1 era: low-poly faceted models, vertex snapping, affine
texture warping, a low internal resolution with a nearest-neighbour upscale, color per area.

Before moving up an era, prototype it behind a flag (`?look=...`) on one room and measure:

| Tried on the first game | Cost per frame | What changed | Decision |
|---|---|---|---|
| PS2-like | about 3x | little | stay |
| PS3-like (5 CC0 assets) | 3-4x, plus 10-14 agent-days for the whole game | brighter and flatter, the mood was lost | stay |

The better path was the same era with fewer defects and better objects: a bevel on hard edges,
ambient occlusion baked into vertices, a tighter palette, more variety.

## Audit before you polish

One agent walks every room and writes `ref/look-audit.md`: each defect with a photo, a severity
and the file that owns it. The first audit found 22 defects, 6 of them high: speech bubbles that hid
the boss, one marble texture repeated everywhere, arms with open ends, identical chairs in a room,
signs cut by pillars. Then two agents fix them in parallel, split by files (rooms and textures in
one, models and rigs in the other). Each fix ships as a before/after pair of photos.

Readability rules that came out of it:

- **Color per area** helps the player know where they are (cold blue in the lobby, green in
  security, warm at the end).
- **Light the characters, not only the room.** A dark navy hero disappeared in a dark room.
- **Small props vanish at low resolution.** At 320x240 an object on a desk is about 5 pixels: make
  easter eggs big and near the camera.
- **A real photo in the world** (a portrait on a wall) needs the full-size source, cropped. A
  100-pixel thumbnail became a mosaic.

## Generated art, under a cap

Generated characters and textures beat placeholder shapes fast, and they cost money: quote, then
get the owner's OK on the exact number.

The first game used Higgsfield (credits at the time of writing):

| Asset | Model | Credits |
|---|---|---|
| A texture or a character image | Nano Banana Pro | 2 |
| Image to 3D model | Hunyuan3D v3, Normal | 11 (LowPoly cost 14) |

- A pilot first: 3 textures, the hero's image and the hero in 3D, 19 credits. Then 3 more
  characters under a cap of 40; it used 39.
- **Use a square image (1024x1024) for image-to-3D.** A 2:3 image failed (without a charge).
- **Simplify every model to the era's budget:** about 1,100-1,200 triangles and a 256x128 texture
  atlas on the first game, rigid segments per bone.
- **Check every generated image for things you did not ask for.** A guard came back with a police
  badge. With no credits left to regenerate, it was painted out of the texture.
- **Keep the old asset behind a flag** (`?chars=old`) until the owner approves the new one from a
  photo.
- Raw outputs, prompts and costs live in `art-src/` with a README. They never ship: a 25 MB source
  model in `dist/` is a mistake that `scripts/check-dist.mjs` catches.

## Sound and music

The agent cannot hear. Measure in code: the length of each loop, how many times it repeats in a
typical room, what changes on alert and how fast. Prefer one piece in layers that add up as danger
rises (Winifred Phillips) over a short loop that becomes noise. Check the license of any generated
music for commercial use before you build on it.

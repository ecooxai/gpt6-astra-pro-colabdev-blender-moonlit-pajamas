# Moonlit Pajamas — original procedural Blender reconstruction

A three-dimensional interpretation of the supplied illustration, authored by GPT-6 Astra Pro with MCP Colabdev and headless Blender. Geometry, garment prints, eye textures, hair color maps and accessories were built in this project; no downloaded character models or texture assets are used. Blender, Three.js and Playwright are software dependencies.

## Current checkpoint

R31 is visually reviewed at **95/100, a subjective self-assessment**. It is not a measured 95% image match, a AAA certification, or an animation-ready asset. The model is a static posed character without an armature. Front, face, three-quarter, both side profiles, back, hands, pillow grip, slippers and cotton gathers have dedicated inspection images.

There are **19 retained production-model reviews and 6 separate render studies**. The requested 20,000 build-and-review iterations were not completed. Earlier R07–R17 work was lost in a Colab reset and is not represented as retained source or render evidence. The recorded 26,000 hand-contact candidates are previous numerical geometry tests, not visual model iterations.

## Preview

Persistent site: https://ecooxai.github.io/gpt6-astra-pro-colabdev-blender-moonlit-pajamas/

Run `python3 src/server.py` from this folder to serve `preview/` on port 8791. Open `http://localhost:8791/`. Drag to orbit, scroll or pinch to zoom, right-drag to pan. The viewer includes front, three-quarter, right, left, back and face presets, automatic rotation, illustration/studio shading and Blender-render mode. The journal refreshes every eight seconds. The vendored viewer dependencies allow the static preview to run without a CDN.

## Rebuild

The scene was tested with **Blender 4.0.2**. Python requirements are in `requirements.txt`. For a different installation set `BLENDER_BIN` to its executable. The wrapper uses the Colab sysroot automatically when present; on headless Linux it uses `xvfb-run` when available. Build scripts write to `/build/gpt6-astra-pro_mcp-colabdev_blender_moonlit-pajamas`, which must be writable.

```sh
python3 -m pip install -r requirements.txt
python3 src/make_textures.py
src/blender.sh -b -t 6 --python src/build_character.py -- \
  --revision R32 --quality showcase --views front,face,quarter,side,left,back,hand,hand_side,grip,feet,cuffs
```

`draft` uses 720-pixel-wide views. `showcase` renders front and three-quarter at 1200×2100 and the face at 1200×1200; the other inspection views are smaller. New candidates are staged under `/build/gpt6-astra-pro_mcp-colabdev_blender_moonlit-pajamas/pending-preview` and do not replace the accepted preview until explicitly reviewed and published.

Inspect the generated images, then run `src/publish.py --help`. Only use `--review` with a real inspection and an honest score. Rejected trials belong in the journal without promoting their model. `render_versions.json` records the actual revision of every view.

## Verify

```sh
python3 src/validate_model.py
src/blender.sh -b preview/assets/gpt6-astra-pro_mcp-colabdev_blender_moonlit-pajamas.blend --python src/audit_hands.py
node src/test_viewer.mjs
python3 src/release_check.py
```

The browser test requires the running preview server, the installed npm dependencies and Chromium at the executable path in `src/test_viewer.mjs`. `npm ci` installs test dependencies. The contact audit is run against the candidate scene before publication; it writes its report to the staging folder. Hand audits write beside the actual loaded `.blend` file.

The final local test reports pass: 581,452 triangles in the full GLB, 354,552 in the web GLB, and 26 observed browser draw calls. Desktop 1440×1000 and mobile 390×844 viewports load all eleven images without horizontal overflow; no frames render while offscreen. These are headless viewport tests, not measurements on a physical phone.

## Save and deploy

Commit the reviewed source, models, reports and documentation first. `python3 src/checkpoint.py --deploy` creates a CRC-verified Git archive, includes `CHECKPOINT.json`, uploads the ZIP and SHA-256 checksum as GitHub release assets, and pushes the preview to `gh-pages`. Authentication and repository write access are required. The release archive is tied to one immutable source commit; the scene separately records the geometry-building commit.

The complete archive includes the source, editable `.blend`, full and optimized GLBs, packed/authored textures, current inspection images, retained review history, studies and test reports. It excludes installed dependencies, Git internals and transient logs. See `Agents.md` for recovery and continuation details.

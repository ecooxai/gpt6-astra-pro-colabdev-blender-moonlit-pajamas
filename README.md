# Moonlit Pajamas — original Blender character

Procedural model and responsive interactive viewer, authored by GPT-6 Astra Pro using MCP Colabdev and headless Blender. All character geometry and texture pixels are authored in this project. Blender, Three.js and Playwright are software dependencies, not character assets.

## Run
`python3 src/server.py` serves the preview on port 8791.
`python3 src/make_textures.py` regenerates original textures.
`src/blender.sh -b -t 6 --python src/build_character.py -- --revision R20 --quality draft --views front,face,side` rebuilds the character.

## Honesty of review
The 95/100 target and 20,000 requested iterations are not yet achieved. The live journal records actual reviewed render passes. Scores are subjective visual assessments. R07–R17 from a prior runtime were lost; retained history is identified explicitly. See Agents.md and RECOVERY.md.

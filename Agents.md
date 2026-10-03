# Moonlit Blender continuation
Project: /home/dev/project/3d/gpt6-astra-pro_mcp-colabdev_blender_moonlit-pajamas
Branch: gpt6-astra-pro_mcp-colabdev_refinement95
## State
Recovered from R06 after Colab rollback. R07–R17 were previously reviewed but their source and images were lost. Do not claim those files exist. R18 was interrupted. R19 is a new reconstruction, not yet reviewed. Preserved score before R19 is 78/100 subjective. Requested goal >95 and 20,000 iterations is not met.
## Build
`python3 src/make_textures.py` then `src/blender.sh -b -t 6 --python src/build_character.py -- --revision R19 --quality draft --views front,side,back,face,hand,grip`
All geometry and texture pixels authored in Python here. The reference is viewed visually only, never baked into the model.
## Persistence
Push source and latest actual artifacts after each reviewed step. A prior runtime rollback erased unpushed work. Never start a new Colab instance or stop the current one without verified backup.

R19 completed and reviewed: 84/100, seven retained review entries. Front, side, back, face, hand and grip images exist. Next: collar intersections, squared hair-cap ends, continuous wrist and actual slipper ribbons.

R20 completed: 87/100 subjective. Eight retained reviews. New builds stage in /build/<project>/pending-preview; publish.py copies them only during an explicit publish. Browser controls passed on desktop/mobile but the report included an extraneous favicon 404; empty favicon added. Model web export is 333645 triangles vs 542952 full. Next R21: hand twist, more natural cloth gathers and collar asymmetry, cap toe openings.

R21 completed and reviewed from front/back/three-quarter: 88/100 subjective, nine retained passes. Hand audit PASS: each full arm/hand is one connected closed surface. Full GLB 534876 triangles; web 332373. Reconstructive work after lost R17 is deliberately numbered R19 onward; unperformed builds are not counted. Next priorities: raised hand, accurate curved shirt tails, longer relaxed sleeve, smooth root-color transitions.

R22 reviewed: 88/100, ten retained reviewed passes. Better projected pocket/placket and curved shirt hem. Remaining/new defects: blue shoulder-panel intrusion in neck opening, too-close index/middle finger paths, stiff rolled collar. Hand connectivity audited. R23 must correct the actual garment neckline and finger paths. Full and web exports preserved.

R24 reviewed: 90/100 subjective; twelve retained reviewed passes. Shirt neckline now sewn to exact lapel underside, no visible blue intrusion or skin gap. Front and side inspected, hand topology audited and desktop/mobile tested. Full GLB 536836 triangles; web 330321. Next: true fingertip/headband contact using generated-mesh geometry tests, followed by illustrated shading and hair/cloth definition.

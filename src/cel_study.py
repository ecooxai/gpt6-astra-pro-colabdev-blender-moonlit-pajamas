"""Two reversible lighting/material studies, using only our generated Blender scene."""
import bpy
from pathlib import Path
root=Path(__file__).resolve().parents[1];scene=bpy.context.scene
original=[]
for mat in bpy.data.materials:
    if not mat.use_nodes:continue
    for node in mat.node_tree.nodes:
        if node.type=='VALTORGB':
            original.append((mat.name,node,node.color_ramp.interpolation,[(e.position,tuple(e.color)) for e in node.color_ramp.elements]))
for name,hard in [('T05-crisp-cotton',True),('T06-soft-cel',False)]:
    for mat_name,node,interpolation,values in original:
        ramp=node.color_ramp;ramp.interpolation=interpolation
        for element,(position,color) in zip(ramp.elements,values):element.position=position;element.color=color
        if mat_name not in ['Original cat-print cotton','white','fabricShade','cuffCotton','collarShade']:continue
        ramp.interpolation='CONSTANT' if hard else 'EASE'
        positions=[.18,.43,.69] if hard else [.30,.48,.54]
        colors=[(.47,.65,.79,1),(.82,.89,.97,1),(1,1,1,1)] if hard else [(.52,.71,.84,1),(.87,.94,.99,1),(1,1,1,1)]
        for element,position,color in zip(ramp.elements,positions,colors):element.position=position;element.color=color
    scene.eevee.taa_render_samples=24
    scene.render.filepath=str(root/'renders/studies'/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    print('CEL_STUDY_READY',name,flush=True)

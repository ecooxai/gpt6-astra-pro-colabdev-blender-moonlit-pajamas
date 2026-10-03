"""Optimize only the browser copy; master BLEND and full GLB are already saved."""
import bpy
from collections import defaultdict
from io_helpers import atomic_copy

def triangle_count(objects):
    return sum(sum(max(0,len(p.vertices)-2) for p in ob.data.polygons) for ob in objects)

def export_web(root,out,assets,objects):
    before=triangle_count(objects);source_objects=len(objects)
    for ob in objects:
        if len(ob.data.polygons)<2200 or ob.name.startswith('Head_'):continue
        ratio=.27 if 'arm' in ob.name else (.50 if ob.name.startswith('Clothes_') else .60)
        bpy.context.view_layer.objects.active=ob
        mod=ob.modifiers.new('Web-only surface reduction','DECIMATE');mod.ratio=ratio
        bpy.ops.object.modifier_apply(modifier=mod.name)
    groups=defaultdict(list)
    for ob in objects:groups[tuple(m.name for m in ob.data.materials)].append(ob)
    batches=[]
    for key,group in groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for ob in group:ob.select_set(True)
        bpy.context.view_layer.objects.active=group[0]
        if len(group)>1:bpy.ops.object.join()
        batch=bpy.context.view_layer.objects.active
        batch.name='WebBatch_'+('_'.join(key) or 'Unpainted').replace(' ','_')
        batches.append(batch)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in batches:ob.select_set(True)
    bpy.context.view_layer.objects.active=batches[0]
    path=out/(root.name+'_web.glb')
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
    atomic_copy(path,assets/path.name)
    after=triangle_count(batches)
    print('WEB_EXPORT_READY',after,'triangles;',len(batches),'batches from',source_objects,'source objects',flush=True)
    return {'web_triangles':after,'web_bytes':path.stat().st_size,'web_draw_batches':len(batches),'source_mesh_objects':source_objects}

import bpy
from io_helpers import atomic_copy

def export_web(root,out,assets,objects):
    before=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects)
    for ob in objects:
        n=len(ob.data.polygons)
        if n<2200 or ob.name.startswith('Head_'):continue
        ratio=.32 if 'arm' in ob.name else .60
        bpy.context.view_layer.objects.active=ob
        mod=ob.modifiers.new('Web-only adaptive reduction','DECIMATE');mod.ratio=ratio
        bpy.ops.object.modifier_apply(modifier=mod.name)
    path=out/(root.name+'_web.glb')
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
    atomic_copy(path,assets/path.name)
    after=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects)
    print('WEB_EXPORT_READY',after,'from',before,flush=True)
    return {'web_triangles':after,'web_bytes':path.stat().st_size}

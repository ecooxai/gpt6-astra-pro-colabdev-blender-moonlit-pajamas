import bpy,bmesh,math,json,shutil,subprocess
from mathutils import Vector
from io_helpers import atomic_copy

def setup(quality):
    s=bpy.context.scene;s.render.engine='BLENDER_EEVEE'
    s.eevee.taa_render_samples=32 if quality=='draft' else 96
    s.eevee.use_gtao=True;s.eevee.gtao_distance=.13;s.eevee.gtao_factor=.85
    s.eevee.use_soft_shadows=True;s.render.film_transparent=True
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
    s.render.resolution_percentage=100
    try:
        s.view_settings.view_transform='Standard';s.view_settings.look='None'
    except Exception:pass
    w=bpy.data.worlds.new('Soft neutral studio');w.use_nodes=True
    w.node_tree.nodes['Background'].inputs[0].default_value=(.68,.72,.82,1)
    w.node_tree.nodes['Background'].inputs[1].default_value=.16;s.world=w
    for name,pos,energy,size,color in [('Key',(-4,-6,9),620,5,(1,.92,.88)),('Fill',(4,-3,6),170,4,(.82,.89,1)),('Rim',(1,4,8),450,4,(.88,.83,1))]:
        d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=color
        o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=pos
        o.rotation_euler=(Vector((0,0,3.7))-o.location).to_track_quat('-Z','Y').to_euler()
    data=bpy.data.cameras.new('Portrait camera');cam=bpy.data.objects.new('Portrait camera',data)
    s.collection.objects.link(cam);s.camera=cam;data.type='ORTHO';data.lens=70;data.clip_end=200
    return s,cam

def normals(ob):
    if ob.type!='MESH':return
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()

def finish(root,out,args,legs):
    character=[o for o in bpy.context.scene.objects if o.type in {'MESH','CURVE','EMPTY'}]
    for ob in character:normals(ob)
    scene,cam=setup(args.quality)
    import toon;toon.install()
    assets=out/'pending-preview';assets.mkdir(exist_ok=True)
    for old in assets.iterdir():
        if old.is_file():old.unlink()
    views=args.views.split(',')
    if 'all' in views:views=['front','quarter','side','back','face']
    def camera_view(view):
        target=Vector((.12,0,3.68));cam.data.ortho_scale=7.68
        positions={'front':(.12,-18,4.03),'quarter':(8,-16,4.8),'side':(18,0,4.1),'back':(.12,18,4.08),'face':(0,-12,6.44),'left':(-18,0,4.1)}
        if view=='face':target=Vector((0,0,6.39));cam.data.ortho_scale=2.05
        details={'hand_side':((-.56,.02,6.40),(-4,-1.8,6.60),1.25),'hand':((-.70,-.27,6.32),(-1.4,-9,6.65),1.12),'grip':((.86,-.10,3.32),(3.7,-10,4.0),1.08),'feet':((-.24,-.06,.43),(1.3,-7,2.1),1.4)}
        if view in details:
            point,position,scale=details[view];target=Vector(point);positions[view]=position;cam.data.ortho_scale=scale
        cam.location=positions[view];cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        scene.render.resolution_x=720 if args.quality=='draft' else 1200
        scene.render.resolution_y=1260 if args.quality=='draft' else 2100
        if view in ['face','hand','hand_side','grip','feet']:scene.render.resolution_y=scene.render.resolution_x
    camera_view('front')
    scene['author']='GPT-6 Astra Pro / MCP Colabdev / Blender';scene['source']='Entirely original procedural geometry and authored textures'
    scene['revision']=args.revision
    scene['source_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    blend=out/(root.name+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True);atomic_copy(blend,assets/blend.name)
    for view in views:
        camera_view(view);path=out/(root.name+'_'+view+'.png');scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True);atomic_copy(path,assets/path.name)
        review=root/'renders/review';review.mkdir(parents=True,exist_ok=True);atomic_copy(path,review/(args.revision+'-'+view+'.png'))
        print('RENDER_READY',view,str(path),flush=True)
    if not args.no_export:
        toon.export_fallback()
        bpy.ops.object.select_all(action='DESELECT')
        selected=[o for o in character if o.type in {'MESH','CURVE'}]
        for o in selected:o.select_set(True)
        bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.convert(target='MESH')
        for o in bpy.context.selected_objects:normals(o)
        glb=out/(root.name+'.glb')
        bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
        atomic_copy(glb,assets/glb.name)
        tri=sum(sum(max(0,len(p.vertices)-2) for p in o.data.polygons) for o in bpy.context.selected_objects if o.type=='MESH')
        stats={'revision':args.revision,'source_commit':scene['source_commit'],'triangles':tri,'objects':len(bpy.context.selected_objects),'legs':legs,'upper_leg_length':scene['upper_leg_length'],'lower_leg_length':scene['lower_leg_length'],'digits_per_hand':5,'asset_origin':'All geometry and textures authored from scratch'}
        from web_export import export_web
        stats.update(export_web(root,out,assets,list(bpy.context.selected_objects)))
        (out/'model_stats.json').write_text(json.dumps(stats,indent=2));atomic_copy(out/'model_stats.json',assets/'model_stats.json')
        print('EXPORT_READY',str(glb),'triangles',tri,flush=True)
    print('BUILD_COMPLETE',args.revision,flush=True)

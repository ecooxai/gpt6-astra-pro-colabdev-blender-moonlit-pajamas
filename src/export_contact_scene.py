"""Export our authored scene geometry for contact tests; never reads a reference image."""
import bpy,sys,ast,json,math
from pathlib import Path
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from geometry import sample
OUT=Path('/build')/ROOT.name/'contact-search';OUT.mkdir(parents=True,exist_ok=True)
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()

def geometry(ob):
    ev=ob.evaluated_get(deps);me=ev.to_mesh();n=len(me.vertices)
    xyz=np.empty((n,3),dtype=np.float64);normal=np.empty((n,3),dtype=np.float64)
    me.vertices.foreach_get('co',xyz.ravel());me.vertices.foreach_get('normal',normal.ravel())
    matrix=np.asarray(ev.matrix_world,dtype=float);xyz=xyz@matrix[:3,:3].T+matrix[:3,3]
    normal=normal@np.linalg.inv(matrix[:3,:3]);normal/=np.maximum(1e-10,np.linalg.norm(normal,axis=1))[:,None]
    edges=np.asarray([tuple(e.vertices) for e in me.edges],dtype=np.int32)
    ev.to_mesh_clear();return xyz,normal,edges

hand,hand_normals,edges=geometry(bpy.data.objects['Body_raised_arm_five_fingers'])
band,band_normals,_=geometry(bpy.data.objects['HeadWear_soft_headband'])
positions=[];normals=[]
for ob in bpy.data.objects:
    if ob.type!='MESH':continue
    if ob.name=='Head_original_anime_head' or ob.name.startswith('HairTop_'):
        xyz,nrm,_=geometry(ob);keep=(xyz[:,0]<.15)&(xyz[:,2]>5.85)
        positions.append(xyz[keep]);normals.append(nrm[keep])
head=np.concatenate(positions);head_normals=np.concatenate(normals)
# Recover the exact authored finger control points and the exact already-used pose warp.
a=ast.parse((ROOT/'src/anatomy.py').read_text());fn=next(n for n in a.body if isinstance(n,ast.FunctionDef) and n.name=='build_hands')
fingers=ast.literal_eval(next(n.value for n in fn.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='fingers' for t in n.targets)))
a=ast.parse((ROOT/'src/pose.py').read_text());fn=next(n for n in a.body if isinstance(n,ast.FunctionDef) and n.name=='adjust_pose');warp_node=next(n for n in fn.body if isinstance(n,ast.FunctionDef) and n.name=='warp')
module=ast.fix_missing_locations(ast.Module(body=[warp_node],type_ignores=[]));ns={'Vector':Vector,'sin':math.sin,'cos':math.cos};exec(compile(module,'authored_pose_warp','exec'),ns);warp=ns['warp']
centers=[];radii=[];names=[]
for name,pts,r in fingers:
    ps,rs=sample(pts,[r,r*.91,r*.79,r*.67],7)
    centers.append(np.asarray([warp('Body_raised_arm',p) for p in ps],dtype=float));radii.append(rs);names.append(name)
pivot=np.asarray(warp('Body_raised_arm',Vector((-.69,-.20,6.02))),dtype=float)
meta={'revision':bpy.context.scene.get('revision'),'source_commit':bpy.context.scene.get('source_commit'),'finger_names':names,'pivot':pivot.tolist(),'scope':'Generated Blender geometry only; original reference pixels are not inputs.'}
np.savez_compressed(OUT/'input.npz',hand=hand,hand_normals=hand_normals,edges=edges,band=band,band_normals=band_normals,head=head,head_normals=head_normals,centers=np.stack(centers),radii=np.asarray(radii),pivot=pivot,metadata=np.asarray(json.dumps(meta)))
print('CONTACT_DATASET',json.dumps({'revision':meta['revision'],'hand_vertices':len(hand),'band_vertices':len(band),'head_vertices':len(head),'pivot':pivot.tolist(),'path':str(OUT/'input.npz')}))

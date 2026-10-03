"""Apply the recorded, tested elbow-based pose to our own generated geometry."""
import json,math
from pathlib import Path
import numpy as np

def rotation(parameters):
    x,y,z=parameters[3:];cx,sx=math.cos(x),math.sin(x);cy,sy=math.cos(y),math.sin(y);cz,sz=math.cos(z),math.sin(z)
    return np.array([[cz*cy,cz*sy*sx-sz*cx,cz*sy*cx+sz*sx],[sz*cy,sz*sy*sx+cz*cx,sz*sy*cx-cz*sx],[-sy,cy*sx,cy*cx]])

def deform(points,config):
    original=np.asarray(points,dtype=float);shape=original.shape;p=original.reshape(-1,3)
    parameters=np.asarray(config['parameters']);pivot=np.asarray(config['pivot']);height=float(config['weight_height']);start=pivot[2]+float(config['weight_start_offset'])
    t=np.clip((p[:,2]-start)/height,0,1);w=t*t*(3-2*t)
    delta=(p-pivot)@(rotation(parameters)-np.eye(3)).T+parameters[:3]
    return (p+w[:,None]*delta).reshape(shape)

def apply(root):
    import bpy
    path=Path(root)/'src/contact_pose_config.json'
    if not path.exists():return
    config=json.loads(path.read_text())
    if config['decision']!='geometry-approved':raise RuntimeError('Unapproved contact candidate')
    if bpy.context.scene.get('contact_adjustment_applied'):raise RuntimeError('Contact adjustment already applied')
    bpy.context.view_layer.update()
    for ob in list(bpy.context.scene.objects):
        if not ob.name.startswith('Body_raised_arm'):continue
        matrix=np.asarray(ob.matrix_world,dtype=float);inverse=np.linalg.inv(matrix)
        def moved(local):
            local=np.asarray(local,dtype=float);world=local@matrix[:3,:3].T+matrix[:3,3]
            world=deform(world,config);return (world-inverse[:3,3]*0-matrix[:3,3])@inverse[:3,:3].T
        if ob.type=='MESH':
            points=np.empty((len(ob.data.vertices),3),dtype=float);ob.data.vertices.foreach_get('co',points.ravel());points=moved(points);ob.data.vertices.foreach_set('co',points.ravel());ob.data.update()
        elif ob.type=='CURVE':
            for spline in ob.data.splines:
                if spline.type=='BEZIER':
                    for p in spline.bezier_points:p.co=moved(np.asarray(p.co)[None,:])[0]
                else:
                    for p in spline.points:p.co=(*moved(np.asarray(p.co[:3])[None,:])[0],1)
    scene=bpy.context.scene;scene['contact_adjustment_applied']=True;scene['contact_candidate_tests']=config['candidate_tests'];scene['contact_index_tip_center']=deform(np.asarray(config['baseline_index_center'])[None,:],config)[0].tolist();scene['contact_index_pad_radius']=config['index_pad_radius']
    scene['contact_pose_parameters']=config['parameters'];scene['contact_pose_pivot']=config['pivot']

"""Moonlit Pajamas — all geometry and textures authored from scratch."""
import bpy, sys, math, json, argparse, pathlib, time, shutil
from mathutils import Vector
from math import sin,cos,pi,sqrt,exp
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from geometry import *
from legs import rounded_leg
P=argparse.ArgumentParser();P.add_argument('--revision',default='R01');P.add_argument('--quality',default='draft');P.add_argument('--views',default='front');P.add_argument('--no-export',action='store_true');A=P.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT=pathlib.Path('/build')/ROOT.name;OUT.mkdir(parents=True,exist_ok=True)
CFG=json.loads((ROOT/'src/config.json').read_text()) if (ROOT/'src/config.json').exists() else {}
bpy.ops.wm.read_factory_settings(use_empty=True)
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def rgb(h):return tuple(linear(int(h[i:i+2],16)/255) for i in (0,2,4))+(1,)
def material(name,h,texture=None,roughness=.86,emission=.15,metallic=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=rgb(h);n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=rgb(h);p.inputs['Roughness'].default_value=roughness;p.inputs['Metallic'].default_value=metallic
    if 'Specular IOR Level' in p.inputs:p.inputs['Specular IOR Level'].default_value=.22
    p.inputs['Emission Color'].default_value=rgb(h);p.inputs['Emission Strength'].default_value=emission
    if texture:
        im=bpy.data.images.load(str(ROOT/'src/textures'/texture));im.pack();t=n.new('ShaderNodeTexImage');t.image=im;t.extension='REPEAT';m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);m.node_tree.links.new(t.outputs['Color'],p.inputs['Emission Color'])
    return m
M={}
for key,h in dict(skin='fff0e9',hair='7772a2',hairLight='8881b2',hairDark='5d547f',hairInk='4d446b',white='faffff',fabricShade='a9cddf',piping='9dbccc',lash='363047',eyeWhite='fff9fb',mouth='b78190',pink='b96594',pinkLight='e2b0cb',nail='f9e2e8',sole='a9b1c4',halo='242732').items():M[key]=material(key,h)
M['fabric']=material('Original cat-print cotton','d3f2fb','cat_cotton_original.png',emission=.2)
M['face']=material('Original face wash','ffefe9','face_wash_original.png',emission=.24)
M['iris']=material('Original violet iris','7262bb','violet_iris_original.png',roughness=.58,emission=.35)
M['haloBlue']=material('Cyan halo inlay','45b7ec',roughness=.5,emission=1.2)
M['halo'].node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value=.48
M['halo'].node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.45
# The torso under the loose, full-coverage pajama shirt.
loft('Body_neck_and_shoulders',[(0,.02,4.78,.34,.23),(.005,.02,5.18,.46,.255),(.005,.02,5.34,.445,.20),(.005,.01,5.45,.22,.16),(.005,.015,5.61,.119,.12),(.005,.02,5.73,.112,.115)],M['skin'])
# Both legs use the same segment lengths; the rear knee bends, rather than shortening.
L1=1.59;L2=1.60
bpy.context.scene['upper_leg_length']=L1;bpy.context.scene['lower_leg_length']=L2
LEG_DATA={}
def knee_position(hip,ankle):
    v=ankle-hip;d=v.length;axis=v.normalized();along=(L1*L1-L2*L2+d*d)/(2*d);height=sqrt(max(0,L1*L1-along*along));pole=Vector((0,-1,0));pole=(pole-axis*pole.dot(axis)).normalized();return hip+axis*along+pole*height
for label,hip,ankle in [('front',Vector((.25,.025,3.38)),Vector((-.025,-.18,.235))),('rear',Vector((-.26,.07,3.38)),Vector((-.29,.25,.58)))]:
    knee=knee_position(hip,ankle);sections=[]
    for t,rx,ry in [(0,.231,.217),(.18,.233,.207),(.45,.211,.181),(.76,.166,.153),(.95,.146,.14),(1,.144,.145)]:
        p=hip.lerp(knee,t);sections.append((*p,rx,ry))
    for t,rx,ry in [(.12,.151,.15),(.30,.175,.158),(.52,.149,.135),(.78,.102,.107),(.94,.078,.091),(1,.076,.085)]:
        p=knee.lerp(ankle,t);sections.append((*p,rx,ry))
    ob=rounded_leg(label,hip,knee,ankle,M['skin']);ob['upper_segment']=L1;ob['lower_segment']=L2;LEG_DATA[label]={'hip':list(hip),'knee':list(knee),'ankle':list(ankle)}
# Raised arm and relaxed arm have curved elbow transitions, not stacked primitives.
upper=tube('Body_raised_arm',[(-.43,.025,5.31),(-.81,-.01,5.18),(-1.12,-.055,5.22),(-1.015,-.13,5.48),(-.83,-.17,5.72),(-.64,-.20,6.02)],[.151,.143,.125,.12,.097,.061],M['skin'],sides=28,steps=8)
lower=tube('Body_relaxed_arm',[(.47,.025,5.25),(.56,-.015,4.70),(.55,-.04,4.21),(.63,-.12,3.74),(.78,-.16,3.29)],[.15,.137,.101,.111,.061],M['skin'],sides=28,steps=8)
from anatomy import build_hands
from face import build_face
from hair import build_hair
from clothing import build_clothes
from accessories import build_pillow,build_headwear,build_slippers
build_hands(M,upper,lower);build_face(M);build_hair(M);build_clothes(M,LEG_DATA)
build_pillow(M);build_headwear(M);build_slippers(M,LEG_DATA)
from pose import adjust_pose
bpy.context.view_layer.update();adjust_pose()
bpy.context.view_layer.update()
bpy.ops.object.empty_add(location=(0,0,6.30));head_root=bpy.context.object;head_root.name='Character_head_pose'
for ob in list(bpy.context.scene.objects):
    if ob.name.startswith(('Head_','HairTop_','HeadWear_')):parent_keep(ob,head_root)
head_root.rotation_euler=(0,-.065,-.035)
from studio import finish
finish(ROOT,OUT,A,LEG_DATA)

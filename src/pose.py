import bpy
from mathutils import Vector

def adjust_pose():
    def warp(name,p):
        p=p.copy();z=p.z
        if name.startswith(('Head_','HairTop_')):p.z+=.18
        elif name.startswith('HeadWear_soft'):p.z+=.18
        elif name.startswith('HeadWear_'):p.z=6.95+(z-6.85)*.85
        elif name.startswith('HairLong_'):p.z+=.18*max(0,min(1,(z-4.0)/2.6))
        elif name.startswith('Clothes_') and not any(t in name for t in ['short','cuff']):p.z=3.8+(z-3.8)*1.15
        elif name.startswith('Body_neck'):p.z=3.8+(z-3.8)*1.15
        elif name.startswith('Body_raised_arm'):
            w=max(0,min(1,(z-5.8)/.22));p.y-=.15*w;p.x-=.03*w
            p.z+=.24-.1*max(0,min(1,(z-5.3)/.9))+.10*max(0,z-6.02)
        elif name.startswith('Body_relaxed_arm'):p.z=3.8+(z-3.8)*1.1+.17
        elif name.startswith('Accessory_') and 'pillow' in name:
            p.z=.86+(z-.86)*1.05;p.x=.86+(p.x-.86)*1.05
        return p
    for ob in list(bpy.context.scene.objects):
        matrix=ob.matrix_world.copy();inverse=matrix.inverted()
        def move(co):return inverse@warp(ob.name,matrix@Vector(co[:3]))
        if ob.type=='MESH':
            for v in ob.data.vertices:v.co=move(v.co)
            ob.data.update()
        elif ob.type=='CURVE':
            for sp in ob.data.splines:
                if sp.type=='BEZIER':
                    for bp in sp.bezier_points:bp.co=move(bp.co)
                else:
                    for p in sp.points:p.co=(*move(p.co),1)

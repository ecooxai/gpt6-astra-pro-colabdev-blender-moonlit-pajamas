"""Pose offsets shared by anatomy and garment surfaces; no image measurements."""
import bpy
from mathutils import Vector
from math import sin,cos

def adjust_pose():
    def warp(name,p):
        p=p.copy();z=p.z
        if name.startswith(('Head_','HairTop_')):p.z+=.18;p.x*=.90
        elif name.startswith('HeadWear_soft'):p.z+=.18;p.x*=.90
        elif name.startswith('HeadWear_'):p.z=6.95+(z-6.85)*.85;p.x*=1.15
        elif name.startswith('HairLong_'):
            p.x*=1-.04*max(0,min(1,(z-5.35)/1.3));p.z+=.18*max(0,min(1,(z-4.0)/2.6))
        elif name.startswith('Clothes_') and not any(t in name for t in ['short','cuff']):
            p.x-=.13*(1-max(0,min(1,(z-3.8)/1.6)));p.z=3.8+(z-3.8)*1.15+.075*max(0,min(1,(z-4.95)/.45))
        elif name.startswith('Body_neck'):p.z=3.8+(z-3.8)*1.15
        elif name.startswith('Body_raised_arm'):
            t=max(0,min(1,(z-6.01)/.17));angle=.55*t*t*(3-2*t);x=p.x+.71;y=p.y+.24;p.x=-.71+x*cos(angle)-y*sin(angle);p.y=-.24+x*sin(angle)+y*cos(angle)
            w=max(0,min(1,(z-5.8)/.22));p.y-=.12*w;p.x-=.008*w
            p.z+=.24-.1*max(0,min(1,(z-5.3)/.9))+.10*max(0,z-6.02)
        elif name.startswith('Body_relaxed_arm'):p.z=3.8+(z-3.8)*1.1+.17
        elif name.startswith('Accessory_') and 'pillow' in name:
            t=max(0,min(1,(3.3-z)/2.44));p.x=.86+(p.x-.86)*1.10-.36*t;p.z=.86+(z-.86)*1.08
        elif name.startswith(('Accessory_front_','Accessory_rear_')):
            front=name.startswith('Accessory_front_');cx=-.11 if front else -.34;cy=-.31 if front else .12;base=.035 if front else .38
            p.x=cx+(p.x-cx)*1.30;p.y=cy+(p.y-cy)*1.08
            if 'slipper_upper' in name:p.z=base+.081+(p.z-base-.081)*1.20
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

def blend_long_hair_pose(head_root):
    rotation=head_root.rotation_euler.to_matrix();pivot=head_root.location.copy()
    for ob in list(bpy.context.scene.objects):
        if not ob.name.startswith('HairLong_'):continue
        matrix=ob.matrix_world.copy();inverse=matrix.inverted()
        def move(co):
            p=matrix@Vector(co[:3]);t=max(0,min(1,(p.z-5.45)/.90));w=t*t*(3-2*t)
            return inverse@p.lerp(pivot+rotation@(p-pivot),w)
        if ob.type=='MESH':
            for v in ob.data.vertices:v.co=move(v.co)
            ob.data.update()
        elif ob.type=='CURVE':
            for s in ob.data.splines:
                for b in s.bezier_points:b.co=move(b.co)

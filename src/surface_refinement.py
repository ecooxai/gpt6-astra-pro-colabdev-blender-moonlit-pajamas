"""Refine our own authored 3D surfaces; no image pixels are accessed."""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def finish_surfaces():
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH' or not ob.name.startswith(('HairTop_','HairLong_')):continue
        layer=ob.data.uv_layers.active or ob.data.uv_layers.new(name='UVMap')
        for poly in ob.data.polygons:
            for li,vi in zip(poly.loop_indices,poly.vertices):
                z=ob.data.vertices[vi].co.z
                layer.data[li].uv=(.5,max(.002,min(.998,(z-3.98)/2.755)))
    shirt=bpy.data.objects['Clothes_pajama_shirt']
    surf=BVHTree.FromPolygons([v.co.copy() for v in shirt.data.vertices],[tuple(p.vertices) for p in shirt.data.polygons])
    def fabric_y(x,z):
        for k in range(95):
            hit=surf.ray_cast(Vector((x,-2,z-k*.006)),Vector((0,1,0)),4)
            if hit[0] is not None:return hit[0].y
        return -.24
    for ob in bpy.context.scene.objects:
        lapel=ob.name.startswith(('Clothes_white_lapel_','Clothes_lapel_piping_'))
        collar=ob.name.startswith(('Clothes_white_rolled_collar_','Clothes_rolled_collar_piping_'))
        if not(lapel or collar):continue
        def move(co):
            p=Vector(co);x,y,z=p
            offset=.028 if ob.type=='CURVE' else .022
            target=fabric_y(x,z)-offset
            if abs(x)<.255:target=min(target,-.265)
            if lapel:p.y=target
            else:
                weight=max(0,min(1,(abs(x)-.14)/.20));p.y=y*(1-weight)+target*weight
            return p
        if ob.type=='MESH':
            for v in ob.data.vertices:v.co=move(v.co)
            ob.data.update()
        elif ob.type=='CURVE':
            for spline in ob.data.splines:
                if spline.type=='BEZIER':
                    for bp in spline.bezier_points:bp.co=move(bp.co)
                else:
                    for bp in spline.points:bp.co=(*move(bp.co[:3]),1)

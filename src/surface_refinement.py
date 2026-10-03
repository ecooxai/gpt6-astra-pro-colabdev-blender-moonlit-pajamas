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


def fit_collar_in_pose():
    """Fit after all pose offsets; sample both cloth and the actual body surface."""
    import bmesh
    bpy.context.view_layer.update()
    def surface(ob):
        return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons])
    shirt=surface(bpy.data.objects['Clothes_pajama_shirt'])
    skin=surface(bpy.data.objects['Body_neck_and_shoulders'])
    def cast(surf,x,z):
        return surf.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4)[0]
    def cloth_y(x,z):
        for k in range(100):
            hit=cast(shirt,x,z-k*.006)
            if hit is not None:return hit.y
        return -.24
    for ob in bpy.context.scene.objects:
        lapel=ob.name.startswith(('Clothes_white_lapel_','Clothes_lapel_piping_'))
        collar=ob.name.startswith(('Clothes_white_rolled_collar_','Clothes_rolled_collar_piping_'))
        if not(lapel or collar):continue
        if ob.type=='MESH' and lapel:
            bm=bmesh.new();bm.from_mesh(ob.data)
            bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=3,use_grid_fill=True)
            bm.to_mesh(ob.data);bm.free();ob.data.update()
        matrix=ob.matrix_world.copy();inverse=matrix.inverted()
        def move(co):
            p=matrix@Vector(co);x,y,z=p
            offset=.030 if ob.type=='CURVE' else .023
            target=cloth_y(x,z)-offset
            body=cast(skin,x,z)
            if body is not None:target=min(target,body.y-offset-.008)
            if lapel:p.y=target
            else:
                weight=max(0,min(1,(abs(x)-.12)/.20));p.y=y*(1-weight)+target*weight
                if body is not None:p.y=min(p.y,body.y-offset-.008)
            return inverse@p
        if ob.type=='MESH':
            for v in ob.data.vertices:v.co=move(v.co)
            ob.data.update()
        elif ob.type=='CURVE':
            for sp in ob.data.splines:
                if sp.type=='BEZIER':
                    for bp in sp.bezier_points:bp.co=move(bp.co)
                else:
                    for bp in sp.points:bp.co=(*move(bp.co[:3]),1)

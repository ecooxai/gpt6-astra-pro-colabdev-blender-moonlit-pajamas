import bpy, bmesh, math
from mathutils import Vector
from math import sin,cos,pi

def mesh(name,verts,faces,mat=None,uv=None):
    me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
    if mat:me.materials.append(mat)
    for p in me.polygons:p.use_smooth=True
    if uv:
        lay=me.uv_layers.new(name='UVMap')
        for p in me.polygons:
            for li,vi in zip(p.loop_indices,p.vertices):lay.data[li].uv=uv[vi]
    return ob

def sphere(name,loc,scale,mat,segments=32,rings=20,rotation=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=loc)
    ob=bpy.context.object;ob.name=name;ob.scale=scale
    if rotation:ob.rotation_euler=rotation
    if mat:ob.data.materials.append(mat)
    for p in ob.data.polygons:p.use_smooth=True
    return ob

def curve(name,points,mat,radius=.006,resolution=8,cyclic=False,radii=None):
    cu=bpy.data.curves.new(name+'_curve','CURVE');cu.dimensions='3D';cu.resolution_u=resolution;cu.bevel_depth=radius;cu.bevel_resolution=2
    sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for i,(bp,p) in enumerate(zip(sp.bezier_points,points)):
        bp.co=p;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO';bp.radius=radii[i] if radii else 1
    sp.use_cyclic_u=cyclic;ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);cu.materials.append(mat);return ob

def sample(points,values=None,steps=7):
    ps=[Vector(p) for p in points];vs=values;out=[];vals=[]
    for i in range(len(ps)-1):
        p0=ps[max(0,i-1)];p1=ps[i];p2=ps[i+1];p3=ps[min(len(ps)-1,i+2)]
        for j in range(steps):
            t=j/steps;t2=t*t;t3=t2*t
            out.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t2+(-p0+3*p1-3*p2+p3)*t3))
            if vs is not None:
                v0=vs[max(0,i-1)];v1=vs[i];v2=vs[i+1];v3=vs[min(len(vs)-1,i+2)]
                vals.append(.5*(2*v1+(-v0+v2)*t+(2*v0-5*v1+4*v2-v3)*t2+(-v0+3*v1-3*v2+v3)*t3))
    out.append(ps[-1])
    if vs is not None:vals.append(vs[-1])
    return out,vals

def tube(name,points,radii,mat,sides=20,steps=6,flatten=1.0,normal=(0,-1,0),caps=True):
    ps,rs=sample(points,radii,steps)
    vertices=[];polygons=[];coords=[]
    axis=Vector(normal)
    for i,p in enumerate(ps):
        tangent=(ps[min(i+1,len(ps)-1)]-ps[max(i-1,0)]).normalized()
        side=tangent.cross(axis).normalized()
        if side.length<.01:side=tangent.cross(Vector((1,0,0))).normalized()
        depth=side.cross(tangent).normalized()
        for j in range(sides+1):
            a=2*pi*j/sides;r=max(.001,rs[i])
            vertices.append(p+side*r*cos(a)+depth*r*flatten*sin(a));coords.append((j/sides,i/(len(ps)-1)))
    for i in range(len(ps)-1):
        for j in range(sides):
            a=i*(sides+1)+j;b=a+sides+1;polygons.append((a,a+1,b+1,b))
    if caps:
        polygons.append(tuple(reversed(range(sides))))
        polygons.append(tuple((len(ps)-1)*(sides+1)+j for j in range(sides)))
    return mesh(name,vertices,polygons,mat,coords)

def loft(name,sections,mat,sides=64,steps=4,uvscale=1.0,wrinkle=0):
    points=[s[:3] for s in sections];ps,rxs=sample(points,[s[3] for s in sections],steps);_,rys=sample(points,[s[4] for s in sections],steps)
    verts=[];faces=[];uv=[]
    for i,(p,rx,ry) in enumerate(zip(ps,rxs,rys)):
        for j in range(sides+1):
            a=2*pi*j/sides-pi;factor=1+wrinkle*(sin(7*a+p.z*7)+.4*sin(13*a-p.z*4))
            verts.append((p.x+rx*sin(a)*factor,p.y-ry*cos(a)*factor,p.z));uv.append(((a+pi)/(2*pi)*uvscale,p.z*.91))
    for i in range(len(ps)-1):
        for j in range(sides):
            a=i*(sides+1)+j;b=a+sides+1;faces.append((a,b,b+1,a+1))
    faces.append(tuple(reversed(range(sides))));faces.append(tuple((len(ps)-1)*(sides+1)+j for j in range(sides)))
    return mesh(name,verts,faces,mat,uv)

def panel(name,boundary,mat,bulge=.012,thickness=.014,uvscale=1):
    p=[Vector(x) for x in boundary];ext=[p[-1]]+p+[p[0],p[1]];bd=[]
    for i in range(1,len(p)+1):
        p0,p1,p2,p3=ext[i-1:i+3]
        for j in range(5):
            t=j/5;bd.append(.5*(2*p1+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
    c=sum(bd,Vector())/len(bd);verts=[];uv=[];faces=[];nr=5;n=len(bd)
    for k in range(nr):
        r=(k+1)/nr
        for q in bd:
            v=c.lerp(q,r);v.y-=bulge*(1-r*r);verts.append(v);uv.append((v.x*uvscale,v.z*uvscale))
    faces.append(tuple(reversed(range(n))))
    for k in range(nr-1):
        for j in range(n):
            a=k*n+j;b=k*n+(j+1)%n;faces.append((a,b,b+n,a+n))
    ob=mesh(name,verts,faces,mat,uv)
    if thickness:
        mod=ob.modifiers.new('Sewn fabric thickness','SOLIDIFY');mod.thickness=thickness
    return ob,bd

def hair_lock(name,points,widths,depths,mat,normal=(0,-1,0),steps=8,sides=12,groove_mat=None):
    ps,ws=sample(points,widths,steps);_,ds=sample(points,depths,steps);norm=Vector(normal);verts=[];faces=[];uv=[];edges=[]
    for i,p in enumerate(ps):
        t=(ps[min(i+1,len(ps)-1)]-ps[max(0,i-1)]).normalized();b=t.cross(norm).normalized();n=b.cross(t).normalized();w=max(.001,ws[i]);d=max(.001,ds[i]);edges.append(p+b*w*.80+n*d*.60)
        for j in range(sides):
            a=2*pi*j/sides;verts.append(p+b*(w*cos(a))+n*(d*sin(a)));uv.append((j/sides,i/(len(ps)-1)))
    for i in range(len(ps)-1):
        for j in range(sides):
            a=i*sides+j;b=i*sides+(j+1)%sides;faces.append((a,b,b+sides,a+sides))
    faces.append(tuple(reversed(range(sides))));faces.append(tuple((len(ps)-1)*sides+j for j in range(sides)))
    ob=mesh(name,verts,faces,mat,uv)
    if groove_mat and len(edges)>8:
        pp=[edges[i] for i in range(3,len(edges)-3,5) if not name.startswith('HairLong_') or edges[i].z<6.15]
        if len(pp)>=2:curve(name+'_edge_ink',pp,groove_mat,.0025,radii=[.04]+[.7]*(len(pp)-2)+[.03])
    return ob

def union(name,objects,voxel=.015,smooth=3):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objects:
        ob.select_set(True)
        if ob.type=='MESH':
            bm=bmesh.new();bm.from_mesh(ob.data)
            bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001)
            bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();ob=bpy.context.object;ob.name=name
    rem=ob.modifiers.new('Continuous anatomical surface','REMESH');rem.mode='VOXEL';rem.voxel_size=voxel;rem.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=rem.name)
    sm=ob.modifiers.new('Soft tissue relaxation','SMOOTH');sm.factor=.7;sm.iterations=smooth;bpy.ops.object.modifier_apply(modifier=sm.name)
    for p in ob.data.polygons:p.use_smooth=True
    return ob

def box_uv(ob,scale=1.0):
    if ob.type!='MESH':return
    uv=ob.data.uv_layers.active or ob.data.uv_layers.new(name='UVMap')
    for p in ob.data.polygons:
        n=p.normal
        for li,vi in zip(p.loop_indices,p.vertices):
            v=ob.matrix_world@ob.data.vertices[vi].co;uv.data[li].uv=((v.x if abs(n.y)>=abs(n.x) else v.y)*scale,v.z*scale)

def parent_keep(ob,parent):
    mx=ob.matrix_world.copy();ob.parent=parent;ob.matrix_world=mx

def flat_panel(name,boundary,mat,bulge=0,thickness=.014,uvscale=1):
    from mathutils.geometry import tessellate_polygon
    points=[Vector(p) for p in boundary]
    triangles=tessellate_polygon([points])
    faces=[tuple(v if isinstance(v,int) else min(range(len(points)),key=lambda i:(points[i]-v).length_squared) for v in tri) for tri in triangles]
    ob=mesh(name,points,faces,mat,[(p.x*uvscale,p.z*uvscale) for p in points])
    if thickness:
        solid=ob.modifiers.new('Sewn panel thickness','SOLIDIFY');solid.thickness=thickness
        bevel=ob.modifiers.new('Soft fabric edge','BEVEL');bevel.width=.005;bevel.segments=3
    return ob,points

def crease(name,points,mat,radius=.004,cyclic=True):
    cu=bpy.data.curves.new(name+'_curve','CURVE');cu.dimensions='3D';cu.bevel_depth=radius;cu.bevel_resolution=2
    sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points):p.co=(*co,1)
    sp.use_cyclic_u=cyclic;ob=bpy.data.objects.new(name,cu)
    bpy.context.collection.objects.link(ob);cu.materials.append(mat)
    return ob

from geometry import *
from math import exp,sqrt

def sleeve(name,start,end,material,piping):
    start=Vector(start);end=Vector(end);axis=(end-start).normalized();side=axis.cross(Vector((0,-1,0))).normalized();depth=side.cross(axis).normalized()
    verts=[];faces=[];uv=[];edge=[];ns=80;nr=20
    for i in range(nr+1):
        t=i/nr;rad=.195+.047*sin(pi*t*.72)
        for j in range(ns+1):
            a=2*pi*j/ns;along=(end-start).length*t+.058*(.5+.5*cos(7*a))*t**5
            p=start+axis*along+side*(rad*cos(a))+depth*(rad*sin(a));verts.append(p);uv.append((j/ns*1.5,t*.64))
            if i==nr:edge.append(p)
    for i in range(nr):
        for j in range(ns):
            a=i*(ns+1)+j;faces.append((a,a+1,a+ns+2,a+ns+1))
    ob=mesh(name,verts,faces,material,uv);sol=ob.modifiers.new('Cotton shell','SOLIDIFY');sol.thickness=.018
    curve(name+'_white_scallop_edge',edge[::5],piping,.008,cyclic=True)

def cuff(name,cx,M,leg=None):
    verts=[];faces=[];uv=[];ns=96;nr=10;edge=[]
    for i in range(nr+1):
        t=i/nr
        for j in range(ns+1):
            a=2*pi*j/ns;r=.285+.027*sin(pi*t);z=3.025-.13*t-.082*(.5+.5*cos(8*a))*t**2
            center=leg_center(leg,z) if leg else Vector((cx,.024,z))
            p=(center.x+r*sin(a),center.y-(.251+.022*sin(pi*t))*cos(a),z);verts.append(p);uv.append((j/ns*1.6,z*.91))
            if i==0:edge.append(p)
    for i in range(nr):
        for j in range(ns):
            a=i*(ns+1)+j;faces.append((a,a+1,a+ns+2,a+ns+1))
    ob=mesh(name,verts,faces,M['fabric'],uv);sol=ob.modifiers.new('Rounded cuff thickness','SOLIDIFY');sol.thickness=.025
    curve(name+'_upper_piping',edge[::4],M['white'],.008,cyclic=True)

def build_clothes(M,legs):
    verts=[];faces=[];uv=[];ns=128;nr=48;hem=[]
    for i in range(nr+1):
        t=i/nr
        for j in range(ns+1):
            a=2*pi*j/ns-pi;bottom=3.755+.060*cos(a)+.14*exp(-(a/.068)**2);top=5.395-.43*exp(-(a/.32)**2);z=bottom+(top-bottom)*t
            rx=.49+.13*(1-t)**2+.065*t**6-.022*sin(t*pi);ry=.245+.045*(1-t)+.024*sin(t*pi)
            ripple=1+.013*sin(7*a+z*5)*(1-t)+.009*sin(12*a-z*4)
            x=.025*t+rx*sin(a)*ripple;y=.012-ry*cos(a)*ripple
            verts.append((x,y,z));uv.append((j/ns*2.9,z*.91))
            if i==0:hem.append((x,y-.001,z))
    for i in range(nr):
        for j in range(ns):
            a=i*(ns+1)+j;faces.append((a,a+1,a+ns+2,a+ns+1))
    shirt=mesh('Clothes_pajama_shirt',verts,faces,M['fabric'],uv)
    solid=shirt.modifiers.new('Cotton thickness','SOLIDIFY');solid.thickness=.015
    curve('Clothes_shirt_hem_seam',hem[::5],M['piping'],.0035,cyclic=True)
    sleeve('Clothes_raised_scalloped_sleeve',(-.43,.02,5.335),(-.77,-.015,5.235),M['fabric'],M['white'])
    sleeve('Clothes_relaxed_scalloped_sleeve',(.455,.025,5.285),(.585,-.025,4.665),M['fabric'],M['white'])
    shoulder_caps(M);fitted_shorts(M,legs)
    garment_details(M);close_shoulders(M)

def garment_details(M):
    for sign in [-1,1]:
        boundary=[(sign*.14,-.15,5.46),(sign*.29,-.185,5.445),(sign*.46,-.245,5.335),(sign*.405,-.30,5.255),(sign*.265,-.322,5.266),(sign*.348,-.333,5.135),(sign*.315,-.348,5.072),(sign*.022,-.355,4.985),(sign*.16,-.285,5.315)]
        ob,edge=panel('Clothes_white_lapel_'+str(sign),boundary,M['white'],bulge=.017,thickness=.014)
        curve('Clothes_collar_piping_'+str(sign),edge[::2],M['piping'],.0045,cyclic=True)
    line=[(.005,-.30,3.965),(-.012,-.302,4.11),(.011,-.295,4.43),(.014,-.29,4.72),(.008,-.293,4.995)]
    curve('Clothes_button_placket',line,M['white'],.017)
    curve('Clothes_placket_stitch',[(x+.022,y+.003,z) for x,y,z in line],M['piping'],.003)
    for i,z in enumerate([4.78,4.46,4.13,3.9]):
        x=.004*sin(z*7);y=-.318
        sphere('Clothes_pearl_button_'+str(i),(x,y,z),(.027,.012,.030),M['white'],segments=24,rings=16)
        for s in [-1,1]:sphere('Clothes_button_hole_'+str(i)+'_'+str(s),(x+s*.008,y-.012,z),(.0035,.002,.0045),M['sole'],segments=12,rings=8)
    border=[(.20,-.29,4.65),(.41,-.173,4.63),(.40,-.185,4.31),(.28,-.272,4.30),(.20,-.298,4.38)]
    ob,edge=panel('Clothes_chest_pocket',border,M['fabric'],bulge=.012,thickness=.010,uvscale=.96)
    curve('Clothes_pocket_stitch',edge[::4],M['piping'],.0033,cyclic=True)
    curve('Clothes_pocket_opening',border[:2],M['white'],.010)

def close_shoulders(M):
    verts=[];faces=[];uv=[];n=128
    for i in range(n+1):
        a=2*pi*i/n-pi;z=5.395-.43*exp(-(a/.32)**2)
        r=1+.009*sin(12*a-z*4)
        outer=(.025+.555*sin(a)*r,.012-.245*cos(a)*r,z)
        inner=(.008+.14*sin(a),.012-.135*cos(a),5.435)
        verts.extend([outer,inner]);uv.extend([(outer[0],outer[2]),(inner[0],inner[2])])
    for i in range(n):
        if abs(2*pi*(i+.5)/n-pi)>.36:faces.append((2*i,2*i+2,2*i+3,2*i+1))
    mesh('Clothes_closed_shoulders',verts,faces,M['fabric'],uv)

def leg_center(leg,z):
    hip=Vector(leg['hip']);knee=Vector(leg['knee'])
    t=max(0,min(1,(hip.z-z)/(hip.z-knee.z)))
    return hip.lerp(knee,t)

def fitted_shorts(M,legs):
    pants=[]
    for sign,label in [(-1,'rear'),(1,'front')]:
        sections=[];leg=legs[label]
        for z,rx,ry in [(2.945,.30,.28),(3.16,.34,.31),(3.44,.33,.31),(3.80,.315,.30)]:
            p=leg_center(leg,z);p.x+=sign*.025
            if z>3.4:p.x=sign*.28;p.y=.026+(p.y-.026)*max(0,(3.8-z)/.4)
            sections.append((p.x,p.y,z,rx,ry))
        pants.append(loft('Clothes_short_leg_'+label,sections,M['fabric'],sides=64,steps=5,uvscale=1.8,wrinkle=.01))
    waist=[(0,.03,3.42,.59,.31),(0,.025,3.67,.615,.31),(0,.02,3.86,.604,.30)]
    pants.append(loft('Clothes_short_waist',waist,M['fabric'],sides=80,steps=4,uvscale=2.8))
    pants=union('Clothes_soft_pajama_shorts',pants,.015,4);box_uv(pants,.96)
    for sign,label in [(-1,'rear'),(1,'front')]:
        cuff('Clothes_'+label+'_gathered_cuff',sign*.29,M,leg=legs[label])

def shoulder_caps(M):
    specs=[('raised',(-.43,.02,5.29),(.23,.23,.16)),('relaxed',(.435,.015,5.27),(.21,.235,.15))]
    for label,location,scale in specs:
        ob=sphere('Clothes_'+label+'_shoulder_patch',location,scale,M['fabric'])
        bpy.context.view_layer.update();box_uv(ob,.96)

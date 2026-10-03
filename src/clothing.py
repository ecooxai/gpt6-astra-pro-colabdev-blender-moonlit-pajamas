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

def cuff(name,cx,M):
    verts=[];faces=[];uv=[];ns=96;nr=10;edge=[]
    for i in range(nr+1):
        t=i/nr
        for j in range(ns+1):
            a=2*pi*j/ns;r=.285+.027*sin(pi*t);z=3.025-.13*t-.082*(.5+.5*cos(8*a))*t**2
            p=(cx+r*sin(a),.024-(.251+.022*sin(pi*t))*cos(a),z);verts.append(p);uv.append((j/ns*1.6,z*.91))
            if i==0:edge.append(p)
    for i in range(nr):
        for j in range(ns):
            a=i*(ns+1)+j;faces.append((a,a+1,a+ns+2,a+ns+1))
    ob=mesh(name,verts,faces,M['fabric'],uv);sol=ob.modifiers.new('Rounded cuff thickness','SOLIDIFY');sol.thickness=.025
    curve(name+'_upper_piping',edge[::4],M['white'],.008,cyclic=True)

def build_clothes(M):
    verts=[];faces=[];uv=[];ns=128;nr=48;hem=[]
    for i in range(nr+1):
        t=i/nr
        for j in range(ns+1):
            a=2*pi*j/ns-pi;bottom=3.785+.045*cos(a);top=5.395-.43*exp(-(a/.32)**2);z=bottom+(top-bottom)*t
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
    pants=[]
    for s in [-1,1]:
        sections=[(s*.29,.024,2.945,.285,.254),(s*.30,.025,3.16,.333,.283),(s*.285,.03,3.44,.331,.292),(s*.28,.02,3.80,.315,.295)]
        pants.append(loft('Clothes_short_leg_'+str(s),sections,M['fabric'],sides=64,steps=5,uvscale=1.8,wrinkle=.014))
    pants.append(loft('Clothes_short_waist',[(0,.03,3.42,.59,.291),(0,.025,3.67,.615,.305),(0,.02,3.86,.604,.294)],M['fabric'],sides=80,steps=4,uvscale=2.8))
    pants=union('Clothes_soft_pajama_shorts',pants,.019,4);box_uv(pants,.96)
    cuff('Clothes_left_gathered_cuff',-.29,M);cuff('Clothes_right_gathered_cuff',.29,M)
    garment_details(M);close_shoulders(M)

def garment_details(M):
    for sign in [-1,1]:
        boundary=[(sign*.14,-.135,5.46),(sign*.36,-.17,5.42),(sign*.48,-.185,5.30),(sign*.285,-.305,5.20),(sign*.35,-.265,5.055),(sign*.022,-.343,4.985),(sign*.16,-.267,5.315)]
        ob,edge=flat_panel('Clothes_white_lapel_'+str(sign),boundary,M['white'],bulge=.017,thickness=.014)
        crease('Clothes_collar_piping_'+str(sign),edge,M['piping'],.0045)
    line=[(.005,-.30,3.83),(-.012,-.302,4.11),(.011,-.295,4.43),(.014,-.29,4.72),(.008,-.293,4.995)]
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

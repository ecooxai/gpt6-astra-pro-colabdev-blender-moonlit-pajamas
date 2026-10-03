from geometry import *
from math import exp,sqrt

def sleeve(name,start,end,material,piping):
    start=Vector(start);end=Vector(end);axis=(end-start).normalized();side=axis.cross(Vector((0,-1,0))).normalized();depth=side.cross(axis).normalized()
    verts=[];faces=[];uv=[];edge=[];ns=80;nr=20
    for i in range(nr+1):
        t=i/nr;rad=.212+(.085 if 'raised' in name else .052)*sin(pi*t*.72)
        for j in range(ns+1):
            a=2*pi*j/ns;along=(end-start).length*t+.075*(.5+.5*cos((5 if 'raised' in name else 7)*a))*t**5
            p=start+axis*along+side*(rad*cos(a))+depth*(rad*sin(a));verts.append(p);uv.append((j/ns*1.5,-t*.64))
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
            a=2*pi*j/ns;r=.285+.022*t+.035*sin(pi*t)+.012*cos(8*a)*sin(pi*t);z=3.04-.13*t-.095*(.5+.5*cos(8*a))*t**2
            center=leg_center(leg,z) if leg else Vector((cx,.024,z))
            p=(center.x+r*sin(a),center.y-(.251+.022*t+.030*sin(pi*t))*cos(a),z);verts.append(p);uv.append((j/ns*1.6,z*.91))
            if i==0:edge.append(p)
    for i in range(nr):
        for j in range(ns):
            a=i*(ns+1)+j;faces.append((a,a+1,a+ns+2,a+ns+1))
    ob=mesh(name,verts,faces,M['fabricShade'],uv);sol=ob.modifiers.new('Rounded cuff thickness','SOLIDIFY');sol.thickness=.025
    curve(name+'_upper_piping',edge[::4],M['fabricShade'],.003,cyclic=True)

def build_clothes(M,legs):
    verts=[];faces=[];uv=[];ns=128;nr=48;hem=[]
    for i in range(nr+1):
        t=i/nr
        for j in range(ns+1):
            a=2*pi*j/ns-pi;bottom=3.785+.055*cos(a)+.14*exp(-((a+.16)/.068)**2);top=5.395-.43*exp(-(a/.32)**2);z=bottom+(top-bottom)*t
            rx=.49+.13*(1-t)**2+.065*t**6-.022*sin(t*pi);ry=.245+.045*(1-t)+.024*sin(t*pi)
            ripple=1+.023*sin(7*a+z*5)*(1-t)+.012*sin(12*a-z*4)
            ripple+=.035*sin(18*a+z*8)*exp(-((t-.27)/.24)**2)
            x=.025*t+rx*sin(a)*ripple;y=.012-ry*cos(a)*ripple
            verts.append((x,y,z));uv.append((j/ns*2.9,z*.91))
            if i==0:hem.append((x,y-.001,z))
    for i in range(nr):
        for j in range(ns):
            a=i*(ns+1)+j;faces.append((a,a+1,a+ns+2,a+ns+1))
    shirt=mesh('Clothes_pajama_shirt',verts,faces,M['fabric'],uv)
    solid=shirt.modifiers.new('Cotton thickness','SOLIDIFY');solid.thickness=.015
    curve('Clothes_shirt_hem_seam',hem[::5],M['piping'],.0035,cyclic=True)
    sleeve('Clothes_raised_scalloped_sleeve',(-.43,.02,5.39),(-.77,-.015,5.32),M['fabric'],M['white'])
    sleeve('Clothes_relaxed_scalloped_sleeve',(.455,.025,5.36),(.585,-.025,4.665),M['fabric'],M['white'])
    shoulder_caps(M);fitted_shorts(M,legs)
    garment_details(M);close_shoulders(M)

def garment_details(M):
    # Rolled collar sits around the neck and flows into broad pajama lapels.
    for sign in [-1,1]:
        roll=[(sign*.135,-.085,5.47),(sign*.260,-.115,5.475),(sign*.448,-.197,5.365),
              (sign*.410,-.263,5.285),(sign*.270,-.286,5.270),(sign*.163,-.236,5.344)]
        roll=[(x if sign>0 else -.135+(x+.135)*.73,y-.09,z+.025*max(0,(5.40-z)/.13)) for x,y,z in roll]
        ob,edge=panel('Clothes_white_rolled_collar_'+str(sign),roll,M['collarShade'],bulge=.012,thickness=.018)
        curve('Clothes_rolled_collar_piping_'+str(sign),edge[::3],M['white'],.008,cyclic=True)
    left=[(-.165,-.332,5.347),(-.267,-.290,5.268),(-.404,-.302,5.218),
          (-.360,-.320,5.117),(-.165,-.352,4.936),(-.102,-.323,5.075)]
    right=[(.161,-.325,5.346),(.273,-.289,5.275),(.350,-.318,5.188),
           (.362,-.348,5.080),(-.150,-.366,4.945),(.148,-.309,5.183)]
    for label,bd in [('left',left),('right',right)]:
        ob,edge=panel('Clothes_white_lapel_'+label,bd,M['white'],bulge=.012,thickness=.013)
        curve('Clothes_lapel_piping_'+label,edge[::3],M['piping'],.0045,cyclic=True)
    line=[(-.098,-.303,3.960),(-.112,-.308,4.13),(-.106,-.302,4.43),(-.108,-.307,4.72),(-.150,-.357,4.944)]
    curve('Clothes_button_placket',line,M['white'],.017)
    curve('Clothes_placket_stitch',[(x+.022,y+.003,z) for x,y,z in line],M['piping'],.003)
    for i,z in enumerate([4.81,4.47,4.12,3.90]):
        x=-.108;y=-.331
        sphere('Clothes_pearl_button_'+str(i),(x,y,z),(.030,.014,.034),M['white'],segments=24,rings=16)
        curve('Clothes_button_rim_'+str(i),[(x+.023*cos(2*pi*j/16),y-.013,z+.026*sin(2*pi*j/16)) for j in range(16)],M['piping'],.002,cyclic=True)
        for t in [-1,1]:sphere('Clothes_button_hole_'+str(i)+'_'+str(t),(x+t*.008,y-.015,z),(.0035,.002,.0045),M['sole'],segments=12,rings=8)
    border=[(.155,-.322,4.975),(.467,-.231,4.925),(.432,-.270,4.555),(.307,-.316,4.507),(.151,-.340,4.567)]
    ob,edge=panel('Clothes_chest_pocket',border,M['fabric'],bulge=.022,thickness=.012,uvscale=.96)
    curve('Clothes_pocket_stitch',edge[::4],M['piping'],.0038,cyclic=True)
    curve('Clothes_pocket_opening',[border[0],(.320,-.293,4.968),border[1]],M['white'],.011)
    curve('Clothes_pocket_fold',[(.164,-.337,4.913),(.307,-.321,4.907),(.456,-.250,4.866)],M['piping'],.003)

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
        for z,rx,ry in [(2.945,.311,.28),(3.16,.354,.31),(3.44,.34,.31),(3.80,.315,.30)]:
            p=leg_center(leg,z);p.x+=sign*.025
            if z>3.4:p.x=-.12+sign*.28;p.y=.026+(p.y-.026)*max(0,(3.8-z)/.4)
            sections.append((p.x,p.y,z,rx,ry))
        pants.append(loft('Clothes_short_leg_'+label,sections,M['fabric'],sides=64,steps=5,uvscale=1.8,wrinkle=.01))
    waist=[(-.12,.03,3.14,.38,.10),(-.12,.03,3.31,.57,.23),(-.12,.03,3.49,.605,.30),(-.12,.025,3.67,.615,.31),(-.12,.02,3.86,.604,.30)]
    pants.append(loft('Clothes_short_waist',waist,M['fabric'],sides=80,steps=4,uvscale=2.8))
    pants=union('Clothes_soft_pajama_shorts',pants,.015,4)
    for v in pants.data.vertices:
        x,y,z=v.co;front=max(0,min(1,(-y-.05)/.22));weight=exp(-((z-3.12)/.21)**2)
        v.co.y-=front*.040*sin(15*(x+.12)+7*z)*weight
    pants.data.update();box_uv(pants,.96)
    for sign,label in [(-1,'rear'),(1,'front')]:
        cuff('Clothes_'+label+'_gathered_cuff',sign*.29,M,leg=legs[label])

def shoulder_caps(M):
    specs=[('raised',(-.48,.02,5.32),(.185,.23,.15)),('relaxed',(.485,.015,5.30),(.17,.23,.14))]
    for label,location,scale in specs:
        ob=sphere('Clothes_'+label+'_shoulder_patch',location,scale,M['fabric'])
        bpy.context.view_layer.update();box_uv(ob,.96)

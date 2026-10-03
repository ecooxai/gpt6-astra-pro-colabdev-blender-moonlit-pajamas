from geometry import *
from math import exp,sqrt

def pillow_point(u,v,side):
    d=(u+1)**2+(v-1)**2
    inflate=.29*max(0,(1-u*u)*(1-v*v))**.55
    folds=.040*exp(-((v-.77+.66*(u+1))/.065)**2)*exp(-d/1.65)
    folds-=.028*exp(-((v-.72+.91*(u+1))/.075)**2)*exp(-d/1.30)
    folds+=.018*sin(19*v-6*u)*exp(-((u-.83)**2+(v+.68)**2)/.18)
    folds+=.038*exp(-((u+.32-.22*v)/.085)**2)*max(0,1-v*v)**.6
    pinch=-.207*exp(-d/.085)
    x=.86+.47*u+.45*v+.036*sin(pi*v)*(1-u*u)+.019*sin(3*pi*v)*abs(u)**9
    z=2.08-.37*u+.85*v+.027*sin(pi*u)*sin(pi*v)+.015*sin(3*pi*u)*abs(v)**9
    return (x,.12+side*(.018+inflate+folds)+pinch,z)

def build_pillow(M):
    verts=[];faces=[];uv=[];n=52;offset=(n+1)**2
    for side in [-1,1]:
        for i in range(n+1):
            for j in range(n+1):
                u=2*i/n-1;v=2*j/n-1;verts.append(pillow_point(u,v,side));uv.append((i/n,j/n))
    for layer in range(2):
        for i in range(n):
            for j in range(n):
                a=layer*offset+i*(n+1)+j;f=(a,a+n+1,a+n+2,a+1);faces.append(f if layer==0 else tuple(reversed(f)))
    perimeter=[i*(n+1) for i in range(n+1)]+[n*(n+1)+j for j in range(1,n+1)]+[i*(n+1)+n for i in range(n-1,-1,-1)]+[j for j in range(n-1,0,-1)]
    for i,a in enumerate(perimeter):
        b=perimeter[(i+1)%len(perimeter)];faces.append((a,b,b+offset,a+offset))
    mesh('Accessory_inflated_cotton_pillow',verts,faces,M['white'],uv)
    edge=[verts[k] for k in perimeter[::4]]
    curve('Accessory_pillow_piped_seam',edge,M['sole'],.0055,cyclic=True)

def build_headwear(M):
    pts=[];rs=[]
    for i in range(33):
        a=-1.56+3.12*i/32;pts.append((.582*sin(a),.09-.18*cos(a),6.07+.684*cos(a)));rs.append(.067*(1+.11*sin(i*2.2)))
    tube('HeadWear_soft_headband',pts,rs,M['white'],sides=16,steps=2,flatten=.62)
    left=[(-.015,-.12,6.80),(-.27,-.14,6.83),(-.45,-.10,6.98),(-.30,-.045,7.05),(-.18,-.07,7.02),(-.01,-.11,6.86)]
    right=[(.01,-.12,6.81),(.24,-.13,6.86),(.42,-.08,7.14),(.29,-.035,7.115),(.10,-.07,6.99),(.005,-.10,6.86)]
    for name,bd in [('left',left),('right',right)]:
        ob,edge=panel('HeadWear_bow_'+name,bd,M['white'],bulge=.047,thickness=.022)
        curve('HeadWear_bow_edge_'+name,edge[::4],M['piping'],.0025,cyclic=True)
    sphere('HeadWear_bow_knot',(.004,-.142,6.85),(.067,.059,.077),M['white'],rotation=(0,-.2,0))
    curve('HeadWear_bow_fold_left',[(-.02,-.19,6.85),(-.14,-.165,6.9),(-.23,-.145,6.95)],M['piping'],.0028,radii=[.2,.6,.03])
    curve('HeadWear_bow_fold_right',[(.03,-.187,6.87),(.12,-.161,6.94),(.23,-.13,7.04)],M['piping'],.0028,radii=[.2,.6,.03])
    verts=[];faces=[];ns=128
    for i in range(ns):
        a=2*pi*i/ns
        for radial,z in [(-.019,-.024),(.019,-.024),(.019,.024),(-.019,.024)]:
            verts.append(((.685+radial)*cos(a),(.40+radial)*sin(a),z))
    for i in range(ns):
        for j in range(4):faces.append((i*4+j,((i+1)%ns)*4+j,((i+1)%ns)*4+(j+1)%4,i*4+(j+1)%4))
    halo=mesh('Accessory_dark_elliptical_halo',verts,faces,M['halo']);halo.location=(0,.045,7.31);halo.rotation_euler=(-.15,.045,0)
    bevel=halo.modifiers.new('Machined halo bevel','BEVEL');bevel.width=.005;bevel.segments=3
    pts=[(.704*cos(2*pi*i/32),.419*sin(2*pi*i/32),-.011) for i in range(32)]
    glow=curve('Accessory_cyan_halo_inlay',pts,M['haloBlue'],.004,cyclic=True);glow.location=halo.location;glow.rotation_euler=halo.rotation_euler

def slipper_ribbon(label,cx,cy,base,sign,M):
    verts=[];faces=[];edge=[];nu=22;nv=12
    for i in range(nu+1):
        t=i/nu;span=.014+.034*sin(pi*t*.62)
        for j in range(nv+1):
            v=2*j/nv-1;yr=span*v;zr=.020*sin(pi*t)*(1-v*v)
            p=(cx+sign*(.009+.105*t),cy-.14+yr*cos(.76)-zr*sin(.76),base+.315+yr*sin(.76)+zr*cos(.76))
            verts.append(p)
            if j==0:edge.append(p)
    for i in range(nu):
        for j in range(nv):
            k=i*(nv+1)+j;faces.append((k,k+1,k+nv+2,k+nv+1))
    ob=mesh('Accessory_'+label+'_pink_bow_loop_'+str(sign),verts,faces,M['pink'])
    mod=ob.modifiers.new('Folded ribbon thickness','SOLIDIFY');mod.thickness=.006
    curve('Accessory_'+label+'_bow_stitch_'+str(sign),edge[::3],M['pinkLight'],.0015)

def build_slippers(M,legs):
    for label,base in [('front',.035),('rear',.38)]:
        ankle=Vector(legs[label]['ankle']);cx=ankle.x;cy=ankle.y-.13
        sphere('Body_'+label+'_foot',(cx,ankle.y-.06,base+.132),(.097,.232,.091),M['skin'])
        sections=[(cx,cy,base,.152,.25),(cx,cy,base+.021,.176,.29),(cx,cy,base+.058,.179,.294),(cx,cy,base+.076,.166,.28)]
        loft('Accessory_'+label+'_slipper_sole',sections,M['sole'],sides=64,steps=3)
        edge=[(cx+.176*sin(2*pi*i/40),cy-.289*cos(2*pi*i/40),base+.072) for i in range(40)]
        curve('Accessory_'+label+'_sole_piping',edge,M['white'],.008,cyclic=True)
        profiles=[(-.299,.015,.027),(-.26,.116,.066),(-.175,.17,.135),(-.07,.174,.176),(.015,.153,.155),(.084,.128,.128)]
        verts=[];faces=[];uv=[];ns=32
        ps,width=sample([(0,y,0) for y,w,h in profiles],[w for y,w,h in profiles],5)
        _,height=sample([(0,y,0) for y,w,h in profiles],[h for y,w,h in profiles],5)
        for i,p in enumerate(ps):
            for j in range(ns+1):
                a=-pi/2+pi*j/ns;ripple=1+.013*cos(j*1.9)
                verts.append((cx+width[i]*sin(a)*ripple,cy+p.y,base+.081+height[i]*cos(a)))
                uv.append((j/ns,i/(len(ps)-1)))
        for i in range(len(ps)-1):
            for j in range(ns):
                a=i*(ns+1)+j;faces.append((a,a+1,a+ns+2,a+ns+1))
        faces.append(tuple(reversed(range(ns+1))))
        ob=mesh('Accessory_'+label+'_soft_slipper_upper',verts,faces,M['white'],uv)
        sol=ob.modifiers.new('Plush upper thickness','SOLIDIFY');sol.thickness=.021
        edge=verts[-(ns+1):];curve('Accessory_'+label+'_slipper_opening',edge[::3],M['white'],.012)
        for sign in [-1,1]:slipper_ribbon(label,cx,cy,base,sign,M)
        sphere('Accessory_'+label+'_pink_bow_knot',(cx,cy-.141,base+.315),(.020,.022,.020),M['pinkLight'],segments=24,rings=16)

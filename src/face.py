from geometry import *
from math import sqrt,exp
HEAD=[(5.59,.022,.06,-.006),(5.61,.09,.125,-.012),(5.65,.19,.185,-.006),(5.75,.315,.265,.002),(5.87,.414,.32,.016),(6.02,.475,.357,.028),(6.2,.493,.375,.04),(6.39,.47,.36,.055),(6.54,.37,.31,.066),(6.63,.20,.20,.07),(6.675,.02,.04,.075)]
def profile(z):
    z=max(HEAD[0][0],min(HEAD[-1][0],z))
    for a,b in zip(HEAD[:-1],HEAD[1:]):
        if a[0]<=z<=b[0]:
            t=(z-a[0])/(b[0]-a[0]);return [a[k]*(1-t)+b[k]*t for k in [1,2,3]]
    return HEAD[-1][1:]
def face_y(x,z):
    rx,ry,cy=profile(z)
    return cy-ry*max(.004,1-(x/rx)**2)**.25-.031*exp(-(x/.067)**2-((z-5.94)/.09)**2)
def eye_bounds(s):
    s=max(0,min(1,s));a=max(0,sin(pi*s))
    return 6.025-.078*a**.70+.026*s,6.025+.062*a**.72+.026*s

def build_face(M):
    verts=[];uv=[];faces=[];nr=82;ns=128
    for i in range(nr+1):
        z=HEAD[0][0]+(HEAD[-1][0]-HEAD[0][0])*i/nr;rx,ry,cy=profile(z)
        for j in range(ns+1):
            a=2*pi*j/ns-pi;x=rx*sin(a);c=cos(a);y=cy-ry*abs(c)**(.5 if c>0 else 1)*(1 if c>=0 else -1)
            if c>0:y-=.031*exp(-(x/.067)**2-((z-5.94)/.09)**2)*c**4
            verts.append((x,y,z));uv.append((j/ns,i/nr))
    for i in range(nr):
        for j in range(ns):
            a=i*(ns+1)+j;b=a+ns+1;faces.append((a,a+1,b+1,b))
    faces.append(tuple(reversed(range(ns))));faces.append(tuple(nr*(ns+1)+j for j in range(ns)))
    head=mesh('Head_original_anime_head',verts,faces,M['face'],uv)
    for sign in [-1,1]:
        sphere('Head_ear_'+str(sign),(sign*.471,.025,5.952),(.075,.065,.117),M['skin'])
        sphere('Head_ear_inner_'+str(sign),(sign*.508,-.022,5.956),(.026,.018,.069),M['pinkLight'],segments=24,rings=16)
        verts=[];uv=[];faces=[];nu=40;nv=14
        for i in range(nu+1):
            s=i/nu;x=sign*(.07+.29*s);lo,hi=eye_bounds(s)
            for j in range(nv+1):
                v=j/nv;z=lo+(hi-lo)*v;y=face_y(x,z)-.012-.018*sin(pi*s)*sin(pi*v)
                verts.append((x,y,z));uv.append((s,v))
        for i in range(nu):
            for j in range(nv):
                a=i*(nv+1)+j;faces.append((a,a+nv+1,a+nv+2,a+1) if sign>0 else (a,a+1,a+nv+2,a+nv+1))
        mesh('Head_eye_white_'+str(sign),verts,faces,M['eyeWhite'],uv)
        cx=sign*.215;cz=6.034;rx=.078;rz=.087
        vv=[(cx,face_y(cx,cz)-.052,cz)];uu=[(.5,.5)];ff=[];sides=80;nr=9
        for k in range(1,nr+1):
            r=k/nr
            for j in range(sides):
                a=2*pi*j/sides;x=cx+rx*r*cos(a);z=cz+rz*r*sin(a)
                lo,hi=eye_bounds((abs(x)-.07)/.29);z=max(lo+.002,min(hi-.002,z))
                vv.append((x,face_y(x,z)-.042-.01*sqrt(max(0,1-r*r)),z));uu.append((.5+.5*r*cos(a),.5+.5*r*sin(a)))
        for j in range(sides):ff.append((0,1+j,1+(j+1)%sides))
        for k in range(nr-1):
            for j in range(sides):
                a=1+k*sides+j;b=1+k*sides+(j+1)%sides;ff.append((a,a+sides,b+sides,b))
        mesh('Head_violet_iris_'+str(sign),vv,ff,M['iris'],uu)
        def pt(x,z,offset=.029):return (sign*x,face_y(sign*x,z)-offset,z)
        top=[pt(.07+.29*s,eye_bounds(s)[1],.027) for s in [0,.17,.4,.67,.87,1]]
        top.append(pt(.397,6.078,.022))
        curve('Head_upper_eyelash_'+str(sign),top,M['lash'],.011,radii=[.12,.6,.95,1.2,1.3,.8,.015])
        panel('Head_lash_wing_'+str(sign),[pt(.342,6.083),pt(.392,6.106),pt(.362,6.047)],M['lash'],bulge=0,thickness=.002)
        pts=[pt(.07+.29*s,eye_bounds(s)[0],.016) for s in [.22,.43,.66,.89,.98]]
        curve('Head_lower_lid_'+str(sign),pts,M['mouth'],.0036,radii=[.1,.5,.7,.8,.1])
        pts=[pt(.075,6.235,.009),pt(.18,6.253,.009),pt(.280,6.249,.009),pt(.360,6.227,.009)]
        curve('Head_brow_'+str(sign),pts,M['hairDark'],.008,radii=[.22,1,.7,.08])
        for j in range(3):
            x=sign*(.284+j*.032);z=5.933-j*.004
            curve('Head_blush_'+str(sign)+'_'+str(j),[(x-.007,face_y(x-.007,z-.016)-.002,z-.016),(x+.007,face_y(x+.007,z+.012)-.002,z+.012)],M['pinkLight'],.0022,radii=[.5,.3])
    z=5.825
    curve('Head_quiet_mouth',[(-.009,face_y(-.009,z)-.005,z),(.006,face_y(.006,z+.003)-.005,z+.003),(.021,face_y(.021,z-.001)-.004,z-.001)],M['mouth'],.0042,radii=[.08,.8,.2])
    sphere('Head_nose_tip',(0,face_y(0,5.932)-.003,5.932),(.012,.007,.015),M['nail'],segments=24,rings=14)
    return head

HEAD=[(5.635,.008,.043,0),(5.665,.075,.11,-.005),(5.725,.17,.17,0),(5.80,.29,.25,.015),(5.88,.40,.315,.028),(6.02,.475,.357,.028),(6.20,.493,.375,.04),(6.39,.47,.36,.055),(6.54,.37,.31,.066),(6.63,.20,.20,.07),(6.675,.02,.04,.075)]

def profile(z):
    z=max(HEAD[0][0],min(HEAD[-1][0],z))
    for i,(a,b) in enumerate(zip(HEAD[:-1],HEAD[1:])):
        if a[0]<=z<=b[0]:
            prev=HEAD[max(0,i-1)];nxt=HEAD[min(len(HEAD)-1,i+2)]
            dz=b[0]-a[0];t=(z-a[0])/dz;result=[]
            for k in [1,2,3]:
                m0=(b[k]-prev[k])/(b[0]-prev[0]);m1=(nxt[k]-a[k])/(nxt[0]-a[0])
                result.append((2*t**3-3*t*t+1)*a[k]+(t**3-2*t*t+t)*dz*m0+(-2*t**3+3*t*t)*b[k]+(t**3-t*t)*dz*m1)
            return result
    return HEAD[-1][1:]

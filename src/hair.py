"""Original volumetric hair: wrapped scalp, crown-rooted tresses, and swept bangs."""
from geometry import *
from math import exp

def smoothstep(a,b,x):
    t=max(0,min(1,(x-a)/(b-a)))
    return t*t*(3-2*t)

def build_hair(M):
    verts=[];faces=[];uv=[];nr=48;ns=144
    for i in range(nr+1):
        for j in range(ns+1):
            a=2*pi*j/ns-pi
            # Forehead opening stays in front; side and rear scalp wrap below the ears.
            end=.98+1.32*smoothstep(.54,1.20,abs(a))-.17*exp(-((a-.40)/.18)**2)
            p=.006+(end-.006)*i/nr
            c=cos(a); front=abs(c)**.48 if c>0 else abs(c)
            verts.append((.558*sin(p)*sin(a),.07-.478*sin(p)*front*(1 if c>=0 else -1),6.07+.660*cos(p)))
            uv.append((j/ns,i/nr))
    for i in range(nr):
        for j in range(ns):
            k=i*(ns+1)+j;faces.append((k,k+1,k+ns+2,k+ns+1))
    mesh('HairTop_crown_cap',verts,faces,M['hair'],uv)
    # Tresses follow the scalp from the crown before separating at the nape.
    # Their top points are deliberately outside the scalp, avoiding cut-off roots.
    for i in range(13):
        a=pi*i/12;c=cos(a);s=sin(a)
        pts=[(.075*c,.07+.065*s,6.733),(.285*c,.07+.255*s,6.61),
             (.482*c,.07+.421*s,6.36),(.554*c,.07+.468*s,6.02),
             (.62*c+.095,.32+.24*s,5.32),(.78*c+.18,.32+.20*s,4.62),
             (.93*c+.24+.065*sin(i*1.7),.23+.18*s,4.02+.19*sin(i*1.73)**2)]
        mat=M[['hair','hair','hairLight','hair','hairDark'][i%5]]
        hair_lock('HairLong_layer_'+str(i+1),pts,[.002,.065,.105,.15,.176,.143,.001],
                  [.002,.014,.023,.035,.059,.040,.001],mat,normal=(c,s,0),groove_mat=M['hairInk'])
    for sign in [-1,1]:
        for i in range(3):
            pts=[(sign*.47,.13,5.99-i*.09),(sign*(.59+i*.025),.18,5.36-i*.1),
                 (sign*(.86+i*.05),.17,4.72-i*.15),(sign*(1.13-i*.16),.08,4.55-i*.22)]
            hair_lock('HairLong_side_wisp_'+str(sign)+'_'+str(i),pts,
                      ([.018,.060,.038,.001] if sign<0 else [.035,.09,.075,.001]),
                      ([.008,.022,.016,.001] if sign<0 else [.020,.037,.028,.001]),
                      M['hair' if i%2 else 'hairDark'],normal=(0,-1,0),groove_mat=M['hairInk'])
    def lock(name,pts,widths,key='hair'):
        return hair_lock('HairTop_'+name,pts,widths,[min(.044,max(.002,w*.31)) for w in widths],M[key],groove_mat=M['hairInk'],sides=16)
    lock('left_outer_fringe',[(-.05,-.20,6.69),(-.31,-.32,6.46),(-.49,-.33,6.12),(-.50,-.29,5.78),(-.37,-.24,5.63)],[.085,.15,.15,.08,.002])
    lock('left_inner_fringe',[(-.07,-.22,6.69),(-.23,-.44,6.40),(-.34,-.44,6.28),(-.35,-.41,6.14)],[.06,.105,.085,.002],'hairLight')
    lock('central_swept_fringe',[(-.035,-.24,6.70),(-.095,-.445,6.49),(-.055,-.50,6.27),(.13,-.455,6.085)],[.060,.150,.131,.002])
    lock('right_outer_frame',[(.035,-.18,6.70),(.33,-.29,6.54),(.48,-.31,6.17),(.46,-.29,5.79),(.32,-.27,5.65)],[.07,.16,.135,.085,.002])
    lock('right_inner_frame',[(.025,-.25,6.68),(.235,-.37,6.50),(.29,-.42,6.23),(.39,-.35,5.95)],[.05,.087,.060,.002],'hairLight')
    for sign in [-1,1]:
        lock('temple_layer_'+str(sign),[(sign*.44,-.020,6.42),(sign*.545,-.095,6.10),(sign*.585,-.12,5.82),(sign*.53,-.18,5.53),(sign*.44,-.20,5.60)],[.07,.09,.104,.053,.002],'hairDark' if sign<0 else 'hair')
    lock('curled_flyaway',[(-.03,-.055,6.71),(-.37,-.07,6.67),(-.61,-.06,6.79),(-.59,-.045,6.93),(-.50,-.015,6.98)],[.013,.025,.028,.015,.001],'hairLight')

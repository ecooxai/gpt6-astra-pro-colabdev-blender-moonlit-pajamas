from geometry import *
from math import exp

def build_hair(M):
    verts=[];faces=[];uv=[];nr=42;ns=128
    for i in range(nr+1):
        for j in range(ns+1):
            a=2*pi*j/ns-pi;end=1.16+.99*(.5-.5*cos(a))**.4-.75*exp(-((a-.40)/.28)**2);p=.008+(end-.008)*i/nr
            verts.append((.548*sin(p)*sin(a),.07-.451*sin(p)*cos(a),6.07+.657*cos(p)));uv.append((j/ns,i/nr))
    for i in range(nr):
        for j in range(ns):
            a=i*(ns+1)+j;faces.append((a,a+1,a+ns+2,a+ns+1))
    mesh('HairTop_crown_cap',verts,faces,M['hair'],uv)
    # Eleven broad, solid back tresses with varied pointed ends.
    for i in range(11):
        a=pi*i/10;c=cos(a);s=sin(a)
        pts=[(.17*c,.09+.15*s,6.65),(.46*c,.16+.27*s,6.19),(.53*c,.25+.22*s,5.82),(.62*c+.10,.31+.22*s,5.13),(.75*c+.18,.30+.18*s,4.58),(.89*c+.24+.06*sin(i*2),.22+.18*s,4.05+.14*sin(i*1.9)**2)]
        mat=M[['hair','hairDark','hair','hairLight'][i%4]]
        hair_lock('HairLong_layer_'+str(i+1),pts,[.008,.125,.18,.205,.15,.002],[.008,.04,.075,.069,.045,.002],mat,normal=(c,s,0),groove_mat=M['hairInk'])
    for sign in [-1,1]:
        for i in range(3):
            pts=[(sign*.47,.13,5.99-i*.09),(sign*(.59+i*.025),.18,5.36-i*.1),(sign*(.86+i*.05),.17,4.72-i*.15),(sign*(1.13-i*.16),.08,4.55-i*.22)]
            hair_lock('HairLong_side_wisp_'+str(sign)+'_'+str(i),pts,([.018,.06,.038,.001] if sign<0 else [.035,.09,.075,.001]),([.008,.022,.016,.001] if sign<0 else [.02,.037,.028,.001]),M['hair' if i%2 else 'hairDark'],normal=(0,-1,0),groove_mat=M['hairInk'])
    def lock(name,pts,widths,key='hair'):
        return hair_lock('HairTop_'+name,pts,widths,[min(.039,max(.002,w*.33)) for w in widths],M[key],groove_mat=M['hairInk'])
    lock('left_outer_fringe',[(-.05,-.20,6.68),(-.31,-.31,6.46),(-.49,-.31,6.12),(-.5,-.27,5.78),(-.37,-.24,5.63)],[.085,.15,.15,.08,.002])
    lock('left_inner_fringe',[(-.07,-.22,6.67),(-.23,-.43,6.38),(-.34,-.43,6.27),(-.34,-.41,6.16)],[.06,.11,.095,.002],'hairLight')
    lock('central_swept_fringe',[(-.035,-.24,6.69),(-.085,-.445,6.48),(-.04,-.50,6.25),(.15,-.445,6.075)],[.06,.16,.14,.002])
    lock('right_outer_frame',[(.035,-.18,6.68),(.33,-.29,6.52),(.48,-.29,6.17),(.46,-.28,5.79),(.32,-.27,5.65)],[.07,.16,.135,.085,.002])
    lock('right_inner_frame',[(.025,-.25,6.67),(.235,-.37,6.48),(.29,-.41,6.21),(.39,-.33,5.95)],[.05,.09,.065,.002],'hairLight')
    for sign in [-1,1]:
        lock('temple_layer_'+str(sign),[(sign*.45,-.025,6.19),(sign*.59,-.075,5.86),(sign*.55,-.17,5.55),(sign*.44,-.20,5.60)],[.075,.103,.058,.002],'hairDark' if sign<0 else 'hair')
    lock('curled_flyaway',[(-.03,-.055,6.70),(-.37,-.07,6.67),(-.61,-.06,6.79),(-.59,-.045,6.93),(-.50,-.015,6.98)],[.013,.025,.028,.015,.001],'hairLight')

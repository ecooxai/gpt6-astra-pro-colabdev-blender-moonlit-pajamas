from geometry import *

def radius(t,knots):
    for (a,ra),(b,rb) in zip(knots[:-1],knots[1:]):
        if a<=t<=b:
            s=(t-a)/(b-a);s=s*s*(3-2*s);return ra*(1-s)+rb*s
    return knots[-1][1]

def rounded_leg(label,hip,knee,ankle,mat):
    hip=Vector(hip);knee=Vector(knee);ankle=Vector(ankle)
    upper=[(0,.232),(.2,.235),(.5,.204),(.85,.155),(1,.142)]
    upper_d=[(0,.216),(.2,.207),(.5,.176),(.85,.143),(1,.140)]
    lower=[(0,.142),(.12,.156),(.28,.173),(.52,.148),(.80,.098),(1,.076)]
    lower_d=[(0,.140),(.12,.155),(.28,.162),(.52,.133),(.80,.103),(1,.085)]
    u=.15/(knee-hip).length;v=.15/(ankle-knee).length
    a=hip.lerp(knee,1-u);b=knee.lerp(ankle,v)
    centers=[];rx=[];ry=[]
    for i in range(27):
        t=i/26*(1-u);centers.append(hip.lerp(knee,t));rx.append(radius(t,upper));ry.append(radius(t,upper_d))
    for i in range(1,15):
        t=i/14;centers.append((1-t)**2*a+2*(1-t)*t*knee+t*t*b)
        rx.append(radius(1-u,upper)*(1-t)+radius(v,lower)*t)
        ry.append(radius(1-u,upper_d)*(1-t)+radius(v,lower_d)*t)
    for i in range(1,34):
        t=v+(1-v)*i/33;centers.append(knee.lerp(ankle,t));rx.append(radius(t,lower));ry.append(radius(t,lower_d))
    verts=[];faces=[];n=64
    for i,p in enumerate(centers):
        tangent=(centers[min(i+1,len(centers)-1)]-centers[max(0,i-1)]).normalized()
        side=(Vector((1,0,0))-tangent*tangent.x).normalized();depth=side.cross(tangent).normalized()
        for j in range(n):
            angle=2*pi*j/n;verts.append(p+side*rx[i]*sin(angle)-depth*ry[i]*cos(angle))
    for i in range(len(centers)-1):
        for j in range(n):
            a=i*n+j;b=i*n+(j+1)%n;faces.append((a,b,b+n,a+n))
    faces.append(tuple(reversed(range(n))));faces.append(tuple((len(centers)-1)*n+j for j in range(n)))
    return mesh('Body_'+label+'_leg',verts,faces,mat)

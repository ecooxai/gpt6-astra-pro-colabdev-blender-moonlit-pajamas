"""Original posed hands with continuous wrists and individually authored digits."""
from geometry import *

def digit(name,pts,r,M):
    return [tube(name,pts,[r,r*.91,r*.79,r*.67],M['skin'],sides=16,steps=7),
            sphere(name+'_pad',pts[-1],(r*.69,)*3,M['skin'],segments=16,rings=12)]

def build_hands(M,raised,relaxed):
    # A single varying-section surface runs through each wrist: no arm/palm cap seam.
    bpy.data.objects.remove(raised,do_unlink=True)
    raised=hair_lock('Body_raised_continuous',[(-.43,.025,5.31),(-.92,-.01,5.29),(-1.26,-.055,5.35),(-1.09,-.13,5.55),(-.88,-.17,5.75),(-.69,-.20,6.02),(-.731,-.235,6.135),(-.763,-.246,6.225)],
        [.151,.143,.125,.12,.097,.061,.077,.066],[.151,.143,.125,.12,.097,.061,.046,.039],M['skin'],steps=10,sides=28)
    parts=[raised]
    fingers=[
      ('index',[(-.687,-.238,6.211),(-.668,-.275,6.292),(-.619,-.281,6.308),(-.593,-.270,6.290)],.0145),
      ('middle',[(-.726,-.240,6.234),(-.727,-.279,6.370),(-.674,-.270,6.386),(-.642,-.255,6.369)],.0155),
      ('ring',[(-.764,-.245,6.226),(-.782,-.278,6.307),(-.735,-.278,6.330),(-.708,-.258,6.316)],.0145),
      ('little',[(-.800,-.235,6.204),(-.857,-.246,6.287),(-.844,-.260,6.355),(-.826,-.244,6.380)],.0125),
      ('thumb',[(-.695,-.220,6.120),(-.662,-.250,6.180),(-.627,-.255,6.230),(-.602,-.240,6.205)],.024)]
    for name,pts,r in fingers:parts.extend(digit('Hand_raised_'+name,pts,r,M))
    raised=union('Body_raised_arm_five_fingers',parts,.0065,4);raised['digits']=5
    for name,pts,r in fingers:
        p=Vector(pts[-1]);p.y-=r*.61
        sphere('Body_raised_arm_nail_'+name,p,(r*.47,.002,r*.60),M['nail'],segments=16,rings=10,rotation=(0,-.5,0))
    bpy.data.objects.remove(relaxed,do_unlink=True)
    relaxed=hair_lock('Body_relaxed_continuous',[(.47,.025,5.25),(.56,-.015,4.70),(.55,-.04,4.21),(.63,-.12,3.74),(.78,-.16,3.29),(.813,-.176,3.215),(.846,-.191,3.160)],
        [.15,.137,.101,.111,.058,.076,.068],[.15,.137,.101,.111,.059,.043,.039],M['skin'],steps=10,sides=28)
    parts=[relaxed]
    for i in range(4):
        root=Vector((.795+i*.031,-.195+i*.009,3.171+i*.008))
        pts=[root,root+Vector((.027,-.017,-.052)),root+Vector((.048,.016,-.102+abs(i-1)*.008)),root+Vector((.030,.063,-.100+abs(i-1)*.008))]
        r=.0145 if i==3 else .017
        parts.extend(digit('Hand_grip_digit_'+str(i),pts,r,M))
    thumb_path=[(.788,-.189,3.240),(.841,-.236,3.185),(.902,-.256,3.112),(.939,-.229,3.048)]
    parts.extend(digit('Hand_grip_thumb',thumb_path,.025,M))
    relaxed=union('Body_relaxed_arm_five_fingers',parts,.0065,5);relaxed['digits']=5
    sphere('Body_relaxed_arm_thumb_nail',(.925,-.250,3.074),(.010,.0025,.017),M['nail'],segments=16,rings=10,rotation=(0,-.55,0))
    curve('Body_relaxed_arm_knuckle_crease',[(.814,-.236,3.213),(.838,-.242,3.197),(.861,-.238,3.190)],M['pinkLight'],.0011,radii=[.02,.35,.02])
    return raised,relaxed

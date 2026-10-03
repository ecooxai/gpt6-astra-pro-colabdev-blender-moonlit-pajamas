"""Original posed hands with continuous wrists and individually authored digits."""
from geometry import *

def digit(name,pts,r,M):
    return [tube(name,pts,[r,r*.91,r*.79,r*.67],M['skin'],sides=16,steps=7),
            sphere(name+'_pad',pts[-1],(r*.69,)*3,M['skin'],segments=16,rings=12)]

def build_hands(M,raised,relaxed):
    # A single varying-section surface runs through each wrist: no arm/palm cap seam.
    bpy.data.objects.remove(raised,do_unlink=True)
    raised=hair_lock('Body_raised_continuous',[(-.43,.025,5.31),(-.92,-.01,5.29),(-1.26,-.055,5.35),(-1.09,-.13,5.55),(-.88,-.17,5.75),(-.69,-.20,6.02),(-.710,-.235,6.09),(-.728,-.246,6.175)],
        [.151,.143,.125,.12,.097,.061,.077,.066],[.151,.143,.125,.12,.097,.061,.046,.039],M['skin'],steps=10,sides=28)
    parts=[raised]
    fingers=[
      ('index',[(-.665,-.246,6.168),(-.654,-.263,6.235),(-.605,-.276,6.253),(-.573,-.263,6.229)],.018),
      ('middle',[(-.702,-.246,6.186),(-.714,-.266,6.294),(-.683,-.278,6.333),(-.647,-.265,6.315)],.0185),
      ('ring',[(-.740,-.242,6.180),(-.774,-.262,6.265),(-.756,-.280,6.298),(-.723,-.269,6.286)],.0175),
      ('little',[(-.778,-.233,6.155),(-.814,-.245,6.227),(-.812,-.258,6.275),(-.794,-.251,6.284)],.0145),
      ('thumb',[(-.669,-.241,6.080),(-.641,-.282,6.133),(-.595,-.295,6.170),(-.562,-.278,6.159)],.025)]
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
    parts.extend(digit('Hand_grip_thumb',[(.788,-.189,3.240),(.828,-.230,3.202),(.878,-.241,3.162),(.902,-.219,3.126)],.025,M))
    relaxed=union('Body_relaxed_arm_five_fingers',parts,.0065,5);relaxed['digits']=5
    return raised,relaxed

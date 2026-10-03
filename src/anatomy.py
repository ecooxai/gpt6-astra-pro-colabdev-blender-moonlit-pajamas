from geometry import *

def build_hands(M,raised,relaxed):
    parts=[raised,sphere('Hand_raised_palm',(-.647,-.202,6.113),(.085,.044,.126),M['skin'])]
    for i,length in enumerate([.153,.175,.151,.124]):
        root=Vector((-.585-i*.042,-.212,6.204+.015*sin(i)))
        side=-.018 if i>1 else .018
        pts=[root,root+Vector((side,-.015,length*.53)),root+Vector((side*.7,.0,length)),root+Vector((.025,.037,length*.86))]
        r=.014 if i==3 else .017
        parts.append(tube('Hand_raised_digit_'+str(i+1),pts,[r,r*.9,r*.73,r*.55],M['skin'],sides=16))
        parts.append(sphere('Hand_raised_tip_'+str(i),pts[-1],(r*.58,)*3,M['skin'],segments=16,rings=12))
    pts=[(-.59,-.204,6.09),(-.55,-.24,6.13),(-.51,-.25,6.175),(-.48,-.22,6.17)]
    parts.append(tube('Hand_raised_thumb',pts,[.027,.022,.018,.012],M['skin']))
    raised=union('Body_raised_arm_five_fingers',parts,.008,4);raised['digits']=5
    parts=[relaxed,sphere('Hand_grip_palm',(.814,-.175,3.225),(.075,.042,.112),M['skin'],rotation=(0,-.36,0))]
    for i in range(4):
        root=Vector((.811+i*.031,-.178+i*.008,3.155+i*.009))
        pts=[root,root+Vector((.035,-.015,-.047)),root+Vector((.045,.014,-.092)),root+Vector((.025,.064,-.087))]
        r=.013 if i==3 else .016
        parts.append(tube('Hand_grip_digit_'+str(i+1),pts,[r,r*.89,r*.76,r*.54],M['skin'],sides=16))
    pts=[(.775,-.177,3.236),(.827,-.226,3.193),(.876,-.242,3.149),(.888,-.215,3.11)]
    parts.append(tube('Hand_grip_thumb',pts,[.027,.023,.017,.011],M['skin']))
    relaxed=union('Body_relaxed_arm_five_fingers',parts,.008,4);relaxed['digits']=5
    return raised,relaxed

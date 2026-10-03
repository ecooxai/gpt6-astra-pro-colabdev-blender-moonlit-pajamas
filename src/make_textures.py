"""Original drawn textures. No reference image is loaded or analyzed."""
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
import math
OUT=Path(__file__).resolve().parent/'textures';OUT.mkdir(exist_ok=True)
N=1024;S=2
im=Image.new('RGB',(N*S,N*S),(211,242,251));d=ImageDraw.Draw(im)
def bezier(a,b,c,e,n=12):
    return [((1-t)**3*a[0]+3*(1-t)**2*t*b[0]+3*(1-t)*t*t*c[0]+t**3*e[0],(1-t)**3*a[1]+3*(1-t)**2*t*b[1]+3*(1-t)*t*t*c[1]+t**3*e[1]) for t in np.linspace(0,1,n)]
segs=[((-0.84,-.13),(-.93,-.44),(-.96,-.95),(-.73,-.91)),((-.73,-.91),(-.55,-.89),(-.35,-.67),(-.23,-.65)),((-.23,-.65),(-.05,-.69),(.12,-.66),(.27,-.63)),((.27,-.63),(.51,-.89),(.75,-1.02),(.83,-.84)),((.83,-.84),(.9,-.58),(.86,-.29),(.92,-.08)),((.92,-.08),(1.18,.57),(.56,.87),(.00,.85)),((.00,.85),(-.58,.86),(-1.08,.57),(-.84,-.13))]
outline=sum([bezier(*s) for s in segs],[])
def cat(cx,cy,r,a):
    def pt(p):
        x,y=p;return ((cx+r*(x*math.cos(a)-y*math.sin(a)))*N*S,(cy+r*(x*math.sin(a)+y*math.cos(a)))*N*S)
    coords=[pt(p) for p in outline];d.line(coords,fill=(253,255,255),width=7*S,joint='curve')
    for tri in [[(-.75,-.73),(-.40,-.55),(-.68,-.38)],[(.66,-.74),(.39,-.54),(.71,-.39)]]:
        q=[pt(p) for p in tri];d.polygon(q,fill=(224,187,222));d.line(q+[q[0]],fill=(224,187,222),width=3*S,joint='curve')
    for x in [-.34,.34]:
        points=[pt((x+.075*math.cos(t),.13+.108*math.sin(t))) for t in np.linspace(0,2*math.pi,36)]
        d.polygon(points,fill=(252,255,255))
for dx in [-1,0,1]:
    for dy in [-1,0,1]:
        cat(.20+dx,.23+dy,.15,-.18);cat(.72+dx,.28+dy,.15,.23);cat(.45+dx,.77+dy,.158,-.14)
for cx,cy,r in[(.58,.30,.017),(.15,.76,.021),(.90,.14,.013),(.42,.65,.015)]:
    d.ellipse(((cx-r)*N*S,(cy-r)*N*S,(cx+r)*N*S,(cy+r)*N*S),fill=(250,255,255))
im.resize((N,N),Image.Resampling.LANCZOS).save(OUT/'cat_cotton_original.png')
N=512;y,x=np.mgrid[0:N,0:N];X=(x/(N-1)-.5)*2;Y=(y/(N-1)-.5)*2;r=np.sqrt(X*X+Y*Y);a=np.arctan2(Y,X)
base=np.zeros((N,N,3),float);t=np.clip((Y+.75)/1.5,0,1)
for k,(top,bottom) in enumerate(zip([48,34,93],[137,109,207])):base[:,:,k]=top+(bottom-top)*t
stri=(np.sin(a*54+np.sin(a*17)*2)+np.sin(a*117+r*18))*(np.clip((r-.23)*1.3,0,1))*4
base+=stri[:,:,None]
limbus=np.clip((r-.85)/.13,0,1);base=base*(1-limbus[:,:,None]*.76)
blue=np.exp(-((X+.25)**2/.11+(Y-.62)**2/.08));base=base*(1-blue[:,:,None]*.5)+np.array([107,177,235])*blue[:,:,None]*.5
pupil=(X/.27)**2+(Y/.60)**2<1;base[pupil]=[34,27,67];base[r>1]=[27,23,56]
ir=Image.fromarray(np.uint8(np.clip(base,0,255)),'RGB');di=ImageDraw.Draw(ir)
di.ellipse((111,62,173,147),fill=(255,252,255));di.ellipse((290,335,317,364),fill=(225,249,255));di.ellipse((119,334,143,374),fill=(127,213,254));di.polygon([(274,341),(292,356),(280,393),(269,373)],fill=(182,106,206));di.polygon([(141,346),(154,360),(147,393),(132,380)],fill=(109,190,239));ir.save(OUT/'violet_iris_original.png')
N=1024;yy,xx=np.mgrid[0:N,0:N];u=xx/(N-1);v=1-yy/(N-1);skin=np.empty((N,N,3),float);skin[:]=[255,239,234]
for c in [.385,.615]:
    w=np.exp(-((u-c)/.043)**2-((v-.27)/.068)**2)*.42;skin=skin*(1-w[:,:,None])+np.array([244,157,165])*w[:,:,None]
Image.fromarray(np.uint8(np.clip(skin,0,255)),'RGB').save(OUT/'face_wash_original.png')
print('Created original cotton, iris, and face textures')

# Root-color transitions are authored gradients, never sampled reference pixels.
height,width=256,32
v=1-np.arange(height)[:,None]/(height-1);u=np.arange(width)[None,:]/(width-1)
t=np.clip(v/.38,0,1);t=t*t*(3-2*t)
for name,color in [('hairlight_roots_original.png',[136,129,178]),('hairdark_roots_original.png',[93,84,127])]:
    root=np.array([119,114,162]);target=np.array(color)
    rgb=root[None,None,:]*(1-t[:,:,None])+target[None,None,:]*t[:,:,None]
    rgb=np.broadcast_to(rgb,(height,width,3)).copy()
    rgb+=3*np.exp(-((u-.43)/.24)**2)[:,:,None]*np.sin(np.pi*v)[:,:,None]
    Image.fromarray(np.uint8(np.clip(rgb,0,255)),'RGB').save(OUT/name)

# Original common-height hair palettes: continuous crown, deeper lower locks.
height,width=512,16
v=1-np.arange(height,dtype=float)[:,None]/(height-1)
t=np.clip((v-.12)/.84,0,1);t=t*t*(3-2*t)
root=np.array([123.,121.,171.]);tip=np.array([83.,76.,124.])
base=tip[None,None,:]*(1-t[:,:,None])+root[None,None,:]*t[:,:,None]
fall=np.clip((.985-v)/.30,0,1);fall=fall*fall*(3-2*fall)
for name,delta in [('hair_base_height_original.png',[0,0,0]),('hair_light_height_original.png',[9,8,12]),('hair_dark_height_original.png',[-8,-7,-9])]:
    rgb=base+np.array(delta)[None,None,:]*fall[:,:,None]
    rgb=np.broadcast_to(rgb,(height,width,3)).copy()
    Image.fromarray(np.uint8(np.clip(rgb,0,255)),'RGB').save(OUT/name)

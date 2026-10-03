"""Publish actual files and explicitly reviewed iterations to the live preview."""
from pathlib import Path
import json,datetime,argparse,shutil
from io_helpers import atomic_copy
ROOT=Path(__file__).resolve().parents[1];OUT=Path('/build')/ROOT.name;PREVIEW=ROOT/'preview'
p=argparse.ArgumentParser();p.add_argument('--revision',required=True);p.add_argument('--score',type=int);p.add_argument('--title',required=True);p.add_argument('--notes',required=True);p.add_argument('--review',action='store_true');a=p.parse_args()
previous=json.loads((PREVIEW/'status.json').read_text())
previous_views={Path(f['url']).stem.removeprefix(ROOT.name+'_'):f.get('revision','unknown') for f in previous.get('renders',[])}
staged_views={}
pending=OUT/'pending-preview'
if pending.exists() and a.review:
    staged_stats=pending/'model_stats.json'
    if not staged_stats.exists() or json.loads(staged_stats.read_text()).get('revision')!=a.revision:
        raise SystemExit('Refusing to publish missing or mismatched staged model revision')
    metadata=pending/'render_versions.json'
    if metadata.exists():staged_views=json.loads(metadata.read_text())
    for source in pending.iterdir():
        if source.is_file():atomic_copy(source,PREVIEW/'assets'/source.name)
status_path=PREVIEW/'status.json';d=json.loads(status_path.read_text());now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
d.update(revision=a.revision,phase=a.title,note=a.notes,updated=now)
if a.review:
    d.pop('sourceCommit',None);d.pop('archiveRevision',None)
stats=PREVIEW/'assets/model_stats.json'
if stats.is_file():d['modelRevision']=json.loads(stats.read_text()).get('revision',a.revision)
files=[]
for ext,label in [('glb','Interactive 3D model · GLB'),('blend','Editable Blender source · BLEND')]:
    f=PREVIEW/'assets'/(ROOT.name+'.'+ext)
    if f.is_file():
        size=f.stat().st_size;files.append(dict(label=label,url='assets/'+f.name,size=f'{size/1048576:.1f} MB',path=str(f)))
        if ext=='glb':d['model']='assets/'+f.name
renders=[]
for view,label in [('front','Front silhouette'),('quarter','Three-quarter'),('back','Back construction'),('face','Face & expression'),('side','Right-side anatomy'),('left','Left-side anatomy'),('hand_side','Raised hand profile'),('hand','Raised hand detail'),('grip','Pillow grip detail'),('feet','Slippers and ribbons'),('cuffs','Rounded cotton gathers')]:
    f=PREVIEW/'assets'/(ROOT.name+'_'+view+'.png')
    if f.is_file():renders.append(dict(label=label,url='assets/'+f.name,path=str(f)))

for item in renders:
    view=Path(item['url']).stem.removeprefix(ROOT.name+'_')
    item['revision']=staged_views.get(view,previous_views.get(view,'unknown'))
web=PREVIEW/'assets'/(ROOT.name+'_web.glb')
if web.exists():
    files.insert(0,dict(label='Optimized interactive model · GLB',url='assets/'+web.name,size=f'{web.stat().st_size/1048576:.1f} MB',path=str(web)))
    d['model']='assets/'+web.name
for name,label in [('validation.json','Model validation'),('browser_validation.json','Desktop / mobile test report'),('hand_audit.json','Hand surface audit'),('contact_surface_audit.json','Fingertip / headband contact audit')]:
    f=PREVIEW/'assets'/name
    if f.exists():files.append(dict(label=label,url='assets/'+name,size='JSON',path=str(f)))
renders.sort(key=lambda item:(-int(item.get('revision','R00')[1:]),0 if 'front.png' in item['url'] else 1))
files.append(dict(label='Render studies and rejected trials',url='studies/index.html',size=f"{len(list((PREVIEW/'studies').glob('T*.png')))} studies",path=str(PREVIEW/'studies/index.html')))
d['files']=files;d['renders']=renders
history=PREVIEW/'history';history.mkdir(exist_ok=True)
if a.review:
    if a.score is None:raise SystemExit('Reviewed passes require an explicit subjective score.')
    image=ROOT/'renders/review'/(a.revision+'-front.png')
    if not image.is_file():raise SystemExit('Cannot journal a review without an actual front render.')
    shutil.copy2(image,history/image.name)
    d['journal']=[j for j in d.get('journal',[]) if j['revision']!=a.revision]
    d['journal'].append(dict(revision=a.revision,title=a.title,notes=a.notes,score=a.score,time=now,kind='Subjective visual review',image='history/'+image.name))
    d['score']=a.score
    d['iterations']=len(d['journal'])
status_path.with_suffix('.tmp').write_text(json.dumps(d,indent=2));status_path.with_suffix('.tmp').replace(status_path)
print(json.dumps(dict(revision=d['revision'],reviewed_iterations=d['iterations'],score=d['score'],files=len(files),renders=len(renders))))

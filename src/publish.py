"""Publish actual files and explicitly reviewed iterations to the live preview."""
from pathlib import Path
import json,datetime,argparse,shutil
ROOT=Path(__file__).resolve().parents[1];OUT=Path('/build')/ROOT.name;PREVIEW=ROOT/'preview'
p=argparse.ArgumentParser();p.add_argument('--revision',required=True);p.add_argument('--score',type=int);p.add_argument('--title',required=True);p.add_argument('--notes',required=True);p.add_argument('--review',action='store_true');a=p.parse_args()
status_path=PREVIEW/'status.json';d=json.loads(status_path.read_text());now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
d.update(revision=a.revision,phase=a.title,note=a.notes,updated=now)
stats=PREVIEW/'assets/model_stats.json'
if stats.is_file():d['modelRevision']=json.loads(stats.read_text()).get('revision',a.revision)
files=[]
for ext,label in [('glb','Interactive 3D model · GLB'),('blend','Editable Blender source · BLEND'),('zip','Complete project · ZIP')]:
    f=PREVIEW/'assets'/(ROOT.name+'.'+ext)
    if f.is_file():
        size=f.stat().st_size;files.append(dict(label=label,url='assets/'+f.name,size=f'{size/1048576:.1f} MB',path=str(f)))
        if ext=='glb':d['model']='assets/'+f.name
renders=[]
for view,label in [('front','Front silhouette'),('quarter','Three-quarter'),('back','Back construction'),('face','Face & expression'),('side','Side anatomy')]:
    f=PREVIEW/'assets'/(ROOT.name+'_'+view+'.png')
    if f.is_file():renders.append(dict(label=label,url='assets/'+f.name,path=str(f)))

for item in renders:
    view=Path(item['url']).stem.rsplit('_',1)[-1]
    versions=list((ROOT/'renders/review').glob('R*-'+view+'.png'))
    if versions:item['revision']=max(versions,key=lambda p:int(p.stem.split('-')[0][1:])).stem.split('-')[0]
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

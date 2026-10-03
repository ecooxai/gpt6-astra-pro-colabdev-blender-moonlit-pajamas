"""Archive an immutable Git commit and optionally publish its preview to Pages."""
from pathlib import Path
import subprocess,zipfile,shutil,json,argparse
ROOT=Path(__file__).resolve().parents[1];PREVIEW=ROOT/'preview';ASSETS=PREVIEW/'assets';OUT=Path('/build')/ROOT.name

def run(args,cwd=ROOT):
    r=subprocess.run(args,cwd=cwd,capture_output=True,text=True)
    if r.returncode:raise RuntimeError(r.stderr[-2000:] or r.stdout[-2000:])
    return r.stdout.strip()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--deploy',action='store_true');a=parser.parse_args()
    commit=run(['git','rev-parse','HEAD']);status=json.loads((PREVIEW/'status.json').read_text());stats=json.loads((ASSETS/'model_stats.json').read_text())
    assert status['modelRevision']==stats['revision'],'Model/review revision mismatch'
    dest=ASSETS/(ROOT.name+'.zip');run(['git','archive','--format=zip','--prefix='+ROOT.name+'/','--output='+str(dest),commit])
    item={'label':'Complete source and model · ZIP','url':'assets/'+dest.name,'size':f'{dest.stat().st_size/1048576:.1f} MB','path':str(dest)}
    status['files']=[f for f in status['files'] if not f['url'].endswith('.zip')]+[item];status['sourceCommit']=commit;(PREVIEW/'status.json').write_text(json.dumps(status,indent=2))
    print('ARCHIVE',str(dest),dest.stat().st_size,'COMMIT',commit)
    if a.deploy:
        pages=OUT/'pages-deploy';pages.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(dest) as archive:
            prefix=ROOT.name+'/preview/'
            for info in archive.infolist():
                if not info.filename.startswith(prefix) or info.is_dir():continue
                rel=Path(info.filename[len(prefix):]);assert '..' not in rel.parts
                target=pages/rel;target.parent.mkdir(parents=True,exist_ok=True)
                with archive.open(info) as src,open(target,'wb') as dst:shutil.copyfileobj(src,dst)
        shutil.copy2(dest,pages/'assets'/dest.name);shutil.copy2(PREVIEW/'status.json',pages/'status.json');(pages/'.nojekyll').touch()
        run(['git','add','.'],pages)
        if subprocess.run(['git','diff','--cached','--quiet'],cwd=pages).returncode:
            run(['git','commit','-m','Deploy reviewed '+status['revision']+' with immutable archive'],pages)
        run(['git','push','origin','gh-pages'],pages)
        print('DEPLOYED',status['revision'])

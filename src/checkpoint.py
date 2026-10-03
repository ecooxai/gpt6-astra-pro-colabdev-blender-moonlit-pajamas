"""Archive a reviewed Git commit; store its ZIP as a release asset and deploy Pages."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/'preview';ASSETS=PREVIEW/'assets';OUT=Path('/build')/ROOT.name

def run(args,cwd=ROOT):
    r=subprocess.run(args,cwd=cwd,capture_output=True,text=True)
    if r.returncode:raise RuntimeError(r.stderr[-2400:] or r.stdout[-2400:])
    return r.stdout.strip()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--deploy',action='store_true');args=parser.parse_args()
    if run(['git','status','--porcelain','--untracked-files=no']):
        raise RuntimeError('Commit tracked changes before making an immutable checkpoint.')
    commit=run(['git','rev-parse','HEAD'])
    status=json.loads((PREVIEW/'status.json').read_text())
    stats=json.loads((ASSETS/'model_stats.json').read_text())
    if status['modelRevision']!=stats['revision']:raise RuntimeError('Model/review revision mismatch.')
    gate=json.loads((ASSETS/'release_validation.json').read_text())
    if gate.get('revision')!=stats['revision'] or gate.get('result')!='PASS':raise RuntimeError('Missing current release-validation gate.')
    revision=stats['revision'];dest=ASSETS/(ROOT.name+'.zip');partial=dest.with_suffix('.zip.partial')
    run(['git','archive','--format=zip','--prefix='+ROOT.name+'/','--output='+str(partial),commit])
    metadata={'sourceCommit':commit,'geometrySourceCommit':stats.get('geometry_source_commit'),
              'modelRevision':revision,'scope':'Immutable Git source, model, tests and preview snapshot; ZIP excludes Git internals and installed dependencies.'}
    with zipfile.ZipFile(partial,'a',compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(ROOT.name+'/CHECKPOINT.json',json.dumps(metadata,indent=2))
    with zipfile.ZipFile(partial) as archive:
        bad=archive.testzip()
        if bad:raise RuntimeError('Archive CRC failure: '+bad)
        required=[ROOT.name+'/src/build_character.py',ROOT.name+'/Agents.md',ROOT.name+'/preview/assets/'+ROOT.name+'.blend',ROOT.name+'/preview/assets/'+ROOT.name+'_web.glb']
        if any(name not in archive.namelist() for name in required):raise RuntimeError('Archive is missing required project files.')
    partial.replace(dest)
    digest=hashlib.sha256(dest.read_bytes()).hexdigest()
    checksum=dest.with_suffix('.zip.sha256');checksum.write_text(digest+'  '+dest.name+'\n')
    url='assets/'+dest.name;release_url=None;tag=None
    if args.deploy:
        repo=run(['gh','repo','view','--json','nameWithOwner','--jq','.nameWithOwner'])
        tag='checkpoint-'+revision.lower()+'-'+commit[:8]
        probe=subprocess.run(['gh','api','repos/'+repo+'/releases/tags/'+tag],cwd=ROOT,capture_output=True,text=True)
        if probe.returncode:
            run(['gh','release','create',tag,'--repo',repo,'--target',commit,'--title',revision+' · Moonlit Blender checkpoint','--notes','Reviewed procedural Blender character, source, web viewer, inspection renders and validation reports. Scores are subjective visual assessments; unperformed iterations are not counted.'])
        run(['gh','release','upload',tag,str(dest),str(checksum),'--repo',repo,'--clobber'])
        release=json.loads(run(['gh','api','repos/'+repo+'/releases/tags/'+tag]))
        asset=next(a for a in release['assets'] if a['name']==dest.name)
        if asset['size']!=dest.stat().st_size:raise RuntimeError('Uploaded archive size mismatch.')
        url=asset['browser_download_url'];release_url=release['html_url']
    item={'label':'Complete source, model and review history · ZIP','url':url,'size':f'{dest.stat().st_size/1048576:.1f} MB','path':str(dest)}
    status['files']=[f for f in status['files'] if not f['url'].endswith('.zip')]+[item]
    status['sourceCommit']=commit;status['archiveRevision']=revision;status['archiveSha256']=digest
    if release_url:status['releaseUrl']=release_url
    (PREVIEW/'status.json').write_text(json.dumps(status,indent=2))
    receipt={**metadata,'archiveBytes':dest.stat().st_size,'archiveSha256':digest,'archiveCrc':'PASS','archiveUrl':url,'releaseUrl':release_url,'releaseTag':tag}
    print('ARCHIVE_VERIFIED',dest.stat().st_size,digest,flush=True)
    if args.deploy:
        pages=OUT/'pages-deploy';pages.mkdir(parents=True,exist_ok=True)
        if not (pages/'.git').exists():
            if any(pages.iterdir()):raise RuntimeError('Deployment folder is not an empty Git checkout.')
            remote=run(['git','remote','get-url','origin'])
            run(['git','clone','--depth','1','--single-branch','--branch','gh-pages',remote,str(pages)])
            for key in ['user.name','user.email']:run(['git','config',key,run(['git','config',key])],pages)
        else:run(['git','pull','--ff-only','origin','gh-pages'],pages)
        with zipfile.ZipFile(dest) as archive:
            prefix=ROOT.name+'/preview/'
            for info in archive.infolist():
                if not info.filename.startswith(prefix) or info.is_dir():continue
                rel=Path(info.filename[len(prefix):])
                if '..' in rel.parts or rel.is_absolute():raise RuntimeError('Unsafe archive path.')
                target=pages/rel;target.parent.mkdir(parents=True,exist_ok=True)
                with archive.open(info) as src,open(target,'wb') as dst:shutil.copyfileobj(src,dst)
        old_zip=pages/'assets'/dest.name
        if old_zip.exists():old_zip.unlink()  # ZIP is stored as a release asset, not in Pages Git.
        shutil.copy2(PREVIEW/'status.json',pages/'status.json');(pages/'.nojekyll').touch()
        run(['git','add','.'],pages)
        if subprocess.run(['git','diff','--cached','--quiet'],cwd=pages).returncode:
            run(['git','commit','-m','Deploy reviewed '+revision+' with verified immutable release archive'],pages)
        run(['git','push','origin','gh-pages'],pages)
        receipt['pagesCommit']=run(['git','rev-parse','HEAD'],pages)
        receipt['pagesUrl']=run(['gh','api','repos/'+repo+'/pages','--jq','.html_url'])
        print('DEPLOYED_URL',receipt['pagesUrl'],flush=True)
        print('RELEASE_URL',release_url,flush=True)
    (ASSETS/'checkpoint_receipt.json').write_text(json.dumps(receipt,indent=2))
    print('CHECKPOINT_COMPLETE',revision,commit,flush=True)

if __name__=='__main__':main()

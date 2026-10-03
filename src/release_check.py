"""Require matching reviewed assets and genuine test reports before packaging."""
from pathlib import Path
import datetime
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1];ASSETS=ROOT/'preview/assets'

def check():
    def read(name):return json.loads((ASSETS/name).read_text())
    status=json.loads((ROOT/'preview/status.json').read_text());stats=read('model_stats.json');rev=stats['revision']
    if status['modelRevision']!=rev or status['revision']!=rev:raise RuntimeError('Review/model revision mismatch')
    for name in ['validation.json','hand_audit.json','contact_surface_audit.json']:
        d=read(name)
        if d.get('revision')!=rev or d.get('result')!='PASS':raise RuntimeError('Stale or failing report: '+name)
    browser=read('browser_validation.json')
    if browser.get('result')!='PASS' or browser.get('errors'):raise RuntimeError('Browser errors remain')
    if len(browser.get('report',[]))!=2:raise RuntimeError('Missing desktop/mobile test report')
    for device in browser['report']:
        if device.get('revision')!=rev or device.get('result')!='PASS':raise RuntimeError('Stale/failing browser result')
        if device.get('galleryImages')!=11 or device.get('drawCalls',999)>48:raise RuntimeError('Browser gallery or draw-call check failed')
    expected={'front','face','quarter','side','left','back','hand','hand_side','grip','feet','cuffs'}
    versions=read('render_versions.json')
    if set(versions)!=expected or any(r!=rev for r in versions.values()):raise RuntimeError('Inspection set is not entirely current')
    if len(status.get('renders',[]))!=11 or any(r.get('revision')!=rev for r in status['renders']):raise RuntimeError('Published view labels are stale')
    files=[]
    for f in sorted(ASSETS.iterdir()):
        if not f.is_file() or not (f.name.startswith(ROOT.name) and f.suffix in {'.glb','.blend','.png'}):continue
        files.append({'file':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
    report={'revision':rev,'result':'PASS','testedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
            'geometrySourceCommit':stats.get('geometry_source_commit'),'retainedModelReviews':len(status['journal']),
            'renderStudies':len(list((ROOT/'preview/studies').glob('T*.png'))),'inspectionViews':len(expected),
            'scope':'Revision integrity, required files and test-report consistency. This does not certify visual similarity or AAA production readiness.',
            'files':files}
    (ASSETS/'release_validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2))
    return report

if __name__=='__main__':check()

"""Expose actual retained render files, never invented or lost review images."""
from pathlib import Path
import json,shutil,html
ROOT=Path(__file__).resolve().parents[1];PREVIEW=ROOT/'preview'

def update():
    path=PREVIEW/'status.json';d=json.loads(path.read_text())
    for entry in d['journal']:
        revision=entry['revision'];sources=sorted((ROOT/'renders/review').glob(revision+'-*.png'))
        if not sources:
            old=PREVIEW/'history'/(revision+'-front.png')
            if old.exists():sources=[old]
        if not sources:continue
        folder=PREVIEW/'history'/revision;folder.mkdir(parents=True,exist_ok=True);cards=[]
        for source in sources:
            name=source.name.split('-',1)[1];shutil.copy2(source,folder/name)
            cards.append('<article><a href="'+html.escape(name)+'"><img loading="lazy" src="'+html.escape(name)+'"></a><h2>'+html.escape(name)+'</h2><code>'+html.escape(str(source))+'</code></article>')
        text='<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+revision+' · Moonlit inspection</title><style>body{margin:40px;background:#11121a;color:#e8e7f2;font:16px system-ui}a{color:#bbb0ef}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:24px}img{width:100%;height:460px;object-fit:contain;background:#1d1e29;border-radius:12px}code{font-size:11px;overflow-wrap:anywhere}h2{font-size:15px}</style><a href="../../index.html">← Character studio</a><h1>'+revision+' · '+html.escape(entry['title'])+'</h1><p>'+str(entry['score'])+'/100 · Subjective visual review. Only actual retained renders are shown.</p><main>'+''.join(cards)+'</main></html>'
        (folder/'index.html').write_text(text);entry['image']='history/'+revision+'/index.html'
    path.write_text(json.dumps(d,indent=2))
if __name__=='__main__':update()
